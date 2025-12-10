#include <uapi/linux/ptrace.h>  // Required for BPF kprobes and pt_regs
#include <net/sock.h>            // Kernel socket structures
#include <net/tcp.h>             // TCP-specific socket structures
#include <bcc/proto.h>           // Helper macros for BPF programs

// Define the structure of a TCP event to send to user space
struct tcp_event_t {
    u32 pid;           // Process ID of the sender
    u32 saddr;         // Source IP address (IPv4)
    u32 daddr;         // Destination IP address (IPv4)
    u16 sport;         // Source port
    u16 dport;         // Destination port
    u32 srtt_us;       // Smoothed round-trip time (in microseconds)
    u32 rtt_var;       // RTT variance (in microseconds)
    u64 bytes_sent;    // Total bytes sent by this PID so far
    u64 timestamp_ns;  // Timestamp in nanoseconds when event was captured
};

// Define a hash map to track bytes sent per PID
// Key: PID, Value: total bytes sent
BPF_HASH(pid_tracker, u32, u64);

// Define a perf buffer to send events to user space
BPF_PERF_OUTPUT(tcp_events);

// Main function hooked to tcp_sendmsg kernel function
// This fires every time a TCP message is sent
int trace_tcp_sendmsg(struct pt_regs *ctx, struct sock *sk, struct msghdr *msg, size_t size) {
    // If socket pointer is NULL, exit early
    if (!sk) return 0;

    // --- FILTER ONLY TCP SOCKETS ---
    u8 protocol;
    bpf_probe_read_kernel(&protocol, sizeof(protocol), &sk->sk_protocol); // read protocol type
    if (protocol != IPPROTO_TCP) return 0;  // skip non-TCP sockets

    // --- FILTER ONLY IPV4 SOCKETS ---
    u16 family;
    bpf_probe_read_kernel(&family, sizeof(family), &sk->__sk_common.skc_family); // read address family
    if (family != AF_INET) return 0; // skip non-IPv4 sockets

    // Initialize an event structure to send to user space
    struct tcp_event_t event = {};
    
    // Get PID of current process
    u64 pid_tgid = bpf_get_current_pid_tgid();
    event.pid = pid_tgid >> 32;  // upper 32 bits is PID
    
    // Record the current timestamp in nanoseconds
    event.timestamp_ns = bpf_ktime_get_ns();

    // --- READ SOCKET ADDRESSES ---
    bpf_probe_read_kernel(&event.saddr, sizeof(event.saddr), &sk->__sk_common.skc_rcv_saddr); // source IP
    bpf_probe_read_kernel(&event.daddr, sizeof(event.daddr), &sk->__sk_common.skc_daddr);     // dest IP
    bpf_probe_read_kernel(&event.sport, sizeof(event.sport), &sk->__sk_common.skc_num);      // source port

    // Destination port is stored in network byte order, convert to host order
    u16 dport;
    bpf_probe_read_kernel(&dport, sizeof(dport), &sk->__sk_common.skc_dport);
    event.dport = ntohs(dport);

    // --- FILTER ONLY TRAFFIC FROM PORT 8000 ---
    if (event.sport != 8000) {
        return 0; // ignore packets not from our port of interest
    }

    // --- READ TCP-LEVEL METRICS ---
    struct tcp_sock *tp = (struct tcp_sock *)sk;  // cast generic socket to TCP socket
    u32 srtt, rttvar;
    bpf_probe_read_kernel(&srtt, sizeof(srtt), &tp->srtt_us);    // read smoothed RTT
    bpf_probe_read_kernel(&rttvar, sizeof(rttvar), &tp->mdev_us); // read RTT variance
    event.srtt_us = srtt;
    event.rtt_var = rttvar;

    // --- TRACK TOTAL BYTES PER PID ---
    u32 pid = event.pid;
    u64 *total_bytes = pid_tracker.lookup(&pid); // lookup previous total
    u64 current_total = 0;
    if (total_bytes) {
        current_total = *total_bytes; // if exists, use it
    }
    current_total += size; // add current message size
    pid_tracker.update(&pid, &current_total); // store updated total

    // Store total bytes in event
    event.bytes_sent = current_total;

    // --- SEND EVENT TO USER SPACE ---
    tcp_events.perf_submit(ctx, &event, sizeof(event)); // send event to perf buffer

    return 0; // return 0 to indicate success
}

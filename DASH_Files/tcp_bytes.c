#include <uapi/linux/ptrace.h>   // Needed for tracing kernel functions
#include <linux/tcp.h>            // Definitions related to TCP connections
#include <linux/sched.h>          // Access task info (like PID)

// Define a struct to hold the data we want to capture
struct data_t {
    u32 pid;       // Process ID of the process receiving the data
    u64 bytes;     // Number of bytes received in this TCP call
    u64 ts_ns;     // Timestamp in nanoseconds
};

// Define a perf buffer to send events from kernel to user space
BPF_PERF_OUTPUT(events);

// This function is attached to a kernel function (kprobe) like tcp_cleanup_rbuf
int trace_tcp_recv(struct pt_regs *ctx, struct sock *sk, int copied) {
    // Ignore calls where no bytes were actually copied
    if (copied <= 0)
        return 0;

    // Initialize our data struct
    struct data_t data = {};

    // Get the current process PID (upper 32 bits of PID/TGID)
    data.pid = bpf_get_current_pid_tgid() >> 32;

    // Store how many bytes were copied in this TCP call
    data.bytes = copied;

    // Store the current time in nanoseconds
    data.ts_ns = bpf_ktime_get_ns();

    // Send this data to user space via the perf buffer
    events.perf_submit(ctx, &data, sizeof(data));

    return 0; // Let the kernel function continue
}

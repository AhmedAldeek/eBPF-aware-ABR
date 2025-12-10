from bcc import BPF
import ctypes
import time
import struct
import threading
import json
from collections import defaultdict, deque
from websocket_server import WebsocketServer
import socket
import sys
import os

# === Load eBPF Program ===
bpf = BPF(src_file="tcp_metrics.c")
bpf.attach_kprobe(event="tcp_sendmsg", fn_name="trace_tcp_sendmsg")

# === Event Structure from tcp_metrics.c ===
class TcpEvent(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_uint),
        ("saddr", ctypes.c_uint),
        ("daddr", ctypes.c_uint),
        ("sport", ctypes.c_ushort),
        ("dport", ctypes.c_ushort),
        ("srtt_us", ctypes.c_uint),
        ("rtt_var", ctypes.c_uint),
        ("bytes_sent", ctypes.c_ulonglong),
        ("timestamp_ns", ctypes.c_ulonglong)
    ]

# === Global metrics storage ===
connection_metrics = defaultdict(lambda: {
    'bytes_history': deque(maxlen=5),
    'time_history': deque(maxlen=5),
    'throughput_history': deque(maxlen=3),
    'rtt_history': deque(maxlen=5),
    'jitter_history': deque(maxlen=5),
    'last_bytes': 0,
    'last_update': time.time()
})

# Latest global values
latest_metrics = {
    'throughput_kbps': 0,
    'rtt_ms': 0,
    'jitter_ms': 0,
    'timestamp': time.time()
}

# === WebSocket server (global ref) ===
ws_server = None

# ---------- Metric Calculations ----------
def calculate_smoothed_metrics(pid, current_bytes, current_time):
    metrics = connection_metrics[pid]
    
    if metrics['last_bytes'] == 0:
        metrics['last_bytes'] = current_bytes
        metrics['last_update'] = current_time
        return 0
    
    bytes_diff = current_bytes - metrics['last_bytes']
    time_diff = current_time - metrics['last_update']
    
    throughput_kbps = 0
    if time_diff > 0 and bytes_diff >= 0:
        throughput_kbps = (bytes_diff * 8) / time_diff / 1000  # bits → kbps
    
    if 0 <= throughput_kbps <= 100000:
        metrics['throughput_history'].append(throughput_kbps)
    
    smoothed = 0
    if metrics['throughput_history']:
        sorted_tput = sorted(metrics['throughput_history'])
        smoothed = sorted_tput[len(sorted_tput) // 2]
    
    metrics['last_bytes'] = current_bytes
    metrics['last_update'] = current_time
    return max(0, smoothed)

# ---------- eBPF Event Handler ----------
def print_event(cpu, data, size):
    event = ctypes.cast(data, ctypes.POINTER(TcpEvent)).contents
    pid = event.pid
    current_time = time.time()
    
    # Only monitor DASH-related traffic (port 8000)
    if not (event.dport == 8000 or event.sport == 8000):
        return
    
    # Throughput
    throughput_kbps = calculate_smoothed_metrics(pid, event.bytes_sent, current_time)
    
    # RTT / Jitter
    rtt_ms = max(1, event.srtt_us / 1000.0)
    jitter_ms = max(0.1, event.rtt_var / 1000.0)
    
    metrics = connection_metrics[pid]
    metrics['rtt_history'].append(rtt_ms)
    metrics['jitter_history'].append(jitter_ms)
    
    smoothed_rtt = sum(metrics['rtt_history']) / len(metrics['rtt_history'])
    smoothed_jitter = sum(metrics['jitter_history']) / len(metrics['jitter_history'])
    
    if throughput_kbps > 0:
        latest_metrics.update({
            'throughput_kbps': throughput_kbps,
            'rtt_ms': smoothed_rtt,
            'jitter_ms': smoothed_jitter,
            'timestamp': current_time
        })
        try:
            saddr = socket.inet_ntoa(struct.pack("I", event.saddr))
            daddr = socket.inet_ntoa(struct.pack("I", event.daddr))
        except:
            saddr = str(event.saddr)
            daddr = str(event.daddr)
        print(f"📡 DASH: {throughput_kbps:.1f}kbps, RTT: {smoothed_rtt:.1f}ms ({saddr}:{event.sport} → {daddr}:{event.dport})")

bpf["tcp_events"].open_perf_buffer(print_event)

# ---------- WebSocket Handlers ----------
def new_client(client, server):
    print(f"🎯 New WebSocket client connected: {client['address']}")
    send_bandwidth(client, server)

def client_left(client, server):
    print(f"⚠️ WebSocket client disconnected: {client['address']}")

def send_bandwidth(client, server):
    try:
        if latest_metrics['throughput_kbps'] > 0:
            msg = json.dumps({
                'throughput_kbps': round(latest_metrics['throughput_kbps'], 2),
                'rtt_ms': round(latest_metrics['rtt_ms'], 2),
                'jitter_ms': round(latest_metrics['jitter_ms'], 2),
                'timestamp': time.time()
            })
            server.send_message(client, msg)
    except Exception as e:
        print(f"❌ Error sending metrics: {e}")

def broadcast_metrics():
    """Send metrics to all clients every second"""
    while True:
        try:
            if ws_server and latest_metrics['throughput_kbps'] > 0:
                msg = json.dumps({
                    'throughput_kbps': round(latest_metrics['throughput_kbps'], 2),
                    'rtt_ms': round(latest_metrics['rtt_ms'], 2),
                    'jitter_ms': round(latest_metrics['jitter_ms'], 2),
                    'timestamp': time.time()
                })
                ws_server.send_message_to_all(msg)
            time.sleep(1)
        except Exception as e:
            print(f"❌ Broadcast error: {e}")
            time.sleep(1)

# ---------- WebSocket + BPF ----------
def run_websocket_server():
    global ws_server
    print("🚀 Starting WebSocket server on port 5000...")
    ws_server = WebsocketServer(port=5000, host='0.0.0.0')
    ws_server.set_fn_new_client(new_client)
    ws_server.set_fn_client_left(client_left)
    
    t = threading.Thread(target=broadcast_metrics, daemon=True)
    t.start()
    
    print("✅ WebSocket server ready - waiting for connections...")
    ws_server.run_forever()

def run_bpf_monitor():
    print("🔍 Starting TCP metrics monitoring for DASH traffic...")
    while True:
        try:
            bpf.perf_buffer_poll(timeout=100)
        except Exception as e:
            print(f"❌ BPF monitor error: {e}")
            time.sleep(1)

# ---------- Main ----------
if __name__ == "__main__":
    # Start WebSocket in background
    ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()

    # Wait for WebSocket to be ready
    time.sleep(2)
    print("🎯 Starting BPF monitoring - waiting for DASH traffic on port 8000...")

    # Start BPF monitor in background
    bpf_thread = threading.Thread(target=run_bpf_monitor, daemon=True)
    bpf_thread.start()

    print("✅ eBPF agent and WebSocket server are running in the background.")

    # Keep alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("🛑 Agent interrupted, exiting.")
        sys.exit(0)

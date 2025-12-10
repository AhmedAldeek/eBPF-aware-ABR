from bcc import BPF
from websocket_server import WebsocketServer
import json, time
from threading import Thread

# Load eBPF
bpf = BPF(src_file="tcp_bytes.c")
bpf.attach_kprobe(event="tcp_cleanup_rbuf", fn_name="trace_tcp_recv")

bytes_accum = 0

# Perf buffer callback
def perf_callback(cpu, data, size):
    global bytes_accum
    event = bpf["events"].event(data)
    bytes_accum += event.bytes

def poll_perf():
    bpf["events"].open_perf_buffer(perf_callback)
    while True:
        bpf.perf_buffer_poll(timeout=100)

Thread(target=poll_perf, daemon=True).start()

# Send bandwidth to client
def send_bandwidth(client, server):
    global bytes_accum
    kbps = (bytes_accum * 8) / 1000
    now = time.time() * 1000  # ms

    # Measure prep + send overhead
    start = time.time() * 1000
    message = json.dumps({
        "bandwidth_kbps": kbps,
        "timestamp": now  # when Python produced the metric
    })
    server.send_message(client, message)
    end = time.time() * 1000

    print(f"📤 Sent metric: {kbps:.2f} kbps at {now}, PythonPrepCost={(end - start):.4f} ms")
    bytes_accum = 0

def run_server():
    server = WebsocketServer(port=5000, host='0.0.0.0')

    def broadcast():
        while True:
            loop_start = time.time() * 1000
            time.sleep(1)
            for client in server.clients:
                send_bandwidth(client, server)
            loop_end = time.time() * 1000
            print(f"⏱ Python loop overhead: {(loop_end - loop_start):.4f} ms to prepare+send all metrics")

    Thread(target=broadcast, daemon=True).start()
    server.run_forever()

print("Python eBPF WebSocket server running on ws://localhost:5000")
run_server()

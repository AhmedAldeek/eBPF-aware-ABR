import { BPF } from '@nabla/ebpf';
import fs from 'fs';
import WebSocket from 'ws';

// DASH WebSocket server
const wss = new WebSocket.Server({ port: 4000 });
console.log('Node.js eBPF agent running on ws://localhost:4000');

let clients = [];
wss.on('connection', (ws) => {
    clients.push(ws);
    ws.on('close', () => {
        clients = clients.filter(c => c !== ws);
    });
});

async function main() {
    // Load eBPF object file
    const prog = await BPF.load(fs.readFileSync('tcp_bytes.o'));

    // Attach kprobe to tcp_cleanup_rbuf
    await prog.attachKprobe('tcp_cleanup_rbuf', 'bpf_tcp_recv');

    // Open perf buffer
    const perf = prog.openPerfBuffer('events', (cpu, data) => {
        // Parse struct: u32 pid, u64 bytes
        const pid = data.readUInt32LE(0);
        const bytes = Number(data.readBigUInt64LE(4));
        const event = { pid, bytes, timestamp: Date.now() };

        // Broadcast to connected DASH clients
        const message = JSON.stringify(event);
        clients.forEach(ws => ws.send(message));
    });

    // Poll perf buffer periodically
    setInterval(() => {
        perf.poll();
    }, 50);
}

main().catch(console.error);

# eBPF-Aware ABR Video Streaming

## Project Overview
This repository contains the code and experiments for **eBPF-aware Adaptive Bitrate (ABR) video streaming**.  
The project leverages **eBPF programs** to collect real-time network telemetry, which is used to enhance ABR decisions, optimize video quality, and reduce latency for live streaming scenarios.

This includes:
- A Mininet network topology (`mininet_topo.py`) with hosts and a switch
- DASH video streaming setup with FFmpeg
- HTTP servers for video content and the player UI
- Python eBPF agent (`agent2.py`) providing throughput, RTT, and jitter metrics to the DASH player
- Two DASH player HTML files:
  - `dash_eBPF.html` — eBPF-aware ABR player
  - `dash_default.html` — default ABR player

---

## **Features**
- Real-time kernel-level telemetry using eBPF
- ABR video streaming with optimized bitrate selection
- QoE collection including stalls, bitrate switches, throughput, RTT, and jitter
- Mininet automation for testing network scenarios
- Scripts for starting, running, and cleaning up experiments

---

## **Prerequisites**

Ensure the following packages are installed:

### **System Packages**
- Linux kernel ≥ 5.x (required for eBPF)
- Python 3.x
- [Mininet](http://mininet.org/)
```bash
sudo apt install mininet

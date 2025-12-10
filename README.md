eBPF-Aware ABR Video Streaming
Project Overview

This repository contains the code and experiments for eBPF-aware Adaptive Bitrate (ABR) video streaming.
The project leverages eBPF programs to collect real-time network telemetry, which is used to enhance ABR decisions, optimize video quality, and reduce latency for live streaming scenarios.

It includes:

A Mininet network topology (mininet_topo.py) with two hosts and a switch

DASH video streaming setup using FFmpeg

HTTP servers for video content and player UI

Python eBPF agent (agent2.py) providing throughput, RTT, and jitter metrics

Two DASH HTML players:

dash_eBPF.html — eBPF-aware ABR player

dash_default.html — default ABR player

Features

Real-time kernel-level telemetry using eBPF

ABR video streaming with optimized bitrate selection

QoE collection including stalls, bitrate switches, throughput, RTT, and jitter

Mininet automation for testing network scenarios

Scripts for starting, running, and cleaning up experiments

Prerequisites
System Packages

Linux kernel ≥ 5.x (required for eBPF)

Python 3.x

Mininet

sudo apt install mininet


bpftool

sudo apt install bpftool


FFmpeg

sudo apt install ffmpeg


Optional: tcpdump for packet inspection

sudo apt install tcpdump

Python Packages

Install required Python packages using pip:

pip install -r requirements.txt


(Ensure requirements.txt includes packages like bcc, scapy, numpy, matplotlib if used)

Browser

Any modern browser (Chrome, Firefox, Edge) to open DASH player HTML files

Project Structure
eBPF-aware-ABR/
├── DASH_Files/               # DASH video files and resources
├── eBPF_programs/            # Kernel-level eBPF/XDP programs
│   └── tcp_metrics.c         # eBPF C code for TCP metrics
├── scripts/
│   ├── mininet_topo.py       # Mininet network + DASH + eBPF agent setup
│   └── agent2.py             # Python agent for eBPF metrics
├── html/
│   ├── dash_eBPF.html        # eBPF-aware DASH player
│   └── dash_default.html     # Default ABR DASH player
├── logs/                     # Experiment logs
└── README.md

Installation & Setup

Clone the repository

git clone https://github.com/AhmedAldeek/eBPF-aware-ABR.git
cd eBPF-aware-ABR


Install dependencies
Follow the prerequisites section to install system packages and Python libraries.

Running the Experiment

Start Mininet with DASH + eBPF setup

sudo python3 scripts/mininet_topo.py


This will:

Start a Mininet network with two hosts (h1, h2) and one switch (s1)

Launch FFmpeg to generate DASH video streams on h1

Start HTTP servers for video (h1) and player UI (h2)

Run the eBPF agent on h2

Open the Mininet CLI for manual interaction if needed

Open DASH players in your browser:

http://10.0.0.2:8000/html/dash_eBPF.html — eBPF-aware ABR

http://10.0.0.2:8000/html/dash_default.html — Default ABR

eBPF agent

sudo python3 scripts/agent2.py


Starts monitoring TCP metrics and sends them to the eBPF-aware DASH player via WebSocket

Collecting Metrics

eBPF-aware DASH player collects:

Throughput (kbps)

RTT (ms)

Jitter (ms)

Buffer length, stalls, quality switches

Cumulative QoE

Default DASH player collects:

Bitrate, buffer, stalls, quality switches

Cumulative QoE

Metrics are saved via HTTP POST when video ends (to http://10.0.0.2:9100/save_metrics)

Cleaning Up

After finishing the experiment, clean the Mininet environment to remove virtual networks and processes:

sudo mn -c

eBPF Program Details

File: eBPF_programs/tcp_metrics.c

Hooks into tcp_sendmsg kernel function using kprobe

Tracks per-process TCP metrics for IPv4 traffic on source port 8000

Sends metrics to user-space via BPF perf buffer

Metrics include:

PID, source/destination IPs and ports

Smoothed RTT, RTT variance

Total bytes sent per process

Timestamp

Dependencies:

bcc Python library (sudo apt install python3-bcc)

Linux kernel ≥ 5.x

Usage: Loaded by agent2.py during the experiment.

Contributing

Maintain folder structure

Document new scripts or eBPF programs

Update README if new dependencies are added

License

MIT License. See the LICENSE
 file.

References

eBPF: https://ebpf.io

Mininet: http://mininet.org

DASH / ABR Streaming: ISO/IEC 23009-1


---

If you want, I can also **write a ready-to-use `requirements.txt`** for Python packages so users can install everything in one command.  

Do you want me to do that?

You said:
I mean in markup README ready status
ChatGPT said:

Got it! Here’s the ready-to-paste Markdown README for your GitHub repo, fully formatted and structured for immediate use:

# eBPF-Aware ABR Video Streaming

## Project Overview
This repository contains the code and experiments for **eBPF-aware Adaptive Bitrate (ABR) video streaming**.  
The project leverages **eBPF programs** to collect real-time network telemetry, which is used to enhance ABR decisions, optimize video quality, and reduce latency for live streaming scenarios.

It includes:

- A Mininet network topology (`mininet_topo.py`) with two hosts and a switch  
- DASH video streaming setup using FFmpeg  
- HTTP servers for video content and player UI  
- Python eBPF agent (`agent2.py`) providing throughput, RTT, and jitter metrics  
- Two DASH HTML players:
  - `dash_eBPF.html` — eBPF-aware ABR player
  - `dash_default.html` — default ABR player

---

## Features

- Real-time kernel-level telemetry using eBPF  
- ABR video streaming with optimized bitrate selection  
- QoE collection including stalls, bitrate switches, throughput, RTT, and jitter  
- Mininet automation for testing network scenarios  
- Scripts for starting, running, and cleaning up experiments  

---

## Prerequisites

### System Packages

- Linux kernel ≥ 5.x (required for eBPF)  
- Python 3.x  
- [Mininet](http://mininet.org/)

```bash
sudo apt install mininet


bpftool

sudo apt install bpftool


FFmpeg

sudo apt install ffmpeg


Optional: tcpdump for packet inspection

sudo apt install tcpdump

Python Packages

Install required Python packages using pip:

pip install -r requirements.txt


(Ensure requirements.txt includes packages like bcc, scapy, numpy, matplotlib if used)

Browser

Any modern browser (Chrome, Firefox, Edge) to open DASH player HTML files

Project Structure
eBPF-aware-ABR/
├── DASH_Files/               # DASH video files and resources
├── eBPF_programs/            # Kernel-level eBPF/XDP programs
│   └── tcp_metrics.c         # eBPF C code for TCP metrics
├── scripts/
│   ├── mininet_topo.py       # Mininet network + DASH + eBPF agent setup
│   └── agent2.py             # Python agent for eBPF metrics
├── html/
│   ├── dash_eBPF.html        # eBPF-aware DASH player
│   └── dash_default.html     # Default ABR DASH player
├── logs/                     # Experiment logs
└── README.md

Installation & Setup

Clone the repository

git clone https://github.com/AhmedAldeek/eBPF-aware-ABR.git
cd eBPF-aware-ABR


Install dependencies
Follow the prerequisites section to install system packages and Python libraries.

Running the Experiment

Start Mininet with DASH + eBPF setup

sudo python3 scripts/mininet_topo.py


This will:

Start a Mininet network with two hosts (h1, h2) and one switch (s1)

Launch FFmpeg to generate DASH video streams on h1

Start HTTP servers for video (h1) and player UI (h2)

Run the eBPF agent on h2

Open the Mininet CLI for manual interaction if needed

Open DASH players in your browser:

http://10.0.0.2:8000/html/dash_eBPF.html — eBPF-aware ABR

http://10.0.0.2:8000/html/dash_default.html — Default ABR

eBPF agent

sudo python3 scripts/agent2.py


Starts monitoring TCP metrics and sends them to the eBPF-aware DASH player via WebSocket.

Collecting Metrics

eBPF-aware DASH player collects:

Throughput (kbps)

RTT (ms)

Jitter (ms)

Buffer length, stalls, quality switches

Cumulative QoE

Default DASH player collects:

Bitrate, buffer, stalls, quality switches

Cumulative QoE

Metrics are saved via HTTP POST when video ends (to http://10.0.0.2:9100/save_metrics).

Cleaning Up

After finishing the experiment, clean the Mininet environment to remove virtual networks and processes:

sudo mn -c

eBPF Program Details

File: eBPF_programs/tcp_metrics.c

Hooks into tcp_sendmsg kernel function using kprobe

Tracks per-process TCP metrics for IPv4 traffic on source port 8000

Sends metrics to user-space via BPF perf buffer

Metrics include:

PID, source/destination IPs and ports

Smoothed RTT, RTT variance

Total bytes sent per process

Timestamp

Dependencies:

bcc Python library (sudo apt install python3-bcc)

Linux kernel ≥ 5.x

Usage: Loaded by agent2.py during the experiment.

Contributing

Maintain folder structure

Document new scripts or eBPF programs

Update README if new dependencies are added

License

MIT License. See the LICENSE
 file.

References

eBPF: https://ebpf.io

Mininet: http://mininet.org

DASH / ABR Streaming: ISO/IEC 23009-1

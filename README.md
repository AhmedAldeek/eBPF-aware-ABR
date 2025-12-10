# eBPF-Aware ABR Video Streaming

## Project Overview

This repository contains the code and experiments for eBPF-aware Adaptive Bitrate (ABR) video streaming. The project leverages eBPF programs to collect real-time network telemetry, which is used to enhance ABR decisions, optimize video quality, and reduce latency for live streaming scenarios.

It includes:
- A Mininet network topology (`mininet_topo.py`) with two hosts and a switch
- DASH video streaming setup using FFmpeg
- HTTP servers for video content and player UI
- Python eBPF agent (`agent2.py`) providing throughput, RTT, and jitter metrics
- Two DASH HTML players:
  - `dash_eBPF.html` — eBPF-aware ABR player
  - `dash_default.html` — default ABR player

## Features

- Real-time kernel-level telemetry using eBPF
- ABR video streaming with optimized bitrate selection
- QoE collection including stalls, bitrate switches, throughput, RTT, and jitter
- Mininet automation for testing network scenarios
- Scripts for starting, running, and cleaning up experiments

## Prerequisites

### System Packages

- Linux kernel ≥ 5.x (required for eBPF)
- Python 3.x
- Mininet
  ```bash
  sudo apt install mininet
  ```
  
- bpftool
  
   ```bash
  sudo apt install bpftool
  ```

- FFmpeg
  
 ```bash
  sudo apt install ffmpeg
 ```

## Python Packages
Install required Python packages using pip:
 ```bash
pip install -r requirements.txt
```

## Project Structure
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

## Installation & Setup
1. Clone the repository
 ```bash
git clone https://github.com/AhmedAldeek/eBPF-aware-ABR.git
cd eBPF-aware-ABR
```

2. Install dependencies
Follow the prerequisites section to install system packages and Python libraries.

## Running the Experiment
Start Mininet with DASH + eBPF setup
 ```bash
sudo python3 scripts/mininet_topo.py
```

This will:

- Start a Mininet network with two hosts (h1, h2) and one switch (s1)

- Launch FFmpeg to generate DASH video streams on h1

- Start HTTP servers for video (h1) and player UI (h2)

- Run the eBPF agent on h2

- Open the Mininet CLI for manual interaction if needed

## Open DASH players in your browser:
- http://10.0.0.2:8000/html/eBPF.html — eBPF-aware ABR

- http://10.0.0.2:8000/html/no_eBPF.html — Default ABR

## Collecting Metrics
eBPF-aware DASH player collects:

-Throughput (kbps)
- RTT (ms)
- Jitter (ms)
- Buffer length, stalls, quality switches
-Cumulative QoE

Metrics are saved via a websocket

## Cleaning Up
 ```bash
sudo mn -c
```


## Refrences
-eBPF: https://ebpf.io
-Mininet: http://mininet.org
-DASH / ABR Streaming: ISO/IEC 23009-1

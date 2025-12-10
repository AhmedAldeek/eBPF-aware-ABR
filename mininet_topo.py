# filename: mininet_topo.py
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
import time
import os

def setup():
    # Create network
    net = Mininet(controller=None, link=TCLink)

    print("🚀 Setting up hosts and switch...")

    # Hosts
    h1 = net.addHost('h1', ip='10.0.0.1/8')
    h2 = net.addHost('h2', ip='10.0.0.2/8')

    # Switch (NEW)
    s1 = net.addSwitch('s1', failMode='standalone')


    # Links (NEW: using switch instead of direct link)
    net.addLink(h1, s1, bw=10, delay='5ms', max_queue_size=10000)
    net.addLink(h2, s1, bw=10, delay='5ms', max_queue_size=10000)

    net.start()
    print("✅ Network started with switch s1")

    project_dir = "/home/kali/dash_project"
    live_dir = f"{project_dir}/live"
    video_file = f"{project_dir}/video.mp4"

    # Prepare directories
    h1.cmd(f'mkdir -p {live_dir}')

    # ===============================
    # DASH FFmpeg on h1
    # ===============================
    ffmpeg_cmd = (
	    f'nohup ffmpeg -re -i {video_file} '
	    # Split into three video streams
	    f'-filter_complex "[0:v]split=3[v1][v2][v3];'
	    f'[v1]scale=640:360,fps=24[v1out];'
	    f'[v2]scale=1280:720,fps=24[v2out];'
	    f'[v3]scale=1920:1080,fps=24[v3out]" '
	    # 360p stream
	    f'-map "[v1out]" -c:v:0 libx264 -preset ultrafast -tune zerolatency '
	    f'-profile:v:0 baseline -b:v:0 600k -maxrate 600k -bufsize 1200k -g 48 -keyint_min 48 -sc_threshold 0 '
	    # 720p stream
	    f'-map "[v2out]" -c:v:1 libx264 -preset ultrafast -tune zeralatency '
	    f'-profile:v:1 main -b:v:1 1500k -maxrate 1500k -bufsize 3000k -g 48 -keyint_min 48 -sc_threshold 0 '
	    # NEW 4000 kbps stream
	    f'-map "[v3out]" -c:v:2 libx264 -preset ultrafast -tune zerolatency '
	    f'-profile:v:2 high -b:v:2 4000k -maxrate 4000k -bufsize 8000k -g 48 -keyint_min 48 -sc_threshold 0 '
	    # Audio
	    f'-map 0:a -c:a aac -b:a 128k -ar 48000 '
	    # DASH settings
	    f'-f dash -seg_duration 2 -window_size 15 -extra_window_size 3 -remove_at_exit 1 '
	    f'-use_template 1 -use_timeline 1 -adaptation_sets "id=0,streams=v id=1,streams=a" '
	    f'{live_dir}/stream.mpd > {project_dir}/ffmpeg_h1.log 2>&1 &')

   
    h1.cmd(ffmpeg_cmd)
    print("✅ Optimized DASH FFmpeg started on h1")

    # ===============================
    # HTTP server h1 (video)
    # ===============================
    h1.cmd(f'cd {project_dir} && nohup python3 - <<EOF > http_h1.log 2>&1 &\n'
           'import http.server\n'
           'import socketserver\n'
           'class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):\n'
           '    def end_headers(self):\n'
           '        self.send_header("Access-Control-Allow-Origin", "*")\n'
           '        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")\n'
           '        self.send_header("Access-Control-Allow-Headers", "Content-Type")\n'
           '        super().end_headers()\n'
           '    def do_OPTIONS(self):\n'
           '        self.send_response(200)\n'
           '        self.end_headers()\n'
           'PORT = 8000\n'
           'with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:\n'
           '    print(f"Serving at http://0.0.0.0:{PORT}")\n'
           '    httpd.serve_forever()\n'
           'EOF')
    print("✅ HTTP server started on h1")

    # ===============================
    # HTTP server h2 (player UI)
    # ===============================
    h2.cmd(f'cd {project_dir} && nohup python3 -m http.server 8000 > http_h2.log 2>&1 &')
    print("✅ HTTP server started on h2")

    # ===============================
    # eBPF agent on h2
    # ===============================
    h2.cmd(f'cd {project_dir} && nohup sudo python3 agent2.py > agent2_h2.log 2>&1 &')
    print("✅ agent2.py started on h2")

    time.sleep(3)
    CLI(net)

    # Cleanup after CLI exit
    h1.cmd('pkill -f ffmpeg')
    h1.cmd('pkill -f "python3 -"')
    h2.cmd('pkill -f "http.server"')
    h2.cmd('pkill -f agent2.py')

    net.stop()

if __name__ == '__main__':
    setup()

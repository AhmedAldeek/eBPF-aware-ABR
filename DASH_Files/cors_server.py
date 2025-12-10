
from http.server import SimpleHTTPRequestHandler, HTTPServer
class CORSHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
import os
os.chdir(/home/kali/dash_project)
server_address = ('', 8000)
httpd = HTTPServer(server_address, CORSHandler)
print(Serving with CORS on port 8000...)
httpd.serve_forever()


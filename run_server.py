import http.server
import socketserver
import os

PORT = 8000
DIR = "website_copy"

os.chdir(DIR)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving clone website at http://localhost:{PORT}")
    httpd.serve_forever()
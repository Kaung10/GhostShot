# ----- License -------------------------------------------------- # 

#  GhostShot - GhostShot simulates ransomware attacks to test EDR systems, enabling users to strengthen their defense strategies.
#  Copyright (c) 2026 - ThrillByte (Operated by Kaung10). All rights reserved.

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
#  🔗 Author: Kaung Min Myat (@Kaung10)

# ----- Libraries ------------------------------------------------ #

import os
import random
from faker import Faker
from rich.console import Console

# ----- Global Declaration --------------------------------------- #

fake = Faker()
file_count = 99
console = Console()
target_folder = "Important_Data"
os.makedirs(target_folder, exist_ok=True)

# ----- Generate PAN Card ---------------------------------------- #

def generate_pan_card():
	return fake.random_uppercase_letter() + \
			''.join(fake.random_letters(length=4)).upper() + \
			str(random.randint(1000, 9999)) + \
			fake.random_uppercase_letter()

# ----- Generate File Content ------------------------------------ #

def generate_file_content():
	address = fake.address().replace("\n", ", ")
	return f"""
# ----- Personal Information ------------------------------ #
Full Name: {fake.name()}
Date of Birth: {fake.date_of_birth()}
Gender: {random.choice(['Male', 'Female', 'Other'])}
Nationality: {random.choice(['Indian', 'American', 'Australian', 'Nigerian', 'British', 'South African'])}

# ----- Contact Information ------------------------------- #
Phone Number: {fake.phone_number()}
Email Address: {fake.email()}
Address: {address}

# ----- Government ID Information ------------------------- #
Aadhaar Number: {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}
PAN Card Number: {generate_pan_card()}
Passport Number: {fake.bothify(text='??#######').upper()}
Voter ID: {fake.bothify(text='???######').upper()}
Driving License: DL-{random.randint(1000,9999)}{random.randint(1000000,9999999)}
SSN (US): {fake.ssn()}
Medicare Number (AU): {random.randint(1000, 9999)} {random.randint(10000, 99999)} {random.randint(0,9)}
NIN (UK): QQ{random.randint(100000, 999999)}C
South Africa ID: {fake.msisdn()[:13]}
Nigerian NIN: {random.randint(10000000000, 99999999999)}

# ----- Financial Information ----------------------------- #
Bank Account Number: {random.randint(100000000000, 999999999999)}
IFSC Code: HDFC{random.randint(1000, 9999)}
Credit Card Number: 4111 1111 1111 1111
CVV: {random.randint(100, 999)}
Expiry Date: 12/{random.randint(25, 29)}
UPI ID: {fake.first_name().lower()}{random.randint(10,99)}@hdfcbank

# ----- Login Information --------------------------------- #
Username: {fake.user_name()}
Password: {fake.password(length=12, special_chars=True)}
Security Question: First pet's name?
Security Answer: {fake.first_name()}

# ----- Medical Information ------------------------------- #
Blood Group: {random.choice(['A+', 'B+', 'AB+', 'O+', 'A-', 'B-', 'AB-', 'O-'])}
Health Insurance Number: HIN-{random.randint(100000, 999999)}
Allergies: {random.choice(['None', 'Penicillin', 'Dust', 'Peanuts', 'Gluten'])}

# ----- Technology Information ---------------------------- #
IP Address: {fake.ipv4()}
MAC Address: {fake.mac_address()}
IMEI Number: {random.randint(100000000000000, 999999999999999)}
Browser Fingerprint: bfp_{fake.sha1()[:16]}

# ----- Employment Information ---------------------------- #
Employee ID: EMP{random.randint(100000, 999999)}
Designation: {fake.job()}
Company: {fake.company()}

# ----- Education Information ----------------------------- #
University: {fake.company()} Institute of Technology
Degree: {random.choice(['B.Tech', 'B.Sc', 'M.Tech', 'M.Sc'])} in {fake.job().split()[0]}
Graduation Year: {random.randint(2010, 2022)}
Student ID: {fake.bothify(text='UNI#######')}

# ----- Sensitive Information ----------------------------- #
Religion: {random.choice(['Hindu', 'Christian', 'Muslim', 'Jewish', 'Buddhist'])}
Marital Status: {random.choice(['Single', 'Married', 'Divorced'])}
Sexual Orientation: {random.choice(['Straight', 'Gay', 'Bisexual', 'Prefer not to say'])}
Political Affiliation: {random.choice(['Independent', 'Democrat', 'Republican', 'Other', 'Undisclosed'])}

# ----- End of File --------------------------------------- #
"""

# ----- Create Files --------------------------------------------- #

def create_files():
	console.print(rf"[green][+] Creating {file_count} fake PII files in '{target_folder}'.....")
	for i in range(1, file_count + 1):  # <--- fixed this line!
		file_path = os.path.join(target_folder, f"Important_{i:04}.txt")
		with open(file_path, 'w', encoding='utf-8') as f:
			f.write(generate_file_content())
	console.print(rf"[green][+] All fake data files have been created successfully.")

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
	console.print(rf"[#C6ECE3]  GhostShot - Test Defenses. Simulate Threats. Strike Silently.")
	console.print(rf"[#C6ECE3]  Created by [ThrillByte]Kaung10")
	console.print(rf"[#C6ECE3]+--------------------------------------------------------------+")

# ----- Main Function -------------------------------------------- #

if __name__ == "__main__":
	os.system("cls" if os.name == "nt" else "clear")
	ascii()
	create_files()
	console.print("[#C6ECE3]+--------------------------------------------------------------+")

# ----- End ------------------------------------------------------ #

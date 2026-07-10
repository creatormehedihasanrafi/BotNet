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
```text
┌─────────────────────────────────────────────────────────────┐
│ C2 SERVER (c2_server.py)                                     │
│ ┌─────────────────────────────────────────────────────┐      │
│ │ Admin Console (CLI)                                 │      │
│ │ - broadcast <cmd> - list - bot <number>             │      │
│ │ - DOWNLOAD <file> - UPDATE - DDOS                   │      │
│ │ - STEAL - TOR_START - SHOW_STEAL                    │      │
│ └─────────────────────────────────────────────────────┘      │
│           │                                                  │
│ ┌─────────▼──────────┐                                       │
│ │ Socket Server      │                                       │
│ │ (Port 4444)        │                                       │
│ └─────────┬──────────┘                                       │
│           │                                                  │
│ ┌─────────┼──────────┐                                       │
│ ▼         ▼          ▼                                       │
│ ┌──────┐ ┌──────┐ ┌──────┐                                 │
│ │ Bot1 │ │ Bot2 │ │ Bot3 │                                 │
│ └──────┘ └──────┘ └──────┘                                 │
└─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│ BOT CLIENTS (bot_client.py)                                 │
│ ┌─────────────────────────────────────────────────────┐      │
│ │ Features                                            │      │
│ │ - Data Steal - DDoS Attack - Tor Relay              │      │
│ │ - Auto-Update - Persistence - AV Evasion            │      │
│ └─────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
📁 File StructurePlaintextyour_project_folder/
│
├── 📄 c2_server.py           # C2 Server (Command Center)
├── 📄 bot_client.py          # Bot Client (Target Machine)
├── 📄 config.py              # Configuration File
├── 📄 requirements.txt       # Required Packages
│
├── 📁 modules/               # All Modules
│ ├── 📄 anti_av.py           # Antivirus Evasion
│ ├── 📄 auto_update.py       # Auto-Update System
│ ├── 📄 data_steal.py        # Data Stealing Module
│ ├── 📄 ddos.py              # DDoS Attack Module
│ ├── 📄 encryption.py        # Encryption Module
│ ├── 📄 persistence.py       # Persistence (Startup)
│ └── 📄 tor_relay.py         # Tor Relay Module
│
├── 📁 steal_data/            # C2 Steal Data Storage
├── 📁 extracted_data/        # Extracted Data Storage
├── 📁 steal_data_bot/        # Bot Steal Data Storage
└── 📁 extracted_data_bot/    # Bot Extracted Data Storage
🔧 InstallationStep 1: Install Required PackagesBashpip install -r requirements.txt
Step 2: Start C2 ServerBashpython c2_server.py
Step 3: Start Bot ClientBashpython bot_client.py
💻 C2 Server CommandsBasic Commands:CommandDescriptionExamplehelpShows help messagehelpdir / lsLists C2 folder filesdirlistShows connected botslistbot Shows bot detailsbot 1refreshRefreshes bot listrefreshstatsShows server statisticsstatsstatusShows feature statusstatusFeature Toggle:CommandDescriptionsteal_onEnable Data Stealsteal_offDisable Data Stealddos_onEnable DDoSddos_offDisable DDoStor_onEnable Tortor_offDisable TorOperational Commands:CommandDescriptionExampleDOWNLOAD Download fileDOWNLOAD bot_client.pyUPDATEUpdate botsUPDATEDDOS    DDoS attackDDOS 192.168.1.1 80 60 SYNSTEALStart data theftSTEALSTOP_STEALStop data theftSTOP_STEALTOR_STARTStart TorTOR_STARTTOR_STOPStop TorTOR_STOPTOR_INFOGet Tor infoTOR_INFOSHOW_STEALShow steal dataSHOW_STEALLATEST_STEALShow latest steal fileLATEST_STEALAdmin Commands:CommandDescriptionExamplebroadcast Broadcast to all botsbroadcast PINGcreate_updateCreate update filecreate_updateupload_update Upload updateupload_update bot_v2.pydebug on/offToggle debugdebug onquit / exitShutdown serverquit🤖 Bot ClientBot Features:🔑 Dynamic Session Key - New key generated each session🔐 Encrypted Communication - All data encrypted📁 Auto Data Extraction - Automatically extracts stolen data🔄 Auto-Update - Checks for updates every hour🕵️ Anti-AV - Antivirus evasion techniques💾 Persistence - Adds to startup🌐 Tor Support - Tor relay connectionBot Commands (Sent from C2):CommandDescriptionPINGPing responsePONGPong responseLISTShows bot infoUPDATECheck for updatesEXEC Execute commandSTEALStart data theftSTOP_STEALStop data theftDDOS   DDoS attackTOR_STARTStart TorTOR_STOPStop TorTOR_INFOTor informationDOWNLOAD Download fileEXITShutdown bot🧩 Modulesanti_av.py - Antivirus EvasionWindows Defender bypass, Process hiding, Sandbox detectionauto_update.py - Auto-UpdateHourly update checks, Manual update trigger, Download and install updatesdata_steal.py - Data TheftBrowser password theft, Cookie/History theft, Key-logging, Screenshot/Webcam capture, File miningddos.py - DDoS AttackSYN/UDP/HTTP/ICMP Floodencryption.py - EncryptionAES encryption, Encrypt/Decrypt data, Session key generationpersistence.py - PersistenceWindows startup addition, Service creation, Run key additiontor_relay.py - Tor RelayTor process management, Anonymous connection, .onion site support🎯 Usage StepsStart C2 Server: python c2_server.pyStart Bot Client: python bot_client.py (on target)Check Bots: listDownload: bot 1 then DOWNLOAD payload.exeRun Commands: EXEC dirDDoS: DDOS 192.168.1.1 80 60 SYNSteal: STEAL then SHOW_STEALUpdate: create_update then broadcast UPDATE🔐 Security & Warnings⚠️ Important Warnings: Educational Purpose Only. Get permission. Follow local laws.🔒 Security Tips: Change C2 IP/Port, change keys, monitor logs, use Tor.🛠️ TroubleshootingIssueSolutionC2 not connectingCheck if C2 is runningFile not downloadingCheck if file exists in C2 folderBot disconnectingCheck network connectionUpdate not workingCheck modules/auto_update.py📜 LicenseEducational purposes only. User responsibility.

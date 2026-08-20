#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.3

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configurazione UTF-8 e ANSI su Windows
if sys.platform == "win32":
    os.system("chcp 65001 >nul")
    os.system("")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def configure_utf8_stdio() -> None:
    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")


def utf8_child_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


configure_utf8_stdio()

CLR_GREEN = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN = "\033[96m"
CLR_RESET = "\033[0m"

BANNER = f"{CLR_GREEN}=================== [ NEW LOG DETECTED ] ==================={CLR_RESET}"

# tail-watch.py vive in .../.catsw-utility/artifacts; il json di posizione
# e get-win-pos.ps1 seguono la stessa convenzione di from-llm-watcher.py
SCRIPT_DIR = Path(__file__).resolve().parent
CATSW_DIR = SCRIPT_DIR.parent
WIN_POS_CONFIG = CATSW_DIR / "tail-watch.json"
GET_WIN_POS_SCRIPT = SCRIPT_DIR / "get-win-pos.ps1"

_WT_POS_RE = re.compile(r'set "WT_POS=(-?\d+),(-?\d+)"')
_WT_SIZE_RE = re.compile(r'set "WT_SIZE=(\d+),(\d+)"')


def get_current_win_geometry(ps1_path: Path) -> Optional[tuple[int, int, int, int]]:
    """Invoca get-win-pos.ps1 senza argomenti (modalità non interattiva) e
    ne fa il parsing per ottenere (x, y, width, height) della finestra corrente."""
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps1_path)],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None

    if result.returncode != 0:
        return None

    x = y = w = h = None
    for line in result.stdout.splitlines():
        m = _WT_POS_RE.search(line)
        if m:
            x, y = int(m.group(1)), int(m.group(2))
            continue
        m = _WT_SIZE_RE.search(line)
        if m:
            w, h = int(m.group(1)), int(m.group(2))

    if None in (x, y, w, h):
        return None
    return x, y, w, h


def update_win_pos_if_changed(config_path: Path, ps1_path: Path) -> None:
    """Su Ctrl+C: se posizione/dimensione correnti differiscono da quelle salvate,
    riscrive il json senza bisogno che l'utente lo cancelli o lo editi a mano."""
    if not ps1_path.exists():
        return

    geometry = get_current_win_geometry(ps1_path)
    if geometry is None:
        return
    x, y, w, h = geometry

    current: dict = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8-sig") as f:
                current = json.load(f)
        except (OSError, ValueError):
            current = {}

    if (
        current.get("x-win-pos"),
        current.get("y-win-pos"),
        current.get("width"),
        current.get("height"),
    ) == (x, y, w, h):
        return

    new_config = {"x-win-pos": x, "y-win-pos": y, "width": w, "height": h}
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=4)
    except OSError:
        pass

def read_file_direct(file_path: Path, offset: int, last_header: bytes):
    """Legge i byte su disco. Rileva il reset se la dimensione cala o se l'header iniziale varia."""
    try:
        flags = os.O_RDONLY
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        fd = os.open(str(file_path), flags)
        try:
            size = os.lseek(fd, 0, os.SEEK_END)

            # Legge l'header iniziale (proporzionato al vecchio header, min 64 byte)
            read_len = max(64, len(last_header))
            os.lseek(fd, 0, os.SEEK_SET)
            current_header = os.read(fd, read_len)

            was_reset = False
            # Reset se: la dimensione è diminuita OR i primi byte non coincidono più con quanto letto in precedenza
            if size < offset or (offset > 0 and len(last_header) > 0 and not current_header.startswith(last_header)):
                offset = 0
                was_reset = True

            os.lseek(fd, offset, os.SEEK_SET)
            bytes_to_read = size - offset
            if bytes_to_read > 0:
                data = os.read(fd, bytes_to_read)
                return data, size, was_reset, current_header[:64]

            return b"", size, was_reset, current_header[:64]
        finally:
            os.close(fd)
    except (OSError, FileNotFoundError):
        return b"", offset, False, last_header


def show_last_lines(file_path: Path, n: int = 50) -> tuple[int, bytes]:
    """Mostra le ultime n righe e restituisce (size, header_bytes)."""
    try:
        flags = os.O_RDONLY
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        fd = os.open(str(file_path), flags)
        try:
            size = os.lseek(fd, 0, os.SEEK_END)
            os.lseek(fd, 0, os.SEEK_SET)
            header = os.read(fd, 64)
            if size == 0:
                return 0, b""

            max_read = min(size, 256 * 1024)
            start = max(0, size - max_read)
            os.lseek(fd, start, os.SEEK_SET)
            data = os.read(fd, size - start)
            text = data.decode("utf-8", errors="replace")
            lines = text.splitlines(keepends=True)
            last = lines[-n:] if len(lines) > n else lines
            if last:
                print("".join(last), end="", flush=True)
            return size, header
        finally:
            os.close(fd)
    except (OSError, FileNotFoundError):
        return 0, b""


def main():
    if len(sys.argv) < 2:
        print("Uso: tail-watch <file_path> [secondi_inattivita]")
        sys.exit(1)

    file_path = Path(sys.argv[1]).resolve()
    inactivity_limit = 15
    if len(sys.argv) > 2:
        try:
            inactivity_limit = int(sys.argv[2])
            if inactivity_limit < 1:
                inactivity_limit = 15
        except ValueError:
            sys.exit(1)

    if not file_path.exists():
        print(f"Errore: Il file '{file_path}' non esiste.")
        sys.exit(1)

    print(f"{CLR_CYAN}=== tail-watch V1.3 su: {file_path.name} ==={CLR_RESET}")
    print(f"Avviso inattività: {inactivity_limit}s\n")

    last_offset, last_header = show_last_lines(file_path, 50)
    last_update = time.time()
    warning_active = False
    poll_interval = 0.35

    while True:
        try:
            time.sleep(poll_interval)

            if not file_path.exists():
                continue

            data, new_offset, was_reset, current_header = read_file_direct(file_path, last_offset, last_header)

            if data or was_reset:
                text = data.decode("utf-8", errors="replace")
                if was_reset or warning_active:
                    print(f"\n{BANNER}")
                    warning_active = False

                print(text, end="", flush=True)
                last_offset = new_offset
                last_header = current_header
                last_update = time.time()
            else:
                elapsed = int(time.time() - last_update)
                if elapsed >= inactivity_limit and not warning_active:
                    time_str = datetime.fromtimestamp(last_update).strftime("%H:%M:%S")
                    print(
                        f"\n{CLR_YELLOW}[TailWatch] ⚠️  Nessuna modifica al file da {elapsed}s. "
                        f"(Ultimo update: {time_str}){CLR_RESET}",
                        flush=True,
                    )
                    warning_active = True

        except KeyboardInterrupt:
            print(f"\n{CLR_CYAN}[TailWatch arrestato]{CLR_RESET}")
            update_win_pos_if_changed(WIN_POS_CONFIG, GET_WIN_POS_SCRIPT)
            sys.exit(0)


if __name__ == "__main__":
    main()
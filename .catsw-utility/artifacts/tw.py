#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.1

import os
import sys
import time
from datetime import datetime
from pathlib import Path

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

CLR_GREEN = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN = "\033[96m"
CLR_RESET = "\033[0m"

BANNER = f"{CLR_GREEN}=================== [ NEW LOG DETECTED ] ==================={CLR_RESET}"

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
        print("Uso: tw <file_path> [secondi_inattivita]")
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

    print(f"{CLR_CYAN}=== TailWatch v1.1 su: {file_path.name} ==={CLR_RESET}")
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
            sys.exit(0)


if __name__ == "__main__":
    main()
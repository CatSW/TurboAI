#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Configurazione UTF-8 e ANSI su Windows (Soluzione End-to-End UTF-8)
if sys.platform == "win32":
    os.system("chcp 65001 >nul")  # Forza la code page della console a UTF-8 (65001)
    os.system("")  # Abilita sequenze ANSI
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

def read_file_direct(file_path: Path, offset: int):
    """Legge direttamente i byte su disco bypassando le cache di Python.
    Ritorna: (data_bytes, new_size, was_reset)
    """
    try:
        flags = os.O_RDONLY
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        fd = os.open(str(file_path), flags)
        try:
            size = os.lseek(fd, 0, os.SEEK_END)
            if size < offset:
                # File azzerato o ricreato
                return b"", 0, True

            os.lseek(fd, offset, os.SEEK_SET)
            bytes_to_read = size - offset
            if bytes_to_read > 0:
                data = os.read(fd, bytes_to_read)
                return data, size, False
            return b"", size, False
        finally:
            os.close(fd)
    except (OSError, FileNotFoundError):
        return b"", offset, False


def show_last_lines(file_path: Path, n: int = 50) -> int:
    """Mostra le ultime n righe del file e ritorna l'offset corrente (size)."""
    try:
        flags = os.O_RDONLY
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        fd = os.open(str(file_path), flags)
        try:
            size = os.lseek(fd, 0, os.SEEK_END)
            if size == 0:
                return 0

            max_read = min(size, 256 * 1024)  # max 256 KB dalla fine
            start = max(0, size - max_read)
            os.lseek(fd, start, os.SEEK_SET)
            data = os.read(fd, size - start)
            text = data.decode("utf-8", errors="replace")
            lines = text.splitlines(keepends=True)
            last = lines[-n:] if len(lines) > n else lines
            if last:
                print("".join(last), end="", flush=True)
            return size
        finally:
            os.close(fd)
    except (OSError, FileNotFoundError):
        return 0


def main():
    if len(sys.argv) < 2:
        print("Uso: tw <file_path> [secondi_inattivita]")
        print("Esempio: python tw.py ToLlm.txt 15")
        sys.exit(1)

    file_path = Path(sys.argv[1]).resolve()
    inactivity_limit = 15
    if len(sys.argv) > 2:
        try:
            inactivity_limit = int(sys.argv[2])
            if inactivity_limit < 1:
                inactivity_limit = 15
        except ValueError:
            print("Secondo argomento non valido: deve essere un intero (secondi).")
            sys.exit(1)

    if not file_path.exists():
        print(f"Errore: Il file '{file_path}' non esiste.")
        sys.exit(1)

    print(f"{CLR_CYAN}=== TailWatch v1.4 (Unbuffered Python) su: {file_path.name} ==={CLR_RESET}")
    print(f"Avviso inattività: {inactivity_limit}s\n")

    # Mostra le ultime 50 righe e posiziona l'offset alla fine
    last_offset = show_last_lines(file_path, 50)
    last_update = time.time()
    warning_active = False
    poll_interval = 0.35  # ~350 ms

    while True:
        try:
            time.sleep(poll_interval)

            if not file_path.exists():
                continue

            data, new_offset, was_reset = read_file_direct(file_path, last_offset)

            if was_reset:
                last_offset = 0
                warning_active = True
                continue

            if data:
                text = data.decode("utf-8", errors="replace")
                if warning_active:
                    print(f"\n{BANNER}")
                    warning_active = False

                print(text, end="", flush=True)
                last_offset = new_offset
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
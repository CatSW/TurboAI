#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""
Sposta, dalla cartella .catsw-utility (non ricorsivamente), tutti i file
context-request*.md, context-out*.md e FromLlm-* (.ps1, .py, .zip, ecc.)
nella sottocartella .catsw-utility/history/ — la stessa usata da
ProcessZipAndScriptsFromLlm.py per archiviare gli script eseguiti con successo.

Se il file esiste gia' nella destinazione, aggiunge un suffisso _n
incrementale invece di sovrascrivere.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ARTEFACTS_ROOT = Path(__file__).resolve().parent
UTILITY_ROOT = ARTEFACTS_ROOT.parent  # .catsw-utility
HISTORY_DIR = UTILITY_ROOT / "history"


def get_downloads_path() -> Path:
    if sys.platform == "win32":
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            )
            value, _ = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")
            expanded = Path(winreg.ExpandEnvironmentStrings(value) if "%" in value else value)
            if expanded.exists():
                return expanded
        except OSError:
            pass
    return Path.home() / "Downloads"


TO_LLM_PATH = get_downloads_path() / "ToLlm.txt"

MATCH_SUBSTRINGS = ("context-request", "context-out")
MATCH_PREFIX = "FromLlm-"


def log(msg: str) -> None:
    print(msg)
    with TO_LLM_PATH.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def matches(name: str) -> bool:
    lowered = name.lower()
    if any(sub in lowered for sub in MATCH_SUBSTRINGS):
        return True
    return name.startswith(MATCH_PREFIX)


def unique_destination(name: str) -> Path:
    dest = HISTORY_DIR / name
    if not dest.exists():
        return dest
    stem, dot, ext = name.partition(".")
    n = 1
    while True:
        candidate = HISTORY_DIR / f"{stem}_{n}{dot}{ext}"
        if not candidate.exists():
            return candidate
        n += 1


def main() -> int:
    log(f"=== move-to-history v1.0 (Python) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    HISTORY_DIR.mkdir(exist_ok=True)

    candidates = [p for p in UTILITY_ROOT.iterdir() if p.is_file() and matches(p.name)]

    if not candidates:
        log("Nessun file da spostare.")
        return 0

    for file in candidates:
        dest = unique_destination(file.name)
        file.rename(dest)
        if dest.name != file.name:
            log(f"Spostato e rinominato: {file.name} -> {dest.name}")
        else:
            log(f"Spostato: {file.name}")

    log("")
    log(f"Operazione completata. Destinazione: {HISTORY_DIR}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        log(f"ERRORE: {exc}")
        sys.exit(1)

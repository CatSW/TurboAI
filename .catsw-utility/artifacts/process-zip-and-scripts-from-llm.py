#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""
Preleva lo zip di artefatti piu' recente scaricato dalla chat LLM, lo sposta
nella root della solution, lo estrae (sovrascrivendo eventuali file con lo
stesso nome) ed esegue gli script FromLlm-*.ps1 / FromLlm-*.py trovati in
.catsw-utility. Se non trova alcuno zip, cerca in Download lo script piu'
recente (.py o .ps1), lo sposta in .catsw-utility e lo esegue.

Tutto l'output viene anche accodato in <Downloads>\\ToLlm.txt, per la
visibilita' delle operazioni al canale LLM (es. TailWatcher).

Convenzione per gli script FromLlm-*: devono limitarsi a print() su stdout/
stderr. La scrittura su ToLlm.txt e' responsabilita' esclusiva di questo
orchestratore (Tee): se uno script scrive anche lui direttamente sul file,
ogni riga risulta duplicata.

Dopo ogni esecuzione, lo script eseguito viene spostato in
.catsw-utility/history/ (con prefisso timestamp), sia in caso di successo
sia in caso di errore: nessuno script FromLlm-* resta mai in .catsw-utility
al termine, ne' viene ritentato automaticamente al giro successivo. In caso
di errore l'exit code non-zero e' comunque riportato in ToLlm.txt, quindi va
corretto e riconsegnato con una nuova esecuzione se necessario.

T4.1: dopo extractall i timestamp (mtime/atime) dei file estratti vengono
impostati a now, cosi' una successiva build incrementale MSBuild/dotnet
vede i sorgenti come modificati e non riusa assembly stale.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ZIP_PATTERN = "FromLlm-*.zip"
SCRIPT_PATTERNS = ("FromLlm-*.ps1", "FromLlm-*.py")

ARTEFACTS_ROOT = Path(__file__).resolve().parent
SCRIPT_DIR = ARTEFACTS_ROOT.parent  # .catsw-utility
SOLUTION_ROOT = SCRIPT_DIR.parent
HISTORY_DIR = SCRIPT_DIR / "history"


def get_downloads_path() -> Path:
    """Replica la risoluzione del registro Explorer\\Shell Folders del .ps1
    originale, per rispettare eventuali redirezioni (es. OneDrive)."""
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


DOWNLOADS_PATH = get_downloads_path()
TO_LLM_PATH = DOWNLOADS_PATH / "ToLlm.txt"


def log(msg: str) -> None:
    """Unico punto di scrittura su ToLlm.txt: print a console + append su file."""
    print(msg)
    with TO_LLM_PATH.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def latest_by_mtime(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda p: p.stat().st_mtime)


def run_and_capture(cmd: list[str], cwd: Path) -> int:
    """Esegue cmd, inoltrando ogni riga di stdout/stderr sia a console sia a
    ToLlm.txt via log(). Ritorna l'exit code."""
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    assert process.stdout is not None
    for line in process.stdout:
        log(line.rstrip("\n"))
    process.wait()
    return process.returncode


def invoke_llm_script(script: Path, target_location: Path) -> int:
    log(f"==> Esecuzione script LLM: {script.name}...")
    if script.suffix == ".py":
        cmd = [sys.executable, str(script)]
    else:
        cmd = ["pwsh.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]
    return run_and_capture(cmd, cwd=target_location)


def archive_script(script: Path) -> None:
    HISTORY_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = HISTORY_DIR / f"{timestamp}-{script.name}"
    shutil.move(str(script), str(dest))
    log(f"==> Archiviato in history: {dest.relative_to(SOLUTION_ROOT)}")


def main() -> int:
    TO_LLM_PATH.write_text("", encoding="utf-8")
    log("=== process-zip-and-scripts-from-llm v1.2 (Python) ===")
    log(f"Esecuzione avviata: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Solution Root: {SOLUTION_ROOT}")

    log(f"==> Cerco in Download il file piu' recente con pattern '{ZIP_PATTERN}'...")
    zip_candidates = list(DOWNLOADS_PATH.glob(ZIP_PATTERN))
    latest_zip = latest_by_mtime(zip_candidates)

    if latest_zip is None:
        log("==> Nessuno zip trovato. Cerco in Download lo script piu' recente (.ps1 o .py)...")
        script_candidates = [
            p for pattern in SCRIPT_PATTERNS for p in DOWNLOADS_PATH.glob(pattern)
        ]
        latest_script = latest_by_mtime(script_candidates)

        if latest_script is None:
            err = f"Nessuno zip o script (.ps1 / .py) trovato in {DOWNLOADS_PATH}."
            log(f"ERRORE: {err}")
            raise SystemExit(err)

        dest_script = SCRIPT_DIR / latest_script.name
        log(f"==> Script selezionato: {latest_script}")
        log("==> Sposto lo script in .catsw-utility...")
        shutil.move(str(latest_script), str(dest_script))

        rc = invoke_llm_script(dest_script, SOLUTION_ROOT)
        if rc != 0:
            log(f"==> Script terminato con exit code {rc}.")
        archive_script(dest_script)

        log("==> Esecuzione completata.")
        return rc

    # --- Gestione ZIP ---
    dest_zip = SOLUTION_ROOT / latest_zip.name
    log(f"==> Zip selezionato: {latest_zip}")
    log("==> Sposto lo zip nella root della solution...")
    shutil.move(str(latest_zip), str(dest_zip))

    log("==> Estraggo il contenuto...")
    with zipfile.ZipFile(dest_zip) as zf:
        members = zf.namelist()
        zf.extractall(SOLUTION_ROOT)

    # T4.1: forza timestamp correnti sui file estratti.
    # Senza questo MSBuild/dotnet build incrementale puo' ignorare i sorgenti
    # appena patchati (Anomalia 9).
    now = datetime.now().timestamp()
    touched = 0
    for member in members:
        if member.endswith("/"):
            continue
        path = SOLUTION_ROOT / member
        if path.is_file():
            os.utime(path, times=(now, now))
            touched += 1
    log(f"==> Timestamp aggiornati su {touched} file estratti (T4.1).")

    log("==> Elimino lo zip...")
    dest_zip.unlink()

    from_llm_scripts = [
        p for pattern in SCRIPT_PATTERNS for p in SCRIPT_DIR.glob(pattern) if p.is_file()
    ]

    if not from_llm_scripts:
        log("==> Nessuno script FromLlm-* (.ps1 / .py) trovato in .catsw-utility. Fine.")
        return 0

    exit_code = 0
    for script in from_llm_scripts:
        rc = invoke_llm_script(script, SOLUTION_ROOT)
        if rc != 0:
            log(f"==> {script.name} terminato con exit code {rc}.")
            exit_code = rc
        archive_script(script)

    log("==> Esecuzione completata.")
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        log(f"ERRORE: {exc}")
        sys.exit(1)

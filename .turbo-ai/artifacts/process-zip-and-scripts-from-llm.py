#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.7
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path


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

ZIP_PATTERN = "FromLlm-*.zip"
SCRIPT_PATTERNS = ("FromLlm-*.ps1", "FromLlm-*.py")

ARTEFACTS_ROOT = Path(__file__).resolve().parent
SCRIPT_DIR = ARTEFACTS_ROOT.parent  # .turbo-ai
SOLUTION_ROOT = SCRIPT_DIR.parent
HISTORY_DIR = SCRIPT_DIR / "history"
TEMP_DIR = SCRIPT_DIR / "temp"


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
        env=utf8_child_env(),
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


def archive_zip_to_history(src_zip: Path) -> Path:
    """
    Sposta lo ZIP da Downloads a .turbo-ai/history aggiungendo
    -YYYYMMDD-HHMMSS prima di .zip. In caso di collisione sullo stesso
    secondo aggiunge un suffisso numerico deterministico senza sovrascrivere.
    Ritorna il path assoluto dell'archivio preservato.
    """
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    # Preserve canonical base name (stem) and insert timestamp before .zip
    stem = src_zip.stem  # e.g. FromLlm-foo
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = HISTORY_DIR / f"{stem}-{timestamp}.zip"
    counter = 1
    while candidate.exists():
        candidate = HISTORY_DIR / f"{stem}-{timestamp}-{counter}.zip"
        counter += 1
    shutil.move(str(src_zip), str(candidate))
    log(f"==> ZIP archiviato in history (T1.1): {candidate.relative_to(SOLUTION_ROOT)}")
    return candidate


def validate_zip_members(members: list[str], solution_root: Path) -> None:
    """
    T1.2: rifiuta path assoluti, traversal (..) e destinazioni che risolvono
    fuori dalla solution root. Solleva ValueError con messaggio esplicito.
    Non modifica i member names; solo ispeziona.
    """
    root_resolved = solution_root.resolve()
    for name in members:
        # Skip pure directory markers (trailing slash)
        if not name or name.endswith("/"):
            # Still check the directory path itself for safety
            check_name = name.rstrip("/")
            if not check_name:
                continue
        else:
            check_name = name

        # Absolute paths (Unix or Windows style)
        if check_name.startswith("/") or (len(check_name) >= 2 and check_name[1] == ":"):
            raise ValueError(f"ZIP entry rifiutata (path assoluto): {name!r}")

        # Explicit traversal sequences
        parts = Path(check_name).parts
        if ".." in parts:
            raise ValueError(f"ZIP entry rifiutata (traversal '..'): {name!r}")

        # Resolve and ensure still under solution root
        try:
            target = (solution_root / check_name).resolve()
        except (OSError, ValueError) as exc:
            raise ValueError(f"ZIP entry rifiutata (risoluzione fallita): {name!r} ({exc})") from exc

        try:
            target.relative_to(root_resolved)
        except ValueError:
            raise ValueError(
                f"ZIP entry rifiutata (destinazione fuori dalla solution root): {name!r} -> {target}"
            )



def find_zip_declared_script(members: list[str]) -> str | None:
    """
    T2.1: individua esattamente 0 o 1 script operativo dichiarato dallo ZIP.
    Path attesi (separatori / o \\ normalizzati):
      .turbo-ai/temp/FromLlm-*.py
      .turbo-ai/temp/FromLlm-*.ps1
    Se ne trova piu' di uno solleva ValueError.
    Ritorna il path relativo normalizzato con / oppure None.
    """
    matches: list[str] = []
    for raw in members:
        if raw.endswith("/"):
            continue
        # Normalizza separatori
        norm = raw.replace("\\", "/").replace("\\", "/")
        # Accetta solo sotto .turbo-ai/temp/
        lower = norm.lower()
        if not lower.startswith(".turbo-ai/temp/"):
            continue
        name = Path(norm).name
        if not name.lower().startswith("fromllm-"):
            continue
        if name.lower().endswith((".py", ".ps1")):
            matches.append(norm)
    if len(matches) > 1:
        raise ValueError(
            f"ZIP dichiara {len(matches)} script operativi (max 1 consentito): {matches}"
        )
    return matches[0] if matches else None


def main() -> int:
    TO_LLM_PATH.write_text("", encoding="utf-8")
    log("=== process-zip-and-scripts-from-llm v1.6 (Python) ===")
    log(f"Esecuzione avviata: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Solution Root: {SOLUTION_ROOT}")

    log(f"==> Cerco in Download il file piu' recente con pattern '{ZIP_PATTERN}'...")
    zip_candidates = list(DOWNLOADS_PATH.glob(ZIP_PATTERN))
    latest_zip = latest_by_mtime(zip_candidates)

    if latest_zip is None:
        # T2.4: ramo standalone esplicito — solo script da Downloads, niente scan root/temp
        log("==> Nessuno zip trovato. Cerco in Download lo script standalone piu' recente (.ps1 o .py)...")
        script_candidates = [
            p for pattern in SCRIPT_PATTERNS for p in DOWNLOADS_PATH.glob(pattern)
        ]
        latest_script = latest_by_mtime(script_candidates)

        if latest_script is None:
            err = f"Nessuno zip o script FromLlm-*.{{py|ps1}} trovato in {DOWNLOADS_PATH}."
            log(f"ERRORE: {err}")
            return 1

        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        dest_script = TEMP_DIR / latest_script.name
        log(f"==> Script standalone selezionato: {latest_script.name}")
        log("==> Stage in .turbo-ai/temp (T2.4)...")
        if dest_script.exists():
            dest_script.unlink()
        shutil.move(str(latest_script), str(dest_script))

        rc = 1
        try:
            rc = invoke_llm_script(dest_script, SOLUTION_ROOT)
            if rc != 0:
                log(f"==> Script terminato con exit code {rc}.")
        finally:
            # T2.4: elimina in finally (allineato al ramo ZIP)
            try:
                if dest_script.is_file():
                    dest_script.unlink()
                    log(f"==> Script standalone eliminato (T2.4): {dest_script.name}")
            except OSError as exc:
                log(f"==> WARNING: impossibile eliminare script standalone {dest_script.name}: {exc}")

        log("==> Esecuzione completata.")
        return rc

    # --- Gestione ZIP (T1.1 + T1.2) ---
    log(f"==> Zip selezionato: {latest_zip}")
    archived_zip = archive_zip_to_history(latest_zip)

    log("==> Validazione entry ZIP (T1.2)...")
    with zipfile.ZipFile(archived_zip) as zf:
        members = zf.namelist()
        try:
            validate_zip_members(members, SOLUTION_ROOT)
        except ValueError as exc:
            log(f"ERRORE validazione ZIP: {exc}")
            log("==> ZIP lasciato in history per ispezione. Nessuna estrazione eseguita.")
            return 1
        log(f"==> Validazione OK ({len(members)} entry).")

        # T2.1: individua lo script dichiarato PRIMA dell'estrazione
        try:
            declared_script_rel = find_zip_declared_script(members)
        except ValueError as exc:
            log(f"ERRORE inventario script ZIP: {exc}")
            log("==> ZIP lasciato in history per ispezione. Nessuna estrazione eseguita.")
            return 1
        if declared_script_rel:
            log(f"==> Script dichiarato dall'inventario ZIP: {declared_script_rel}")
        else:
            log("==> Nessuno script operativo dichiarato dall'inventario ZIP.")

        log("==> Estraggo il contenuto dall'archivio preservato...")
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

    # ZIP resta in history come copia autorevole (T1.1) — non viene eliminato.

    # T2.1 + T2.2 + T2.3: esegui solo lo script dichiarato; elimina in finally.
    if declared_script_rel is None:
        log("==> Nessuno script operativo dichiarato dallo ZIP. Fine.")
        return 0

    script_path = SOLUTION_ROOT / declared_script_rel
    if not script_path.is_file():
        log(f"ERRORE: script dichiarato dallo ZIP non trovato dopo estrazione: {declared_script_rel}")
        return 1

    log(f"==> Script dichiarato dallo ZIP: {declared_script_rel}")
    rc = 1
    try:
        rc = invoke_llm_script(script_path, SOLUTION_ROOT)
        if rc != 0:
            log(f"==> {script_path.name} terminato con exit code {rc}.")
    finally:
        # T2.3: elimina lo script estratto; la copia autorevole resta nel ZIP in history
        try:
            if script_path.is_file():
                script_path.unlink()
                log(f"==> Script estratto eliminato (T2.3): {declared_script_rel}")
        except OSError as exc:
            log(f"==> WARNING: impossibile eliminare script estratto {declared_script_rel}: {exc}")

    log("==> Esecuzione completata.")
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        log(f"ERRORE: {exc}")
        sys.exit(1)


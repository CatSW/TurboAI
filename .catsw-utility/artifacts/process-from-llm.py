#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.5 – 2026-08-14
# T4.4: resolve_base64_mode completa (Env > Governance > default false)
"""
Orchestratore unificato per artefatti LLM e context-request.

Scansiona Downloads, individua il file più recente tra:
  - context-request-*.md          (Categoria A)
  - FromLlm-*.{py|ps1|zip}        (Categoria B)

Se il nome è "adornato" (prefissi, virgolette, doppie estensioni) lo
rinomina subito nella forma canonica.

Poi:
  - Categoria A → lascia il .md in Downloads e lancia ContextBundler.exe
  - Categoria B → delega a process-zip-and-scripts-from-llm.py
                  (che gestisce zip/script e archivia gli script eseguiti)

Al termine sposta il file originale da Downloads in
.catsw-utility/history/ con prefisso timestamp (così non viene
rielaborato e non si sovrascrivono versioni diverse con lo stesso nome).

Tutto l'output va su console + Downloads\\ToLlm.txt (tee).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Path layout
# ---------------------------------------------------------------------------
# Questo script vive in .catsw-utility/artifacts/

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


def _parse_boolish(raw: str) -> bool | None:
    """Return True/False for known values, None if invalid/empty."""
    if raw is None:
        return None
    val = raw.strip().lower()
    if not val:
        return None
    if val in ("true", "1", "yes"):
        return True
    if val in ("false", "0", "no"):
        return False
    return None


def _read_governance_base64(solution_root: Path) -> bool | None:
    """
    Parse ContextBundler_output_base64 from .ai-context/SOLUTION_GOVERNANCE.md.
    Returns True/False if a valid value is found, None if missing/invalid/file absent.
    Tolerant of markdown list markers, backticks, extra whitespace and case.
    """
    gov_path = solution_root / ".ai-context" / "SOLUTION_GOVERNANCE.md"
    if not gov_path.is_file():
        return None
    try:
        text = gov_path.read_text(encoding="utf-8")
    except OSError:
        return None

    # Look for lines containing the key (case-insensitive)
    key_re = re.compile(
        r"ContextBundler_output_base64\s*[:=]\s*[`'\"]?([^\s`'\"]+)[`'\"]?",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        m = key_re.search(line)
        if m:
            return _parse_boolish(m.group(1))
    return None


def resolve_base64_mode(solution_root: Path | None = None) -> tuple[bool, str]:
    """
    Effective base64 mode for ContextBundler.
    Precedence: env TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64
                > Governance ContextBundler_output_base64
                > default false.
    Accepts true/false/1/0/yes/no (case-insensitive, surrounding whitespace).
    Invalid values are ignored and fall through to the next level.
    """
    # 1. Environment variable (highest priority)
    env_val = os.environ.get("TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64")
    parsed = _parse_boolish(env_val) if env_val is not None else None
    if parsed is not None:
        return parsed, "env"

    # 2. Governance file
    if solution_root is None:
        # Best-effort: derive from this script location
        artefacts = Path(__file__).resolve().parent
        solution_root = artefacts.parent.parent
    gov_val = _read_governance_base64(solution_root)
    if gov_val is not None:
        return gov_val, "governance"

    # 3. Default
    return False, "default"


configure_utf8_stdio()

ARTEFACTS_ROOT = Path(__file__).resolve().parent          # .../.catsw-utility/artifacts
UTILITY_ROOT = ARTEFACTS_ROOT.parent                      # .../.catsw-utility
SOLUTION_ROOT = UTILITY_ROOT.parent                       # root della solution
HISTORY_DIR = UTILITY_ROOT / "history"

CONTEXT_BUNDLER_EXE = ARTEFACTS_ROOT / "ContextBundler.exe"
PROCESS_ZIP_SCRIPT = ARTEFACTS_ROOT / "process-zip-and-scripts-from-llm.py"

# ---------------------------------------------------------------------------
# Downloads + logging (identico allo stile esistente)
# ---------------------------------------------------------------------------
def get_downloads_path() -> Path:
    """Replica la risoluzione del registro Explorer\\Shell Folders."""
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


# ---------------------------------------------------------------------------
# Pattern e sanitizzazione
# ---------------------------------------------------------------------------
# Categoria A: context-request-*.md (separatore dopo il prefisso tollerante a - _ spazio)
RE_CONTEXT = re.compile(
    r"context-request[-_ ]+([^\"'<>|?*]+\.md)",
    re.IGNORECASE,
)

# Categoria B: FromLlm-*.{py|ps1|zip} (stesso discorso sul separatore)
RE_FROMLLM = re.compile(
    r"FromLlm[-_ ]+([^\"'<>|?*]+\.(?:py|ps1|zip))",
    re.IGNORECASE,
)


def sanitize_name(original_name: str) -> str | None:
    """
    Estrae il nome canonico da un nome eventualmente adornato, normalizzando
    il separatore dopo il prefisso (-, _, spazio) sempre al trattino canonico.
    Ritorna None se non riconosce nessun pattern valido.
    """
    # Prova prima FromLlm (più specifico sulle estensioni)
    m = RE_FROMLLM.search(original_name)
    if m:
        return f"FromLlm-{m.group(1)}"

    m = RE_CONTEXT.search(original_name)
    if m:
        return f"context-request-{m.group(1)}"

    return None


def is_context_request(name: str) -> bool:
    return name.lower().startswith("context-request-") and name.lower().endswith(".md")


def is_fromllm(name: str) -> bool:
    lower = name.lower()
    return lower.startswith("fromllm-") and lower.endswith((".py", ".ps1", ".zip"))


def latest_by_mtime(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda p: p.stat().st_mtime)


# ---------------------------------------------------------------------------
# Archiviazione in history
# ---------------------------------------------------------------------------
def archive_to_history(file_path: Path) -> Path:
    """Sposta il file in history/ con prefisso timestamp. Ritorna il path di destinazione."""
    HISTORY_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = HISTORY_DIR / f"{timestamp}-{file_path.name}"
    shutil.move(str(file_path), str(dest))
    log(f"==> Archiviato in history: {dest.relative_to(SOLUTION_ROOT)}")
    return dest


# ---------------------------------------------------------------------------
# Esecuzione ContextBundler
# ---------------------------------------------------------------------------
def run_context_bundler() -> int:
    if not CONTEXT_BUNDLER_EXE.exists():
        log(f"ERRORE: ContextBundler.exe non trovato in {CONTEXT_BUNDLER_EXE}")
        return 1

    # Eseguiamo move-to-history.py per archiviare i file residui della sessione precedente
    move_script = ARTEFACTS_ROOT / "move-to-history.py"
    if move_script.exists():
        log(f"==> Esecuzione di {move_script.name}...")
        move_result = subprocess.run(
            [sys.executable, str(move_script)],
            cwd=str(ARTEFACTS_ROOT),
            check=False,
            env=utf8_child_env(),
        )
        if move_result.returncode != 0:
            log(f"==> Attenzione: {move_script.name} ha terminato con codice {move_result.returncode}")
    else:
        log(f"==> ERRORE: Script di archiviazione {move_script.name} non trovato")
        return 1

    to_base64, source = resolve_base64_mode(SOLUTION_ROOT)
    cmd = [str(CONTEXT_BUNDLER_EXE)]
    if to_base64:
        cmd.append("--base64")

    log(f"==> Lancio ContextBundler: {CONTEXT_BUNDLER_EXE.name}  (base64={to_base64}, source={source})")
    # Nessun argomento posizionale: ContextBundler (SmartAssFileResolver) cerca già in Downloads.
    try:
        result = subprocess.run(
            cmd,
            cwd=str(UTILITY_ROOT),
            check=False,
            env=utf8_child_env(),
        )
        return result.returncode
    except Exception as exc:
        log(f"ERRORE durante l'esecuzione di ContextBundler: {exc}")
        return 1


# ---------------------------------------------------------------------------
# Delega a process-zip-and-scripts-from-llm.py
# ---------------------------------------------------------------------------
def run_process_zip_and_scripts() -> int:
    if not PROCESS_ZIP_SCRIPT.exists():
        log(f"ERRORE: {PROCESS_ZIP_SCRIPT.name} non trovato")
        return 1

    log(f"==> Delega a {PROCESS_ZIP_SCRIPT.name}...")
    # Eseguiamo lo script esistente come sottoprocesso così riusiamo tutta
    # la logica di zip/script/archiviazione interna senza duplicarla.
    cmd = [sys.executable, str(PROCESS_ZIP_SCRIPT)]
    result = subprocess.run(cmd, cwd=str(ARTEFACTS_ROOT), check=False, env=utf8_child_env())
    return result.returncode


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    TO_LLM_PATH.write_text("", encoding="utf-8")
    log("=== process-from-llm v1.5 (Python) - orchestratore unificato ===")
    log(f"Esecuzione avviata: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Solution Root : {SOLUTION_ROOT}")
    log(f"Utility Root  : {UTILITY_ROOT}")
    log(f"Downloads     : {DOWNLOADS_PATH}")

    # 1. Raccogli tutti i candidati (anche con nomi adornati)
    candidates: list[Path] = []
    try:
        for entry in DOWNLOADS_PATH.iterdir():
            if not entry.is_file():
                continue
            # Accettiamo sia nomi già puliti sia nomi adornati che contengono
            # una delle due forme canoniche.
            if sanitize_name(entry.name) is not None:
                candidates.append(entry)
    except Exception as exc:
        log(f"ERRORE durante la scansione di Downloads: {exc}")
        return 1

    if not candidates:
        # Fallback root/temp rimosso (assessment T0.1 / T2.4): gli orfani sono
        # gestiti dalla rotazione preventiva move-to-history, non rieseguiti qui.
        err = f"Nessun file context-request-*.md o FromLlm-*.{{py|ps1|zip}} trovato in {DOWNLOADS_PATH}."
        log(f"ERRORE: {err}")
        return 1

    # 2. Prendi solo il più recente
    latest = latest_by_mtime(candidates)
    assert latest is not None
    log(f"==> File più recente selezionato: {latest.name}")

    # 3. Sanitizzazione / rename se necessario
    clean_name = sanitize_name(latest.name)
    assert clean_name is not None

    working_file = latest
    if latest.name != clean_name:
        dest = DOWNLOADS_PATH / clean_name
        if dest.exists():
            log(f"WARNING: destinazione di rename già esistente ({dest.name}), sovrascrivo.")
            dest.unlink()
        log(f"WARNING: nome adornato rilevato → rinomino '{latest.name}' → '{clean_name}'")
        latest.rename(dest)
        working_file = dest
    else:
        log(f"==> Nome già canonico: {working_file.name}")

    # 4. Delega in base alla categoria
    exit_code = 0
    try:
        if is_context_request(working_file.name):
            log("==> Categoria A (context-request) → ContextBundler")
            exit_code = run_context_bundler()
            # ContextBundler sposta/gestisce il file da solo.
            # Se il file è ancora in Downloads dopo l'esecuzione lo archiviamo noi.
            if working_file.exists():
                archive_to_history(working_file)
            else:
                log("==> Il file non è più in Downloads (gestito da ContextBundler).")
        elif is_fromllm(working_file.name):
            log("==> Categoria B (FromLlm artifact) → process-zip-and-scripts-from-llm")
            # process-zip-and-scripts-from-llm.py cerca lui stesso in Downloads
            # il file più recente FromLlm-*.{zip|py|ps1}. Dopo la sanitizzazione
            # il file è già in forma corretta, quindi lo troverà.
            exit_code = run_process_zip_and_scripts()
            # Lo script interno archivia solo gli script eseguiti dentro
            # .catsw-utility. Il file originale in Downloads lo archiviamo noi
            # (se è ancora presente: per gli zip viene archiviato dallo script interno).
            if working_file.exists():
                archive_to_history(working_file)
            else:
                log("==> Il file non è più in Downloads (già gestito dallo script interno).")
        else:
            log(f"ERRORE: nome non riconosciuto dopo sanitizzazione: {working_file.name}")
            exit_code = 1
    except Exception as exc:
        log(f"ERRORE durante l'elaborazione: {exc}")
        exit_code = 1

    if exit_code != 0:
        log(f"==> Elaborazione terminata con exit code {exit_code}.")
    log("==> Esecuzione completata.")
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        log(f"ERRORE non gestito: {exc}")
        sys.exit(1)

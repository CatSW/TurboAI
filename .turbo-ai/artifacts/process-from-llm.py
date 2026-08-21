#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.10

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
    gov_path = solution_root / ".ai-context" / "SOLUTION_GOVERNANCE.md"
    if not gov_path.is_file():
        return None
    try:
        text = gov_path.read_text(encoding="utf-8")
    except OSError:
        return None

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
    env_val = os.environ.get("TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64")
    parsed = _parse_boolish(env_val) if env_val is not None else None
    if parsed is not None:
        return parsed, "env"

    if solution_root is None:
        artefacts = Path(__file__).resolve().parent
        solution_root = artefacts.parent.parent
    gov_val = _read_governance_base64(solution_root)
    if gov_val is not None:
        return gov_val, "governance"

    return False, "default"


configure_utf8_stdio()

ARTEFACTS_ROOT = Path(__file__).resolve().parent          # .../.turbo-ai/artifacts
UTILITY_ROOT = ARTEFACTS_ROOT.parent                      # .../.turbo-ai
SOLUTION_ROOT = UTILITY_ROOT.parent                       # root della solution
HISTORY_DIR = UTILITY_ROOT / "history"

CONTEXT_BUNDLER_EXE = ARTEFACTS_ROOT / "ContextBundler.exe"
PROCESS_ZIP_SCRIPT = ARTEFACTS_ROOT / "process-zip-and-scripts-from-llm.py"
PROCESS_C_CHANNEL_CMD = UTILITY_ROOT / "process-c-channel.cmd"
MOVE_TO_HISTORY_CMD = UTILITY_ROOT / "move-to-history.cmd"

# ---------------------------------------------------------------------------
# Downloads + logging
# ---------------------------------------------------------------------------
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


DOWNLOADS_PATH = get_downloads_path()
TO_LLM_PATH = DOWNLOADS_PATH / "ToLlm.txt"


def log(msg: str) -> None:
    print(msg)
    with TO_LLM_PATH.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


# ---------------------------------------------------------------------------
# Pattern e sanitizzazione
# ---------------------------------------------------------------------------
RE_CONTEXT = re.compile(
    r"context-request[-_ ]+([^\"'<>|?*]+\.md)",
    re.IGNORECASE,
)

RE_FROMLLM = re.compile(
    r"FromLlm[-_ ]+([^\"'<>|?*]+\.(?:py|ps1|zip))",
    re.IGNORECASE,
)

RE_FROMC = re.compile(
    r"FromC[-_ ]+([^\"'<>|?*]+\.py)",
    re.IGNORECASE,
)


def sanitize_name(original_name: str) -> str | None:
    # FromC-*.py → normalizzato a FromLlm-*.py (riusa il flusso standard)
    m = RE_FROMC.search(original_name)
    if m:
        return f"FromLlm-{m.group(1)}"

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


def is_fromc_original(original_name: str) -> bool:
    """True se il nome originale (prima del rename) era un FromC-*.py."""
    return RE_FROMC.search(original_name) is not None


def latest_by_mtime(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda p: p.stat().st_mtime)


# ---------------------------------------------------------------------------
# Archiviazione in history
# ---------------------------------------------------------------------------
def archive_to_history(file_path: Path) -> Path:
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

    to_base64, source = resolve_base64_mode(SOLUTION_ROOT)
    cmd = [str(CONTEXT_BUNDLER_EXE)]
    if to_base64:
        cmd.append("--base64")

    log(f"==> Lancio ContextBundler: {CONTEXT_BUNDLER_EXE.name}  (base64={to_base64}, source={source})")
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
    cmd = [sys.executable, str(PROCESS_ZIP_SCRIPT)]
    result = subprocess.run(cmd, cwd=str(ARTEFACTS_ROOT), check=False, env=utf8_child_env())
    return result.returncode


def run_cmd_file(cmd_path: Path) -> int:
    """Esegue un .cmd in UTILITY_ROOT e restituisce l'exit code."""
    if not cmd_path.exists():
        log(f"ERRORE: {cmd_path.name} non trovato in {cmd_path.parent}")
        return 1
    log(f"==> Lancio {cmd_path.name}...")
    try:
        result = subprocess.run(
            ["cmd.exe", "/c", str(cmd_path)],
            cwd=str(UTILITY_ROOT),
            check=False,
            env=utf8_child_env(),
        )
        return result.returncode
    except Exception as exc:
        log(f"ERRORE durante l'esecuzione di {cmd_path.name}: {exc}")
        return 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    TO_LLM_PATH.write_text("", encoding="utf-8")
    log("=== process-from-llm v1.8 - orchestratore unificato + FromC ===")
    log(f"Esecuzione avviata: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Solution Root : {SOLUTION_ROOT}")
    log(f"Utility Root  : {UTILITY_ROOT}")
    log(f"Downloads     : {DOWNLOADS_PATH}")

    candidates: list[Path] = []
    try:
        for entry in DOWNLOADS_PATH.iterdir():
            if not entry.is_file():
                continue
            if sanitize_name(entry.name) is not None:
                candidates.append(entry)
    except Exception as exc:
        log(f"ERRORE durante la scansione di Downloads: {exc}")
        return 1

    if not candidates:
        err = (
            f"Nessun file context-request-*.md, FromLlm-*.{{py|ps1|zip}} "
            f"o FromC-*.py trovato in {DOWNLOADS_PATH}."
        )
        log(f"ERRORE: {err}")
        return 1

    latest = latest_by_mtime(candidates)
    assert latest is not None
    original_name = latest.name
    log(f"==> File più recente selezionato: {original_name}")

    # Flag: era un FromC-*.py? (serve per le post-azioni)
    was_fromc = is_fromc_original(original_name)

    clean_name = sanitize_name(original_name)
    assert clean_name is not None

    working_file = latest
    if latest.name != clean_name:
        dest = DOWNLOADS_PATH / clean_name
        if dest.exists():
            log(f"WARNING: destinazione di rename già esistente ({dest.name}), sovrascrivo.")
            dest.unlink()
        if was_fromc:
            log(f"==> FromC rilevato → rinomino '{original_name}' → '{clean_name}' (flusso FromLlm)")
        else:
            log(f"WARNING: nome adornato rilevato → rinomino '{original_name}' → '{clean_name}'")
        latest.rename(dest)
        working_file = dest
    else:
        log(f"==> Nome già canonico: {working_file.name}")

    exit_code = 0
    try:
        if is_context_request(working_file.name):
            # Il contenuto va letto ORA: ContextBundler.exe consuma/sposta
            # il file da Downloads durante la propria esecuzione, quindi
            # dopo la chiamata non e' piu' garantito poterlo rileggere.
            context_request_content: str | None = None
            try:
                context_request_content = working_file.read_text(encoding="utf-8")
            except OSError as exc:
                log(f"WARNING: impossibile leggere il contenuto di {working_file.name} prima dell'esecuzione: {exc}")

            log("==> Categoria A (context-request) → ContextBundler")
            exit_code = run_context_bundler()
            if working_file.exists():
                archive_to_history(working_file)
            else:
                log("==> Il file non è più in Downloads (gestito da ContextBundler).")

            if context_request_content is not None:
                log("==> Contenuto context-request:")
                log(context_request_content)
        elif is_fromllm(working_file.name):
            log("==> Categoria B (FromLlm artifact) → process-zip-and-scripts-from-llm")
            exit_code = run_process_zip_and_scripts()
            if working_file.exists():
                archive_to_history(working_file)
            else:
                log("==> Il file non è più in Downloads (già gestito dallo script interno).")

            # Post-azioni solo per FromC e solo su successo (fail-fast)
            if was_fromc and exit_code == 0:
                log("==> FromC: avvio post-azioni (process-c-channel + move-to-history)")
                rc1 = run_cmd_file(PROCESS_C_CHANNEL_CMD)
                if rc1 != 0:
                    log(f"==> process-c-channel.cmd terminato con exit code {rc1} (fail-fast)")
                    exit_code = rc1
                else:
                    rc2 = run_cmd_file(MOVE_TO_HISTORY_CMD)
                    if rc2 != 0:
                        log(f"==> move-to-history.cmd terminato con exit code {rc2}")
                        exit_code = rc2
                    else:
                        log("==> Post-azioni FromC completate con successo")
            elif was_fromc and exit_code != 0:
                log("==> FromC: script fallito → post-azioni saltate (fail-fast)")
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


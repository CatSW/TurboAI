#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.1
# -*- coding: utf-8 -*-
r"""
from-llm-watcher.py
Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
Version 1.1

Monitora %USERPROFILE%\Downloads e, quando arrivano file FromLlm-* o
context-request-*, lancia l'unico orchestratore process-from-llm.cmd
nella cartella .catsw-utility.

Lo spostamento effettivo dei file e la sanitizzazione dei nomi "adornati"
sono responsabilità di process-from-llm.py.
Questo watcher si limita a rilevare il file stabile e lanciare il .cmd.
"""

from __future__ import annotations

import os
import re
import sys
import time
import logging
import subprocess
from pathlib import Path
from typing import Optional, Set

# ---------------------------------------------------------------------------
# Configurazione
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


configure_utf8_stdio()

DOWNLOADS = Path(os.environ["USERPROFILE"]) / "Downloads"
SCRIPT_DIR = Path(__file__).resolve().parent          # .../.catsw-utility/artifacts
CATSW_DIR = SCRIPT_DIR.parent                         # .../.catsw-utility

# Unico entry-point unificato (sostituisce i due vecchi .cmd)
PROCESS_CMD = CATSW_DIR / "process-from-llm.cmd"

# Tempo di stabilizzazione (secondi) per considerare un file "completo"
STABLE_SECONDS = 2.0
# Tempo minimo tra due lanci sullo stesso file (anti-ripetizione)
COOLDOWN_SECONDS = 15.0

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("from-llm-watcher")

# ---------------------------------------------------------------------------
# Stato
# ---------------------------------------------------------------------------
# file_path -> timestamp ultimo lancio
_last_launch: dict[Path, float] = {}
# file attualmente in fase di stabilizzazione
_pending: dict[Path, float] = {}          # path -> size visto l'ultima volta
_pending_time: dict[Path, float] = {}     # path -> quando abbiamo visto quella size

# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------
def is_fromllm(path: Path) -> bool:
    name = path.name
    # Accettiamo anche nomi leggermente adornati: basta che contengano il pattern
    lower = name.lower()
    return (
        "fromllm-" in lower
        and any(lower.endswith(ext) or f"{ext}." in lower for ext in (".zip", ".py", ".ps1"))
    ) or (
        name.startswith("FromLlm-")
        and path.suffix.lower() in {".zip", ".py", ".ps1"}
    )


_CONTEXT_REQUEST_RE = re.compile(r"context-request[-_ ]+")


def is_context_request(path: Path) -> bool:
    lower = path.name.lower()
    return bool(_CONTEXT_REQUEST_RE.search(lower)) and (lower.endswith(".md") or ".md." in lower)


def get_target_cmd(path: Path) -> Optional[Path]:
    if is_fromllm(path) or is_context_request(path):
        return PROCESS_CMD
    return None


def can_launch(path: Path) -> bool:
    """True se non abbiamo già lanciato di recente sullo stesso file."""
    last = _last_launch.get(path)
    if last is None:
        return True
    return (time.time() - last) >= COOLDOWN_SECONDS


def launch_cmd(cmd: Path, source_file: Path) -> None:
    if not cmd.exists():
        log.error("Cmd non trovato: %s", cmd)
        return

    log.info("Lancio %s per %s", cmd.name, source_file.name)

    # Nuova console visibile (Windows)
    creationflags = subprocess.CREATE_NEW_CONSOLE  # type: ignore[attr-defined]

    try:
        subprocess.Popen(
            ["cmd.exe", "/c", str(cmd)],
            cwd=str(CATSW_DIR),
            creationflags=creationflags,
            env=utf8_child_env(),
        )
        _last_launch[source_file] = time.time()
    except Exception as e:
        log.exception("Errore nel lancio di %s: %s", cmd.name, e)


def check_stability(path: Path) -> bool:
    """
    Restituisce True se il file esiste e la size è stabile da STABLE_SECONDS.
    """
    if not path.exists() or not path.is_file():
        _pending.pop(path, None)
        _pending_time.pop(path, None)
        return False

    try:
        size = path.stat().st_size
    except OSError:
        return False

    now = time.time()
    prev_size = _pending.get(path)

    if prev_size is None or prev_size != size:
        # Size cambiata → reset timer
        _pending[path] = size
        _pending_time[path] = now
        return False

    # Size uguale → verifica se è passato abbastanza tempo
    if (now - _pending_time[path]) >= STABLE_SECONDS:
        return True
    return False


def try_process(path: Path) -> None:
    """Controlla e, se pronto, lancia il cmd appropriato."""
    cmd = get_target_cmd(path)
    if cmd is None:
        return

    if not can_launch(path):
        return

    if check_stability(path):
        launch_cmd(cmd, path)
        # Pulisco lo stato di stabilizzazione
        _pending.pop(path, None)
        _pending_time.pop(path, None)


# ---------------------------------------------------------------------------
# Scansione iniziale
# ---------------------------------------------------------------------------
def process_existing() -> None:
    log.info("Scansione file già presenti in Downloads...")
    try:
        for entry in DOWNLOADS.iterdir():
            if entry.is_file() and get_target_cmd(entry):
                log.info("File esistente trovato: %s", entry.name)
                # Forziamo la stabilizzazione immediata (file già scritto)
                _pending[entry] = entry.stat().st_size
                _pending_time[entry] = time.time() - STABLE_SECONDS - 1
                try_process(entry)
    except Exception as e:
        log.exception("Errore durante la scansione iniziale: %s", e)


# ---------------------------------------------------------------------------
# Watcher (watchdog se disponibile, altrimenti polling)
# ---------------------------------------------------------------------------
def run_with_watchdog() -> None:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class Handler(FileSystemEventHandler):
        def on_created(self, event):
            if not event.is_directory:
                p = Path(event.src_path)
                if get_target_cmd(p):
                    log.info("Nuovo file rilevato: %s", p.name)
                    try_process(p)

        def on_modified(self, event):
            if not event.is_directory:
                p = Path(event.src_path)
                if get_target_cmd(p):
                    try_process(p)

    observer = Observer()
    observer.schedule(Handler(), str(DOWNLOADS), recursive=False)
    observer.start()
    log.info("Watcher avviato (watchdog) su %s", DOWNLOADS)

    try:
        while True:
            # Periodicamente riproviamo i file ancora in pending
            for p in list(_pending.keys()):
                try_process(p)
            time.sleep(0.5)
    except KeyboardInterrupt:
        log.info("Arresto richiesto")
    finally:
        observer.stop()
        observer.join()


def run_with_polling() -> None:
    log.info("Watcher avviato (polling) su %s", DOWNLOADS)
    known: Set[Path] = set()

    try:
        while True:
            current: Set[Path] = set()
            try:
                for entry in DOWNLOADS.iterdir():
                    if entry.is_file() and get_target_cmd(entry):
                        current.add(entry)
                        if entry not in known:
                            log.info("Nuovo file rilevato: %s", entry.name)
                        try_process(entry)
            except Exception as e:
                log.warning("Errore durante il polling: %s", e)

            known = current
            time.sleep(1.0)
    except KeyboardInterrupt:
        log.info("Arresto richiesto")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    log.info("from-llm-watcher avviato (v1.1 - orchestratore unificato)")
    log.info("Cartella monitorata : %s", DOWNLOADS)
    log.info("Cartella .catsw-utility: %s", CATSW_DIR)
    log.info("Cmd unificato       : %s", PROCESS_CMD.name)

    if not DOWNLOADS.exists():
        log.error("Cartella Downloads non trovata: %s", DOWNLOADS)
        return 1

    if not PROCESS_CMD.exists():
        log.warning("process-from-llm.cmd non trovato – il watcher non potrà lanciare nulla")

    process_existing()

    try:
        run_with_watchdog()
    except ImportError:
        log.warning("watchdog non installato → uso polling (pip install watchdog consigliato)")
        run_with_polling()

    return 0


if __name__ == "__main__":
    sys.exit(main())

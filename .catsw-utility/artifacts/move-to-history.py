#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.1

from __future__ import annotations

import fnmatch
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def configure_utf8_stdio() -> None:
    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")


def get_unique_dest(history_dir: Path, timestamp: str, src_path: Path) -> Path:
    """
    Genera un path unico in history per evitare sovrascritture in caso di collisioni.
    Format: YYYYMMDD-HHMMSS-<nome_originale>
    Collisione: YYYYMMDD-HHMMSS-<stem>_<N><suffix>
    """
    stem = src_path.stem
    suffix = src_path.suffix
    candidate_name = f"{timestamp}-{src_path.name}"
    candidate_path = history_dir / candidate_name

    counter = 1
    while candidate_path.exists():
        candidate_name = f"{timestamp}-{stem}_{counter}{suffix}"
        candidate_path = history_dir / candidate_name
        counter += 1

    return candidate_path


def should_rotate_root_file(filename: str) -> bool:
    """Verifica se un file presente nella radice di .catsw-utility deve essere ruotato."""
    patterns = (
        "context-request-*",
        "context-out-*",
        "ToLlm_*",
        "*-ToLlm.txt",
    )
    return any(fnmatch.fnmatch(filename, pat) for pat in patterns)


def main() -> int:
    configure_utf8_stdio()

    artefacts_root = Path(__file__).resolve().parent
    utility_root = artefacts_root.parent
    temp_dir = utility_root / "temp"
    history_dir = utility_root / "history"

    history_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    candidates: list[Path] = []

    # 1. Scansione non ricorsiva della radice di .catsw-utility
    if utility_root.exists():
        for item in utility_root.iterdir():
            if item.is_file() and should_rotate_root_file(item.name):
                candidates.append(item)

    # 2. Scansione non ricorsiva della cartella temp
    if temp_dir.exists():
        for item in temp_dir.iterdir():
            if item.is_file():
                candidates.append(item)

    if not candidates:
        print("Nessun file residuo da spostare in history.")
        return 0

    rotated_count = 0
    errors_count = 0

    for src_path in candidates:
        try:
            dest_path = get_unique_dest(history_dir, timestamp, src_path)
            shutil.move(str(src_path), str(dest_path))
            print(f"Archiviato: {src_path.name} -> history/{dest_path.name}")
            rotated_count += 1
        except Exception as exc:
            print(
                f"ERRORE durante l'archiviazione di {src_path.name}: {exc}",
                file=sys.stderr,
            )
            errors_count += 1

    print(f"Completato. File ruotati: {rotated_count}, Errori: {errors_count}")
    return 1 if errors_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""Convert a file to a plain Base64 text file.

Usage:
    py FromLlm-file-to-base64.py <input-file>

Example:
    py FromLlm-file-to-base64.py nome.md

Output:
    nome_md_base64.txt
"""

from __future__ import annotations

import argparse
import base64
import hashlib
from pathlib import Path


def output_path_for(source: Path) -> Path:
    extension = source.suffix[1:] if source.suffix else "file"
    stem = source.name[: -len(source.suffix)] if source.suffix else source.name
    return source.with_name(f"{stem}_{extension}_base64.txt")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a file to plain Base64 text.")
    parser.add_argument("input_file", type=Path, help="Path of the file to encode")
    args = parser.parse_args()

    source = args.input_file.expanduser().resolve()
    if not source.is_file():
        parser.error(f"File not found: {source}")

    raw = source.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    destination = output_path_for(source)
    destination.write_text(encoded + "\n", encoding="ascii", newline="\n")

    print(f"Input:  {source}")
    print(f"Output: {destination}")
    print(f"Bytes:  {len(raw)}")
    print(f"SHA256: {hashlib.sha256(raw).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""Restore a file from a plain Base64 text file.

Usage:
    py FromLlm-base64-to-file.py <base64-file>

Example:
    py FromLlm-base64-to-file.py nome_md_base64.txt

Output:
    nome.md
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
from pathlib import Path


SUFFIX = "_base64.txt"


def output_path_for(source: Path) -> Path:
    if not source.name.endswith(SUFFIX):
        raise ValueError(f"Expected a file name ending with {SUFFIX!r}")

    encoded_name = source.name[: -len(SUFFIX)]
    if "_" not in encoded_name:
        raise ValueError("Expected the name pattern <stem>_<extension>_base64.txt")

    stem, extension = encoded_name.rsplit("_", 1)
    if not stem or not extension:
        raise ValueError("Stem and extension must not be empty")

    return source.with_name(f"{stem}.{extension}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore a file from plain Base64 text.")
    parser.add_argument("base64_file", type=Path, help="Path of the Base64 text file")
    args = parser.parse_args()

    source = args.base64_file.expanduser().resolve()
    if not source.is_file():
        parser.error(f"File not found: {source}")

    try:
        destination = output_path_for(source)
        compact = "".join(source.read_text(encoding="ascii").split())
        raw = base64.b64decode(compact, validate=True)
    except (ValueError, UnicodeError, binascii.Error) as exc:
        parser.error(str(exc))

    destination.write_bytes(raw)

    print(f"Input:  {source}")
    print(f"Output: {destination}")
    print(f"Bytes:  {len(raw)}")
    print(f"SHA256: {hashlib.sha256(raw).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

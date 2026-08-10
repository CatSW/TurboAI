#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""
Extract the content between <next_task> and </next_task> tags from a plan file.
Usage:
    python extract_next_task.py <path-to-Piano.md>
"""

import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def extract_next_task(text: str) -> str:
    match = re.search(r"<next_task>\s*\n?(.*?)\n?\s*</next_task>", text, re.DOTALL)
    if not match:
        return "# No <next_task> tags found in plan."
    return match.group(1).strip("\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_next_task.py <Piano.md>", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    result = extract_next_task(text)
    print(result)


if __name__ == "__main__":
    main()

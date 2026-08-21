#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.1
"""
Extract the content between <next_task> and </next_task> tags from a plan file.

Both tags must appear alone on their own line (optionally surrounded by
whitespace) to be recognized as structural delimiters. This avoids matching
literal mentions of "<next_task>" inside prose elsewhere in the plan (e.g.
a task description that talks *about* the tag), which would otherwise be
picked up by a naive substring/regex search and pull in unrelated content
up to the real closing tag.

Usage:
    python extract-next-task.py <path-to-Piano.md>
"""

import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

NEXT_TASK_RE = re.compile(
    r"^[ \t]*<next_task>[ \t]*$\r?\n"
    r"(?P<body>.*?)"
    r"^[ \t]*</next_task>[ \t]*$",
    re.DOTALL | re.MULTILINE,
)


def extract_next_task(text: str) -> str:
    match = NEXT_TASK_RE.search(text)
    if not match:
        return "# No <next_task> tags found in plan."
    return match.group("body").strip("\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract-next-task.py <Piano.md>", file=sys.stderr)
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

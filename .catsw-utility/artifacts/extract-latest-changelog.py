#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""
Extract only the latest version section from a Keep a Changelog file.
Usage:
    python extract_latest_changelog.py <path-to-Changelog.md>
    python extract_latest_changelog.py <path-to-Changelog.md> --max-lines 80
"""

import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

def extract_latest_section(text: str, max_lines: int | None = None) -> str:
    lines = text.splitlines()
    
    # Find the first version header: ## [x.y.z] or ## [x.y.z] - date ...
    version_pattern = re.compile(r'^##\s+\[.+\]')
    
    start_idx = None
    for i, line in enumerate(lines):
        if version_pattern.match(line.strip()):
            start_idx = i
            break
    
    if start_idx is None:
        return "No version section found in Changelog."
    
    # Find the next version header (or end of file)
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if version_pattern.match(lines[i].strip()):
            end_idx = i
            break
    
    section_lines = lines[start_idx:end_idx]
    
    # Remove trailing empty lines
    while section_lines and not section_lines[-1].strip():
        section_lines.pop()
    
    if max_lines is not None and len(section_lines) > max_lines:
        section_lines = section_lines[:max_lines]
        section_lines.append("... (truncated)")
    
    return "\n".join(section_lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_latest_changelog.py <Changelog.md> [--max-lines N]", file=sys.stderr)
        sys.exit(1)
    
    path = Path(sys.argv[1])
    max_lines = None
    
    if "--max-lines" in sys.argv:
        idx = sys.argv.index("--max-lines")
        if idx + 1 < len(sys.argv):
            max_lines = int(sys.argv[idx + 1])
    
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)
    
    text = path.read_text(encoding="utf-8")
    result = extract_latest_section(text, max_lines)
    print(result)


if __name__ == "__main__":
    main()

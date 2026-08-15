#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.1
# T5: fallback a 3 livelli (Unreleased con contenuto / Unreleased vuota+release precedente / changelog vuoto)
"""
Extract the most relevant version section from a Keep a Changelog file.

Resolution (3-level fallback):
    1. [Unreleased] section, if it has content beyond the header.
    2. If [Unreleased] is empty (or absent), the first dated release section.
    3. If neither has content, an explicit "changelog is empty" message.

Usage:
    python extract-latest-changelog.py <path-to-Changelog.md>
    python extract-latest-changelog.py <path-to-Changelog.md> --max-lines 80
"""

import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

VERSION_HEADER_RE = re.compile(r'^##\s+\[(?P<label>[^\]]+)\]')


def _split_sections(lines: list[str]) -> list[tuple[str, int, int]]:
    """Return list of (label, start_idx, end_idx) for every '## [...]' section."""
    headers = [
        (m.group("label"), i)
        for i, line in enumerate(lines)
        if (m := VERSION_HEADER_RE.match(line.strip()))
    ]
    sections = []
    for idx, (label, start) in enumerate(headers):
        end = headers[idx + 1][1] if idx + 1 < len(headers) else len(lines)
        sections.append((label, start, end))
    return sections


def _section_text(lines: list[str], start: int, end: int) -> list[str]:
    section_lines = lines[start:end]
    while section_lines and not section_lines[-1].strip():
        section_lines.pop()
    return section_lines


def _has_content(section_lines: list[str]) -> bool:
    # section_lines[0] is the '## [...]' header itself; anything non-blank after it counts.
    return any(line.strip() for line in section_lines[1:])


def extract_latest_section(text: str, max_lines: int | None = None) -> str:
    lines = text.splitlines()
    sections = _split_sections(lines)

    if not sections:
        return "Changelog is empty (no version section found)."

    unreleased = next(
        (s for s in sections if s[0].strip().lower() == "unreleased"), None
    )

    if unreleased is not None:
        unreleased_lines = _section_text(lines, unreleased[1], unreleased[2])
        if _has_content(unreleased_lines):
            result_lines = unreleased_lines
        else:
            # Level 2: first non-Unreleased section, if any.
            fallback = next(
                (s for s in sections if s is not unreleased), None
            )
            if fallback is None:
                return "Changelog is empty ([Unreleased] has no content and no prior release exists)."
            result_lines = _section_text(lines, fallback[1], fallback[2])
            if not _has_content(result_lines):
                return "Changelog is empty ([Unreleased] and the latest release both have no content)."
    else:
        # No [Unreleased] section at all: take the first section as-is.
        first = sections[0]
        result_lines = _section_text(lines, first[1], first[2])
        if not _has_content(result_lines):
            return "Changelog is empty (latest release section has no content)."

    if max_lines is not None and len(result_lines) > max_lines:
        result_lines = result_lines[:max_lines]
        result_lines.append("... (truncated)")

    return "\n".join(result_lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract-latest-changelog.py <Changelog.md> [--max-lines N]", file=sys.stderr)
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

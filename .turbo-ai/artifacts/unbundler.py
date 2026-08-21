#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Version 1.1
from __future__ import annotations

import argparse
import base64
import hashlib
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def die(msg: str, code: int = 1) -> None:
    print(f"[ERRORE] {msg}", file=sys.stderr)
    sys.exit(code)


def warn(msg: str) -> None:
    print(f"[WARNING] {msg}", file=sys.stderr)


def is_whole_file_base64(raw: bytes) -> bool:
    """True only if the entire content (stripped) is valid base64 of reasonable length."""
    text = raw.decode("ascii", errors="ignore").strip()
    if len(text) < 64:
        return False
    # base64 alphabet + padding
    if not re.fullmatch(r"[A-Za-z0-9+/=\s]+", text):
        return False
    try:
        # validate
        base64.b64decode(text, validate=True)
        return True
    except Exception:
        return False


def decode_if_base64(raw: bytes) -> Tuple[str, bool]:
    """Return (utf8_text, was_base64)."""
    if is_whole_file_base64(raw):
        text = raw.decode("ascii", errors="ignore").strip()
        try:
            decoded = base64.b64decode(text, validate=True)
            return decoded.decode("utf-8"), True
        except Exception as e:
            die(f"File sembra base64 ma decodifica fallita: {e}")
    try:
        return raw.decode("utf-8"), False
    except UnicodeDecodeError as e:
        die(f"File non è UTF-8 valido e non è base64: {e}")


# --- Parsers -----------------------------------------------------------------

FILE_V3_START = re.compile(
    r'^<<<FILE\s+path="([^"]+)"(?:\s+bytes="(\d+)")?(?:\s+sha256="([0-9a-fA-F]+)")?\s*>>>\s*$'
)
FILE_V3_END = re.compile(r"^<<<END FILE>>>\s*$")

# Legacy headers
LEGACY_HEADER = re.compile(
    r"^(?:#{1,6}\s*File:\s*|={3,}\s*FILE:\s*|-{3,}\s*FILE:\s*)(.+?)(?:\s*(?:={3,}|-{3,})\s*)?$"
)


def parse_v3(lines: List[str]) -> List[Tuple[str, List[str], Optional[int], Optional[str]]]:
    """Return list of (path, content_lines, expected_bytes, expected_sha256)."""
    results = []
    i = 0
    n = len(lines)
    while i < n:
        m = FILE_V3_START.match(lines[i])
        if not m:
            i += 1
            continue
        path = m.group(1).strip()
        exp_bytes = int(m.group(2)) if m.group(2) else None
        exp_sha = m.group(3).lower() if m.group(3) else None
        i += 1
        content: List[str] = []
        while i < n and not FILE_V3_END.match(lines[i]):
            content.append(lines[i])
            i += 1
        if i >= n:
            warn(f"FILE '{path}' senza <<<END FILE>>> – contenuto preso fino a EOF")
        else:
            i += 1  # skip END
        results.append((path, content, exp_bytes, exp_sha))
    return results


def parse_legacy(lines: List[str]) -> List[Tuple[str, List[str], Optional[int], Optional[str]]]:
    results = []
    current_path: Optional[str] = None
    current_content: List[str] = []
    skip_next_fence = False

    def flush():
        nonlocal current_path, current_content
        if current_path is None:
            return
        # strip trailing blank lines and closing fences
        while current_content and (
            not current_content[-1].strip()
            or re.match(r"^\s*```[a-zA-Z0-9_+-]*\s*$", current_content[-1])
        ):
            current_content.pop()
        results.append((current_path, current_content[:], None, None))
        current_path = None
        current_content = []

    for line in lines:
        m = LEGACY_HEADER.match(line)
        if m:
            flush()
            current_path = m.group(1).strip()
            skip_next_fence = True
            continue
        if current_path is None:
            continue
        if skip_next_fence and re.match(r"^\s*```", line):
            skip_next_fence = False
            continue
        skip_next_fence = False
        current_content.append(line)
    flush()
    return results


def parse_bundle(text: str) -> List[Tuple[str, List[str], Optional[int], Optional[str]]]:
    lines = text.splitlines()
    # Prefer v3 if any marker present
    if any(FILE_V3_START.match(l) for l in lines):
        return parse_v3(lines)
    return parse_legacy(lines)


def safe_rel_path(rel: str) -> str:
    p = rel.replace("\\", "/").strip()
    if p.startswith("/") or re.search(r"(^|/)\.\.(/|$)", p):
        die(f"Path non sicuro (traversal o assoluto): {rel}")
    if not p:
        die("Path vuoto")
    return p


def write_file(base: Path, rel: str, content_lines: List[str],
               exp_bytes: Optional[int], exp_sha: Optional[str]) -> None:
    rel = safe_rel_path(rel)
    target = base / Path(rel)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Join with \n (LF). Final newline policy: preserve as in source (splitlines drops
    # the last empty if file ended with \n, so we do not force an extra one).
    body = "\n".join(content_lines)
    data = body.encode("utf-8")

    if exp_bytes is not None and len(data) != exp_bytes:
        warn(f"{rel}: bytes dichiarati={exp_bytes}, reali={len(data)}")
    if exp_sha is not None:
        actual = hashlib.sha256(data).hexdigest()
        if actual != exp_sha:
            warn(f"{rel}: sha256 non corrisponde (dichiarato={exp_sha}, reale={actual})")

    target.write_bytes(data)
    print(f"  Estratto: {rel}")


def find_context_file(search_root: Path, explicit: Optional[str]) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            die(f"File di contesto non trovato: {explicit}")
        return p.resolve()

    candidates = sorted(search_root.glob("context-out-*.md"))
    if not candidates:
        die(f"Nessun file context-out-*.md trovato in: {search_root}")
    if len(candidates) > 1:
        names = ", ".join(c.name for c in candidates)
        die(f"Trovati più file di contesto ({names}). Specifica --file oppure lascia un solo file.")
    return candidates[0]


def extract(context_file: Path, output_dir: Path) -> int:
    raw = context_file.read_bytes()
    text, was_b64 = decode_if_base64(raw)
    if was_b64:
        print(f"[INFO] Rilevato base64 intero → decodificato in UTF-8")

    entries = parse_bundle(text)
    if not entries:
        die("Nessun file trovato nel bundle. Verifica formato (v3 <<<FILE>>> o legacy ## File:).")

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Destinazione estrazione: {output_dir}")
    for path, lines, exp_b, exp_s in entries:
        write_file(output_dir, path, lines, exp_b, exp_s)
    print(f"Completato. Estratti {len(entries)} file.")
    return len(entries)


def main() -> None:
    # Script lives in .turbo-ai/artifacts/ → utility root is parent
    script_dir = Path(__file__).resolve().parent
    utility_root = script_dir.parent

    ap = argparse.ArgumentParser(description="UnBundler – estrae context-out (v3 / legacy / base64)")
    ap.add_argument("--file", "-f", help="Percorso esplicito del context-out-*.md")
    ap.add_argument("--output", "-o", help="Directory di estrazione (default: <utility>/output/_extracted)")
    args = ap.parse_args()

    ctx = find_context_file(utility_root, args.file)
    print(f"Elaborazione: {ctx}")

    out = Path(args.output) if args.output else (utility_root / "output" / "_extracted")
    extract(ctx, out)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Version 1.1

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

# Re-use unbundler helpers (same package dir)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from unbundler import (  # noqa: E402
    die,
    extract,
    find_context_file,
    warn,
)


def description_from_context_name(name: str) -> str:
    """context-out-foo-bar.md → foo-bar ; fallback 'bundle'."""
    m = re.match(r"^context-out-(.+)\.md$", name, re.IGNORECASE)
    if m:
        desc = m.group(1).strip()
        if desc:
            return desc
    return "bundle"


def make_zip_from_tree(src_root: Path, zip_path: Path) -> int:
    """Zip contents of src_root (not the root folder itself). Returns file count."""
    if zip_path.exists():
        zip_path.unlink()
    count = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(src_root.rglob("*")):
            if f.is_file():
                arcname = f.relative_to(src_root).as_posix()
                zf.write(f, arcname)
                count += 1
                print(f"  ZIP + {arcname}")
    return count


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    utility_root = script_dir.parent  # .turbo-ai
    output_dir = utility_root / "output"
    staging = output_dir / "_extracted"

    ap = argparse.ArgumentParser(
        description="GeneraZip – unbundle context-out e produce FromLlm-<desc>.zip"
    )
    ap.add_argument("--file", "-f", help="Percorso esplicito del context-out-*.md")
    ap.add_argument(
        "--keep-extracted",
        action="store_true",
        help="Non cancellare la cartella di estrazione dopo lo ZIP",
    )
    args = ap.parse_args()

    ctx = find_context_file(utility_root, args.file)
    desc = description_from_context_name(ctx.name)
    zip_name = f"FromLlm-{desc}.zip"
    zip_path = output_dir / zip_name

    print(f"Context : {ctx.name}")
    print(f"ZIP     : {zip_path}")

    # Clean previous staging
    if staging.exists():
        shutil.rmtree(staging)

    n = extract(ctx, staging)
    if n == 0:
        die("Nessun file estratto – ZIP non creato")

    output_dir.mkdir(parents=True, exist_ok=True)
    count = make_zip_from_tree(staging, zip_path)
    print(f"Creato {zip_path.name} ({count} file)")

    if not args.keep_extracted:
        shutil.rmtree(staging)
        print("Staging di estrazione rimosso.")
    else:
        print(f"Staging lasciato in: {staging}")

    print("Fatto.")


if __name__ == "__main__":
    main()


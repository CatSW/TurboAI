#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""
Scenario 07 - Triage errore da ToLlm.txt e patch correttiva.
Uso:
    python run_test.py setup
    python run_test.py verify --llm <nome> --zip <path-zip-consegnato>
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_common"))
import validators  # noqa: E402

SCENARIO = "07-tolm-error-triage-patch"
EXPECTED_TARGET = "divider.py"


def cmd_setup() -> None:
    print(f"[{SCENARIO}] Allega skill + golden/fixture-task.md + golden/ToLlm.txt + golden/src/divider.py.")
    print("Scarica lo ZIP consegnato nella cartella dello scenario, poi:")
    print("  python run_test.py verify --llm <nome> --zip <path-zip>")


def cmd_verify(llm_name: str, zip_path: Path) -> None:
    ok, issues = validators.check_fromllm_zip(zip_path)
    try:
        with zipfile.ZipFile(zip_path) as zf:
            names_and_texts = []
            for info in zf.infolist():
                if info.filename.endswith((".py", ".ps1")):
                    try:
                        names_and_texts.append((info.filename, zf.read(info).decode("utf-8", errors="ignore")))
                    except Exception:
                        pass
            mentions_target = any(EXPECTED_TARGET in name or EXPECTED_TARGET in txt for name, txt in names_and_texts)
            if not mentions_target:
                ok = False
                issues.append(f"Nessun riferimento a {EXPECTED_TARGET} (file realmente indicato dal traceback) nello ZIP.")
    except zipfile.BadZipFile:
        pass  # gia' segnalato da check_fromllm_zip
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    report_path = HERE.parent / "reports" / f"report-{SCENARIO}-{llm_name}-{timestamp}.md"
    report_path.parent.mkdir(exist_ok=True)
    validators.write_report(
        report_path, SCENARIO, llm_name, ok, issues,
        notes="Verifica strutturale + euristica (il file giusto e' toccato). "
              "La correttezza del fix (ZeroDivisionError davvero risolto) resta giudizio umano.",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("setup")
    verify_p = sub.add_parser("verify")
    verify_p.add_argument("--llm", required=True)
    verify_p.add_argument("--zip", required=True, type=Path)
    args = parser.parse_args()

    if args.mode == "setup":
        cmd_setup()
    else:
        cmd_verify(args.llm, args.zip)
    return 0


if __name__ == "__main__":
    sys.exit(main())

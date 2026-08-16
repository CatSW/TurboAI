#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""
Scenario 04 - Gap nel context-out, follow-up mirato.
Uso:
    python run_test.py setup
    python run_test.py verify --llm <nome> --output <path-file-txt-o-md>
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_common"))
import validators  # noqa: E402

SCENARIO = "04-context-out-gap-followup"
EXPECTED_MISSING = "src/discount_rules.py"
ALREADY_PROVIDED = "src/order_service.py"


def cmd_setup() -> None:
    print(f"[{SCENARIO}] Allega skill + golden/fixture-task.md + golden/context-out-round1.md.")
    print("Salva la nuova context-request come output-<llm>.md, poi:")
    print("  python run_test.py verify --llm <nome> --output <path>")


def cmd_verify(llm_name: str, output_path: Path) -> None:
    text = output_path.read_text(encoding="utf-8")
    ok, issues = validators.check_context_request(text, expected_paths={EXPECTED_MISSING})
    if EXPECTED_MISSING not in text:
        ok = False
        issues.append(f"Non ha richiesto il file mancante reale: {EXPECTED_MISSING}")
    if ALREADY_PROVIDED in text:
        ok = False
        issues.append(f"Ha ri-richiesto un file gia' fornito nel bundle: {ALREADY_PROVIDED}")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    report_path = HERE.parent / "reports" / f"report-{SCENARIO}-{llm_name}-{timestamp}.md"
    report_path.parent.mkdir(exist_ok=True)
    validators.write_report(report_path, SCENARIO, llm_name, ok, issues)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("setup")
    verify_p = sub.add_parser("verify")
    verify_p.add_argument("--llm", required=True)
    verify_p.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.mode == "setup":
        cmd_setup()
    else:
        cmd_verify(args.llm, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())

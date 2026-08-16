#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""
Scenario 02 - Discovery mirata poi context-request.
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

SCENARIO = "02-discovery-then-request"
EXPECTED_PATHS = {"src/calc.py", "src/utils.py", "src/config.json"}


def cmd_setup() -> None:
    print(f"[{SCENARIO}] Vedi scenario.md per la procedura a 2 turni.")
    print("Turno 1: allega SOLO golden/fixture-task.md (+ skill). NON allegare golden/ls.txt.")
    print("Verifica manualmente che l'LLM chieda una discovery, non che indovini path.")
    print("Turno 2: allega golden/ls.txt, salva la context-request finale come output-<llm>.md.")
    print("Poi: python run_test.py verify --llm <nome> --output <path>")


def cmd_verify(llm_name: str, output_path: Path) -> None:
    text = output_path.read_text(encoding="utf-8")
    ok, issues = validators.check_context_request(text, expected_paths=EXPECTED_PATHS)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    report_path = HERE.parent / "reports" / f"report-{SCENARIO}-{llm_name}-{timestamp}.md"
    report_path.parent.mkdir(exist_ok=True)
    validators.write_report(
        report_path, SCENARIO, llm_name, ok, issues,
        notes="Controllo automatico solo sul secondo turno (context-request finale). "
              "Il primo turno (ha chiesto discovery invece di indovinare?) resta giudizio umano.",
    )


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

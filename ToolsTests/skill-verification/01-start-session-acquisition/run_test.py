#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""
Scenario 01 - Acquisizione start-session.
Uso:
    python run_test.py setup
    python run_test.py verify --llm <nome>
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

SCENARIO = "01-start-session-acquisition"

CHECKLIST = [
    "L'LLM ha identificato correttamente il task corrente (T1.1) senza chiederlo di nuovo?",
    "L'LLM NON ha richiesto file gia' presenti nel bundle (governance/next_task/git)?",
    "L'LLM NON ha inventato file o percorsi assenti dal bundle?",
    "L'LLM ha proposto un prossimo passo operativo concreto (non generico)?",
]


def cmd_setup() -> None:
    print(f"[{SCENARIO}] Materiale in golden/: SOLUTION_GOVERNANCE.md, info_next_task.md, info_git.txt")
    print("Allega questi 3 file + la tua skill Canale B in una chat LLM pulita, poi scrivi:")
    print('  "Questo e\' il bundle di avvio sessione per DemoWidget. Procedi come da protocollo di sessione."')
    print("Quando l'LLM risponde, esegui: python run_test.py verify --llm <nome>")


def cmd_verify(llm_name: str) -> None:
    print(f"[{SCENARIO}] Checklist per {llm_name} (rispondi s/n leggendo la risposta dell'LLM):")
    issues: list[str] = []
    for question in CHECKLIST:
        ans = input(f"  - {question} [s/n] ").strip().lower()
        if ans != "s":
            issues.append(question)
    ok = not issues
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    report_path = HERE.parent / "reports" / f"report-{SCENARIO}-{llm_name}-{timestamp}.md"
    report_path.parent.mkdir(exist_ok=True)
    validators.write_report(report_path, SCENARIO, llm_name, ok, issues,
                             notes="Checklist a giudizio umano (comprensione semantica, non automatizzabile).")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("setup")
    verify_p = sub.add_parser("verify")
    verify_p.add_argument("--llm", required=True)
    args = parser.parse_args()

    if args.mode == "setup":
        cmd_setup()
    else:
        cmd_verify(args.llm)
    return 0


if __name__ == "__main__":
    sys.exit(main())

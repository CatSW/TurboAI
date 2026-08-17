#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.2
"""
Scenario 01 - Acquisizione start-session.
Uso:
    python run_test.py setup
    python run_test.py verify --llm <nome>
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_common"))
import validators  # noqa: E402
import versioning  # noqa: E402

SCENARIO = "01-start-session-acquisition"
SCENARIO_VERSION = "1.2"

CHECKLIST = [
    "L'LLM ha identificato correttamente il task corrente (T1.1) senza chiederlo di nuovo?",
    "L'LLM NON ha richiesto file gia' presenti nel bundle (governance/next_task/git)?",
    "L'LLM NON ha inventato file o percorsi assenti dal bundle?",
    "L'LLM ha proposto come prossimo passo concreto la richiesta dei file dichiarati"
    " in Target Paths, generando una context-request scaricabile?",
    "Dopo aver ricevuto il context-out reale, l'LLM ha usato correttamente il contenuto"
    " ricevuto (nessuna invenzione, nessuna richiesta di file gia' presenti nel context-out)?",
]


def cmd_setup() -> None:
    skill_src = HERE.parent / ".catsw-utility" / "docs" / "skill-uso-tools.md"
    skill_dst = HERE / "golden" / "skill-uso-tools.md"
    if skill_src.is_file():
        shutil.copy2(skill_src, skill_dst)
        print(f"Copiata skill Canale B corrente in {skill_dst}")
    else:
        print(f"ATTENZIONE: skill non trovata in {skill_src}, allega manualmente la tua skill Canale B.")

    print(f"[{SCENARIO}] Allega questi 4 file dalla cartella golden/ in una chat LLM pulita:")
    print("  SOLUTION_GOVERNANCE.md, info_next_task.md, info_git.txt, skill-uso-tools.md")
    print("poi scrivi:")
    print('  "Questo e\' il bundle di avvio sessione per DemoWidget. Procedi come da protocollo di sessione."')
    print()
    print("L'LLM deve proporre come prossimo passo la richiesta dei file dichiarati in")
    print("Target Paths, producendo una context-request-*.md scaricabile. Salvala ed")
    print("eseguila con ContextBundler.exe da .catsw-utility per ottenere il context-out")
    print("reale, poi incolla/allega il context-out nella stessa chat per far proseguire")
    print("l'LLM con la risposta finale.")
    print()
    print("Quando hai finito il giro, esegui: python run_test.py verify --llm <nome>")
    print("(context-request/context-out piu' recenti in .catsw-utility verranno trovati")
    print(" e copiati automaticamente nel report.)")


def _find_latest(pattern: str, folder: Path) -> Path | None:
    matches = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def cmd_verify(llm_name: str) -> None:
    catsw_utility = HERE.parent / ".catsw-utility"
    context_request_path = _find_latest("context-request-*.md", catsw_utility)
    context_out_path = _find_latest("context-out-*.md", catsw_utility)
    if context_request_path is None or context_out_path is None:
        print(f"ERRORE: non trovo context-request-*.md / context-out-*.md in {catsw_utility}.")
        print("Completa prima il giro reale con ContextBundler.exe (vedi 'run_test.py setup').")
        sys.exit(1)

    cr_text = context_request_path.read_text(encoding="utf-8")
    cr_ok, cr_issues = validators.check_context_request(cr_text)

    print(f"[{SCENARIO}] Trovati in {catsw_utility}:")
    print(f"  - {context_request_path.name}")
    print(f"  - {context_out_path.name}")
    print(f"[{SCENARIO}] Controllo automatico formato context-request: "
          f"{'OK' if cr_ok else 'PROBLEMI'}")
    for issue in cr_issues:
        print(f"  - {issue}")

    print(f"\n[{SCENARIO}] Checklist per {llm_name} (rispondi s/n leggendo la risposta dell'LLM):")
    issues: list[str] = [f"context-request: {i}" for i in cr_issues]
    for question in CHECKLIST:
        ans = input(f"  - {question} [s/n] ").strip().lower()
        if ans != "s":
            issues.append(question)
    ok = not issues

    turbo_version = versioning.get_turbo_version(HERE.parent)
    skill_version = versioning.get_skill_version(HERE / "golden" / "skill-uso-tools.md")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    report_dir = HERE.parent / "reports" / f"{timestamp}_report-{SCENARIO}-{llm_name}"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{timestamp}-report-{SCENARIO}-{llm_name}.md"

    shutil.copy2(context_request_path, report_dir / context_request_path.name)
    shutil.copy2(context_out_path, report_dir / context_out_path.name)

    validators.write_report(
        report_path, SCENARIO, llm_name, ok, issues,
        notes="Checklist a giudizio umano (comprensione semantica, non automatizzabile) "
              "+ controllo automatico di formato sulla context-request generata dall'LLM.",
        scenario_version=SCENARIO_VERSION,
        turbo_version=turbo_version,
        skill_version=skill_version,
    )
    print(f"Copiati in {report_dir}: {context_request_path.name}, {context_out_path.name}")


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

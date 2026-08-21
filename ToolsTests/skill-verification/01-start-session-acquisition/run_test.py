#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.5
"""
Scenario 01 - Acquisizione start-session.
Uso:
    python run_test.py setup
    python run_test.py verify --llm <nome>

Questo scenario verifica SOLO fino alla corretta generazione del
context-out da parte di turbo-ai: non prevede che l'LLM prosegua oltre
in quella interazione di chat (vedi cmd_setup).
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
SCENARIO_VERSION = "1.5"

CHECKLIST = [
    "L'LLM ha identificato correttamente il task corrente (T1.1) senza chiederlo di nuovo?",
    "L'LLM ha richiesto solo file non gia' presenti nel bundle (governance/next_task/git)?",
    "L'LLM ha richiesto solo file/percorsi effettivamente dichiarati nel bundle (nessuna invenzione)?",
    "L'LLM ha proposto come prossimo passo concreto la richiesta dei file dichiarati"
    " in Target Paths, generando una context-request scaricabile?",
]


def cmd_setup() -> None:
    skill_src = HERE.parent / ".turbo-ai" / "docs" / "skill-uso-tools.md"
    skill_dst = HERE / "golden" / "skill-uso-tools.md"
    if skill_src.is_file():
        shutil.copy2(skill_src, skill_dst)
        print(f"Copiata skill Canale B corrente in {skill_dst}")
    else:
        print(f"ATTENZIONE: skill non trovata in {skill_src}, allega manualmente la tua skill Canale B.")

    print()
    print(f"--- Istruzioni per lo scenario {SCENARIO} ---")
    print(f"[{SCENARIO}] Allega questi 4 file dalla cartella golden/ in una chat LLM pulita:")
    print("  SOLUTION_GOVERNANCE.md, info_next_task.md, info_git.txt, skill-uso-tools.md")
    print("poi scrivi:")
    print('  "Questo e\' il bundle di avvio sessione per DemoWidget. Procedi come da protocollo di sessione."')
    print()
    print("L'LLM deve proporre come prossimo passo la richiesta dei file dichiarati in")
    print("Target Paths, producendo una context-request-*.md scaricabile. Salvala per fare")
    print("generare da turbo-ai la context-out.")
    print()
    print("Non proseguire oltre la generazione del context-out in questa interazione con")
    print("la chat LLM: questo scenario verifica solo fino a quel punto.")
    print()
    print("Esegui: python run_test.py verify --llm <nome>")
    print("(context-request/context-out piu' recenti in .turbo-ai verranno trovati")
    print(" e copiati automaticamente nel report.)")


def _find_latest(pattern: str, folder: Path) -> Path | None:
    matches = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def cmd_verify(llm_name: str) -> None:
    catsw_utility = HERE.parent / ".turbo-ai"
    context_request_path = _find_latest("context-request-*.md", catsw_utility)
    context_out_path = _find_latest("context-out-*.md", catsw_utility)
    if context_request_path is None or context_out_path is None:
        print(f"ERRORE: non trovo context-request-*.md / context-out-*.md in {catsw_utility}.")
        print("Completa prima il giro reale con turbo-ai (vedi 'run_test.py setup').")
        sys.exit(1)

    cr_text = context_request_path.read_text(encoding="utf-8")
    cr_ok, cr_issues = validators.check_context_request(cr_text)

    context_out_text = context_out_path.read_text(encoding="utf-8")
    next_task_path = HERE / "golden" / "info_next_task.md"
    expected_paths: list[str] = []
    if next_task_path.is_file():
        expected_paths = validators.extract_target_paths(next_task_path.read_text(encoding="utf-8"))
    co_ok, co_issues = validators.check_context_out_has_paths(context_out_text, expected_paths)

    print(f"[{SCENARIO}] Trovati in {catsw_utility}:")
    print(f"  - {context_request_path.name}")
    print(f"  - {context_out_path.name}")
    print(f"[{SCENARIO}] Controllo automatico formato context-request: "
          f"{'OK' if cr_ok else 'PROBLEMI'}")
    for issue in cr_issues:
        print(f"  - {issue}")
    print(f"[{SCENARIO}] Controllo automatico contenuto context-out: "
          f"{'OK' if co_ok else 'PROBLEMI'}")
    for issue in co_issues:
        print(f"  - {issue}")

    details: list[str] = []
    details.append(f"Controllo automatico formato context-request: {'OK' if cr_ok else 'PROBLEMI'}")
    details += [f"  - {i}" for i in cr_issues]
    details.append(f"Controllo automatico contenuto context-out: {'OK' if co_ok else 'PROBLEMI'}")
    details += [f"  - {i}" for i in co_issues]

    issues: list[str] = [f"context-request: {i}" for i in cr_issues] + [f"context-out: {i}" for i in co_issues]

    if not cr_ok or not co_ok:
        print(f"\n[{SCENARIO}] Controllo automatico fallito: interrompo la checklist umana (fail-fast).")
        print("L'LLM non ha gestito correttamente la skill per questo scenario: non ha senso")
        print("proseguire con le domande a giudizio umano.")
        details.append(
            "Checklist umana interrotta (fail-fast): almeno un controllo automatico e' fallito."
        )
    else:
        print(f"\n[{SCENARIO}] Checklist per {llm_name} (rispondi s/n leggendo la risposta dell'LLM):")
        for question in CHECKLIST:
            ans = input(f"  - {question} [s/n] ").strip().lower()
            details.append(f"D: {question}")
            details.append(f"   R: {'Si' if ans == 's' else 'No'}")
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
        report_path, SCENARIO, llm_name, ok, details,
        notes="Controlli automatici: formato della context-request e presenza dei Target Paths"
              " nel context-out. La checklist umana (comprensione semantica, non automatizzabile)"
              " viene saltata (fail-fast) se un controllo automatico fallisce.",
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

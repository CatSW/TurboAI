#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.3
"""
Validatori condivisi per gli scenari di skill-verification.
Ogni funzione ritorna (ok: bool, dettagli: list[str]). Sono controlli
strutturali/euristici: verificano il FORMATO, non la correttezza semantica
del lavoro dell'LLM (quella resta giudizio umano, vedi scenario.md).
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

WILDCARD_CHARS = ("*", "?")
NL_MARKERS = (
    "includ", "cerca", "trova", "assicurati", "per ogni", "tutti i file",
    "search", "include", "ensure", "for every", "ricerca mirata",
)


def check_context_request(text: str, expected_paths: set[str] | None = None) -> tuple[bool, list[str]]:
    """
    Verifica una context-request: solo path relativi, uno per riga, nessuna
    wildcard, nessuna istruzione in linguaggio naturale. Se expected_paths
    e' dato, segnala path non presenti nella fixture (inventati).
    """
    issues: list[str] = []
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
    request_paths: list[str] = []
    for line in lines:
        low = line.lower()
        if any(c in line for c in WILDCARD_CHARS):
            issues.append(f"Wildcard non supportata nella riga: {line!r}")
            continue
        if any(m in low for m in NL_MARKERS) or len(line.split()) > 8:
            issues.append(f"Sembra prosa/istruzione in linguaggio naturale, non un path: {line!r}")
            continue
        request_paths.append(line.lstrip("-*• ").strip("`"))
    if not request_paths:
        issues.append("Nessun path riconosciuto come richiesta file nel testo fornito.")
    if expected_paths is not None:
        unknown = sorted(p for p in request_paths if p not in expected_paths)
        if unknown:
            issues.append(f"Path richiesti non presenti nella fixture (inventati?): {unknown}")
    return (len(issues) == 0), issues


def extract_target_paths(next_task_text: str) -> list[str]:
    """
    Estrae l'elenco dei path dichiarati in una sezione 'Target Paths' di una
    fixture next_task (righe puntate dopo una riga/titolo che contiene
    'Target Paths'). Ritorna [] se la sezione non e' presente: in tal caso
    il chiamante deve trattare il controllo automatico associato come non
    applicabile, non come fallito.
    """
    lines = next_task_text.splitlines()
    paths: list[str] = []
    collecting = False
    for line in lines:
        if "target paths" in line.lower():
            collecting = True
            continue
        if not collecting:
            continue
        stripped = line.strip()
        if not stripped:
            if paths:
                break
            continue
        if stripped.startswith("#"):
            break
        if stripped.startswith(("-", "*")):
            paths.append(stripped.lstrip("-*").strip().strip("`"))
    return paths


def check_context_out_has_paths(context_out_text: str, expected_paths: list[str]) -> tuple[bool, list[str]]:
    """
    Verifica che il context-out contenga un blocco <<<FILE path="..."...>>>
    per ciascuno dei path attesi (tipicamente i Target Paths dichiarati
    nella fixture next_task). Controllo strutturale: non valuta il
    contenuto del file, solo la sua presenza come blocco.
    Se expected_paths e' vuoto il controllo e' considerato non applicabile
    (ok=True, nessun problema) per non generare falsi negativi quando la
    fixture non dichiara Target Paths analizzabili.
    """
    if not expected_paths:
        return True, []
    present = set(re.findall(r'<<<FILE path="([^"]+)"', context_out_text))
    present_normalized = {p.lstrip("./").replace("\\", "/") for p in present}
    issues: list[str] = []
    for expected in expected_paths:
        norm = expected.lstrip("./").replace("\\", "/")
        if norm not in present_normalized:
            issues.append(f"Path atteso assente dal context-out: {expected}")
    return (len(issues) == 0), issues


def check_fromllm_zip(zip_path: Path) -> tuple[bool, list[str]]:
    """
    Verifica il contratto FromLlm ZIP (skill-uso-tools.md §6):
    nome FromLlm-*.zip, nessuna directory contenitore, al massimo uno
    script operativo sotto .turbo-ai/temp/FromLlm-*.py|.ps1, nessun
    path assoluto/traversal, nessuna entry a dimensione zero.
    """
    issues: list[str] = []
    if not zip_path.name.startswith("FromLlm-"):
        issues.append(f"Nome file non conforme (atteso FromLlm-<descrizione>.zip): {zip_path.name}")
    if not zip_path.is_file():
        return False, [f"File non trovato: {zip_path}"]
    try:
        with zipfile.ZipFile(zip_path) as zf:
            infos = zf.infolist()
            if not infos:
                issues.append("ZIP vuoto.")
            scripts: list[str] = []
            for info in infos:
                name = info.filename.replace("\\", "/")
                first_seg = name.split("/")[0]
                if name.startswith("/") or ":" in first_seg or ".." in name.split("/"):
                    issues.append(f"Path assoluto o traversal sospetto: {name}")
                if info.file_size == 0 and not name.endswith("/"):
                    issues.append(f"File a dimensione zero: {name}")
                if re.match(r"^\.turbo-ai/temp/FromLlm-.*\.(py|ps1)$", name):
                    scripts.append(name)
                elif name.endswith((".py", ".ps1")) and "temp/" in name:
                    issues.append(f"Script fuori dalla posizione attesa .turbo-ai/temp/: {name}")
            if len(scripts) > 1:
                issues.append(f"Piu' di uno script operativo nello ZIP: {scripts}")
    except zipfile.BadZipFile:
        issues.append("Il file non e' uno ZIP valido.")
    return (len(issues) == 0), issues


def check_script_conventions(text: str) -> tuple[bool, list[str]]:
    """
    Verifica euristica delle convenzioni per script Python generati
    (skill-uso-tools.md §5): deriva i path dalla propria posizione,
    configura stdout/stderr UTF-8, non hardcoda path utente/repo assoluti.
    """
    issues: list[str] = []
    if "__file__" not in text:
        issues.append("Non deriva i path dalla propria posizione (__file__ non trovato).")
    if not re.search(r"reconfigure\(encoding=.utf-8.", text, re.IGNORECASE) and "PYTHONUTF8" not in text:
        issues.append("Nessuna configurazione esplicita UTF-8 per stdout/stderr trovata.")
    hardcoded = re.findall(r"[A-Za-z]:\\Users\\[^\"'\s]+", text)
    if hardcoded:
        issues.append(f"Possibile path utente hardcoded: {hardcoded}")
    return (len(issues) == 0), issues


def write_report(
    report_path: Path,
    scenario: str,
    llm_name: str,
    ok: bool,
    details: list[str],
    notes: str = "",
    scenario_version: str = "",
    turbo_version: str = "",
    skill_version: str = "",
) -> None:
    """
    details: elenco di righe gia' formattate da mostrare in '## Dettagli'.
    A differenza della versione precedente non contiene solo gli item
    falliti: e' il resoconto completo (controlli automatici + coppie
    domanda/risposta della checklist umana), cosi' il report resta
    leggibile anche quando l'esito e' PASS o quando la checklist umana e'
    stata interrotta per fail-fast.
    """
    lines = [
        f"# Report - {scenario}",
        f"- LLM: {llm_name}",
    ]
    if scenario_version:
        lines.append(f"- Versione scenario di test: {scenario_version}")
    if turbo_version:
        lines.append(f"- Versione TurboAI: {turbo_version}")
    if skill_version:
        lines.append(f"- Versione skill Canale B: {skill_version}")
    lines.append(f"- Esito controlli automatici: {'PASS' if ok else 'FAIL'}")
    lines.append("")
    lines.append("## Dettagli")
    lines += [f"- {d}" for d in details] if details else ["- Nessun dettaglio registrato."]
    if notes:
        lines += ["", "## Note", notes]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Report scritto: {report_path}")

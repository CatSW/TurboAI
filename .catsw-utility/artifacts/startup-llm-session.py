#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.4
# T5: risoluzione dinamica del changelog path (OverrideChangeLogPath del task > DefaultChangeLogPath
#     di governance > fail fast se nessuno dei due è configurato). Step next-task spostato prima
#     dello step changelog perché quest'ultimo dipende dal suo output.
# lightweight start-session for new AI Context model

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def configure_utf8_stdio() -> None:
    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")


def utf8_child_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _parse_boolish(raw: str) -> bool | None:
    """Return True/False for known values, None if invalid/empty."""
    if raw is None:
        return None
    val = raw.strip().lower()
    if not val:
        return None
    if val in ("true", "1", "yes"):
        return True
    if val in ("false", "0", "no"):
        return False
    return None


def _read_governance_key(solution_root: Path, key_name: str) -> str | None:
    """
    Parse a simple `key: value` / `key=value` line from .ai-context/SOLUTION_GOVERNANCE.md.
    Returns the raw string value if found, None if missing/file absent.
    Tolerant of markdown list markers, backticks, extra whitespace and case on the key name.
    """
    gov_path = solution_root / ".ai-context" / "SOLUTION_GOVERNANCE.md"
    if not gov_path.is_file():
        return None
    try:
        text = gov_path.read_text(encoding="utf-8")
    except OSError:
        return None

    key_re = re.compile(
        rf"{re.escape(key_name)}\s*[:=]\s*[`'\"]?([^\s`'\"]+)[`'\"]?",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        m = key_re.search(line)
        if m:
            return m.group(1)
    return None


def _read_governance_base64(solution_root: Path) -> bool | None:
    raw = _read_governance_key(solution_root, "ContextBundler_output_base64")
    return _parse_boolish(raw) if raw is not None else None


def resolve_base64_mode(solution_root: Path | None = None) -> tuple[bool, str]:
    """
    Effective base64 mode for ContextBundler.
    Precedence: env TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64
                > Governance ContextBundler_output_base64
                > default false.
    Accepts true/false/1/0/yes/no (case-insensitive, surrounding whitespace).
    Invalid values are ignored and fall through to the next level.
    """
    # 1. Environment variable (highest priority)
    env_val = os.environ.get("TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64")
    parsed = _parse_boolish(env_val) if env_val is not None else None
    if parsed is not None:
        return parsed, "env"

    # 2. Governance file
    if solution_root is None:
        artefacts = Path(__file__).resolve().parent
        solution_root = artefacts.parent.parent
    gov_val = _read_governance_base64(solution_root)
    if gov_val is not None:
        return gov_val, "governance"

    # 3. Default
    return False, "default"


def _extract_override_changelog_path(next_task_text: str) -> str | None:
    """Look for 'OverrideChangeLogPath=<path>' (or ':') anywhere in the next-task block text."""
    m = re.search(
        r"OverrideChangeLogPath\s*[:=]\s*[`'\"]?([^\s`'\"]+)[`'\"]?",
        next_task_text,
        re.IGNORECASE,
    )
    return m.group(1) if m else None


def resolve_changelog_path(
    solution_root: Path, next_task_text: str
) -> tuple[Path | None, str]:
    """
    Effective changelog path, relative to solution_root.
    Precedence: OverrideChangeLogPath (declared in the active task)
                > DefaultChangeLogPath (governance)
                > (None, "unset") — caller must fail fast on this.
    """
    override = _extract_override_changelog_path(next_task_text)
    if override:
        return solution_root / override, "task override"

    default = _read_governance_key(solution_root, "DefaultChangeLogPath")
    if default:
        return solution_root / default, "governance default"

    return None, "unset"


configure_utf8_stdio()

TO_LLM_PATH = Path.home() / "Downloads" / "ToLlm.txt"


def log(msg: str) -> None:
    """Print to console and append to Downloads/ToLlm.txt for TailWatcher."""
    print(msg)
    with TO_LLM_PATH.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def run(cmd: list[str], cwd: Path | None = None) -> str:
    """Run a command and return stdout (raises on error)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n{result.stderr}"
        )
    return result.stdout


def find_script(script_name: str, artefacts_root: Path) -> Path | None:
    """Cerca lo script nella cartella degli artifacts, nella CWD o accanto allo script di startup."""
    candidates = [
        artefacts_root / script_name,
        Path.cwd() / script_name,
        Path.cwd() / "artifacts" / script_name,
        Path(__file__).resolve().parent / script_name,
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def main() -> int:
    # Reset ToLlm.txt for this run
    TO_LLM_PATH.write_text("", encoding="utf-8")
    log("Executing startup-llm-session v1.4...")

    # --- Path resolution ------------------------------------------------
    artefacts_root = Path(__file__).resolve().parent
    utility_root = artefacts_root.parent
    repo_root = utility_root.parent

    solution_name = repo_root.name
    ai_context_dir = repo_root / ".ai-context"
    ai_context_dir.mkdir(exist_ok=True)

    # --- 1. Move previous context* files to history ---------------------
    sposta_script = find_script("MoveToHistory.py", artefacts_root)
    if sposta_script and sposta_script.exists():
        subprocess.run(
            [sys.executable, str(sposta_script)],
            check=False,
            env=utf8_child_env(),
        )

    # --- 2. Git info → .ai-context/info_git.txt -------------------------
    try:
        git_log = run(["git", "log", "--oneline", "-5"], cwd=repo_root)
        git_status = run(["git", "status", "-sb"], cwd=repo_root)
    except RuntimeError as exc:
        log(f"ERRORE git: {exc}")
        return 1

    info_git = (
        f"# Git status – generated {datetime.now().isoformat(timespec='seconds')}\n\n"
        f"## git log --oneline -5\n{git_log.strip()}\n\n"
        f"## git status -sb\n{git_status.strip()}\n"
    )
    info_git_path = ai_context_dir / "info_git.txt"
    info_git_path.write_text(info_git, encoding="utf-8")

    child_env = utf8_child_env()

    # --- 3. Next task section → .ai-context/info_next_task.md -----------
    # Spostato prima dello step changelog: la risoluzione del changelog path
    # dipende da un eventuale OverrideChangeLogPath dichiarato nel task attivo.
    plan_src = ai_context_dir / "Piano-Multi-Task.md"
    extract_next_task_script = find_script("extract-next-task.py", artefacts_root)
    info_next_task_path = ai_context_dir / "info_next_task.md"

    next_task_text = ""
    if not plan_src.exists():
        log(f"ATTENZIONE: Piano non trovato: {plan_src}")
        info_next_task_path.write_text("# Plan not found\n", encoding="utf-8")
    elif not extract_next_task_script or not extract_next_task_script.exists():
        log("ATTENZIONE: extract-next-task.py non trovato")
        info_next_task_path.write_text("# extract tool missing\n", encoding="utf-8")
    else:
        result = subprocess.run(
            [sys.executable, str(extract_next_task_script), str(plan_src)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=child_env,
        )
        if result.returncode != 0:
            log(f"Errore extract-next-task: {result.stderr}")
            info_next_task_path.write_text("# Extraction failed\n", encoding="utf-8")
        else:
            next_task_text = result.stdout
            header = f"# Next task – generated {datetime.now().isoformat(timespec='seconds')}\n\n"
            info_next_task_path.write_text(header + next_task_text, encoding="utf-8")

    # --- 4. Latest Changelog section → .ai-context/info_Changelog.md ----
    changelog_path, changelog_source = resolve_changelog_path(repo_root, next_task_text)
    info_changelog_path = ai_context_dir / "info_Changelog.md"

    if changelog_path is None:
        log(
            "ERRORE: nessun changelog configurato — imposta DefaultChangeLogPath in "
            "SOLUTION_GOVERNANCE.md oppure OverrideChangeLogPath nel task attivo."
        )
        return 1

    log(f"Changelog path: {changelog_path} (source={changelog_source})")

    extract_changelog_script = find_script("extract-latest-changelog.py", artefacts_root)

    if not changelog_path.exists():
        log(f"ATTENZIONE: Changelog non trovato: {changelog_path}")
        info_changelog_path.write_text("# Changelog not found\n", encoding="utf-8")
    elif not extract_changelog_script or not extract_changelog_script.exists():
        log("ATTENZIONE: extract-latest-changelog.py non trovato")
        info_changelog_path.write_text("# extract tool missing\n", encoding="utf-8")
    else:
        result = subprocess.run(
            [sys.executable, str(extract_changelog_script), str(changelog_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=child_env,
        )
        if result.returncode != 0:
            log(f"Errore extract-latest-changelog: {result.stderr}")
            info_changelog_path.write_text("# Extraction failed\n", encoding="utf-8")
        else:
            header = f"# Latest Changelog section – generated {datetime.now().isoformat(timespec='seconds')}\n\n"
            info_changelog_path.write_text(header + result.stdout, encoding="utf-8")

    # --- 5. Create lightweight manifest ---------------------------------
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    manifest_name = f"context-request-start-session-{timestamp}.md"
    manifest_path = utility_root / manifest_name

    manifest_lines = [
        "# Files to bundle",
        "",
        ".ai-context/SOLUTION_GOVERNANCE.md",
        ".ai-context/info_git.txt",
        ".ai-context/info_Changelog.md",
        ".ai-context/info_next_task.md",
        ".catsw-utility/docs/skill-uso-tools.md",
    ]
    manifest_content = "\n".join(manifest_lines) + "\n"
    manifest_path.write_text(manifest_content, encoding="utf-8", newline="\n")

    # --- 6. Run ContextBundler -------------------------------------------
    bundler = find_script("ContextBundler.exe", artefacts_root)
    if not bundler or not bundler.exists():
        log(f"ERRORE: ContextBundler.exe non trovato in {artefacts_root}")
        return 1

    to_base64, source = resolve_base64_mode(repo_root)
    cmd = [str(bundler)]
    if to_base64:
        cmd.append("--base64")

    log(f"ContextBundler output mode: base64={to_base64} (source={source})")
    result = subprocess.run(
        cmd,
        cwd=utility_root,
        env=utf8_child_env(),
    )
    if result.returncode != 0:
        log(f"ContextBundler ha restituito exit code {result.returncode}")
        return result.returncode

    log("Done.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        log(f"ERRORE: {exc}")
        sys.exit(1)

#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
# lightweight start-session for new AI Context model

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

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
    log("Executing startup-llm-session...")

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

    child_env = os.environ.copy()
    child_env["PYTHONUTF8"] = "1"
    child_env["PYTHONIOENCODING"] = "utf-8"

    # --- 3. Latest Changelog section → .ai-context/info_Changelog.md ----
    changelog_src = repo_root / "ContextBundler" / "Documentation" / "Changelog.md"
    extract_changelog_script = find_script("extract-latest-changelog.py", artefacts_root)
    info_changelog_path = ai_context_dir / "info_Changelog.md"

    if not changelog_src.exists():
        log(f"ATTENZIONE: Changelog non trovato: {changelog_src}")
        info_changelog_path.write_text("# Changelog not found\n", encoding="utf-8")
    elif not extract_changelog_script or not extract_changelog_script.exists():
        log("ATTENZIONE: extract-latest-changelog.py non trovato")
        info_changelog_path.write_text("# extract tool missing\n", encoding="utf-8")
    else:
        result = subprocess.run(
            [sys.executable, str(extract_changelog_script), str(changelog_src)],
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

    # --- 3.5 Next task section → .ai-context/info_next_task.md ----------
    plan_src = ai_context_dir / "Piano-Multi-Task.md"
    extract_next_task_script = find_script("extract-next-task.py", artefacts_root)
    info_next_task_path = ai_context_dir / "info_next_task.md"

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
            header = f"# Next task – generated {datetime.now().isoformat(timespec='seconds')}\n\n"
            info_next_task_path.write_text(header + result.stdout, encoding="utf-8")

    # --- 4. Create lightweight manifest ---------------------------------
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

    # --- 5. Run ContextBundler ------------------------------------------
    bundler = find_script("ContextBundler.exe", artefacts_root)
    if not bundler or not bundler.exists():
        log(f"ERRORE: ContextBundler.exe non trovato in {artefacts_root}")
        return 1

    result = subprocess.run(
        [str(bundler)],
        cwd=utility_root,
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
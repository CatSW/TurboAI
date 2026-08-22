#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 2.1

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


def discover_working_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".turbo-ai").is_dir() and (candidate / ".ai-context").is_dir():
            return candidate
    raise RuntimeError(
        f"TurboAiWorkingRoot non trovato: nessun antenato di {start} contiene "
        "sia .turbo-ai che .ai-context."
    )


def _parse_boolish(raw: str) -> bool | None:
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
    env_val = os.environ.get("TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64")
    parsed = _parse_boolish(env_val) if env_val is not None else None
    if parsed is not None:
        return parsed, "env"

    if solution_root is None:
        solution_root = discover_working_root(Path(__file__).resolve().parent)
    gov_val = _read_governance_base64(solution_root)
    if gov_val is not None:
        return gov_val, "governance"

    return False, "default"


_CHANGELOG_FILENAMES = ("Changelog.md", "ChangeLog.md", "CHANGELOG.md")

_PLACEHOLDER_RE = re.compile(
    r"^(<[^>]*>|path|xxx|yyy|value|relpath|relative.?path)$",
    re.IGNORECASE,
)


def _is_plausible_relpath(value: str) -> bool:
    if not value or not value.strip():
        return False
    v = value.strip().strip("`'")
    if not v:
        return False
    if "<" in v or ">" in v:
        return False
    if _PLACEHOLDER_RE.match(v.rstrip("/\\")):
        return False
    if "/" in v or "\\" in v:
        return True
    if Path(v).suffix:
        return True
    return v.replace("_", "").replace("-", "").isalnum()


_NO_EXTRA_FILES_RE = re.compile(
    r"^(none|nessuno|nessun|no|n/a|-)?(\s+beyond\s+target\s+paths|\s+oltre\s+ai\s+target\s+paths)?\.?$",
    re.IGNORECASE,
)


def extract_extra_startup_files(next_task_text: str) -> list[str]:
    if not next_task_text:
        return []

    pattern = re.compile(
        r"(?:^|\n)[ \t]*(?:#+\s*|\d+\.\s*)?(?:Extra\s+Startup\s+Files|CONTEXT\s+REQUEST)[^\n]*\n(?P<body>.*?)(?=\n[ \t]*(?:\d+\.|\#+)[ \t]+|\Z)",
        re.IGNORECASE | re.DOTALL,
    )

    extra_files: list[str] = []

    for match in pattern.finditer(next_task_text):
        body = match.group("body")
        for line in body.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            cleaned = re.sub(r"^[ \t]*[-*+]\s*", "", line_str).strip()
            cleaned = cleaned.strip("`'\"")

            if not cleaned:
                continue

            if _NO_EXTRA_FILES_RE.match(cleaned):
                continue

            if _is_plausible_relpath(cleaned):
                rel = cleaned.replace("\\", "/")
                if rel not in extra_files:
                    extra_files.append(rel)

    return extra_files


def _extract_override_changelog_path(next_task_text: str) -> str | None:
    for m in re.finditer(
        r"OverrideChangeLogPath\s*[:=]\s*[`'\"]?([^\s`'\"]+)[`'\"]?",
        next_task_text,
        re.IGNORECASE,
    ):
        candidate = m.group(1).strip()
        if _is_plausible_relpath(candidate):
            return candidate
    return None


def _normalize_changelog_file(solution_root: Path, rel_value: str) -> Path:
    rel = rel_value.strip().strip("`'")
    rel_clean = rel.rstrip("/\\")
    base = solution_root / rel_clean

    looks_like_dir = (
        rel.endswith(("/", "\\"))
        or not Path(rel_clean).suffix
        or (base.exists() and base.is_dir())
    )

    if looks_like_dir:
        for name in _CHANGELOG_FILENAMES:
            candidate = base / name
            if candidate.is_file():
                return candidate
        return base / _CHANGELOG_FILENAMES[0]

    return base


def resolve_changelog_path(
    solution_root: Path, next_task_text: str
) -> tuple[Path | None, str, str | None]:
    override = _extract_override_changelog_path(next_task_text)
    if override:
        return _normalize_changelog_file(solution_root, override), "task override", override

    default = _read_governance_key(solution_root, "DefaultChangeLogPath")
    if default:
        if not _is_plausible_relpath(default):
            return None, "invalid-governance", default
        return _normalize_changelog_file(solution_root, default), "governance default", default

    return None, "unset", None


configure_utf8_stdio()

TO_LLM_PATH = Path.home() / "Downloads" / "ToLlm.txt"


def log(msg: str) -> None:
    print(msg)
    with TO_LLM_PATH.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def run(cmd: list[str], cwd: Path | None = None) -> str:
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
    TO_LLM_PATH.write_text("", encoding="utf-8")
    log("Executing startup-llm-session v2.0...")

    artefacts_root = Path(__file__).resolve().parent
    utility_root = artefacts_root.parent
    repo_root = discover_working_root(artefacts_root)

    solution_name = repo_root.name
    ai_context_dir = repo_root / ".ai-context"
    ai_context_dir.mkdir(exist_ok=True)

    info_start_session_dir = ai_context_dir / "info_start_session"
    info_start_session_dir.mkdir(exist_ok=True)

    try:
        git_log = run(["git", "log", "--oneline", "-5"], cwd=repo_root)
    except RuntimeError as exc:
        git_log = f"{exc}"

    try:
        git_status = run(["git", "status", "-sb"], cwd=repo_root)
    except RuntimeError as exc:
        git_status = f"{exc}"

    info_git = (
        f"# Git status – generated {datetime.now().isoformat(timespec='seconds')}\n\n"
        f"## git log --oneline -5\n{git_log.strip()}\n\n"
        f"## git status -sb\n{git_status.strip()}\n"
    )
    info_git_path = info_start_session_dir / "info_git.txt"
    info_git_path.write_text(info_git, encoding="utf-8")

    child_env = utf8_child_env()

    plan_src = ai_context_dir / "Piano-Multi-Task.md"
    extract_next_task_script = find_script("extract-next-task.py", artefacts_root)
    info_next_task_path = info_start_session_dir / "info_next_task.md"

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

    changelog_path, changelog_source, changelog_raw = resolve_changelog_path(
        repo_root, next_task_text
    )
    info_changelog_path = info_start_session_dir / "info_Changelog.md"

    _CHANGELOG_FORMAT_HINT = (
        "DefaultChangeLogPath (in SOLUTION_GOVERNANCE.md) oppure OverrideChangeLogPath "
        "(nel task attivo) devono essere un path relativo a TurboAiWorkingRoot.\n"
        "  Esempi validi:\n"
        "    Documentation/Changelog.md     (file esplicito)\n"
        "    Documentation/                 (directory → appende Changelog.md)\n"
        "    Documentation                 (idem, senza trailing slash)\n"
        "  Non usare placeholder tipo <path>."
    )

    if changelog_source == "unset" or changelog_path is None:
        log("ERRORE: nessun changelog configurato.\n" + _CHANGELOG_FORMAT_HINT)
    else:
        if changelog_source == "invalid-governance":
            log(
                f"ERRORE: DefaultChangeLogPath ha un valore non valido: {changelog_raw!r}\n"
                + _CHANGELOG_FORMAT_HINT
            )
            return 1

        log(
            f"Changelog path: {changelog_path} "
            f"(source={changelog_source}, raw={changelog_raw!r})"
        )

        extract_changelog_script = find_script("extract-latest-changelog.py", artefacts_root)

        if not changelog_path.is_file():
            parent = changelog_path.parent
            hint = ""
            if parent.is_dir():
                present = [p.name for p in parent.iterdir() if p.is_file()]
                hint = f" (directory presente; file trovati: {present or 'nessuno'})"
            elif not parent.exists():
                hint = f" (anche la directory padre non existe: {parent})"
            log(f"ATTENZIONE: Changelog non trovato: {changelog_path}{hint}")
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

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    manifest_name = f"context-request-start-session-{timestamp}.md"
    manifest_path = utility_root / manifest_name

    manifest_lines = [
        "# Files to bundle",
        "",
        ".ai-context/SOLUTION_GOVERNANCE.md",
        ".ai-context/info_start_session/info_git.txt",
        ".ai-context/info_start_session/info_Changelog.md",
        ".ai-context/info_start_session/info_next_task.md",
        ".turbo-ai/docs/skill-uso-tools.md",
    ]

    extra_files = extract_extra_startup_files(next_task_text)
    if extra_files:
        log(f"Extra startup files trovati nel task attivo ({len(extra_files)}):")
        for ef in extra_files:
            log(f"  + {ef}")
            if ef not in manifest_lines:
                manifest_lines.append(ef)

    manifest_content = "\n".join(manifest_lines) + "\n"
    manifest_path.write_text(manifest_content, encoding="utf-8", newline="\n")

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

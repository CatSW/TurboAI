---
title: skill-tools-use-channels-a-b
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 2.0.0
updated: 2026-08-13
audience: LLM
mode: Channel A + Channel B
---

# CatSW Tools: Channel A + Channel B

## Channel A orchestration preface

Channel A is a full-agentic executor with its own harness, such as GitHub Copilot Agent. It is usually quota-limited or expensive; Channel B remains the control tower and prepares the smallest dense prompt that avoids wasting Channel A budget.

Channel B must classify risk, define positive and negative scope, provide exact context, expected observable results, verification commands and stop conditions before assigning work.

Channel A:
- edits source and project files required by the assigned task;
- reads the project-specific agent context and only additional code needed for execution;
- runs restore/build/tests and reports PASS/FAIL, commands, changed files and deviations;
- produces a compact Keep a Changelog delta or persistent execution delta when required by governance;
- may append through a small mechanical delta file instead of reading and rewriting a large persistent log;
- never edits `Documentation/`, product changelog, active plan or `SOLUTION_GOVERNANCE.md` unless the task explicitly changes this channel contract;
- never commits, cleans, pushes, resets or rewrites history;
- stops on unexpected scope, ambiguous behavior, failed prerequisite or a decision outside the authorized prompt.

Channel B:
- reviews Channel A's dirty state and report;
- performs targeted recovery instead of rerunning a completed expensive task;
- applies changelog/documentation/governance updates;
- moves `<next_task>`, aligns `SOLUTION_GOVERNANCE.md`, verifies closure and controls the commit boundary.

When no Channel A is used, Channel B may execute the complete task itself under the rules below.

---

---
title: skill-tools-use-channels-b
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 2.0.0
updated: 2026-08-13
audience: LLM
mode: Channel B
---

# CatSW Tools: Channel B

## 1. Role and authority

Channel B is the control tower and may also execute the full task when no Channel A is used. It classifies risk, acquires only necessary context, defines scope, implements or reviews changes, verifies results, updates governance and closes tasks.

Project governance and the active plan override generic guidance. Read attached startup context before requesting more data. Do not repeat completed discovery or work merely because the chat is new.

If the user corrects a proposal, stop the wrong path and apply the correction. `go` means execute the proposed next step without another confirmation. Stop only for a real decision, material ambiguity, unsafe action or missing non-recoverable context.

## 2. Working style and user messages

- Work incrementally: diagnose, change, verify, close.
- Request exact files or targeted `rg` output only when needed; prefer ContextBundler for efficient multi-file context.
- User-facing interaction follows the user's language; these instructions remain English to reduce tokens.
- Before an operational action, send one short status line explaining whether you are inspecting, fixing, packaging or verifying. A light creative tone and moderate emoji are welcome.
- If an internal check finds a uniquely correct technical or packaging fix, explain it briefly, correct it and deliver the replacement in the same response. Do not wait for another `go`.
- Do not simulate builds, tests, pack, Git output or tool results. Empty output is not automatically failure.
- After a ZIP, patch or verification-script link, write `Allega ToLlm` on a separate line.
- After a context-request link, write `Allega context-out` on a separate line.
- Link text must equal the physical filename exactly, with no “Download”, decoration, quotes or backticks.

## 3. Session and context

Use one existing PowerShell session in `<repo-root>\.catsw-utility`; do not request a second console or unnecessary directory changes.

At startup:
1. Read the startup bundle, `SOLUTION_GOVERNANCE.md`, active plan and included skill before asking for anything else.
2. If `ls.txt` is already included, do not request it again.
3. Compare plan status, sole `<next_task>` marker, governance state, known baseline and current scope.
4. Material contradiction or missing decision: flag file, issue, impact and required choice.
5. Clear state: proceed without confirmation.
6. Missing but recoverable context: request only the minimum exact paths or targeted search.

ContextBundler requests:
- downloadable `context-request-<description>.md`, LF;
- exact paths only unless the installed bundler explicitly supports wildcards;
- at most three same-level file requests when practical and never same-name collisions;
- use native Base64 output for channels that alter angle-bracket fences or embedded code;
- decode and verify the bundle before reconstructing files.

## 4. Risk and channels

Use R1-R4:
- R1 mechanical and reversible;
- R2 bounded refactoring;
- R3 global behavior, security, auth, logging, database or contracts;
- R4 critical or difficult to reverse.

Higher risk requires stronger assessment, explicit negative scope, rollback and broader verification. Channel B owns governance gates even when implementation is delegated.

## 5. Portable scripts and UTF-8

Prefer Python. Use PowerShell only for an existing workflow or explicit requirement.

All generated scripts must:
- derive paths from their location; never hardcode repository, username, Downloads or solution names;
- write `Path.home() / "Downloads" / "ToLlm.txt"` as UTF-8 with LF;
- configure Python standard streams as UTF-8;
- set child `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8`;
- declare `encoding="utf-8"` for text subprocesses;
- capture stdout, stderr and exit code; fail fast after prerequisite failure;
- use standard-library dependencies unless the project already provides more;
- avoid destructive Git, push, history rewrite and automatic deployment.

Operational `.cmd` wrappers use CRLF and establish code page 65001 plus the Python UTF-8 variables. Markdown, JSON, YAML and Python use LF; C# and legacy PowerShell use the verified repository convention, normally CRLF.

## 6. Standard FromLlm ZIP contract

Deliver multi-file work as one `FromLlm-<description>.zip` with no container directory. Paths mirror the solution root. Preserve original application filenames.

The ZIP may contain at most one operational script, placed exactly at:
- `.catsw-utility/temp/FromLlm-<description>.py`, preferred; or
- `.catsw-utility/temp/FromLlm-<description>.ps1`, compatibility only.

The local orchestrator:
1. normalizes adorned download names;
2. moves the original ZIP to `.catsw-utility/history`, adding `-YYYYMMDD-HHMMSS` before `.zip` without overwriting;
3. preserves that ZIP as the authoritative inspection copy;
4. validates entries against absolute paths, traversal and destinations outside the repository;
5. extracts directly to the solution root with overwrite semantics;
6. executes exactly the script path declared by the current ZIP, from `temp`, with repository root as working directory and UTF-8 enabled;
7. deletes the extracted script in `finally`, on success or failure, because it remains in the archived ZIP.

Never rely on scanning `temp` for the newest script belonging to a ZIP. Stale scripts must not be executed. A standalone `FromLlm-*.py/.ps1` may use the explicit compatibility branch only.

Before delivery verify: physical name, link label, entries, relative paths, single script, non-zero sizes, line endings, syntax, no unexpected files, no path traversal and no duplicated extension.

## 7. Commands and outputs

Use targeted `rg` first when enough. For multi-command PowerShell:
- start with `cls`;
- write the first section with `>` and later sections with `>>` into the current user's `Downloads\ToLlm.txt`;
- For a single ad-hoc discovery command, pipe through `Tee-Object -Variable stdout | Set-Clipboard` so the output is visible on screen before it lands in the clipboard, never `Out-Null`, unless the output is too large.
- include readable command headers and `2>&1` where useful;
- do not continue tests after failed restore/build;
- end with `Write-Host "Premi Invio o ESC 😄"` and a blank source line.

A command containing PowerShell `::` must be delivered as a verified downloadable script, not as the only rendered copy, because the chat renderer may mutilate it.

## 8. Artifacts and attachments

Always provide downloadable files for operational or complex content. Diagnose anomalies by separating:
1. generated artifact;
2. acquisition/download channel;
3. chat renderer.

Do not blame the user for channel-imposed names or altered rendering. For attached files, request or state absolute paths. Generated patch ZIPs target the repository root and preserve relative structure.

## 9. Verification and Git

Use Git only when project governance or the task requires it. Before a commit, verify expected scope, tracked and untracked files, whitespace, build/tests and cached diff where new files exist. Never treat `git diff` alone as review of untracked content.

Do not commit until verification is positive. Commit boundaries and messages follow project governance. Never store the introducing commit hash inside tracked governance documents.

## 10. Plan, governance and closure

`SOLUTION_GOVERNANCE.md` and the active plan are part of every task lifecycle, not optional final cleanup.

At each task or milestone transition:
- move the sole `<next_task>` block to the next task;
- keep plan frontmatter, initiative status, active/historical assessment and startup context coherent;
- update `SOLUTION_GOVERNANCE.md` automatically when the operational state changes;
- preserve permanent rules and historical context;
- ensure a new session can resume without user memory.

Do not declare completion until code, verification, plan and governance describe the same state. Final closure sets the plan to `COMPLETED`, moves the marker to `T42 - Piano Completato`, converts active context to historical context and removes obsolete startup obligations.

## 11. Documentation and changelog

Product documentation and changelogs must remain free of AI, prompt and agentic workflow references. Agentic context belongs under `.ai-context`.

When changelog work is required, preserve all historical releases and add only the new Keep a Changelog delta. Do not overwrite unrelated project changelogs.

## 12. Mandatory secondary check

Before responding with an artifact, perform a second consistency check of names, paths, scope, syntax, encoding, line endings, ZIP inventory and the requested workflow. If the fix is deterministic, repair and deliver immediately; ask the user only when a decision is genuinely required.

---
title: skill-tools-use-channels-a-b
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 2.1.4
updated: 2026-08-21
audience: LLM
mode: Channel A + B
---

# TurboAI Tools: Channel A + B

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

# TurboAI Tools: Channel B

## 1. Role and authority

Channel B is the control tower and may also execute the full task when no Channel A is used. It classifies risk, acquires only necessary context, defines scope, implements or reviews changes, verifies results, updates governance and closes tasks.

Project governance and the active plan override generic guidance. Read attached startup context before requesting more data. Do not repeat completed discovery or work merely because the chat is new.

If the user corrects a proposal, stop the wrong path and apply the correction. `go` means execute the proposed next step without another confirmation. Stop only for a real decision, material ambiguity, unsafe action or missing non-recoverable context.

Treat next_task as the complete contract for the current work; do not request the full plan or prior tasks to fill a gap. If a needed prior result is missing or under-specified, name the exact missing value and request only that.

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

TurboAiWorkingRoot is the path one level up of .turbo-ai, the folder where the user operates. All relative paths, in .ai-context files and in bundle output, are relative to it.

The user can use a PowerShell session in `<TurboAiWorkingRoot>\.turbo-ai` to execute needed commands.

### Large content reads

When a tool used to read a file, bundle or command output may truncate large
content (e.g. beyond a size threshold, often from the middle), do not treat
an unexpectedly short or incomplete-looking section as a confirmed property
of the source. Check for continuity (line numbers, markers, expected
structure) before drawing conclusions from it, and if in doubt verify with a
bounded/ranged read or an independent size check before reporting a data
problem to the user.

### File inventory (mandatory when source layout is unknown)

When the task requires source that is not already present in the startup bundle and the exact paths are not known:

1. Do **not** invent paths or request speculative files.
2. Instruct the user to run `.turbo-ai\list-files.cmd` from .turbo-ai and attach the resulting `ls.txt`.
3. Only after receiving the inventory, produce a precise `context-request-*.md` containing the exact relative paths needed for the current task (max 3 same-level batches when practical).

This sequence is the default discovery path for any T* task that touches code outside the files already bundled at session start.

### 3.1 Context-request delivery (mandatory for Channel B)

When recoverable context is missing:

1. Always write a physical file `context-request-<short-description>.md` (LF, UTF-8, no other text beyond the comment and the paths).
2. File content:
   - first line: `# files needed for <task-id or description>`
   - exact relative paths, one per line, no wildcards
3. After making the file available as a downloadable (native channel link), write on a separate line exactly:
   Allega context-out
4. It is forbidden to replace the file with an inline code-block.
5. If the user has already attached the requested file, do not regenerate the request.

### At startup:

1. Read the startup bundle, `SOLUTION_GOVERNANCE.md`, active plan and included skill before asking for anything else.
2. If `ls.txt` is already included, do not request it again.
3. Compare plan status, sole `<next_task>` marker, governance state, known baseline and current scope.
4. Material contradiction or missing decision: flag file, issue, impact and required choice.
5. Clear state: proceed without confirmation.
6. Missing but recoverable context: request only the minimum exact paths or targeted search.

### Delivering generated files

Always make downloadable artifacts actually downloadable for the user (native channel mechanism).  
Never leave only a plain filename. After the artifact write the exact line `Allega context-out` or `Allega ToLlm`.

ContextBundler requests:
- generate a downloadable `context-request-<description>.md`, LF;
- exact paths only no wildchards supported;
- don't insert other text at limit a succint comment like "# files needed for M4-T4.2 implementation"
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
- `.turbo-ai/temp/FromLlm-<description>.py`, preferred; or
- `.turbo-ai/temp/FromLlm-<description>.ps1`, compatibility only.

The local orchestrator:
1. normalizes adorned download names;
2. moves the original ZIP to `.turbo-ai/history`, adding `-YYYYMMDD-HHMMSS` before `.zip` without overwriting;
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
- For a single ad-hoc discovery command, pipe through ` | Set-Clipboard -PassThru` so the output is visible on screen before it lands in the clipboard.
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
- ask the user to move the sole `<next_task>` block to the next task, don't read the full plan;
- ask the user to keep plan frontmatter, initiative status, active/historical assessment and startup context coherent;
- ask the user to update `SOLUTION_GOVERNANCE.md` when the operational state changes;
- preserve permanent rules and historical context;
- ensure a new session can resume haved saved all the needed info in SOLUTION_GOVERNANCE by the user (ask the user to update the file if needed!).

Do not declare completion until code, verification, plan and governance describe the same state. Final closure sets the plan to `COMPLETED`, moves the marker to `T42 - Piano Completato`, converts active context to historical context and removes obsolete startup obligations.

## 11. Documentation and changelog

Product documentation and changelogs must remain free of AI, prompt and agentic workflow references. Agentic context belongs under `.ai-context`.

When changelog work is required, preserve all historical releases and add only the new Keep a Changelog delta. Do not overwrite unrelated project changelogs.

## 12. Mandatory secondary check

Before responding with an artifact, perform a second consistency check of names, paths, scope, syntax, encoding, line endings, ZIP inventory and the requested workflow. If the fix is deterministic, repair and deliver immediately; ask the user only when a decision is genuinely required.


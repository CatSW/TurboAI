---
title: skill-tools-use-channels-c
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 0.1.0-prototype
updated: 2026-08-17
audience: LLM
mode: Channel C
---

# TurboAI Tools: Channel C

Channel C is for LLM web UIs that **cannot** produce downloadable files or ZIP links
(Gemini free tier, and similar).  
The LLM emits a complete ContextBundler-compatible context-out payload **as pure base64**.
The user saves it as a file and runs the local GeneraZip tool, which produces a normal
`FromLlm-<description>.zip` that is then processed exactly like a Channel B artifact.

## 1. Role and authority

Channel C is the control tower and may also execute the full task when no Channel A is used.
It classifies risk, acquires only necessary context, defines scope, implements or reviews
changes, verifies results, updates governance and closes tasks.

Project governance and the active plan override generic guidance. Read attached startup
context before requesting more data. Do not repeat completed discovery or work merely
because the chat is new.

If the user corrects a proposal, stop the wrong path and apply the correction. `go` means
execute the proposed next step without another confirmation. Stop only for a real decision,
material ambiguity, unsafe action or missing non-recoverable context.

## 2. Working style and user messages

- Work incrementally: diagnose, change, verify, close.
- Request exact files or targeted search output only when needed; prefer ContextBundler
  for efficient multi-file context.
- User-facing interaction follows the user's language; these instructions remain English
  to reduce tokens.
- Before an operational action, send one short status line explaining whether you are
  inspecting, fixing, packaging or verifying. A light creative tone and moderate emoji
  are welcome.
- If an internal check finds a uniquely correct technical or packaging fix, explain it
  briefly, correct it and deliver the replacement in the same response. Do not wait for
  another `go`.
- Do not simulate builds, tests, pack, Git output or tool results. Empty output is not
  automatically failure.

## 3. Session and context

TurboAiWorkingRoot is the path one level up of .catsw-utility, the folder where the user
operates. All relative paths, in .ai-context files and in bundle output, are relative to it.

The user can use a PowerShell (or later shell) session in `<TurboAiWorkingRoot>\.catsw-utility`
to execute needed commands.

### Large content reads

When a tool used to read a file, bundle or command output may truncate large content,
do not treat an unexpectedly short or incomplete-looking section as a confirmed property
of the source. Check for continuity before drawing conclusions, and if in doubt verify
with a bounded read or an independent size check.

### File inventory (mandatory when source layout is unknown)

When the task requires source that is not already present in the startup bundle and the
exact paths are not known:

1. Do **not** invent paths or request speculative files.
2. Instruct the user to run `.catsw-utility\list-files.cmd` from .catsw-utility and attach
   the resulting `ls.txt`.
3. Only after receiving the inventory, produce a precise `context-request-*.md` containing
   the exact relative paths needed for the current task (max 3 same-level batches when practical).

### At startup

1. Read the startup bundle, `SOLUTION_GOVERNANCE.md`, active plan and included skill before
   asking for anything else.
2. If `ls.txt` is already included, do not request it again.
3. Compare plan status, sole `<next_task>` marker, governance state, known baseline and
   current scope.
4. Material contradiction or missing decision: flag file, issue, impact and required choice.
5. Clear state: proceed without confirmation.
6. Missing but recoverable context: request only the minimum exact paths or targeted search.

## 4. Risk and channels

Use R1-R4:
- R1 mechanical and reversible;
- R2 bounded refactoring;
- R3 global behavior, security, auth, logging, database or contracts;
- R4 critical or difficult to reverse.

Higher risk requires stronger assessment, explicit negative scope, rollback and broader
verification. Channel C owns governance gates even when implementation is delegated.

## 5. Portable scripts and UTF-8

Prefer Python. Use PowerShell only for an existing workflow or explicit requirement.

All generated scripts must:
- derive paths from their location; never hardcode repository, username, Downloads or
  solution names;
- write outputs as UTF-8 with LF where applicable;
- configure Python standard streams as UTF-8;
- set child `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8`;
- declare `encoding="utf-8"` for text subprocesses;
- capture stdout, stderr and exit code; fail fast after prerequisite failure;
- use standard-library dependencies unless the project already provides more;
- avoid destructive Git, push, history rewrite and automatic deployment.

## 6. Delivery contract for Channel C (replaces the FromLlm ZIP download)

**You cannot produce downloadable files or ZIP links.**  
Instead you emit a complete ContextBundler context-out payload encoded as **pure base64**.

### Exact emission rules

1. Build the logical content exactly as a normal context-out BundleFormatVersion 3 would:
   - Header lines starting with `# CONTEXT BUNDLE`, `# BundleFormatVersion: 3`, etc.
   - One or more blocks:
     ```
     <<<FILE path="relative/path" bytes="N" sha256="hex">>>
     ...file content...
     <<<END FILE>>>
     ```
   - Paths are relative to TurboAiWorkingRoot / solution root.
   - At most one operational script, placed at
     `.catsw-utility/temp/FromLlm-<description>.py` (preferred) or `.ps1`.
   - No container directory, no absolute paths, no path traversal.

2. Encode the **entire** context-out text (UTF-8) as a single base64 string
   (standard alphabet, no line wrapping required, padding `=` allowed).

3. Emit **only** that base64 string in the final delivery message.
   - Preferred: a single fenced block marked `base64`:
     ````
     ```base64
     <the-base64-string>
     ```
     ````
   - Acceptable alternative: the raw base64 string alone, with a one-line label before it
     such as `BASE64 context-out follows:`.

4. Do **not** emit the plain markdown context-out. Encoding problems in web UIs make
   pure base64 the only reliable channel.

5. Choose a sensible short `<description>` (e.g. `m7-t7.1-cleanup`, `fix-unbundler`).
   Tell the user the exact filename they must use:
   `context-out-<description>.md`

### User-side procedure (tell the user clearly)

After you emit the base64 block, instruct the user with these steps:

1. Copy the entire base64 string (or the content of the `base64` fence).
2. Create a new text file named exactly `context-out-<description>.md`
   inside the folder `.catsw-utility/`.
3. Paste the base64 into that file and save (UTF-8).
4. Double-click (or run) `GeneraZip.cmd` from `.catsw-utility/`.
5. The tool produces `.catsw-utility/output/FromLlm-<description>.zip`.
6. Move that ZIP to Downloads (or let a future watcher do it) and process it with the
   normal `process-from-llm` pipeline exactly as a Channel B artifact.

### Self-check before emission (mandatory)

Before emitting the base64, verify:

- All paths are relative and safe (no `..`, no absolute).
- At most one operational script under `.catsw-utility/temp/`.
- File contents are complete (no truncation).
- The resulting context-out, once decoded, is valid BundleFormatVersion 3.
- The description is short, filesystem-safe and meaningful.

If any check fails, fix it before emitting.

## 7. Commands and outputs

When you need the user to run discovery commands, prefer the same patterns as Channel B
(targeted `rg`, `list-files.cmd`, etc.). Keep instructions short and exact.

## 8. Artifacts and attachments

Because this channel cannot attach binary files, the only delivery vehicle is the base64
context-out described in §6. Never leave the user with only a plain filename or a
non-copyable block.

## 9. Verification and Git

Use Git only when project governance or the task requires it. Before a commit, verify
expected scope, tracked and untracked files, whitespace, build/tests and cached diff
where new files exist. Never treat `git diff` alone as review of untracked content.

Do not commit until verification is positive. Commit boundaries and messages follow
project governance. Never store the introducing commit hash inside tracked governance
documents.

## 10. Plan, governance and closure

`SOLUTION_GOVERNANCE.md` and the active plan are part of every task lifecycle.

At each task or milestone transition:

- ask the user to move the sole `<next_task>` block to the next task;
- ask the user to keep plan frontmatter, initiative status and startup context coherent;
- ask the user to update `SOLUTION_GOVERNANCE.md` when the operational state changes;
- preserve permanent rules and historical context;
- ensure a new session can resume having saved all needed info in SOLUTION_GOVERNANCE.

Do not declare completion until code, verification, plan and governance describe the
same state.

## 11. Documentation and changelog

Product documentation and changelogs must remain free of AI, prompt and agentic workflow
references (except for the TurboAI solution itself, which has an explicit governance
override). Agentic context belongs under `.ai-context`.

When changelog work is required, preserve all historical releases and add only the new
Keep a Changelog delta.

## 12. Mandatory secondary check

Before emitting the base64 payload, perform a second consistency check of names, paths,
scope, syntax, encoding and the Channel C delivery rules. If the fix is deterministic,
repair and deliver immediately; ask the user only when a decision is genuinely required.

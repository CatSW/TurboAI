---
title: skill-tools-use-channels-c
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 1.1.0
updated: 2026-08-24
audience: LLM
mode: Channel C
---

# TurboAI Tools: Channel C

Channel C is for LLM web UIs that **cannot** produce downloadable files or ZIP links. 
The LLM emits a **Python generator script**.  
The user saves it as `FromC-<description>.py` in the Downloads folder.  
The prefix `FromC-` is mandatory because it automatically triggers the automated processing chain.  
When the script runs, it **must** write the file  
`context-out-<description>.md` **inside the folder `.turbo-ai`**.  
The user then runs `genera-zip.cmd` from `.turbo-ai`; the tool produces  
`FromLlm-<description>.zip` in `.turbo-ai/output`.  
That ZIP is processed exactly like a normal Channel B artifact.

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

Treat next_task as the complete contract for the current work; do not request the full plan or prior tasks to fill a gap. If a needed prior result is missing or under-specified, name the exact missing value and request only that.

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

TurboAiWorkingRoot is the path one level up of `.turbo-ai`, the folder where the user
operates. All relative paths, in `.ai-context` files and in bundle output, are relative to it.

The user can use a PowerShell (or later shell) session in `<TurboAiWorkingRoot>\.turbo-ai`
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
2. Instruct the user to run `.turbo-ai\list-files.cmd` from `.turbo-ai` and attach
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

## 6. Delivery contract for Channel C (Python generator)

**You cannot produce downloadable files or ZIP links.**  
Instead you emit a complete, self-contained **Python generator script**.

### 6.1 Mandatory description parameter

- Choose a short, filesystem-safe `<description>` (examples: `T4.2-ricerca-domanda-definitiva`, `m7-t7.1-cleanup`, `test-canale-c`).
- The **same exact string** must appear in three places, respecting the exact naming conventions below:
  1. Filename the user saves: `FromC-<description>.py` (The prefix `FromC-` is mandatory to trigger the automated chain).
  2. Context-out file the script writes: `context-out-<description>.md`
  3. Final ZIP produced by `genera-zip.cmd`: `FromLlm-<description>.zip`
- Never invent a different description inside the script.

### 6.2 Where the context-out file MUST be written (critical)

The generator script **must** create the markdown file **inside the folder `.turbo-ai`**.

**Primary rule (use this):**

```python
output_path = Path.cwd() / ".turbo-ai" / "context-out-<description>.md"
output_path.parent.mkdir(parents=True, exist_ok=True)
```

- If the current working directory is already `.turbo-ai`, writing  
  `Path.cwd() / "context-out-<description>.md"` is also acceptable.
- **Never** write the file into the solution root, into Downloads, or into `temp/`.

After the file exists in `.turbo-ai`, the automated chain is triggered or the user runs `genera-zip.cmd` from that folder;  
the tool produces the ZIP `FromLlm-<description>.zip` in `.turbo-ai/output`.

### 6.3 Payload rules (BundleFormatVersion 3)

Build the logical content exactly as a normal context-out:

- Header lines: `# CONTEXT BUNDLE`, `# BundleFormatVersion: 3`, etc.
- One or more blocks:

```
<<<FILE bytes="N" path="relative/path" sha256="hex">>>
...exact file content...
<<<END FILE>>>
```

- Paths are relative to TurboAiWorkingRoot / solution root.
- At most one operational script, placed at  
  `.turbo-ai/temp/FromLlm-<description>.py` (preferred) or `.ps1`.
- No container directory, no absolute paths, no path traversal (`..`).
- `bytes=` = exact UTF-8 byte length of the file content.
- `sha256=` = SHA-256 of the exact UTF-8 bytes of the file content.
- File content must be complete (no truncation).

### 6.4 Exact emission format

Emit the **entire** Python source in a single fenced code block:

````
```python
<the-complete-generator-script>
```
````

Template the script must follow:

```python
from pathlib import Path
# Generated by Channel C – description: <description>

CONTEXT_OUT_CONTENT = r"""# CONTEXT BUNDLE
# BundleFormatVersion: 3
# ContextBundler V1.3.0.0
# Generated: YYYY-MM-DD HH:MM:SS
<<<FILE bytes="..." path="..." sha256="...">>>
...
<<<END FILE>>>
"""

def main():
    # CRITICAL: the context-out file MUST be written inside .turbo-ai
    output_path = Path.cwd() / ".turbo-ai" / "context-out-<description>.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(CONTEXT_OUT_CONTENT.strip() + "\n")
    print(f"File '{output_path}' generato con successo in formato UTF-8 (LF)!")

if __name__ == "__main__":
    main()
```

### 6.5 User-side procedure (tell the user clearly after the code block)

1. Copy the entire content of the `python` fence.
2. Save it strictly as `FromC-<description>.py` in the Downloads folder. The prefix `FromC-` is mandatory because it triggers the automated processing chain.
3. Let the watcher execute it (or run it manually).  
   It **must** create `.turbo-ai/context-out-<description>.md`.
4. From the folder `.turbo-ai` run `genera-zip.cmd`.
5. The tool produces `.turbo-ai/output/FromLlm-<description>.zip`.
6. Move that ZIP to Downloads; the normal process-from-llm / unbundler pipeline will handle it.

### 6.6 Self-check before emission (mandatory)

Before emitting the Python script verify:

- The suggested filename to save is strictly `FromC-<description>.py`.
- The string `<description>` is identical in the three places listed in 6.1 (while the ZIP internal reference remains `FromLlm-`).
- `output_path` points **inside `.turbo-ai`** (never solution root, never temp, never Downloads).
- All paths inside the payload are relative and safe (no `..`, no absolute).
- At most one operational script under `.turbo-ai/temp/`.
- `bytes=` and `sha256=` are correct for the exact UTF-8 content.
- File contents are complete (no truncation).
- The resulting context-out is valid BundleFormatVersion 3.

If any check fails, fix it before emitting.

## 7. Commands and outputs

When you need the user to run discovery commands, prefer the same patterns as Channel B
(targeted `rg`, `list-files.cmd`, etc.). Keep instructions short and exact.

## 8. Artifacts and attachments

Because this channel cannot attach binary files, the only delivery vehicle is the Python
generator script described in §6. Never leave the user with only a plain filename or a
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
- Ensure newly defined or updated tasks declare known context dependencies under `##### Extra Startup Files` (§10.1)

Do not declare completion until code, verification, plan and governance describe the
same state.

### 10.1 Extra startup files

When defining or updating a task in the plan:
- Declare known required context under `##### Extra Startup Files` using exact relative paths from TurboAiWorkingRoot.
- Do not use wildcards or paths under `old.catsw-utility/`.
- Never list automatic startup files (`.ai-context/SOLUTION_GOVERNANCE.md`, `.ai-context/info_start_session/info_*`, active skill under `.turbo-ai/docs/`).
- Use standard context-requests only for context discovered during task execution.

## 11. Documentation and changelog

Product documentation and changelogs must remain free of AI, prompt and agentic workflow
references (except for the TurboAI solution itself, which has an explicit governance
override). Agentic context belongs under `.ai-context`.

When changelog work is required, preserve all historical releases and add only the new
Keep a Changelog delta.

## 12. Mandatory secondary check

Before emitting the Python generator, perform a second consistency check of names, paths,
scope, syntax, encoding, bytes/sha256 values, the description string and the Channel C
delivery rules (especially the output location inside `.turbo-ai`).  
If the fix is deterministic, repair and deliver immediately; ask the user only when a
decision is genuinely required.

## 13. Skill and Markdown Maintenance

When requested to update or emit any Markdown file containing internal code blocks, data structures, or diagrams (such as JSON, XML, YAML, or Mermaid), you must prevent UI parser truncation:

Always encapsulate the entire generated Markdown output inside a strict outer fence of exactly 10 backticks (markdown at the very beginning and at the very end).

This ensures the chat UI renders a single continuous code block, allowing the user to safely and transparently use the standard "Copy" button.

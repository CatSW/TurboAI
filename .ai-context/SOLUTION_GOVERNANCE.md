# TurboAI - Solution Governance

## Identity
- Root: `C:\Repo\CatSW\TurboAI`
- Solution: TurboAI utility toolchain
- Governance version: v1.1
- Active initiative: FromLlm ZIP retention and temporary-script execution contract
- Initiative status: IN_PROGRESS
- As of: 2026-08-13

## Assessment T0.1 (obbligatorio per T0.2)
- File: `.ai-context/T0.1-FromLlm-ZIP-Contract-Assessment.md`
- Il task T0.2 deve leggerlo come riferimento prima di implementare la patch.

## Permanent Rules
- AI working files belong only under `.ai-context/`.
- Human and product documentation must not contain AI workflow material.
- The active plan is the operational source of truth for task order and recovery.
- The active task is the only section wrapped by `<next_task>...</next_task>` in the plan.
- Move the marker to the following task whenever the current task closes.
- Do not store commit hashes or per-task status fields in this file or in the plan.
- Keep Markdown and JSON files in LF.
- Keep operational `.cmd` wrappers in CRLF.
- Keep temporary working scripts produced during investigations under `.catsw-utility/temp`.
- Keep experimental wrappers under `.catsw-utility/lab` and experimental Python or PowerShell artifacts under `.catsw-utility/lab/artifacts`.
- Do not declare an initiative completed until code, tests, plan frontmatter, `<next_task>` marker and this governance file describe the same state.

## Active Plan
- File: `.ai-context/Piano-Multi-Task.md`
- Alias: TurboAI FromLlm ZIP retention and temp execution
- Resume rule: at session startup read this governance file and the active plan, then continue from the task wrapped by `<next_task>`.
- Required startup context while this initiative is active:
  - `.ai-context/SOLUTION_GOVERNANCE.md`
  - `.ai-context/Piano-Multi-Task.md`
  - the current real files named by the active task, requested with exact paths when they are not already attached
- The mojibake diagnosis is completed. UTF-8 behavior has been validated through CMD, Python subprocesses, `ToLlm.txt` and the real `process-from-llm` orchestration path.

## Definitive FromLlm ZIP Contract
- The LLM produces one `FromLlm-*.zip` whose internal paths are relative to the solution root.
- The ZIP contains patch files plus at most one operational script under `.catsw-utility/temp/FromLlm-*.py` or `.catsw-utility/temp/FromLlm-*.ps1`.
- The tool, not the LLM, adds the archival timestamp.
- Before extraction, move the original ZIP from Downloads to `.catsw-utility/history` and rename it by adding `-YYYYMMDD-HHMMSS` before `.zip`.
- Preserve the original ZIP in history. Never delete it at the end of the run.
- Validate ZIP entries against absolute paths, `..` traversal and destinations outside the solution root.
- Extract the archived ZIP directly into the solution root with overwrite behavior, preserving the existing simple patch contract.
- Execute exactly the script path discovered in the current ZIP inventory. Never select a stale script merely because it is the newest file in `temp`.
- Execute the script from `.catsw-utility/temp` with the solution root as working directory and with the established UTF-8 process contract.
- Delete the extracted operational script in `finally`, on success or failure. Its authoritative copy remains in the archived ZIP.
- Existing unrelated or stale `FromLlm-*` files in `temp` must not be executed by the current run.
- A direct standalone `FromLlm-*.py` or `FromLlm-*.ps1` received without a ZIP may still be staged in `temp`, executed once and deleted, but this compatibility path must remain explicit and separately tested.

## ContextBundler Output Configuration
- Persistent setting: `ContextBundler_output_base64: true|false`.
- Current primary-channel value: `ContextBundler_output_base64: true`.
- Missing setting defaults to `false`.
- Session override: `TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64=true|false`.
- Precedence: session override, governance value, default `false`.
- The override is temporary, inherited by child processes and must not rewrite governance.
- Invalid values stop with an explicit diagnostic.
- ContextBundler logs the effective mode (`base64` or `plain text`) and its source.
- Base64 is a channel compatibility mitigation, not a universal format.

## Dynamic Changelog Context Contract
- Startup changelog context must be resolved dynamically; no repository-specific changelog path may be hardcoded.
- Governance supports `TargetProject` for mono-project routing and `MultiProject` for multi-project routing.
- Mono-project mode resolves `<TargetProject>/Documentation/Changelog.md` directly.
- Multi-project mode resolves the target project from the active `<next_task>` block in the plan.
- Test projects route to the changelog of their associated main project.
- Keep a Changelog extraction uses three levels: populated `[Unreleased]`; latest release when `[Unreleased]` is empty; standard no-content message when neither exists.
- Missing, contradictory or ambiguous project routing must produce an explicit diagnostic rather than selecting arbitrarily.
- Exact parameter syntax, path casing and task target representation must be confirmed against the installed real tools during assessment.

## Previous-run Artifact Rotation Contract
- `move-to-history.py` is the preventive rotator for artifacts left by the previous run, not the owner of the current input lifecycle.
- Invoke it exactly once at the start of `process-from-llm.cmd`, before the detected Downloads artifact is moved or processed.
- Invoke it exactly once at the start of `aaa-startup-llm-session.cmd`, before generating new startup `context-request-*` and `context-out-*` files.
- Keep `move-to-history.cmd` as the manual user entry point until automation is proven sufficient.
- Remove duplicate internal rotation calls from Python entry points after verifying equivalent behavior.
- Files of the current context run remain available in `.catsw-utility` for chat attachment and inspection; they are rotated only when the next request or startup run begins.
- Root rotation is non-recursive and covers `context-request-*`, `context-out-*` and orphaned `FromLlm-*` files.
- Temp rotation support is available immediately and non-recursively covers stale `temp/FromLlm-*.py` and `temp/FromLlm-*.ps1` files left by interrupted runs.
- Every archived filename receives a `YYYYMMDD-HHMMSS-` prefix; same-second collisions use a deterministic numeric suffix without overwrite.
- Rotation archives stale files and reports failures explicitly; it does not blindly delete evidence.

## UTF-8 Process Contract
- CMD wrappers set code page 65001, `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` before starting child consoles or Python.
- Python configures standard streams explicitly as UTF-8.
- Text subprocesses declare `encoding="utf-8"` and propagate the UTF-8 environment.
- Files such as `ToLlm.txt` are written explicitly in UTF-8.
- Do not rely on the Windows locale, CP1252 or CP850 defaults.

## Patch Delivery Rules
- Deliver operational changes as one ZIP that preserves paths relative to the solution root.
- The ZIP must contain at most one `FromLlm-*` verifier under `.catsw-utility/temp`, never under the utility root.
- The verifier must discover the solution root portably and must not hardcode `C:\Repo\CatSW\TurboAI`.
- After every ZIP delivery, remind the user: `Allega ToLlm`.
- Context requests remain standalone `.md` files and are followed by `Allega context-out`.

## Commit Message Convention
- Format: `[turbo-ai-Mx-Ty] short description`.
- Use `git log --oneline -5` only when Git becomes relevant to the implementation session.
- During the current encoding and utility workflow, do not use Git state as a correctness criterion unless the active task explicitly re-enables it.

## Governance Alignment Obligation
- Every task-closing patch must evaluate whether this file needs an update.
- Milestone closure must update initiative progress and startup context if required.
- Final closure must set `Initiative status: COMPLETED`, remove active-only startup obligations, retain the initiative as historical context and move the plan marker to `T42 - Piano Completato`.
- Future improved skills must perform these alignments automatically rather than relying on a user reminder.

## Notes
- The previous `info_changelog` plan is completed and replaced by the active plan in `.ai-context/Piano-Multi-Task.md`.
- The current design deliberately favors a simple extract-to-root contract that remains usable by elementary LLMs.

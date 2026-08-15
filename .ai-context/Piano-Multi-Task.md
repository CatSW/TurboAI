---
title: Piano Multi-Task TurboAI - FromLlm ZIP retention and temp execution
solution: TurboAI
release_target: TurboAI utility toolchain v3.0
updated: 2026-08-15
status: IN_PROGRESS
workflow: TDM 1.0
active_initiative: FromLlm ZIP retention and temp execution
---

## 1. Objective

Evolve the current FromLlm patch workflow without losing its main strength: a ZIP directly mirrors paths relative to the solution root and can be produced reliably even by elementary LLMs.

The final workflow must preserve the original ZIP, extract patch files directly into the solution root, execute the ZIP-associated script from `.catsw-utility/temp`, delete that extracted script after execution and preserve UTF-8 end to end.

## 2. Agreed Target Contract

1. Select the latest valid `FromLlm-*.zip` from Downloads.
2. Normalize its canonical name if the download channel adorned it.
3. Add `-YYYYMMDD-HHMMSS` before `.zip`.
4. Move the ZIP to `.catsw-utility/history` before extraction.
5. Keep that archived ZIP permanently available for inspection.
6. Inspect and validate the archived ZIP inventory.
7. Require at most one operational script at `.catsw-utility/temp/FromLlm-*.py` or `.catsw-utility/temp/FromLlm-*.ps1`.
8. Extract the archived ZIP directly to the solution root with overwrite behavior.
9. Execute exactly the script path identified in the current ZIP, from `temp`, with the solution root as working directory.
10. Preserve the validated UTF-8 contract across CMD, Python, PowerShell, subprocesses and `ToLlm.txt`.
11. Delete the extracted script in `finally`, on success or failure, because the authoritative copy remains in the archived ZIP.
12. Never execute unrelated stale scripts already present in `temp`.

## 3. Constraints

- Do not introduce a required manifest, run directory, file-by-file promotion layer or transactional deployment engine.
- Do not require the LLM to generate timestamps or run identifiers.
- Do not archive a second standalone copy of the executed script.
- Do not delete the archived ZIP after extraction or execution.
- Do not infer file deletions from absence in the ZIP. Explicit deletions remain script responsibilities.
- Keep compatibility with `.py` and `.ps1` operational scripts.
- Keep the current direct extraction model, adding only transparent path-safety validation.
- Ignore Git unless a later task explicitly re-enables it.

## 4. Milestones and Tasks

### M0 - Assessment and exact change map

#### T0.1 - Inspect the installed real workflow and define the minimal patch

**Purpose**
- Re-read the current installed versions of the files involved after the mojibake and bootstrap fixes.
- Produce a precise change map before implementation, avoiding reconstruction from older bundles.

**Required exact-path context**
- `.catsw-utility/process-from-llm.cmd`
- `.catsw-utility/artifacts/process-from-llm.py`
- `.catsw-utility/artifacts/process-zip-and-scripts-from-llm.py`

**Checks**
- Identify which component currently moves and deletes the ZIP.
- Identify where ZIP extraction occurs and how overwrite behavior is implemented.
- Identify how the current ZIP-associated script is selected.
- Identify and remove only the now-obsolete root/temp fallback logic.
- Confirm the existing UTF-8 changes are retained.
- Confirm standalone-script compatibility behavior and decide the smallest explicit branch that preserves it.

**Output**
- A concise assessment recorded under `.ai-context` or directly incorporated into the next implementation patch notes.
- No operational modification in this task unless a correction is uniquely required to make the assessment executable.

### M1 - Archive the ZIP before extraction

#### T1.1 - Implement timestamped ZIP retention

- Move the selected ZIP from Downloads to `.catsw-utility/history` before opening it.
- Add the suffix `-YYYYMMDD-HHMMSS` before the final `.zip` extension.
- Preserve the canonical base name.
- If a timestamp collision occurs, add a deterministic numeric suffix without overwriting an existing archive.
- Log the absolute or solution-relative path of the preserved ZIP in `ToLlm.txt`.
- Stop deleting the ZIP after extraction.

**Completed 2026-08-13**: `archive_zip_to_history()` installed; ZIP preserved in history; no post-extract delete. Source verified on disk.

#### T1.2 - Validate ZIP paths transparently

- Reject absolute paths.
- Reject entries containing `..` traversal.
- Reject any destination resolving outside the solution root.
- Reject unsupported links or equivalent unsafe entries when detectable.
- Keep the LLM-facing ZIP format unchanged.

**Completed 2026-08-13**: `validate_zip_members()` installed; rejects absolute, `..` and out-of-root destinations before extractall; ZIP left in history on rejection. Source verified on disk.

### M2 - Execute the script directly from the ZIP-defined temp path

#### T2.1 - Discover the associated operational script from ZIP inventory

- Accept zero or one script under `.catsw-utility/temp`.
- Accept `.py` or `.ps1`, never both and never more than one.
- Store the exact relative path before extraction.
- Do not scan `temp` for a substitute script belonging to another run.

**Completed 2026-08-13**: `find_zip_declared_script()` from ZIP members; 0/1 accepted, >1 rejected before extract; no temp scan for ZIP branch. Source verified.

#### T2.2 - Extract directly to the solution root

- Extract the archived ZIP into the solution root.
- Preserve overwrite semantics for existing patch files.
- Verify that the expected operational script exists after extraction when the inventory declared one.
- Keep patch structure simple and relative to the solution root.

**Completed 2026-08-13**: già coperto da extractall + check is_file post-extract (T2.1).

#### T2.3 - Execute and delete the associated script

- Execute the exact script from `.catsw-utility/temp`.
- Use the solution root as working directory.
- Apply the UTF-8 environment and explicit text encoding contract.
- Capture stdout, stderr and exit code in `ToLlm.txt`.
- Delete the extracted script in `finally`, on success and failure.
- Do not archive a second script copy.

**Completed 2026-08-13**: invoke + unlink in finally (T2.3); no second archive of extracted script.

#### T2.4 - Preserve explicit standalone-script compatibility

- Keep a separate branch for a direct `FromLlm-*.py` or `FromLlm-*.ps1` received without a ZIP.
- Stage it in `temp`, execute it once, delete it in `finally` and report the behavior clearly.
- Do not let this branch influence ZIP-associated script selection.

**Completed 2026-08-13**: standalone branch stages to temp, executes, unlinks in finally; orphan root/temp fallback removed.

### M3 - Regression tests

#### T3.1 - ZIP retention and naming tests

Validate:
- canonical timestamp insertion before `.zip`;
- names containing additional dots;
- adorned download names after normalization;
- collision suffix behavior;
- ZIP remains in history after successful and failed script runs.

**Completed 2026-08-13**: harness 17/17 PASS (naming, collision, retention + partial path validation + script discovery).

#### T3.2 - Extraction and safety tests

#### T3.2 - Extraction and safety tests

Validate:
- direct overwrite into a simulated solution;
- nested project paths;
- rejection of absolute paths;
- rejection of traversal paths;
- no destination outside the simulated solution root.

**Completed 2026-08-13**: path rejection covered by harness (absolute/traversal/nested); extract+overwrite exercised by all production ZIP runs.

#### T3.3 - Script association and cleanup tests

Validate:
- exact `.py` script from current ZIP executes;
- exact `.ps1` script from current ZIP executes when PowerShell is available;
- zero-script ZIP applies files without executing a script;
- multiple-script ZIP is rejected before extraction;
- stale scripts in `temp` are not executed;
- associated script is deleted after success;
- associated script is deleted after non-zero exit or exception;
- archived ZIP still contains the script.

**Completed 2026-08-13**: discovery 0/1/multi + delete-in-finally verified by harness and production runs (incl. failing harness run that still unlinked). .ps1 path accepted by finder; live .ps1 execute deferred if pwsh absent.

#### T3.4 - UTF-8 end-to-end regression

Validate the sample:

`è già più modalità perché € – — ✓ 🔬`

across CMD, Python, PowerShell where applicable, captured stdout/stderr and `ToLlm.txt`, with no `Ã` or replacement character `�`.

**Completed 2026-08-13**: harness PASS — encode/decode, no mojibake, file UTF-8 round-trip.

### M4 - Configurable ContextBundler output mode

#### T4.1 - Add persistent governance setting

- Add `ContextBundler_output_base64: true|false` to `SOLUTION_GOVERNANCE.md`.
- Use `true` for the current Copilot M365 primary channel.
- Missing setting defaults to `false`.
- Accept surrounding whitespace and case-insensitive Boolean values; reject invalid values explicitly.

**Completed 2026-08-13**: persistent governance setting added and independently verified; runtime resolution remains part of T4.2-T4.4.

#### T4.2 - Add session-scoped override

- Support `TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64=true|false`.
- Apply precedence: session override, governance value, default `false`.
- Propagate the override to child processes without persisting it.
- Log effective output mode and configuration source.

**Completed 2026-08-14** da qui in poi aggiorno io next_task per non fare leggere e scrivere questo file ogni volta.

#### T4.3 - Remove hardcoded Base64 behavior

- Locate every wrapper, Python script and executable invocation that forces `--base64`.
- Invoke ContextBundler with Base64 only when the effective value is `true`.
- Use native plain text when it is `false`.
- Preserve request discovery, adorned-name normalization and automatic orchestration.

#### T4.4 - Audit/Fix T4.3 & Test configuration matrix (Sessione 1)

**Target Paths**
- `.catsw-utility/process-from-llm.cmd`
- `.catsw-utility/artifacts/process-from-llm.py`
- `.catsw-utility/aaa-startup-llm-session.cmd`
- `.catsw-utility/artifacts/startup-llm-session.py`
- `SOLUTION_GOVERNANCE.md`

**Implementation Scope**
1. **Audit & Fix T4.3:** Verificare che TUTTI e 4 i file target (wrapper `.cmd` e script Python `.py`) gestiscano correttamente la risoluzione dinamica del parametro Base64 (Env `TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64` > Governance `ContextBundler_output_base64` > Default `false`) e non abbiano flag `--base64` hardcoded.
2. **Execute Test Matrix:** Eseguire e validare la matrice di configurazione completa:
   - Governance `true` / Governance `false`
   - Impostazione assente / File di governance mancante
   - Override variabile d'ambiente `true` / `false` (in entrambe le direzioni rispetto alla governance)
   - Valori non validi o spazi vuoti (tolleranza case/whitespace)
   - Propagazione ai processi figli ed ergonomia non-persistente
   - Verificare l'uso sicuro di Base64 su Copilot M365 e il plain-text su Grok, Claude Sonnet, Gemini e canali equivalenti.

#### T4.5 - Update skill guidance & Milestone Closure (Sessione 2)

**Target Paths**
- `catsw-utility/docs/skill-uso-tools.md` (e relative skill di supporto per ContextBundler / TurboAI)
- `SOLUTION_GOVERNANCE.md`
- `Piano-Multi-Task.md`

**Implementation Scope**
1. Aggiornare le skill e la documentazione guida per rimuovere l'assunzione cablata dell'output in formato Base64 per ContextBundler.
2. Documentare chiaramente nelle skill la gerarchia di precedenza dei parametri (Env Variable > Governance > Default `false`).
3. Aggiornare `Piano-Multi-Task.md` impostando il blocco `<next_task>` sulla Milestone 5 e segnare M4 come completata.

# M5 - Dynamic changelog context extraction (rework)

## Confirmed design

- `SOLUTION_GOVERNANCE.md` defines `DefaultChangeLogPath:<path relative to
  TurboAiWorkingRoot>`. This single key covers both the old "TargetProject"
  case (single project) and the "override" case that came out of TurboAI's
  own needs (Documentation/ living at the top level of the root).
- A specific task may declare `OverrideChangeLogPath=<path>` inside its own
  `<next_task>` block, next to the task header. If present, it takes
  precedence over `DefaultChangeLogPath` for that task. If absent,
  `DefaultChangeLogPath` is used.
- `TargetProject` and `MultiProject` keys are removed: there is no longer an
  indirection "resolve the active task's project, then map it to a
  changelog" — the path is declared directly, never derived.
- **Root reference for paths.** Both `DefaultChangeLogPath` and
  `OverrideChangeLogPath` are relative to **TurboAiWorkingRoot** — the
  directory one level up from the `.catsw-utility`/`.ai-context` instance
  the tool is currently running from, discovered dynamically, never
  hardcoded or derived from a fixed relative offset. This applies identically
  to the TurboAI root solution and to the ContextBundler sub-solution: each
  has its own `.catsw-utility`/`.ai-context` pair and its own
  TurboAiWorkingRoot one level above it. (See the `TurboAiWorkingRoot` skill
  definition — general, not M5-specific.)
- The 3-level fallback on the resolved changelog (Unreleased with content /
  Unreleased empty with a previous release / empty changelog) is unchanged
  from the previous design — independent of the routing mechanism.

## Reuse note: T5.1

The T5.1 assessment has already been executed under the previous design.
Its findings remain valid except for the line reporting
`TargetProject`/`MultiProject` state in `SOLUTION_GOVERNANCE.md`, which is
restated as the state of `DefaultChangeLogPath` (outcome: key absent, same
as the previous ones). Do not re-run the full assessment from scratch — see
point 4 of the rework protocol.

---

### T5.1 - Assess installed changelog and startup tools

1. Target Paths
   - `.catsw-utility/artifacts/startup-llm-session.py`
   - `.ai-context/SOLUTION_GOVERNANCE.md`
   - `Documentation/Changelog.md`
   - Discovery: search `.catsw-utility/artifacts/` for any script referencing a changelog path
     (case-insensitive match on "changelog") to catch other hardcoded lookups beyond startup-llm-session.py.

2. Context & Dependencies
   - Known bug: `startup-llm-session.py` currently passes a hardcoded changelog path to
     `extract-latest-changelog.py`. This task only documents the exact current state, it does not fix it.
   - Target design (for the tasks that follow): `SOLUTION_GOVERNANCE.md` defines `DefaultChangeLogPath`;
     an individual task's `<next_task>` block may define `OverrideChangeLogPath` taking precedence for
     that task only.
   - Changelog format in use: Keep a Changelog conventions (`[Unreleased]` section, dated releases below it).

3. Implementation Scope
   - Report the exact hardcoded changelog path found in `startup-llm-session.py`, with line number.
   - Report whether `DefaultChangeLogPath` already exists in `SOLUTION_GOVERNANCE.md`, and its current
     value if present.
   - Report the real current structure of `Documentation/Changelog.md` (presence/absence and content of
     `[Unreleased]`, most recent dated release).
   - List any other script found via the discovery search above, with its own hardcoded reference if any.
   - Make no operational changes.

4. Acceptance Criteria
   - Assessment covers all points above with exact file/line references, not paraphrase.
   - No file modified.
   - Every value that T5.2-T5.5 will need must be marked explicitly in the report, one line per value:
     - `PROPAGATE TO T5.2: exact hardcoded changelog path/line to remove = <value>`
     - `PROPAGATE TO T5.2: any other script found with a hardcoded changelog reference = <value or "none">`
     - `PROPAGATE TO T5.2: current DefaultChangeLogPath state in SOLUTION_GOVERNANCE.md = <value>`

5. Delivery Artifacts
   - Assessment report in Markdown, pasted directly in chat (no ZIP needed).
   - If reusing the prior assessment (see "Reuse note" above): a short delta note is sufficient, restating
     only the reformulated `DefaultChangeLogPath` line, not a full re-run.

6. Extra Startup Files
   - None beyond Target Paths.

---


### T5.2 - Implement default/override changelog routing

1. Target Paths
   - `.catsw-utility/artifacts/extract-latest-changelog.py` *(confirm exact path against T5.1 findings before
     starting)*
   - `.ai-context/SOLUTION_GOVERNANCE.md`
   - `[FROM T5.1: exact hardcoded changelog path/line to remove]= 
  startup-llm-session.py, riga ~168 (versione pre-patch): 
  changelog_src = repo_root / "Documentation" / "Changelog.md"`
   - `[FROM T5.1: any other script found with a hardcoded changelog reference]= none
  (rg -il changelog artifacts → solo startup-llm-session.py ed extract-latest-changelog.py,
  nessun altro file in artifacts)`

2. Context & Dependencies
   - `[FROM T5.1: current DefaultChangeLogPath state in SOLUTION_GOVERNANCE.md]= 
  assente alla lettura iniziale di questa sessione; ora impostato a "Documentation/`
   - Add `DefaultChangeLogPath=<path relative to TurboAiWorkingRoot>` to governance.
   - Resolution order: if the current task's `<next_task>` block declares `OverrideChangeLogPath`, use it;
     otherwise use `DefaultChangeLogPath`. Re-read fresh on every tool run - never cached.
   - Root resolution: TurboAiWorkingRoot is the parent directory of the currently-running
     `.catsw-utility`/`.ai-context` instance, discovered dynamically (walk up from the script's own
     location to find that pair of directories) - never a path cabled at write time or derived from a
     fixed relative offset.
   - Missing routing (no `OverrideChangeLogPath` and no `DefaultChangeLogPath` set) must be rejected
     explicitly (clear error message), never guessed or defaulted silently.

3. Implementation Scope
   - Remove the hardcoded path identified in T5.1.
   - Implement the default/override resolution logic described above.
   - Implement dynamic TurboAiWorkingRoot discovery as described above.
   - Wire the resolver into `extract-latest-changelog.py` (or the confirmed real path from T5.1).

4. Acceptance Criteria
   - Task with `OverrideChangeLogPath` set: that path is used, `DefaultChangeLogPath` ignored.
   - Task without override: `DefaultChangeLogPath` used.
   - Neither set: explicit error, no silent default.
   - TurboAiWorkingRoot correctly resolved when run from both the TurboAI root instance and the
     ContextBundler sub-solution instance (two distinct `.catsw-utility`/`.ai-context` pairs).

5. Delivery Artifacts
   - Patch ZIP with the operational script under `.catsw-utility/temp/`.

6. Extra Startup Files
   - `[FROM T5.1: any other script found with a hardcoded changelog reference]= none
  (rg -il changelog artifacts → solo startup-llm-session.py ed extract-latest-changelog.py,
  nessun altro file in artifacts)`

---

### T5.3 - Implement Keep a Changelog extraction fallback

Unchanged from the previous version: 3-level fallback (Unreleased with
content / Unreleased empty with a previous release / no content), read-only,
independent of the routing mechanism. No changes required for this rework -
carried over identically from the original plan.

---

### T5.4 - Add simulated routing and extraction tests

1. Target Paths
   - Test harness location *(confirm exact path from repo, same convention as T3.1-T3.4)*.
   - Resolver module/file delivered in T5.2 and T5.3.

2. Context & Dependencies
   - Covers default/override routing from T5.2 and the 3-level fallback from T5.3, against simulated
     governance/task fixtures - no live repository state required.

3. Implementation Scope
   - Build fixtures and assertions for: task with `OverrideChangeLogPath` uses it and ignores
     `DefaultChangeLogPath`; task without override uses `DefaultChangeLogPath`; neither set produces an
     explicit diagnostic (not a silent default); TurboAiWorkingRoot correctly resolved for both a
     root-level `.catsw-utility` instance and a nested sub-solution instance (simulated directory trees);
     populated `[Unreleased]` returns only that fragment; empty `[Unreleased]` with a previous release
     uses Level 2; new/empty changelog uses Level 3; historical releases remain untouched by extraction.

4. Acceptance Criteria
   - All cases listed above pass; no fixture mutates its source file.

5. Delivery Artifacts
   - Patch ZIP with test files under the confirmed harness location.

6. Extra Startup Files
   - None beyond Target Paths.

---
<next_task>
### T5.5 - Integrate with startup session and update governance

1. Target Paths
   - `.catsw-utility/artifacts/startup-llm-session.py`
   - `.ai-context/SOLUTION_GOVERNANCE.md`
   - `.catsw-utility/docs/skill-uso-tools.md`

2. Context & Dependencies
   - Resolver and fallback logic already implemented and tested in T5.2-T5.4; this task only wires them
     into the startup flow and closes the milestone.
   - Startup session output must stay compact: include only the resolved changelog fragment needed for
     session context, not the full changelog file.

3. Implementation Scope
   - Replace the old hardcoded changelog lookup in `startup-llm-session.py` with a call to the T5.2/T5.3
     resolver.
   - Add the `TurboAiWorkingRoot` definition (general, not M5-specific) to the general section of
     `skill-uso-tools.md`, and update the startup/skill guidance text to describe
     `DefaultChangeLogPath`/`OverrideChangeLogPath`.
   - Update `SOLUTION_GOVERNANCE.md` and `Piano-Multi-Task.md`: mark M5 complete, move `<next_task>` to
     M6/T6.1, copy forward into T6.1's `Context & Dependencies` any M5 decision that M6 depends on.
   - Record the rework itself per the rework protocol (tracked in governance/changelog, not only in the
     plan text).

4. Acceptance Criteria
   - Startup session context includes the resolved fragment only, verified against the Level 1/2/3 fixtures.
   - No hardcoded changelog path remains anywhere in the codebase (re-run the T5.1 discovery search to confirm).
   - Rework explicitly tracked in a persistent location (governance/changelog), not only in the plan.

5. Delivery Artifacts
   - Patch ZIP with all modified files.

6. Extra Startup Files
   - None beyond Target Paths.
</next_task>
---

### M6 - Previous-run artifact rotation and stale-artifact cleanup

#### T6.1 - Consolidate the rotation contract

1. Target Paths
   - `.catsw-utility/artifacts/move-to-history.py`
   - `.catsw-utility/move-to-history.cmd`

2. Context & Dependencies
   - Rotation = preventive cleanup of the *previous* run's leftover files, distinct from the ZIP-retention
     contract implemented in M1 (which archives the *current* run's ZIP, not prior leftovers).
   - `context-request-*` and `context-out-*` files from the current run must stay available until the next
     request or the next startup run - rotation must never touch the current run's own files.

3. Implementation Scope
   - Confirm/refactor `move-to-history.py` so it only rotates files belonging to a run prior to the current
     one, non-recursively.
   - Keep `move-to-history.cmd` as the manual entry point calling the same logic.

4. Acceptance Criteria
   - Current-run `context-request-*`/`context-out-*` files are never rotated by this contract.
   - Manual invocation via `move-to-history.cmd` produces the same result as the automatic path.

5. Delivery Artifacts
   - Patch ZIP with the operational script under `.catsw-utility/temp/`.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T6.2 - Add timestamped root and temp rotation

1. Target Paths
   - `.catsw-utility/artifacts/move-to-history.py` (as consolidated in T6.1 - confirm final shape from T6.1's
     delivered patch before starting)
   - `.catsw-utility/temp/`
   - `.catsw-utility/history/`

2. Context & Dependencies
   - Extends T6.1's rotation contract to also catch stray files left in the repository root
     (`context-request-*`, `context-out-*`, orphaned `FromLlm-*`) and stale `.catsw-utility/temp/FromLlm-*.py`
     / `.ps1` residues, including residues that predate the full M1-M2 ZIP/temp contract being deployed.

3. Implementation Scope
   - Archive matched root candidates and stale temp residues into `.catsw-utility/history/`.
   - Prefix every archived filename with `YYYYMMDD-HHMMSS-`.
   - On same-second collisions, append a deterministic numeric suffix; never overwrite an existing archived
     file.
   - Log source path, destination path and any failure explicitly; archive evidence rather than silently
     deleting on failure.

4. Acceptance Criteria
   - Root candidates and stale temp residues are archived with the correct prefix.
   - Same-second collisions produce distinct archived names, no overwrite.
   - A failed rotation is logged, not silently swallowed.

5. Delivery Artifacts
   - Patch ZIP with the operational script under `.catsw-utility/temp/`.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T6.3 - Centralize automatic invocation in wrappers

1. Target Paths
   - `.catsw-utility/process-from-llm.cmd`
   - `.catsw-utility/aaa-startup-llm-session.cmd`
   - `[FROM T6.2: final function name/signature of the rotation entry point]`

2. Context & Dependencies
   - Rotation logic already implemented in T6.1/T6.2; this task only wires a single call site into each
     wrapper, it does not change rotation behavior itself.
   - Must preserve the validated UTF-8 environment contract (CMD/Python/PowerShell) already in place from M3.

3. Implementation Scope
   - Invoke rotation exactly once from `process-from-llm.cmd`, before it processes the newly detected
     Downloads artifact - the new input itself must not be rotated before its normal owner takes control.
   - Invoke rotation exactly once from `aaa-startup-llm-session.cmd`, before it produces new startup context
     files.
   - Propagate any cleanup failure according to an explicit, tested policy (fail loud vs. warn-and-continue -
     decide and document which, consistent with T6.2's "archive evidence, don't delete blindly" rule).

4. Acceptance Criteria
   - Each wrapper calls rotation exactly once, at the specified point.
   - The newly detected Downloads input is never rotated before being processed.
   - UTF-8 contract unaffected (spot-check with the M3 UTF-8 sample string).

5. Delivery Artifacts
   - Patch ZIP with both wrapper files.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T6.4 - Remove duplicate Python cleanup

1. Target Paths
   - `.catsw-utility/artifacts/process-from-llm.py`
   - `.catsw-utility/artifacts/startup-llm-session.py`

2. Context & Dependencies
   - As of M1-M2, ZIP retention/temp execution owns its own input-specific archival; the internal
     `move-to-history.py` call previously embedded inside `process-from-llm.py` is now redundant with the
     wrapper-level call added in T6.3.
   - Do not conflate this preventive previous-run rotation with the current-run ZIP retention contract from
     M1 - they stay two separate mechanisms even after this cleanup.

3. Implementation Scope
   - Remove the internal `move-to-history.py` call from inside `process-from-llm.py`.
   - Inspect `startup-llm-session.py` for an equivalent internal rotation call and remove it if it is now fully
     covered by the T6.3 wrapper-level call.
   - Keep any input-specific archival that is NOT covered by M1-M2's definitive ZIP/temp contract until that
     contract is confirmed to cover it.

4. Acceptance Criteria
   - No duplicate rotation call remains inside either Python script.
   - End-to-end run still rotates exactly once per T6.3's wrapper-level call (no more, no less).

5. Delivery Artifacts
   - Patch ZIP with both modified Python files.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T6.5 - Add rotation regression tests

1. Target Paths
   - Test harness location used in T5.4 *(confirm exact path)*.
   - All files touched in T6.1-T6.4.

2. Context & Dependencies
   - Consolidates and regression-tests the full rotation contract built across T6.1-T6.4: preventive
     previous-run rotation, timestamped archival, wrapper-level single invocation, and removal of the
     duplicate internal call.

3. Implementation Scope
   - Build fixtures/assertions for: wrapper processing of a ZIP, a standalone `.py`, a standalone `.ps1`, and a
     `context-request-*` all invoke rotation exactly once; startup invokes rotation exactly once before
     generating new startup files; current-run context files remain available until the following run; root
     candidates receive timestamp prefixes; same-second collisions do not overwrite; stale temp scripts are
     archived non-recursively; unrelated temp files and nested directories are left untouched; manual
     `move-to-history.cmd` still works standalone; one failing move is reported without silent data loss;
     UTF-8 filenames and logs remain valid throughout.

4. Acceptance Criteria
   - All cases above pass.

5. Delivery Artifacts
   - Patch ZIP with test files under the confirmed harness location.

6. Extra Startup Files
   - None beyond Target Paths.

---

### M7 - Cleanup and documentation

#### T7.1 - Remove obsolete compatibility logic

1. Target Paths
   - `.catsw-utility/artifacts/process-from-llm.py`
   - `.catsw-utility/artifacts/process-zip-and-scripts-from-llm.py`
   - Discovery: search both files (and anything they import) for `archive_script(` and any other helper,
     constant or import left without callers after the ZIP-associated and standalone-script workflows were
     consolidated in M2.

2. Context & Dependencies
   - The root-script discovery path and the "newest file in temp" fallback were intermediate bootstrap
     workarounds, superseded by the exact-inventory script selection implemented in T2.1.
   - The explicit standalone-script branch (T2.4) is the only compatibility path that must be preserved.

3. Implementation Scope
   - Remove root-script discovery introduced only as an intermediate bootstrap workaround.
   - Remove the newest-file fallback for ZIP-associated scripts in `temp`.
   - Retain only the explicit standalone-script branch from T2.4.
   - Remove dead comments/log messages that still claim the script is moved into the utility root.
   - Remove `archive_script()` and any other now-uncalled function, constant or import found in the discovery
     step above.
   - Before deleting any helper, verify with a targeted search (or an AST-based call-site check) that it has
     no remaining callers.

4. Acceptance Criteria
   - No references to root-script discovery or newest-file fallback remain.
   - Standalone-script branch (T2.4 behavior) still passes its T3.3 regression tests unchanged.
   - Every removed helper is confirmed caller-free before deletion (evidence included in the delivery).

5. Delivery Artifacts
   - Patch ZIP with both modified Python files, plus a short note listing exactly what was removed and the
     caller-check evidence for each.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T7.2 - Update utility documentation and examples

1. Target Paths
   - `.catsw-utility/lab/README.md` *(only if the lab is still part of the current setup - confirm before
     editing; if it was removed, skip this file and note it in the delivery)*
   - Any other operational README/comments describing ZIP deletion or script placement in the utility root
     *(discovery: grep for "utility root" and "delete" across `.catsw-utility/`)*

2. Context & Dependencies
   - As of M1-M2, the ZIP is archived (not deleted) and the operational script runs from
     `.catsw-utility/temp/`, not from the utility root - documentation predating this change is now wrong.

3. Implementation Scope
   - Update every found README/comment to reflect archive-not-delete and temp-not-root execution.
   - Add a minimal ZIP tree example showing `.catsw-utility/temp/FromLlm-*.py`.
   - State explicitly that the archived ZIP (`.catsw-utility/history/`) is the authoritative inspection copy.

4. Acceptance Criteria
   - No remaining documentation describes ZIP deletion or utility-root script placement.

5. Delivery Artifacts
   - Patch ZIP with all updated documentation files.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T7.3 - Update future skill contract

1. Target Paths
   - ``.catsw-utility/docs/skill-uso-tools.md`

2. Context & Dependencies
   - Consolidates the operational contract from M1-M6 (ZIP retention, temp execution, Base64 configurability
     from M4, dynamic changelog from M5, rotation from M6) into forward-looking guidance for skills that
     generate future patch ZIPs.

3. Implementation Scope
   - Record for future skills: generate patch ZIPs with the operational script under `.catsw-utility/temp`;
     preserve exact internal file names and relative paths; do not create separate bootstrap/unlock scripts;
     expect automatic ZIP timestamping and preservation by the tool (no LLM-generated timestamps/run IDs);
     require automatic plan and `SOLUTION_GOVERNANCE.md` realignment at every milestone advancement and
     closure (per the Closure Checklist in FaseDefinizionePiano.md §1.3).

4. Acceptance Criteria
   - Skill file updated with all points above, consistent with the actually-implemented behavior from
     M1-M6 (not the pre-M1 behavior).

5. Delivery Artifacts
   - Patch ZIP with the updated skill file.

6. Extra Startup Files
   - None beyond Target Paths.

---

### M8 - Execution identity, execution mode and session overrides

#### T8.1 - Extend governance with execution profile

1. Target Paths
   - `.ai-context/SOLUTION_GOVERNANCE.md`
   - Governance parser/loader script *(discovery: same file(s) that already parse
     `ContextBundler_output_base64` from T4.1 - confirm exact path)*

2. Context & Dependencies
   - Adds five new governance keys, independent from `ContextBundler_output_base64` (M4) and from each other's
     resolution logic beyond precedence: `TurboAI_execution_mode` (`B_ONLY|A_PLUS_B`), `TurboAI_channel_b`,
     `TurboAI_model_b`, `TurboAI_channel_a`, `TurboAI_model_a` (the last two only meaningful in `A_PLUS_B`).

3. Implementation Scope
   - Add the five keys to the governance parser/loader.
   - Missing identity values resolve to the literal string `unspecified`.
   - Trim surrounding whitespace on all values; reject empty values, newlines and control characters
     explicitly (do not silently strip them).
   - Keep execution identity, execution mode and the M4 ContextBundler Base64 mode fully independent - no
     shared resolution code path.

4. Acceptance Criteria
   - All five keys parse correctly when present, absent, or containing rejected characters (explicit error).
   - Independence from `ContextBundler_output_base64` verified (changing one does not affect the other).

5. Delivery Artifacts
   - Patch ZIP with the parser/loader change.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T8.2 - Add session-scoped execution-profile overrides

1. Target Paths
   - Same governance parser/loader confirmed in T8.1's delivery.

2. Context & Dependencies
   - Mirrors the session-override pattern already implemented for
     `TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64` in T4.2 - same precedence style, new variable names.

3. Implementation Scope
   - Support environment overrides `TURBOAI_EXECUTION_MODE`, `TURBOAI_CHANNEL_B`, `TURBOAI_MODEL_B`,
     `TURBOAI_CHANNEL_A`, `TURBOAI_MODEL_A`.
   - Precedence: session override > governance value > `unspecified`.
   - Propagate the effective values to child processes without persisting them back to governance.
   - Log the effective value and its source (override vs. governance vs. default) for each of the five keys.

4. Acceptance Criteria
   - Each override independently verified, and all five together.
   - Child process receives the effective values; `SOLUTION_GOVERNANCE.md` is never rewritten by this.
   - Log output correctly attributes source per key.

5. Delivery Artifacts
   - Patch ZIP with the parser/loader change.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T8.3 - Add Channel B mismatch guidance

1. Target Paths
   - `[FROM T8.1: exact path of the governance parser/loader]`
   - Startup session output logic *(the same component that logs effective values in T8.2)*

2. Context & Dependencies
   - Channel B (the chat session itself) knows its own role/channel/model identity from context; this task
     lets it compare that self-knowledge against the effective configuration resolved in T8.1/T8.2.

3. Implementation Scope
   - On mismatch between Channel B's known identity/mode and the effective resolved configuration, surface a
     clear explanation of the difference and propose exact temporary PowerShell override commands (using the
     T8.2 environment variables) to fix it for the session.
   - Never modify governance silently and never execute the proposed overrides automatically - propose only.
   - Do not claim an exact model version when the hosting channel does not expose one; state "unspecified" or
     "not exposed by this channel" instead of guessing.

4. Acceptance Criteria
   - Mismatch scenario produces the explanation plus copy-pasteable override commands, no automatic action.
   - No fabricated model version ever appears in the guidance.

5. Delivery Artifacts
   - Patch ZIP with the guidance logic.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T8.4 - Preserve A+B responsibility boundaries

1. Target Paths
   - `[FROM T8.1: exact path of the governance parser/loader]`
   - Benchmark report component *(discovery: locate the file/module that currently produces the benchmark
     report, referenced by "make the execution profile available to the benchmark report" below)*

2. Context & Dependencies
   - `B_ONLY`: Channel B performs both governance and execution.
   - `A_PLUS_B`: Channel B retains governance, context acquisition, verification and closure; Channel A
     executes explicitly assigned tasks only.

3. Implementation Scope
   - Encode the two responsibility profiles above as documentation/contract, not just as data - the
     distinction must be visible wherever execution mode is consulted.
   - Make the resolved execution profile (mode + identities) available to the benchmark report without
     requiring per-message automatic logging (i.e., read on demand, not logged on every turn).

4. Acceptance Criteria
   - Benchmark report can read the current execution profile on demand.
   - No per-message automatic logging introduced.

5. Delivery Artifacts
   - Patch ZIP with the benchmark report integration.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T8.5 - Test execution-profile resolution

1. Target Paths
   - Test harness location used in T5.4/T6.5 *(confirm exact path)*.
   - All files touched in T8.1-T8.4.

2. Context & Dependencies
   - Full regression coverage for the execution-profile feature built across T8.1-T8.4.

3. Implementation Scope
   - Build fixtures/assertions for: `B_ONLY` resolution, `A_PLUS_B` resolution, governance-only values (no
     overrides), each of the five overrides applied independently, all five together, missing/invalid values
     (rejected per T8.1), child-process propagation, non-persistence to governance, mismatch guidance (T8.3),
     Channel A identity optionality in `B_ONLY`, and independence from the M4 Base64 mode.

4. Acceptance Criteria
   - All cases above pass.

5. Delivery Artifacts
   - Patch ZIP with test files under the confirmed harness location.

6. Extra Startup Files
   - None beyond Target Paths.

---

### M9 - Timestamped ToLlm snapshots

*ASSUMPTION: the original plan only stated "Add full-date snapshot naming - Keep Downloads/ToLlm.txt as the
live mutable output." The task below infers a scope consistent with that title and with the M1 archival
pattern (timestamped copies into `.catsw-utility/history/`, live file untouched). Review before use.*

#### T9.1 - Add timestamped ToLlm snapshot archival

1. Target Paths
   - `.catsw-utility/artifacts/process-from-llm.py` (or wherever `ToLlm.txt` is written - confirm exact
     write site before editing)
   - `.catsw-utility/history/`

2. Context & Dependencies
   - `Downloads/ToLlm.txt` must remain the live, mutable output consumed by the current channel - this task
     adds an archival copy alongside it, it does not change how the live file is written or consumed.
   - Follows the same timestamp-prefix and collision-handling convention established in T1.1/T6.2
     (`YYYYMMDD-HHMMSS-` prefix, deterministic numeric suffix on same-second collision, never overwrite).

3. Implementation Scope
   - After each write of `Downloads/ToLlm.txt`, copy it into `.catsw-utility/history/` with a
     `YYYYMMDD-HHMMSS-` prefixed name.
   - Apply the same collision-handling rule as T1.1/T6.2.
   - Do not alter how `Downloads/ToLlm.txt` itself is produced or consumed.

4. Acceptance Criteria
   - `Downloads/ToLlm.txt` remains live/mutable, unchanged in behavior.
   - Each write produces exactly one correctly-named, non-overwriting snapshot in history.

5. Delivery Artifacts
   - Patch ZIP with the modified write path.

6. Extra Startup Files
   - None beyond Target Paths.

---

### M10 - Optional manual significant-interaction template

#### T10.1 - Document the optional free-form log

1. Target Paths
   - New file: `.catsw-utility/history/<date>-significant-user-llm-interactions.md`
     *(note: corrects the `itereations`/`significativ` typos present in the original plan text; confirm final
     filename with the user before creating it)*

2. Context & Dependencies
   - Purely a manual, user-owned, optional artifact - not read, written or required by any operational tool.
   - The `.catsw-utility` -> `.turbo-ai` path migration is tracked separately in M11 and not yet done as of
     this task; use the `.catsw-utility` path now. If M11 completes first, this task's path must be updated to
     `.turbo-ai/history/...` before it is used - do not maintain two parallel path conventions.

3. Implementation Scope
   - Provide the agreed Markdown template for significant user-LLM interactions.
   - Document that creation/maintenance is entirely manual and user-owned.
   - Document the exclusions: routine "go" approvals, normal attachments, ordinary workflow transitions are
     not logged here.
   - State explicitly that this file is optional for normal consumer solutions.

4. Acceptance Criteria
   - Template documented with the corrected filename convention and the M11 path-dependency note above.

5. Delivery Artifacts
   - Documentation file (Markdown), delivered directly, no ZIP required.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T10.2 - Keep all operational tools independent from the log

1. Target Paths
   - Discovery: search all operational components (`.catsw-utility/artifacts/`, wrapper `.cmd` files,
     rotation, ContextBundler invocation points) for any reference to the filename pattern from T10.1.

2. Context & Dependencies
   - The log from T10.1 must remain purely manual/user-owned; no operational tool may depend on its presence,
     absence or content.

3. Implementation Scope
   - Confirm (or fix, if found) that the watcher, startup session, ContextBundler invocation, rotation and
     FromLlm processing never create, update, parse, count or classify this file.
   - Confirm absence of the file never produces a warning or alters normal behavior.
   - Confirm any existing instance of the file is preserved untouched as user-owned evidence (rotation must
     not archive/delete it as if it were a stale artifact).
   - Benchmark-specific analysis of this file's content, if any, belongs exclusively to a separate TurboAI
     Benchmark solution - not to any tool in this repository.

4. Acceptance Criteria
   - No operational tool touches the file in any way, confirmed by the discovery search above.

5. Delivery Artifacts
   - If no fix was needed: a short confirmation report. If a fix was needed: patch ZIP plus the report.

6. Extra Startup Files
   - None beyond Target Paths.

---

#### T10.3 - Verify non-interference

1. Target Paths
   - Test harness location used in T8.5 *(confirm exact path)*.
   - All components confirmed/touched in T10.2.

2. Context & Dependencies
   - Regression coverage for the independence guarantee established in T10.2.

3. Implementation Scope
   - Test normal workflows with the T10.1 file absent, present, and present-but-malformed (arbitrary free-form
     text).
   - Confirm no operational tool opens or rewrites it in any of the three states.
   - Confirm rotation (M6) and the M11 path migration, when it happens, preserve the file according to the
     documented history policy from T10.1.

4. Acceptance Criteria
   - All three states pass with zero operational-tool interaction with the file.

5. Delivery Artifacts
   - Patch ZIP with test files under the confirmed harness location.

6. Extra Startup Files
   - None beyond Target Paths.

---

### M11 - Migrate the operational folder to .turbo-ai

*ASSUMPTION: the original plan only stated "Assess the full rename impact - Inventory executable and tracked
operational references to .catsw-utility." Expanded below as a discovery/assessment task consistent with the
M0/T5.1 pattern. This milestone likely needs a second implementation task after this one (not yet planned) -
flagged at the end.*

#### T11.1 - Assess the full rename impact

1. Target Paths
   - Discovery: search the entire repository (tracked files and, separately, executable-only references such
     as strings inside compiled/packaged artifacts if any) for the literal string `.catsw-utility`.

2. Context & Dependencies
   - Goal of the milestone: rename the operational folder from `.catsw-utility` to `.turbo-ai` across the
     whole toolchain, without breaking any in-flight ZIP, history archive, or governance reference.
   - This task only inventories; it must not rename or move anything.

3. Implementation Scope
   - List every tracked file referencing `.catsw-utility` (path literal or substring), grouped by component
     (wrappers, Python scripts, governance, documentation, skill files, test fixtures).
   - Separately list any reference baked into non-source artifacts (e.g. compiled executables, if
     ContextBundler or similar embed the path as a string).
   - Flag references inside already-archived history files (`.catsw-utility/history/...`) as out of scope for
     renaming - historical archives keep their original path as a record, only forward-looking code/config
     gets renamed.

4. Acceptance Criteria
   - Inventory is exhaustive for tracked files (verified via repository-wide search, not sampling).
   - Historical/archived references explicitly separated from active ones needing a rename.

5. Delivery Artifacts
   - Assessment report in Markdown, pasted in chat (no ZIP needed).

6. Extra Startup Files
   - None beyond Target Paths.

*Note: this milestone as originally scoped only covers assessment. A follow-up implementation task
(T11.2, not yet defined) will be needed to actually perform the rename once T11.1's inventory exists - add it
before T11.1 is closed, per the Closure Checklist.*

---

### M12 - Final verification and closure

*ASSUMPTION: the original plan only stated "Execute production workflows." Expanded below as a final
end-to-end smoke test consistent with the milestone title "Final verification and closure". Review before
use.*

#### T12.1 - Real workflow smoke test

1. Target Paths
   - All wrappers and scripts under `.catsw-utility/` (or `.turbo-ai/` if M11 has completed by this point -
     confirm current state before starting).
   - `.ai-context/SOLUTION_GOVERNANCE.md`

2. Context & Dependencies
   - This is the closing verification for the entire initiative (M0-M11): ZIP retention, temp execution,
     Base64 configurability, dynamic changelog, rotation, cleanup/documentation, execution profile, ToLlm
     snapshots, the optional interaction log, and the folder migration if completed.

3. Implementation Scope
   - Run a real (not simulated) end-to-end cycle: produce a genuine patch ZIP, let the watcher/orchestrator
     process it, confirm archival, execution, and cleanup all behave as specified across M1-M11.
   - Run a real startup session and confirm the dynamic changelog fragment (M5) and rotation (M6) both fire
     correctly.
   - Confirm UTF-8 end-to-end with the M3 sample string in a live run, not just the test harness.

4. Acceptance Criteria
   - One full live cycle completes with no manual workaround needed anywhere in the chain.

5. Delivery Artifacts
   - Execution report (Markdown) documenting each step observed, pasted in chat.

6. Extra Startup Files
   - None beyond Target Paths.

---

### M13 - Per-task extra-files declaration in the plan

**Note before rewriting this milestone: its purpose is now largely satisfied by FaseDefinizionePiano.md §1.2,
section 6 ("Extra Startup Files"), already added to the plan-authoring standard itself. Consider whether M13
is still needed as a separate implementation milestone, or whether it should be moved right after M0 instead
of running last - the whole point of this milestone is to give every other task a way to declare its own
extra context files, which would have helped M5-M12 above if it existed already. Left as the last milestone
below only because that was its original position; recommend moving it, not implementing it here.**

#### T13.1 - Per-task extra-files declaration mechanism

1. Target Paths
   - `.catsw-utility/artifacts/startup-llm-session.py` (or wherever the start-session bundle is assembled)
   - `Piano-Multi-Task.md` (the plan template itself)

2. Context & Dependencies
   - Each task in the plan may declare, under its own "Extra Startup Files" section (see
     FaseDefinizionePiano.md §1.2), a list of files to attach automatically at session start for that specific
     task, on top of the standard defaults (`SOLUTION_GOVERNANCE.md`, etc.).

3. Implementation Scope
   - Make the start-session bundler read the "Extra Startup Files" list from the currently active
     `<next_task>` block and attach exactly those files, in addition to the standard defaults.
   - Tasks with an empty/absent list get only the standard defaults, unchanged from current behavior.

4. Acceptance Criteria
   - A task declaring extra files receives exactly those files plus standard defaults at session start.
   - A task without the section behaves exactly as today.

5. Delivery Artifacts
   - Patch ZIP with the bundler change.

6. Extra Startup Files
   - None beyond Target Paths.

---

## Note on original §5/§6 (Delivery Rules / Resume Checklist)

Unchanged in substance, but §5's rule "Place the single operational verifier inside `.catsw-utility/temp` in
every new patch ZIP generated after T2.1" and §6's references to `.catsw-utility` will both need a one-line
update once M11 (folder migration) completes - add that as an explicit follow-up in M11's closure, per the
Closure Checklist, so it is not forgotten.

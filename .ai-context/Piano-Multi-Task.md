---
title: Piano Multi-Task TurboAI - FromLlm ZIP retention and temp execution
solution: TurboAI
release_target: TurboAI utility toolchain v1.1
as_of: 2026-08-13
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

<next_task>
#### T4.1 - Add persistent governance setting

- Add `ContextBundler_output_base64: true|false` to `SOLUTION_GOVERNANCE.md`.
- Use `true` for the current Copilot M365 primary channel.
- Missing setting defaults to `false`.
- Accept surrounding whitespace and case-insensitive Boolean values; reject invalid values explicitly.

</next_task>
#### T4.2 - Add session-scoped override

- Support `TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64=true|false`.
- Apply precedence: session override, governance value, default `false`.
- Propagate the override to child processes without persisting it.
- Log effective output mode and configuration source.

#### T4.3 - Remove hardcoded Base64 behavior

- Locate every wrapper, Python script and executable invocation that forces `--base64`.
- Invoke ContextBundler with Base64 only when the effective value is `true`.
- Use native plain text when it is `false`.
- Preserve request discovery, adorned-name normalization and automatic orchestration.

#### T4.4 - Test configuration matrix

Validate governance `true`/`false`, missing setting, both override directions, absent override, invalid values, missing governance, whitespace/case tolerance, child propagation, non-persistence, diagnostic source, Copilot M365 Base64 safety and plain-text use on Grok, Claude Sonnet, Gemini and equivalent channels.

#### T4.5 - Update skill guidance

- Standard and legacy skills must not assume Base64 universally.
- Document effective resolution as override, governance, default.
- Keep Base64 as channel mitigation and plain text as the default.

### M5 - Dynamic changelog context extraction

#### T5.1 - Assess installed changelog and startup tools

- Read the current real `info_changelog`, startup-session integration, governance parser and related tests.
- Identify hardcoded changelog paths and the current startup output contract.
- Confirm exact governance keys, active-task target syntax and real path casing before implementation.
- Record the minimal change map without reconstructing from the historical plan alone.

#### T5.2 - Implement mono-project and multi-project routing

- Add or consolidate `TargetProject` and `MultiProject` governance support.
- Mono-project mode uses `TargetProject` directly.
- Multi-project mode derives the target from the sole active `` block.
- Route test-project work to the associated main-project changelog.
- Reject missing or ambiguous routing explicitly; never select a project arbitrarily.
- Resolve the changelog using the repository's verified `Documentation/Changelog.md` convention.

#### T5.3 - Implement Keep a Changelog extraction fallback

- Level 1: return populated `[Unreleased]` content.
- Level 2: when `[Unreleased]` is empty, return the latest release and state that `[Unreleased]` is empty.
- Level 3: when neither content nor a previous release exists, return `Nessun contenuto preesistente o release precedente trovata`.
- Preserve the source file and avoid rewriting the changelog.

#### T5.4 - Add simulated routing and extraction tests

Validate at least:
- multi-project solution selects the project declared by the active task;
- mono-project solution uses governance `TargetProject` and ignores task routing;
- populated `[Unreleased]` returns only the intended fragment;
- empty `[Unreleased]` with previous release uses Level 2;
- new or empty changelog uses Level 3;
- missing changelog, missing task target and ambiguous project mapping produce explicit diagnostics;
- test-project mapping resolves to the main-project changelog;
- historical releases remain untouched.

#### T5.5 - Integrate with startup session and update governance

- Replace hardcoded changelog lookup in startup-session flow with the dynamic resolver.
- Include only the selected changelog fragment needed for session context.
- Keep output compact to reduce token consumption.
- Update skill and startup guidance without adding AI workflow content to product documentation.
- Align plan and `SOLUTION_GOVERNANCE.md` when the milestone closes.

### M6 - Previous-run artifact rotation and stale-artifact cleanup

#### T6.1 - Consolidate the rotation contract

- Treat `move-to-history.py` as preventive cleanup for the previous run.
- Keep current `context-request-*` and `context-out-*` files available until the next request or startup run.
- Keep `move-to-history.cmd` as the manual cleanup entry point.
- Make rotation non-recursive and independent from current-input ownership.

#### T6.2 - Add timestamped root and temp rotation

- Archive root `context-request-*`, `context-out-*` and orphaned `FromLlm-*` files.
- Support stale `.catsw-utility/temp/FromLlm-*.py` and `.ps1` residues immediately, even before normal temp usage is fully deployed.
- Prefix every archived name with `YYYYMMDD-HHMMSS-`.
- Resolve same-second collisions with deterministic numeric suffixes and never overwrite.
- Log source area, destination and failures; archive evidence rather than deleting it blindly.

#### T6.3 - Centralize automatic invocation in wrappers

- Invoke rotation once from `process-from-llm.cmd` before processing the newly detected Downloads artifact.
- Invoke rotation once from `aaa-startup-llm-session.cmd` before producing new startup context files.
- Preserve UTF-8 environment and propagate cleanup failure according to an explicitly tested policy.
- Do not rotate the newly detected Downloads input before its normal owner takes control.

#### T6.4 - Remove duplicate Python cleanup

- Remove the internal `move-to-history.py` call from `process-from-llm.py`.
- Inspect and remove equivalent previous-context rotation from `startup-llm-session.py` when covered by the wrapper call.
- Keep input-specific archival in the owning workflow until M1-M2 replace it with the definitive ZIP/temp contract.
- Avoid conflating preventive previous-run rotation with current-run ZIP retention.

#### T6.5 - Add rotation regression tests

Validate:
- wrapper processing of ZIP, standalone `.py`, standalone `.ps1` and `context-request-*` invokes rotation once;
- startup invokes rotation once before generating new startup files;
- current context files remain available until the following run;
- root candidates receive timestamp prefixes;
- same-second collisions do not overwrite;
- stale temp scripts are archived non-recursively;
- unrelated temp files and nested directories are untouched;
- manual `move-to-history.cmd` remains functional;
- one failing move is reported without silent data loss;
- UTF-8 filenames and logs remain valid.

### M7 - Cleanup and documentation

#### T7.1 - Remove obsolete compatibility logic

- Remove root-script discovery introduced only as an intermediate bootstrap workaround.
- Remove newest-file fallback for ZIP-associated scripts in `temp`.
- Retain only the explicit standalone-script branch.
- Remove dead comments and misleading log messages that still say the script is moved into the utility root.

#### T7.2 - Update utility documentation and examples

- Update `.catsw-utility/lab/README.md` if the lab remains documented.
- Update any operational README or comments that describe ZIP deletion or script placement in the utility root.
- Add a minimal ZIP tree example showing `.catsw-utility/temp/FromLlm-*.py`.
- State that the archived ZIP is the authoritative inspection copy.

#### T7.3 - Update future skill contract

Record for the improved skills:
- generate patch ZIPs with the operational script under `.catsw-utility/temp`;
- preserve exact internal file names and relative paths;
- do not create separate bootstrap or unlock scripts;
- expect automatic ZIP timestamping and preservation by the tool;
- require automatic plan and `SOLUTION_GOVERNANCE.md` realignment at every advancement and closure.

### M8 - Final verification and closure

#### T8.1 - Real workflow smoke test

- Execute a real synthetic ZIP through the production entry point.
- Confirm the ZIP is renamed and preserved in history.
- Confirm files are extracted to the intended simulated or controlled solution paths.
- Confirm the exact ZIP-associated script runs from `temp` and is deleted.
- Confirm stale `temp` scripts are untouched.
- Confirm Unicode output is preserved.

#### T8.2 - Closure and recovery-state alignment

- Update this plan frontmatter to `status: COMPLETED`.
- Move `` to `T42 - Piano Completato`.
- Update `.ai-context/SOLUTION_GOVERNANCE.md` to mark the initiative completed and historical.
- Remove active-only startup obligations while preserving permanent rules and the definitive ZIP contract.
- Confirm a new session can determine the completed state without additional user memory.

### M9 - Per-task extra context files and skill addendum (start session)
#### T9.1 - Per-task extra-files declaration in the plan
- Add a per-task field/section (near "next step") listing extra files to attach automatically at start session.
- Update the start-session tool to read the declared extra files for the current `` and attach them alongside the standard startup bundle.
- Tasks that declare no extra files keep the current standard startup behavior unchanged.

#### T9.2 - Prototype minimal skill addendum
- Design the simplest possible skill-addendum file: channel/LLM-specific overrides layered on top of the base skill, ignored when a different model is active in the session.
- Scope the first prototype to a single concrete case only (e.g. whether to attach aggregated list-files output by default on flat/unlimited channels), not a general mechanism.
- Test the prototype in TurboAI Lab before touching the production skill or tool.

#### T9.3 - Evaluate and refine
- Assess the prototype's real effect on token usage and session behavior across at least the Canale B free-tier and Canale B flat scenarios.
- Decide whether to extend the addendum mechanism to other per-channel customizations (e.g. known model-specific workarounds) or keep it scoped to the single case validated in T9.2.

## 5. Delivery Rules for This Initiative

- Work incrementally and request at most three exact-path files at a time.
- Diagnose before modifying.
- Deliver complete files, preserving their original names.
- Deliver operational changes as one ZIP.
- Place the single operational verifier inside `.catsw-utility/temp` in every new patch ZIP generated after T2.1.
- Until T2.1 is installed, a compatibility delivery may use the currently supported bootstrap path only when strictly necessary and must state why.
- After each ZIP link write `Allega ToLlm` on a separate line.
- Ignore Git unless the active task explicitly requests it.

## 6. Resume Checklist

At the start of a new session:

1. Read `.ai-context/SOLUTION_GOVERNANCE.md`.
2. Read this file.
3. Locate the only `` block.
4. Request the exact real files listed by that task if they are not already attached.
5. Do not repeat completed mojibake diagnosis or earlier ReportGenerator work.
6. Continue with the smallest verifiable step.

##### T42 - Piano Completato
- The implementation, regressions, documentation and governance alignment are complete.
- Ask the user to create or activate a new execution plan.



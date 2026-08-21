---
title: Piano Multi-Task TurboAI - FromLlm ZIP retention and temp execution
solution: TurboAI
release_target: TurboAI utility toolchain v3.0
updated: 2026-08-20
status: IN_PROGRESS
workflow: TDM 1.0
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

---

### M6 - Previous-run artifact rotation and stale-artifact cleanup

#### T6.1 - Consolidate the rotation contract

TickTack.cmd:

- Rimuovere del /q "%DEST_DIR%ToLlm_*.txt". Eseguire solo la copia verso .catsw-utility/ToLlm_HHMMSS.txt.

move-to-history.py:

- Includere i file ToLlm_*.txt presenti nella radice di .catsw-utility/.
- Determinare il file ToLlm_*.txt più recente tramite os.path.getmtime e preservarlo.
- Ruotare tutti gli altri ToLlm_*.txt antecedenti.
- Per T6.1, mantenere lo spostamento base (gestione collisione _n.ext se il nome esiste già in history/).

---

#### T6.2 - Add timestamped root and temp rotation

1. **Target Paths**
* `.catsw-utility/artifacts/move-to-history.py`
* `.catsw-utility/temp/`
* `.catsw-utility/history/`


2. **Context & Dependencies**
* Estende il contratto di rotazione consolidato in T6.1 per includere tutti i residui di radice (`context-request-*`, `context-out-*`, `ToLlm_*` / `*-ToLlm.txt`) e le componenti temporanee in `.catsw-utility/temp/` (es. script `FromLlm-*.py` / `.ps1` orfani da sessioni fallite).
* **Validazione Ciclo di Vita**: Poiché `move-to-history.py` viene invocato sempre **all'inizio** dei flussi (`startup-llm-session.py` e `process-from-llm.cmd`), gli unici file presenti durante l'esecuzione sono per definizione i residui del giro precedente e possono essere ruotati in sicurezza.
* Il file `ToLlm` attivo e i file temporanei della sessione corrente generati dai flussi successivi sono preservati automaticamente dall'ordine di invocazione e dal blocco `finally` di `process-from-llm.py`.


3. **Implementation Scope**
* Scansionare non ricorsivamente la radice di `.catsw-utility/` e la directory `.catsw-utility/temp/`.
* Archiviere i file candidati in `.catsw-utility/history/` applicando il prefisso timestamp `YYYYMMDD-HHMMSS-` al nome originale.
* **Gestione Collisioni**: Se la combinazione `<TIMESTAMP>-<NOME_ORIGINALE>` esiste già in `history/`, appendere un suffisso numerico progressivo (`_1`, `_2`) prima dell'estensione. Mai sovrascrivere un file esistente.
* **Resilienza**: Intercettare eventuali eccezioni di I/O (file bloccati, permessi) registrando l'errore a log senza interrompere l'archiviazione degli altri elementi.


4. **Acceptance Criteria**
* I file orfani in root e in `temp/` vengono archiviati in `history/` con il prefisso `YYYYMMDD-HHMMSS-`.
* In caso di collisione nello stesso secondo, vengono generati nomi distinti senza sovrascritture.
* Nessun file del giro corrente viene toccato dall'archiviazione.
* Eventuali errori di spostamento vengono loggati e non ignorati silenziosamente.


5. **Delivery Artifacts**
* Script `move-to-history.py` (v1.2) e relative patch distribuite sotto `.catsw-utility/temp/`.


6. **Extra Startup Files**
* Nessuno oltre ai Target Paths.

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

- Allineamento: L'entry point ufficiale resta il wrapper move-to-history.cmd (che invoca lo script artifacts/move-to-history.py v1.1). I wrapper principali (aaa-startup-llm-session.cmd e process-from-llm.cmd) invocheranno direttamente questo .cmd.  
- Allineamento: La scelta corretta è Warn-and-Continue. Se move-to-history.py riscontra un errore di I/O (es. file bloccato), restituisce exit code 1 e logga l'errore a schermo, ma i wrapper CMD catturano il codice, mostrano un avviso [WARNING] ed eseguono comunque lo step successivo senza interrompere la sessione dell'utente.

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

- Allineamento: Perfettamente coerente. startup-llm-session.py non esegue più lo Step 1 interno, delegando l'operazione al relativo wrapper CMD aaa-startup-llm-session.cmd.

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

- Allineamento: I test andranno collocati sotto la directory standard .catsw-utility/tests/.

---

### ME6 Estemporanea Su Chat - completare supporto canale C 

#### ME6.1 completare integrazione in turbo-ai

  - Bisogna estendere il comportamento di from-llm-watcher per gestire i file che arrivano in Download con nome del tipo FromC-descrizione.py
    - from-llm-watcher sposta tale script da Download in `.catsw-utility/temp`  e lo esegue (questo già lo fa per gli script con nome FromLlm-descrizione.py) ma dopo l'esecuzione, che avrà come conseguenza la generazione in .catsw-utility di un file context-out-descrizione.md, dovrà: 
    - chiamare process-c-channel.cmd (questo prende il file context-out-descrizione.md genrato prima e ne ricava un file FromLlm-descrizione-zip che verrà in seguito processato, come da prassi, da from-llm-watcher)
    - chiamare move-to-history (che deve essere aggiornato per spostare anche i file FromC-*.py da `.catsw-utility/temp` in `.catsw-utility/history`)
  - far testare all'utente, su chat Gemini con watcher modificato se tutto funziona, e farsi dare feedback, eventualmente correggere problemi

#### ME6.2 aggiorna skill canale c 

1. Target Paths
  - `.catsw-utility/docs/tool-skillsets/skill-tools-use-channels-c_en.md`

2. Context & Dependencies
 - `[FROM ME6.1 descrizione_operativita_canale_c = <value>]=`
 
5. Delivery Artifacts 
  - aggiornare le skill canele c (`.catsw-utility/docs/tool-skillsets/skill-tools-use-channels-c_en.md`) per far dire nella chat dal llm che l'utente deve 

#### ME6.3 aggiorna skill canale c e documentazione turbo-ai relativa

1. Target Paths
  - `.catsw-utility/docs/tool-skillsets/skill-tools-use-channels-c_en.md`
  - `.catsw-utility/Readme.md`
  - `.catsw-utility/docs/TurboAI.md`

2. Context & Dependencies
 - `[FROM NewT7.2 descrizione_operativita_canale_c = <value>]=`
 
5. Delivery Artifacts 
  - aggiornare la documentazione di turbo-ai per descrivere la nuova modalità di lavoro con il canale C (documenti `.catsw-utility/Readme.md` e `.catsw-utility/docs/TurboAI.md`)
  
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
   
##### ESITO

**Fatto secondo spec**: rimossa `archive_script()` da
`process-zip-and-scripts-from-llm.py` (dead code, zero chiamanti verificati).
Nessun residuo di root-script discovery o fallback "newest-file" trovato —
già rimossi in una milestone precedente.

**Extra rispetto alla spec (lavoro estemporaneo emerso in sessione)**:
- `process-from-llm.py` v1.8: aggiunto log del contenuto del context-request
  in ToLlm.txt prima dell'esecuzione di ContextBundler.exe (che lo
  consuma/sposta da Downloads), per mantenerne visibilità nel log anche dopo.
- Adottato nuovo standard header script: rimossi i commenti changelog
  inline (`# T-x.y: ...`); restano solo copyright, licenza, versione/data.
  Il changelog per-task da ora si traccia qui nel piano (sezione ESITO di
  ogni task), non più nei commenti del codice.

**Verifica**: nessuna suite di regressione automatica ancora disponibile
(ToolsTests/UnitTests in costruzione separata); regressione verificata via
dogfooding — uso continuativo di TurboAI su se stesso.

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

### M8 - Migrate the operational folder to .turbo-ai

*ASSUMPTION: the original plan only stated "Assess the full rename impact - Inventory executable and tracked
operational references to .catsw-utility." Expanded below as a discovery/assessment task consistent with the
M0/T5.1 pattern. This milestone likely needs a second implementation task after this one (not yet planned) -
flagged at the end.*

#### T8.1 - Assess the full rename impact

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

PROPAGATE TO T8.2:
  - Root .catsw-utility → rename + aggiornamento stringhe interne
  - Nested (ContextBundler, ToolsTests, TurboAI-Benchmark): delete + replace con copia già convertita (dopo test root)
  - Changelog.md: solo delta M8, storia precedente intatta
  - skill-uso-tools.md: delete + rigenera via switch-skill.cmd dopo update tool-skillsets
  - .gitignore: add .turbo-ai patterns subito; remove .catsw-utility patterns solo a fine conversione

---
<next_task>
### T8.1_Estemporaneo - ContextBundler: session directive block + appsettings.json

1. Target Paths
   - Discovery in `C:\Repo\CatSW\TurboAI\Tools\ContextBundler\` (progetto: `ContextBundler\ContextBundler.csproj`)
   - rg mirato per:
     - individuare dove viene assemblato/scritto l'output finale del bundle (es. cercare la stringa letterale che emette l'header `# CONTEXT BUNDLE` / `BundleFormatVersion`, o il footer `<<<END FILE>>>`, per risalire alla classe/metodo responsabile)
     - verificare se esiste già un meccanismo di configurazione (cercare "appsettings", "IConfiguration", "*.json" nel progetto) per allinearsi a una convenzione esistente invece di introdurne una parallela
   - `.ai-context/SOLUTION_GOVERNANCE.md` (per un'eventuale voce di governance su questa nuova personalizzazione, se pertinente)

2. Context & Dependencies
   - Nato dagli episodi 20-21/8: istruzioni operative sepolte nel corpo del bundle (dentro skill/governance) vengono applicate meno affidabilmente di un'istruzione posta in fondo al turno. Letteratura "lost in the middle" (ricerca 21/8) conferma: le posizioni di inizio/fine pesano più del centro nell'attenzione del modello, e per istruzioni d'azione la posizione più vicina al punto di generazione (fine del contesto) è la più efficace.
   - **Vincolo esplicito (21/8):** il blocco va emesso **solo** quando la sorgente è una `context-request-start-session-*.md` — mai per una `context-request-<descrizione>.md` generica intra-sessione, dove aggiungerebbe rumore/token senza motivo (l'utente è già in flusso operativo, non serve un imperativo di "leggi tutto e agisci").
   - Il discriminante è il nome del file di request in input (prefisso `start-session` vs altro) - verificare in discovery come/dove il tool già distingue (se lo fa) le due modalità di generazione, per riusare quel branch invece di introdurne uno nuovo parallelo.
   - Blocco direttivo di default (inglese per coerenza con skill-uso-tools.md):
```xml
     <session_directive>
     Read this bundle's governance, the active plan's <next_task> block, and the attached skill in full before asking for anything else.
     If the state is clear (no material contradiction), proceed directly per the skill contract - do not wait for a "go" or ask for confirmation.
     If something is missing or genuinely ambiguous, name the exact missing value or decision and request only that.
     </session_directive>
```
   - Va emesso **in coda al bundle**, dopo l'ultimo `<<<END FILE>>>`, separato da riga vuota - non dentro il blocco di commenti `#` di intestazione (letto come metadato/contesto, non come istruzione - osservato 21/8).
   - `appsettings.json`: permette di abilitare/disabilitare il blocco e di modificarne il testo senza dover ricompilare il tool. Se assente al primo avvio, ContextBundler lo crea con il testo e lo stato di default.

3. Implementation Scope
   - Individuare via discovery il punto esatto nel codice dove viene scritto l'output finale del bundle, e dove/come il tool distingue una request di tipo start-session da una generica.
   - Iniettare l'emissione del blocco `<session_directive>` **solo nel branch start-session**, con stato e testo letti da configurazione.
   - Gestione `appsettings.json`:
     - Path accanto a eseguibile/progetto (confermare in discovery se esiste già altra convenzione nel progetto).
     - Schema configurazione:
       - `Enabled` (`bool`): abilita/disabilita l'emissione.
       - `DirectiveLines` (`string[]` / array di righe): contiene il testo della direttiva per facilitare l'editing multi-riga nel JSON senza problemi di escaping dei newline.
     - Se `appsettings.json` è assente al lancio, crearlo popolato con i default operativi (`Enabled: true` + testo standard sopra espresso come array di righe).
     - Rete di sicurezza (Fallback): se il file JSON manca, è malformato o il nodo del testo è vuoto, il tool utilizza come fallback il testo cablato nel codice.

4. Acceptance Criteria
   - Un bundle generato da `context-request-start-session-*.md` contiene `<session_directive>` in coda, dopo l'ultimo `<<<END FILE>>>`, ben separato dal resto.
   - Un bundle generato da una `context-request-<descrizione>.md` generica **non** contiene il blocco.
   - Modifica del testo in `appsettings.json`: l'output generato riflette immediatamente il nuovo testo configurato senza richiedere ricompilazione del tool.
   - `appsettings.json` assente: il tool crea il file con i default funzionanti ed emette il blocco regolarmente.
   - `appsettings.json` con direttiva disabilitata (`Enabled: false`): il blocco non viene emesso in nessun caso, nemmeno per start-session.
   - Fallback: in assenza di configurazione valida del testo, il tool emette il testo cablato di default senza fallire.
   - Nessuna regressione sul formato bundle esistente (delimitatori, escaping, header) - verificata con un run reale su entrambi i tipi di request.

5. Delivery Artifacts
   - Patch ZIP con i sorgenti C# modificati/aggiunti e l'`appsettings.json` di default.
   - Nota nel delivery su dove si trova il punto di iniezione trovato via discovery e perché.

6. Extra Startup Files
   - `ContextBundler.csproj` e i sorgenti sotto `Tools\ContextBundler\ContextBundler\` rilevanti al punto di iniezione trovato e al meccanismo di distinzione start-session/generica (da richiedere via context-request dopo la discovery, se non già nello startup bundle).

---

### T8.1.2_Estemporaneo - Gestione info start session in folder separato

1. Target Paths
   - Solution Root: `C:\Repo\CatSW\TurboAI\`
   - Utility & Automation Scripts: `C:\Repo\CatSW\TurboAI\.catsw-utility\` (es. `.catsw-utility\artifacts\extract-next-task.py` e script correlati)
   - Tool C#: `C:\Repo\CatSW\TurboAI\Tools\ContextBundler\` (progetto: `ContextBundler\ContextBundler.csproj`)
   - Nuova cartella di destinazione: `.ai-context/info_start_session/`

2. Context & Dependencies
   - Attualmente i tre file generati all'inizio di ogni sessione (`info_git.txt`, `info_Changelog.md`, `info_next_task.md`) vengono creati direttamente nella radice della cartella `.ai-context/`.
   - **Obiettivo:** Isolare questi file temporanei di sessione nella sottocartella dedicata `.ai-context/info_start_session/` per ridurre il disordine visivo nella radice di `.ai-context/`.
   - **Workflow e ciclo di vita:** Il funzionamento e l'utilità dei file restano invariati; continuano ad essere sovrascritti ad ogni inizio sessione e ad essere usati sia come contesto per l'LLM sia per la verifica/ispezione manuale da parte dell'utente.
   - Nessuna pulizia o cancellazione automatica dei vecchi file è richiesta dal task: si tratta esclusivamente di un cambio di percorso di lettura e scrittura.

3. Implementation Scope
   - **Discovery tramite `rg`:**
     - Eseguire una ricerca mirata con `rg` su tutta la repository (in particolare sotto `.catsw-utility` e `Tools/ContextBundler`) per individuare tutti gli script, file C# e documentazione che referenziano `info_git`, `info_Changelog`, `info_next_task` o il pattern `info_*.md`.
     - Verificare tra i risultati sia i punti di generazione/scrittura (es. `extract-next-task.py`) sia i punti di lettura/inclusione.
   - **Aggiornamento Script di Generazione:**
     - Modificare i percorsi di output degli script affinché scrivano i file in `.ai-context/info_start_session/`.
     - Assicurarsi che gli script verifichino l'esistenza della sottocartella `info_start_session` e la creino automaticamente se assente prima della scrittura.
   - **Aggiornamento ContextBundler (C#):**
     - Aggiornare il codice C# di `ContextBundler` per cercare e leggere i tre file `info_*.md` dal nuovo percorso `.ai-context/info_start_session/` durante l'assemblaggio del bundle di start session.
     - Garantire la creazione automatica della directory se assente al momento della risoluzione dei path.
   - **Aggiornamento Documentazione/Skill:**
     - Aggiornare eventuali riferimenti ai percorsi dei file `info_*.md` presenti nei file Markdown di documentazione o skill individuati via discovery.

4. Acceptance Criteria
   - Esecuzione degli script di avvio sessione: i tre file `info_git.txt`, `info_Changelog.md` e `info_next_task.md` vengono generati correttamente all'interno di `.ai-context/info_start_session/`.
   - Se la directory `.ai-context/info_start_session/` non esiste, viene creata automaticamente senza sollevare errori.
   - Un bundle generato per `start-session` da `ContextBundler` include i tre file leggendoli dal nuovo percorso `.ai-context/info_start_session/`.
   - Nessun errore o regressione durante il flusso di avvio sessione e generazione bundle.

5. Delivery Artifacts
   - Patch ZIP con i file di script (`.py`, `.ps1`, `.cmd`), sorgenti C# di `ContextBundler` e documentazione modificati.
   - Nota nel delivery con l'elenco completo dei file individuati tramite `rg` e aggiornati.

6. Extra Startup Files
   - `.catsw-utility/artifacts/extract-next-task.py` e gli altri script di generazione/utility emersi dalla discovery.
   - `ContextBundler.csproj` e i relativi file sorgente C# coinvolti nella lettura dei file di inizio sessione.
   </next_task>
---

#### T8.2 - switch to .turbo-ai

FROM TO T8.1:
  - Root .catsw-utility → rename + aggiornamento stringhe interne
  - Nested (ContextBundler, ToolsTests, TurboAI-Benchmark): delete + replace con copia già convertita (dopo test root)
  - Changelog.md: solo delta M8, storia precedente intatta
  - skill-uso-tools.md: delete + rigenera via switch-skill.cmd dopo update tool-skillsets
  - .gitignore: add .turbo-ai patterns subito; remove .catsw-utility patterns solo a fine conversione
  
1. Target Paths
 FROM T8.1 Assesment report all the files to be updated from `.catsw-utility` to `.turbo-ai` 
 Se non fornito come allegato generare una context-request per `.ai-context/ListaFileFromT8.1.md`
   
2. Context & Dependencies
   - fare controlli con rg per verificare di modificare ogni script e md .catsw-utility deve diventare .turbo-ai ovunque

3. Implementation Scope
   - Run a real (not simulated) end-to-end cycle: produce a genuine patch ZIP, let the watcher/orchestrator
     process it, confirm archival, execution, and cleanup all behave as specified in the skills.
   - Run a real startup session and confirm the dynamic changelog fragment and rotation both fire
     correctly.
   - Confirm UTF-8 end-to-end with the in a live run.

4. Acceptance Criteria
   - One full live cycle completes with no manual workaround needed anywhere in the chain.

5. Delivery Artifacts
   - all the modified files with version incremented
   - versione da rilasciare TurboAI 1.1 (aggiornare nel front matter di .turbo-ai/Readme.md)
   - un lingotto d'oro a IK0VCK.

6. Extra Startup Files
   - None beyond Target Paths.

---

### M9 - Per-task extra-files declaration in the plan

**Note before rewriting this milestone: its purpose is now largely satisfied by FaseDefinizionePiano.md §1.2,
section 6 ("Extra Startup Files"), already added to the plan-authoring standard itself. Consider whether M13
is still needed as a separate implementation milestone, or whether it should be moved right after M0 instead
of running last - the whole point of this milestone is to give every other task a way to declare its own
extra context files, which would have helped M5-M12 above if it existed already. Left as the last milestone
below only because that was its original position; recommend moving it, not implementing it here.**

#### T9.1 - Per-task extra-files declaration mechanism

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

#### T9.1 - Fine del Piano

- muovere il piano in .ai-context/PianiCompletati con nome Piano-TurboAI-utility-toolchain-v3.0.md e front matter aggiornata



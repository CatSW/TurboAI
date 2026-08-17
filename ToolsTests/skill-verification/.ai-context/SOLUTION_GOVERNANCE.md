# SOLUTION_GOVERNANCE — skill-verification

- TurboAiWorkingRoot: C:\Repo\CatSW\TurboAI\ToolsTests\skill-verification
- DefaultChangeLogPath: `Documentation/`

## Active Plan
- File: `.ai-context/Piano-Multi-Task.md`
- Alias: skill-verification

## Purpose
Test harness verifying whether an LLM correctly interprets/applies TurboAI skills.
Not a product solution. Golden fixtures per scenario, run_test.py per scenario checks
LLM-produced context-request/context-out against expectations.

## Scenarios present
- 01-start-session-acquisition
- 02-discovery-then-request
- 03-declared-files-request
- 04-context-out-gap-followup
- 05-zip-delivery-sanity
- 06-single-script-delivery
- 07-tolm-error-triage-patch

## Report convention
reports/<yyyymmdd-hhmm>_report-<scenario>-<llm>/
  <yyyymmdd-hhmm>-report-<scenario>-<llm>.md
  context-request-<label>.md   (copy of what was produced)
  context-out-<label>.md       (copy of what was produced)
Automating the move of these files from .catsw-utility into the report folder
(instead of manual copy) is an open improvement — not yet implemented.

## Token discipline
Skill and governance content must stay concise: no prose beyond what the LLM needs
to operate. This file must never report plan progress — that is inferred only from
the last Git commit and the next_task passed at session start.

## Context-request format
context-request-*.md sent to ContextBundler.exe must contain only what the tool can
parse (file paths, standard sections). Any free-text note not meant as tool input
must be prefixed with `#` so it is treated as a comment.

## Authoritative references
README.md and verifica-skill.cmd in this folder are authoritative on scenario
execution mechanics — this file does not restate them.

## Versionamento nei report

- Versione dello scenario di test: costante `SCENARIO_VERSION` a inizio di ogni
  `NN-scenario/run_test.py`, incrementata ad ogni modifica a scenario/golden.
- Versione TurboAI: campo `versione-turbo-ai` nel front-matter di
  `.catsw-utility/README.md`, letta da `_common/versioning.py:get_turbo_version()`.
- Versione skill Canale B: campo `version` nel front-matter del file skill copiato
  in `golden/` ad ogni `run_test.py setup` (sorgente:
  `.catsw-utility/docs/skill-uso-tools.md`), letta da
  `_common/versioning.py:get_skill_version()`.
- Nessuna di queste tre va chiesta interattivamente: sono sempre derivate dai file.

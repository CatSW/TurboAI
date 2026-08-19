# TurboAI - Solution Governance

## Identity
- DefaultChangeLogPath: `Documentation/`

## Active Plan
- File: `.ai-context/Piano-Multi-Task.md`
- Alias: TurboAI-Evolution

## ContextBundler Output Configuration
- `ContextBundler_output_base64: false`
- Precedenza di risoluzione: Env `TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64` > questo valore di governance > default `false`.
- Missing setting defaults to `false`.

## Documentation & Changelog Policy Override (skill-uso-tools.md §11)

- Skill Section 11 ("Product documentation and changelogs must remain free of AI, prompt and agentic workflow references") does NOT apply to the TurboAI solution itself.
- Rationale: TurboAI is an AI-orchestration framework; documenting its own multi-agent dogfooding workflow (e.g. Changelog "Folclore" sections) is legitimate product history, not incidental AI-tooling noise.
- Scope: this override is local to TurboAI's own documentation/changelog. Skill Section 11 remains the default rule for every client solution built using TurboAI - it is NOT edited or weakened by this note.

## Token Discipline (skills & governance)
- Skills carry zero explanatory prose: only what the LLM needs to work with
  the user and operate TurboAI tools/workflow efficiently. Every line is
  paid on every roundtrip.
- This file stays synthetic for the same reason (loaded at every session
  start). No plan/task status here — status comes only from `info_git.txt`
  + `info_next_task.md` at session start.
- The active plan (`Piano-Multi-Task.md`) is user-owned. The LLM never
  reads or edits it directly — cost-prohibitive at its size. Moving
  `<next_task>` and other plan edits: manual, or via a future dedicated
  script.
  
  ## versione-turbo-ai: nel front-matter del file Readme.md in .ai-context (o .turbo-ai) bisogna allineare la versione quando si cambia nel Documentation/Changelog.md
  
  se si ha una Unreleased si prende la ultima veriosne, la si incrementa e si mette un alpha temporaneamente
  
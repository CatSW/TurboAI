# TurboAI - Solution Governance

## Identity
- TurboAiWorkingRoot: `C:/Repo/CatSW/TurboAI/`
- DefaultChangeLogPath: `Documentation/`

## Active Plan
- File: `.ai-context/Piano-Multi-Task.md`
- Alias: TurboAI-evolution

## ContextBundler Output Configuration (stato corrente)
- `ContextBundler_output_base64: false`
- Precedenza di risoluzione (T4.4): Env `TURBOAI_CONTEXTBUNDLER_OUTPUT_BASE64` > questo valore di governance > default `false`.
- Missing setting defaults to `false`.

## Documentation & Changelog Policy Override (skill-uso-tools.md §11)

- Skill Section 11 ("Product documentation and changelogs must remain free of AI, prompt and agentic workflow references") does NOT apply to the TurboAI solution itself.
- Rationale: TurboAI is an AI-orchestration framework; documenting its own multi-agent dogfooding workflow (e.g. Changelog "Folclore" sections) is legitimate product history, not incidental AI-tooling noise.
- Scope: this override is local to TurboAI's own documentation/changelog. Skill Section 11 remains the default rule for every client solution built using TurboAI - it is NOT edited or weakened by this note.

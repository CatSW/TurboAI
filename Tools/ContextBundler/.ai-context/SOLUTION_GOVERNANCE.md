# ContextBundler – Solution Governance

## Identity
- Local root (session cwd, for `git -C ..`): `C:\Repo\CatSW\TurboAI\Tools\ContextBundler`
- Git top-level (real repo root — verify with `git rev-parse --show-toplevel`): `C:\Repo\CatSW\TurboAI`
- Solution: `ContextBundler.slnx`
- Version: v1.0

## Permanent Rules
- AI working files only under `.ai-context/`
- `Documentation/` = human/product docs only. No AI workflow content.
- Progress tracking = Git only.
- Dirty working tree = current task in progress (or spot task indicated in the prompt).
- Never write commit hashes inside this file.
- The plan holds no per-task status/hash fields. Which task is next is
  marked by the `<next_task>...</next_task>` tags wrapping its section in
  the plan file; move the tags to the following task when the current one
  closes.

## Plan
- File: Piano-Multi-Task.md
- Alias: copilot365

## Commit Message Convention
- Format: `[alias-Mx-Ty...]` short description
- Example: `[phenix-M2-T2.3+T3.2-prep] M2 Closed + internal refactoring (T3.2-prep)`
- Details of what changed are only in `ContextBundler/Documentation/Changelog.md`
- Use `git log --oneline -5` to see recent progress

## Patch Rules (FromLlm-*.zip)
- Zip paths are always relative to the Git top-level (see Identity), never to the local root
- One zip → extract to root
- Contains code/docs + single `FromLlm-*.py` under `.catsw-utility`
- Script may: `git add` (patch paths only) + `git commit`
- Forbidden: reset, checkout tracked files, clean, push, history rewrite
- Read-only git always allowed

## Changelog
- Path: `ContextBundler/Documentation/Changelog.md`
- Format: Keep a Changelog
- Startup injects only the latest version entries

## Notes
- If a task is executed out of sequence or intentionally skipped, note it
  here with a reference to the task and the reason — not in the plan, not
  as a per-task field.

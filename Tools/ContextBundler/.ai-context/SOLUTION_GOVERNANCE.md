# ContextBundler – Solution Governance

## Identity
- Local root (session cwd, for `git -C ..`, AND the effective root for ContextBundler tool paths and FromLlm-*.zip patch paths in this solution — see Repo Structure Peculiarity below): `C:\Repo\CatSW\TurboAI\Tools\ContextBundler`
- Git top-level (real repo root — verify with `git rev-parse --show-toplevel`): `C:\Repo\CatSW\TurboAI`
- Solution: `ContextBundler.slnx`
- Version: v1.0

## Repo Structure Peculiarity
- This monorepo does NOT follow the usual convention of a single `.catsw-utility` living at the Git top-level. This solution (`ContextBundler`) has its own nested `.catsw-utility` under `Tools/ContextBundler/.catsw-utility`, dedicated to dogfooding the tool on its own source. A separate, independent `.catsw-utility` also exists at the Git top-level for the rest of the monorepo — the two instances are unrelated, with no sync mechanism between them.
- Practical consequence: when operating from THIS solution's `.catsw-utility` session, both ContextBundler context-request paths AND `FromLlm-*.zip` patch entry paths are relative to the LOCAL root (`C:\Repo\CatSW\TurboAI\Tools\ContextBundler`), NOT the Git top-level. The tooling launched from this nested `.catsw-utility` resolves its own root as the parent of its own location (this solution's folder), never the monorepo root.
- Do not default to the generic "paths relative to Git top-level" assumption here — for this solution it is inverted (see Patch Rules below). If unsure which `.catsw-utility` instance a session belongs to, check the session's working directory, not the repo's overall layout.

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
- **This solution is a nested-`.catsw-utility` exception (see Repo Structure Peculiarity above)**: zip paths are relative to the LOCAL root (this solution's folder), never to the Git top-level — the reverse of the generic default used elsewhere in the monorepo.
- One zip → extract to local root
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

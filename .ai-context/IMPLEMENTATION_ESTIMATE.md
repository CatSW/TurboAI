---
title: TurboAI Implementation Estimate
as_of: 2026-08-13
scope: Active Piano-Multi-Task.md
status: ROUGH_ORDER_OF_MAGNITUDE
---

# Implementation Estimate

## Purpose and assumptions

This is a planning estimate, not a commitment. It is calibrated on the workflow observed on 2026-08-13: incremental diagnosis, exact-file acquisition, ZIP delivery, watcher execution, `ToLlm.txt` review, deterministic repackaging when needed, end-to-end regression and governance alignment.

Three ranges are used:
- **Ideal:** implementation and local checks succeed with complete context and no channel/tool anomaly.
- **Realistic:** includes normal context acquisition, ZIP/ToLlm cycles and one bounded corrective iteration.
- **Prudent:** includes bootstrap, Windows encoding, file-locking, rendering or incomplete-context regressions.

A work session means roughly 60-120 focused minutes. User waiting time between download and attachment is not counted as engineering effort, but it affects elapsed calendar time.

## Estimated effort by milestone

### M0 - Assessment and exact change map
- Complexity: medium.
- Main work: collect current operational files, reconcile interim fixes and finalize ownership boundaries.
- Ideal: 1.0-1.5 h.
- Realistic: 2-3 h, 1-2 sessions, 1-2 artifact cycles.
- Prudent: 4 h.

### M1 - ZIP retention and safe paths
- Complexity: medium-high.
- Main work: canonical timestamp naming, history preservation, collisions and ZIP path validation.
- Ideal: 2.5-4 h.
- Realistic: 5-7 h, 3-4 sessions, 2-4 cycles.
- Prudent: 9 h.

### M2 - ZIP-associated temp script execution
- Complexity: high.
- Main work: exact inventory association, direct extraction, `.py`/`.ps1` execution, `finally` cleanup and standalone compatibility.
- Ideal: 4-6 h.
- Realistic: 8-12 h, 5-7 sessions, 4-7 cycles.
- Prudent: 16 h.
- Highest risk: ownership handoff between watcher, orchestrator and delegated processor.

### M3 - Regression suite
- Complexity: high but mostly mechanical after M1-M2 stabilize.
- Main work: retention, traversal, association, stale temp, failure cleanup and Unicode matrix.
- Ideal: 4-6 h.
- Realistic: 8-11 h, 4-7 sessions, 3-6 cycles.
- Prudent: 15 h.

### M4 - Configurable ContextBundler output
- Complexity: medium.
- Main work: governance parser, session override, precedence, diagnostics and channel matrix.
- Ideal: 2.5-4 h.
- Realistic: 5-7 h, 3-4 sessions, 2-4 cycles.
- Prudent: 10 h.

### M5 - Dynamic changelog context
- Complexity: high.
- Main work: mono/multi-project routing, task target resolution, three-level Keep a Changelog extraction and startup integration.
- Ideal: 4-7 h.
- Realistic: 9-14 h, 5-8 sessions, 4-7 cycles.
- Prudent: 20 h.
- Highest uncertainty: exact project-target representation and test-project mapping in real governance files.

### M6 - Previous-run artifact rotation
- Complexity: medium.
- Main work: timestamped root/temp rotation, two wrapper integrations, duplicate Python cleanup removal and regressions.
- Ideal: 2-3.5 h.
- Realistic: 4-6 h, 2-4 sessions, 2-3 cycles.
- Prudent: 8 h.

### M7 - Cleanup, documentation and skills
- Complexity: medium-low after earlier milestones close.
- Main work: remove obsolete fallback paths, update examples, skills and operational docs.
- Ideal: 2-3 h.
- Realistic: 4-6 h, 2-4 sessions, 2-3 cycles.
- Prudent: 8 h.

### M8 - Final smoke test and closure
- Complexity: medium-high because it crosses all workflows.
- Main work: production-entry smoke tests, recovery state, plan/governance closure.
- Ideal: 2.5-4 h.
- Realistic: 5-8 h, 3-5 sessions, 2-4 cycles.
- Prudent: 12 h.

## Overall range

- Ideal engineering effort: **24.5-38 h**.
- Realistic engineering effort: **46-74 h**.
- Prudent upper planning envelope: **98 h**.
- Realistic focused sessions: **25-43 sessions**.
- At 1-2 focused sessions per day: approximately **3-6 calendar weeks**.
- At 3-4 focused sessions per day: approximately **2-3 calendar weeks**.

## Recommended sequencing and consolidation

1. Close M0 with the current real files.
2. Implement M6 early or together with the first wrapper changes, because it removes duplicate cleanup and stabilizes session boundaries.
3. Implement M1 and M2 together only at design level; deliver them in separate verified steps.
4. Build M3 incrementally during M1-M2 instead of postponing every test.
5. M4 is relatively isolated and can be scheduled when a shorter work window is available.
6. M5 should start only after its real governance and startup files are acquired.
7. Consolidate documentation and skill updates in M7 to avoid repeated rewrites.
8. Reserve M8 for a clean work window with enough time to inspect end-to-end output.

## Estimate maintenance

At every milestone closure, replace the estimate for that milestone with actual effort, cycles and notable causes of variance. Recalculate remaining ranges without rewriting historical actuals. The active plan remains authoritative for scope and task order.

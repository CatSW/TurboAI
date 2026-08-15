# TurboAI Benchmark - Solution Governance

## Identity
- Root: `<repository-root>`
- Solution: `TurboAI.Benchmark`
- Solution type: reusable TurboAI reference workload and regression benchmark
- Target framework: `.NET 10`
- Governance version: `v1.0`
- Active initiative: benchmark reference solution bootstrap and deterministic CSV-to-JSON pipeline
- Initiative status: `IN_PROGRESS`
- As of: `2026-08-14`

## Permanent Rules
- AI working files belong only under `.ai-context/`.
- Human and product documentation must not contain prompt or transient agent-workflow material.
- The active plan is the operational source of truth for task order and recovery.
- The active task is the only section wrapped by `<next_task>...</next_task>` in the plan.
- Move the marker whenever the current task closes.
- Keep Markdown and JSON files in LF.
- Keep C# and operational Windows scripts in CRLF unless repository evidence establishes a different convention.
- Do not store introducing commit hashes in tracked governance documents.
- Do not declare completion until code, tests, golden files, documentation, plan and governance describe the same state.

## Active Plan
- File: `.ai-context/Piano-Multi-Task.md`
- Alias: TurboAI Benchmark Reference Solution
- Resume rule: read this governance file and the active plan, then continue from the sole `<next_task>` block.
- Required startup context while active:
  - `.ai-context/SOLUTION_GOVERNANCE.md`
  - `.ai-context/Piano-Multi-Task.md`
  - files explicitly named by the active task

## Technical Baseline
- Use `.NET 10`.
- Use a console application plus a separate xUnit V3 test project.
- Use Serilog for structured application logging.
- Separate CSV parsing, validation, transformation, aggregation and JSON serialization.
- Use dependency injection and configuration through `appsettings.json` where useful.
- Return explicit process exit codes.
- Write output atomically through a temporary file followed by final rename.
- Never leave a partial final JSON file after a failed run.
- Do not depend on the host locale, local time zone, current clock, random identifiers or absolute paths.

## Input Contract
- Encoding: UTF-8 without BOM.
- Header: `TransactionId,CustomerId,Category,Amount,Quantity,Timestamp`.
- `TransactionId`, `CustomerId` and `Category` are required trimmed strings.
- `Amount` uses invariant decimal syntax with `.` as decimal separator.
- `Quantity` is a positive integer.
- `Timestamp` is ISO 8601 UTC and is normalized to `yyyy-MM-ddTHH:mm:ssZ`.
- Empty lines may be ignored and counted separately only if the implementation documents that behavior.
- Invalid records must not silently contaminate valid aggregates.

## Output Contract
- Encoding: UTF-8 without BOM.
- JSON indentation: two spaces.
- Final newline: exactly one LF.
- Property and collection ordering must be deterministic.
- Decimal values are emitted as JSON numbers with two fractional digits in golden-file comparisons.
- Records are ordered by `transactionId` using ordinal comparison.
- Customer and category aggregates are ordered by key using ordinal comparison.
- No generated timestamp, duration, machine name, absolute path or random value is written into golden JSON.
- Execution timing belongs in logs or benchmark result files, never in deterministic golden output.

## Aggregation Contract
- `recordCount`: number of valid transformed records.
- `invalidRecordCount`: number of rejected records.
- `totalAmount`: sum of `amount * quantity` for valid records.
- `totalQuantity`: sum of valid quantities.
- `averageLineAmount`: `totalAmount / recordCount`, or `0.00` when no valid record exists.
- `minimumLineAmount` and `maximumLineAmount`: minimum and maximum `amount * quantity`; `null` when no valid record exists.
- `periodStartUtc` and `periodEndUtc`: earliest and latest valid timestamps; `null` when no valid record exists.
- `byCustomer` and `byCategory`: valid-record count, total quantity and total amount for each key.

## Golden File Contract
- Root folder: `GoldenFiles/`.
- `GoldenFiles/Input/` contains valid or mixed CSV inputs.
- `GoldenFiles/Invalid/` contains inputs expected to fail before producing final output.
- `GoldenFiles/Expected/` contains deterministic expected JSON.
- `GoldenFiles/manifest.json` defines scenario intent, expected exit code and expected artifact.
- Golden files are authoritative observable expectations and must not be regenerated automatically during normal tests.
- Updating a golden file requires an explicit contract decision and review of the semantic JSON diff.

## Test Contract
- Use xUnit V3.
- Cover parser, validation, transformation, aggregation, serialization and full pipeline.
- Compare JSON semantically and verify deterministic byte output where specified.
- Run the same scenario repeatedly to detect nondeterminism.
- Verify invalid-input exit codes and absence of partial final output.
- Verify Serilog events at high-value boundaries without coupling tests to incidental message text.

## Benchmark Contract
- Measure model elapsed time, human operational time, build/test time and application execution time separately.
- Application performance runs must use a warm-up and multiple measured iterations.
- Record median elapsed time and throughput; do not draw conclusions from one run.
- Every comparison starts from the same clean baseline and frozen specification.
- Record TurboAI version, model, channel mode, artifact cycles, corrections, test result and golden-file result.
- Do not rank models using elapsed time alone; correctness is the primary gate.

## TurboAI Readiness Gate
- Do not execute the formal cross-model benchmark until the TurboAI evolution plan has completed identity overrides, timestamped ToLlm snapshots, manual interaction evidence, report generation and the canonical operational-root migration.

## Execution Profile for Benchmark Runs
- Read effective execution mode and participant identities from TurboAI's finalized governance/override resolver.
- Supported initial modes are `B_ONLY` and `A_PLUS_B`.
- `B_ONLY` records one Channel B participant.
- `A_PLUS_B` records Channel B as governance/verification owner and Channel A as the optional executor of assigned tasks.
- Preserve every effective value and configuration source in the single-run report.
- Never derive Base64 mode from participant identity.
- If a value remains `unspecified`, report it rather than guessing.
- Each benchmark copy represents one independent run. Cross-model or cross-profile comparison happens later from final reports and is not part of the run script.

## Benchmark Report Contract
- Produce one independent `BenchmarkResults/<run-id>/BenchmarkReport.md` and `BenchmarkReport.json` for the current run only.
- Include baseline version, execution mode, Channel B identity and source, optional Channel A identity and source, TurboAI version, task range, correctness gates, build/tests/golden results, artifact cycles and available timing data.
- The end-of-plan analysis script may locate the optional manual interaction file and count case-insensitive trimmed lines beginning with `User:`.
- Include the source path/link and the resulting single indicative count for this run.
- Treat the count as a coarse manual indicator, not a normalized quality score and not a transcript-derived metric.
- Missing file means `not recorded`, never zero. An explicit no-interaction file with zero matching lines means zero significant interventions.
- Multiple candidate files for the run boundary are reported as ambiguous and are not silently summed.
- Separate model elapsed time, human operational time, build/test duration and application execution time.
- Correctness is the primary gate; speed and autonomy are secondary observations.
- Do not ask the active LLM to maintain the manual interaction log.
- Comparison between models or execution profiles is a later operation over their independent final reports.

## Governance Alignment Obligation
- Every task-closing patch evaluates plan and governance alignment.
- Milestone closure updates the sole `<next_task>` marker.
- Final closure sets `Initiative status: COMPLETED` and moves the marker to `T42 - Piano Completato`.

---
title: Piano Multi-Task TurboAI - Benchmark Reference Solution
solution: TurboAI.Benchmark
release_target: TurboAI Benchmark baseline v1.0.0
as_of: 2026-08-14
status: IN_PROGRESS
workflow: TDM 1.0
active_initiative: Deterministic CSV-to-JSON reference workload
---

## 1. Objective

Create a reusable `.NET 10` reference solution that exercises TurboAI on a realistic but bounded workload: read transaction CSV data, validate and transform records, calculate deterministic aggregates, write JSON, log through Serilog, verify behavior with xUnit V3 and golden files, and measure execution time.

The same frozen baseline will be executed with different models, channel modes and TurboAI releases to detect regressions and improvements in correctness, scope discipline, engineering quality and operational efficiency.

## 2. Fixed Benchmark Scope

- One `.slnx` solution.
- One console application.
- One xUnit V3 test project.
- Serilog structured logging.
- CSV input and JSON output using the contracts in `SOLUTION_GOVERNANCE.md`.
- Deterministic aggregation by customer and category.
- Golden-file and integration tests.
- Product documentation and Keep a Changelog history.
- Execution timing recorded outside deterministic JSON output.

## 3. Constraints

- Do not add a database, web API, message broker or UI.
- Do not introduce nondeterministic output fields.
- Do not silently update golden files.
- Do not couple the core pipeline directly to console I/O or static global state.
- Do not use the current culture for numbers or timestamps.
- Do not continue to serialization after a fatal validation or I/O error.
- Do not leave partial final output.
- Do not optimize performance before correctness and deterministic behavior are established.

## 4. Milestones and Tasks

### M0 - Freeze specification and baseline

<next_task>
#### T0.1 - Validate the benchmark contract and golden scenarios

**Purpose**
- Review `SOLUTION_GOVERNANCE.md` and every file under `GoldenFiles/`.
- Confirm that field meanings, aggregation formulas, ordering and error behavior are unambiguous.
- Identify contradictions before creating application code.

**Checks**
- Recalculate every expected aggregate independently.
- Verify JSON syntax, LF endings and UTF-8 encoding.
- Confirm every manifest scenario references an existing file.
- Confirm no expected JSON contains volatile data.

**Output**
- A concise assessment under `.ai-context/`.
- A minimal correction patch only if the golden baseline is internally inconsistent.
</next_task>

### M1 - Bootstrap the .NET 10 solution

#### T1.1 - Create solution and projects
- Create `TurboAI.Benchmark.slnx`.
- Create `TurboAI.Benchmark` project folder
- Create `TurboAI.Benchmark/Documentation` folder
- Create `TurboAI.Benchmark.Tests` folder
- Create Changelog.md file in the Documentation folder using the file in Documentation/Changelog.md in the root of the solution as a format exemple
- Create in `TurboAI.Benchmark` a Console project targeting .NET 10.
- Create in `TurboAI.Benchmark.Tests` a Test targeting targeting .NET 10 and xUnit V3.
- Add project references and deterministic build settings.

#### T1.2 - Configure application bootstrap and Serilog
- Add dependency injection and options binding.
- Configure Serilog for structured console and file output.
- Keep `Program.cs` focused on composition and exit-code handling.
- Avoid global logger state that makes parallel tests unreliable.

### M2 - Implement parsing and validation

#### T2.1 - Define domain and transport models
- Define immutable or tightly controlled models for CSV rows, transformed records, issues and result documents.
- Use explicit JSON names and deterministic collection types or sorting.

#### T2.2 - Implement CSV parsing
- Parse quoted fields, escaped quotes, UTF-8 content and invariant decimals.
- Produce line-aware diagnostics.
- Avoid leaking implementation exceptions as the public error contract.

#### T2.3 - Implement validation
- Validate required fields, positive quantity, non-negative amount and UTC timestamp.
- Separate fatal file/schema errors from rejectable record errors.
- Ensure invalid records do not enter aggregates.

### M3 - Implement transformation and aggregation

#### T3.1 - Transform valid records
- Normalize text and UTC timestamps.
- Calculate deterministic line amount as `amount * quantity`.
- Sort transformed records by transaction identifier.

#### T3.2 - Calculate summary aggregates
- Implement overall metrics from the governance contract.
- Implement customer and category groups ordered ordinally.
- Define empty-set behavior exactly as specified.

### M4 - Deterministic JSON and atomic output

#### T4.1 - Implement deterministic serialization
- Configure stable property naming, indentation and ordering.
- Preserve monetary precision and exactly one final LF.
- Keep timing and environment data out of golden JSON.

#### T4.2 - Implement atomic file publication
- Write to a temporary sibling file.
- Flush and rename only after successful serialization.
- Delete partial temporary output after failure.
- Return explicit exit codes.

### M5 - xUnit V3 and golden verification

#### T5.1 - Unit-test parser and validation
- Cover valid, quoted, Unicode, empty and malformed input.
- Use focused theory data without hiding scenario intent.

#### T5.2 - Unit-test aggregation
- Verify totals, averages, minimum, maximum, dates and grouped aggregates.
- Include empty and single-record cases.

#### T5.3 - Implement golden-file tests
- Execute every manifest scenario.
- Compare semantic JSON and required byte-level determinism.
- Fail with a readable diff.
- Never overwrite expected files automatically.

#### T5.4 - Add pipeline integration tests
- Verify exit codes, logs, output publication and no partial output after failure.
- Run deterministic scenarios repeatedly.

### M6 - Performance measurement

#### T6.1 - Add application timing
- Measure parsing, transformation, aggregation, serialization and total execution separately.
- Emit structured timing events through Serilog.
- Keep measured values out of deterministic output.

#### T6.2 - Add repeatable benchmark runner
- Provide warm-up and repeated measured runs.
- Record median elapsed time, record count, input size, output size and throughput.
- Avoid claiming microbenchmark precision from the console stopwatch.

### M7 - Documentation

#### T7.1 - Write product documentation
- Add documentation index, functional specification, architecture, CSV/JSON contract and benchmark protocol.
- Keep README concise and point to detailed documents.

#### T7.2 - Add changelog and execution guide
- Add Keep a Changelog history without deleting previous releases.
- Document restore, build, test and benchmark commands.

### M8 - Benchmark protocol validation

#### T8.1 - Execute clean-baseline trial
- Run the workload from a clean copy using one selected model and TurboAI release.
- Capture artifact cycles, corrections, build/test results, golden results and timings.

#### T8.2 - Validate cross-model comparability
- Confirm the same frozen prompt, baseline, files, environment and acceptance criteria are used.
- Separate correctness gates from quality and speed observations.

### M9 - Generate the single-run benchmark report

#### T9.1 - Implement the final evidence-analysis script
- Create a portable script that runs only after the benchmark implementation tasks are complete.
- Discover the finalized TurboAI operational history directory without hardcoded repository paths.
- Inspect timestamped ToLlm snapshots, archived FromLlm artifacts, context files and verification outputs without modifying, moving or deleting evidence.
- Look for the optional `<data>_significativ_user_llm_itereations.md` file within the explicit run/date boundary.

#### T9.2 - Calculate the indicative intervention count
- When exactly one manual file is associated with the run, count case-insensitive trimmed lines beginning with `User:`.
- Include a repository-relative path or link to the source Markdown file.
- Do not perform semantic classification, sentiment analysis or automatic judgment.
- Do not count routine prompts from other transcripts and never rewrite the manual source.

#### T9.3 - Handle missing, zero and ambiguous evidence
- Missing file reports `not recorded` and a null count.
- An explicit no-significant-interaction file with zero `User:` lines reports zero.
- Multiple candidate files are listed as ambiguous and are not summed silently.
- Malformed free-form content remains linkable; only readable line prefixes are counted.

#### T9.4 - Generate one Markdown and JSON report
- Generate `BenchmarkResults/<run-id>/BenchmarkReport.md` and `BenchmarkReport.json` for this run only.
- Include execution mode, Channel B, optional Channel A, effective configuration sources, correctness gates, timings, artifact cycles, manual-log status, source link and indicative intervention count.
- State that the count is a coarse manual indicator.
- Do not scan or compare reports produced by other model runs.

#### T9.5 - Test the report script
Validate absent file, explicit zero, one occurrence, multiple occurrences, casing/whitespace, embedded non-prefix `User:` text, multiple candidates, UTF-8, source immutability, correct links and JSON null semantics.

### M10 - Final verification and closure

#### T10.1 - Full smoke test
- Restore, build and run the full xUnit V3 suite.
- Execute all golden scenarios and the benchmark runner.
- Generate the single-run Markdown and JSON reports from preserved evidence.
- Confirm deterministic output, UTF-8 behavior and unchanged history/manual evidence.

#### T10.2 - Closure and recovery-state alignment
- Update plan status to `COMPLETED`.
- Move `<next_task>` to `T42 - Piano Completato`.
- Mark the initiative completed and historical in governance.
- Confirm a new session can determine the completed state without user memory.

## 5. Delivery Rules

- Work incrementally and diagnose before modifying.
- Request only exact files needed by the active task.
- Preserve complete filenames and repository-relative paths.
- Deliver multi-file changes as one ZIP.
- Keep golden updates separate and explicitly justified.
- Align plan and governance at every task transition.

## 6. Resume Checklist

1. Read `.ai-context/SOLUTION_GOVERNANCE.md`.
2. Read `.ai-context/Piano-Multi-Task.md`.
3. Locate the sole `<next_task>` block.
4. Read the golden manifest and files named by the active task.
5. Continue with the smallest verifiable step.

##### T42 - Piano Completato
- The implementation, tests, golden files, documentation, benchmark protocol and governance alignment are complete.

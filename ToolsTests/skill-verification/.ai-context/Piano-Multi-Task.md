# Piano-Multi-Task — skill-verification: verify & fix scenarios

## Goal
Verify and fix all scenario harnesses under ToolsTests\skill-verification now that
.catsw-utility has been installed locally in this folder (TurboAiWorkingRoot corrected
to C:\Repo\CatSW\TurboAI\ToolsTests\skill-verification).

## T0 - 01-start-session-acquisition: root cause diagnosed [DONE, 16/8]
sonnet5 run FAILed: context-out did not include the requested file (src/config.py),
TurboAiWorkingRoot in the bundle did not match the scenario (DemoWidget), git log/status
referenced TurboAI/skill-verification instead of DemoWidget.
Root cause: .catsw-utility was missing under skill-verification, so the tool ran against
the wrong root. Also found: context-request-config-py.md contained a free-text line
("T1.1 - Rename a stale constant") not prefixed with `#`.
Fix applied by user: .catsw-utility copied into skill-verification.

<next_task>
## T1 - Re-verify 01-start-session-acquisition
- Rerun the scenario with the corrected TurboAiWorkingRoot.
- Confirm context-out includes the requested file(s) with real content.
- Confirm context-request-*.md has no unmarked free-text line (comment with `#` if needed).
- Update the report in reports/ per the naming convention in SOLUTION_GOVERNANCE.md.
</next_task>

## T2 - Verify 02-discovery-then-request
- Rerun, confirm output matches golden fixtures (src/calc.py, utils.py, config.json).
- Fix any working-root/path issues found, using the T0/T1 fix as reference.

## T3 - Verify 03-declared-files-request
- Rerun, confirm output matches golden fixtures (src/order.py, unused.py, validators.py).

## T4 - Verify 04-context-out-gap-followup
- Rerun, confirm correct handling of the context-out-round1.md gap-followup flow.

## T5 - Verify 05-zip-delivery-sanity
- Rerun, confirm zip-delivery flow sanity (golden/src/greeting.py).

## T6 - Verify 06-single-script-delivery
- Rerun, confirm single-script delivery flow.

## T7 - Verify 07-tolm-error-triage-patch
- Rerun, confirm ToLlm.txt error-triage/patch flow (golden/src/divider.py, ToLlm.txt).

## T8 - Wrap-up
- Bump scenario versions; add reference to which skill/TurboAI version each scenario
  was last run against.
- Add a Documentation/ folder with Changelog.md tracking changes to the
  skill-verification system itself.
- Generalize across all scenarios any fix found while working through T1-T7
  (e.g. automated move of report files by run_test.py, the `#` comment rule for
  context-request free text).

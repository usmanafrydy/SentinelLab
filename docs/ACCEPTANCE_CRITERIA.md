# Acceptance criteria

All criteria are pending as of September 24, 2026. These are future checks, not passed tests.

| ID | Requirement | Verification before release |
| --- | --- | --- |
| AC-01 | Validate the documented JSON Lines format | Mixed input reports accepted and rejected line counts, reasons, and line numbers; malformed data does not crash the process. |
| AC-02 | Normalize timestamps | Equivalent timezone-offset timestamps compare as the same UTC instant; timestamps without an offset are rejected. |
| AC-03 | Preserve evidence and deduplicate | Original accepted records are retained; importing identical events again creates no new events. An existing ID with different content is reported as a conflict, not overwritten. |
| AC-04 | Persist and search | Restart retains events and investigations; account, source IP, time-range, and outcome filters return the expected records. |
| AC-05 | Detect repeated account failures | Five failures for one account/source within the default inclusive five-minute window trigger R1; four do not. |
| AC-06 | Detect failures across accounts | Failures against ten distinct accounts from one source within the default inclusive ten-minute window trigger R2; repeated failures against one account do not inflate the distinct count. |
| AC-07 | Detect success after failures | A success with a matching account/source triggers R3 when at least five failures occurred in the preceding inclusive five-minute window; unrelated account/source activity does not. |
| AC-08 | Explain and reproduce alerts | Each alert records rule ID/version, parameters, evidence IDs, event interval, and a readable reason. Re-running unchanged input/configuration creates no duplicate alerts. |
| AC-09 | Investigate without losing evidence | Notes, status, and disposition survive restart; changes leave an action history; changing a conclusion does not alter original events. |
| AC-10 | Export a faithful report | Markdown and JSON exports match stored evidence, UTC timestamps, notes, disposition, and rule details. Untrusted text is safely handled in any rendered preview. |
| AC-11 | Protect analyst access | Unauthenticated reads of protected evidence and unauthorized state changes fail; logout invalidates access; credentials are stored with an established password-hashing library. |
| AC-12 | Handle hostile input safely | Enforce documented upload size/record limits, parameterized queries, output escaping, and CSRF protection for cookie-authenticated writes; do not log passwords or secrets. |
| AC-13 | Exercise detection edge cases | Test exact boundaries, normal typos, shared source addresses, duplicated records, and out-of-order events. Document intentional blind spots. |
| AC-14 | Evaluate honestly | A held-out labeled scenario set reports true/false positives and missed scenarios using a stated unit of evaluation and no unsupported real-world accuracy claim. |
| AC-15 | Reproduce and demonstrate | Follow setup instructions in a clean environment, run documented checks, load demo data, investigate an alert, and export a report. Save the demo and final release on GitHub. |

## Rule defaults and terminology

Defaults are lab design choices, not universal security thresholds. Rules run on stored event time, not import time. Version 1 uses batch evaluation; out-of-order input is sorted for evaluation. R1/R2 include both window endpoints; R3 includes the start and excludes failures at the success timestamp. All three rules are specified and tested in DETECTION_RULES.md.

R1: group by exact normalized username and source IP; count distinct failure events in [t - 5 minutes, t].
R2: group by source IP; count distinct usernames with failure events in [t - 10 minutes, t]. This pattern can suggest spraying but does not establish which passwords were attempted.
R3: for a success at time t, group by the same username and source IP; count failures in [t - 5 minutes, t). Equal-time failures are excluded because the source format does not establish order within a timestamp.

The observation of a pattern is distinct from a confirmed incident. Shared IP addresses, misconfigured clients, and human typing mistakes can produce suspicious-looking activity.

## Day 2 evidence - September 26

The command-line reader has automated coverage for AC-01 field validation/line summaries and AC-02 timezone normalization. Resource limits and rejection of hostile/malformed records cover part of AC-12. The 27-test suite also checks the command-line entry point and safe error output. These are component-level results: web upload, persistence, and all remaining release workflow criteria still require implementation and verification. Do not interpret these checks as a completed release acceptance run.

## Day 3 evidence

AC-03 has storage coverage for original preservation, canonical duplicates, conflicts, and first-import provenance. AC-04 event persistence is tested across processes; search and investigation storage remain pending. AC-12 has parameterized-query and safe-error tests. A forced write failure verifies rollback of event rows and the import summary. Full suite: 46 passing tests. These are component checks, not a completed release acceptance run.

## Day 4 evidence

AC-04 event search now has combined-filter, UTC boundary, empty-result, and deterministic pagination coverage; investigation persistence remains pending. AC-12 search values are parameterized, output is escaped, and read-only operations leave database bytes unchanged in tests. Full suite: 57 passing tests. These remain component checks, not a completed release acceptance run.

## Day 5 evidence

Browser upload/search/evidence now exercises AC-01 through AC-04 for events. AC-12 has HTTP upload limits, origin/token checks, safe text rendering, asset allowlisting, and automated/browser checks. Analyst authentication, investigation persistence, cookie-session CSRF controls, and final release acceptance remain pending. Full suite: 67 passing tests. Browser UI is a local prototype, not a finished alert dashboard.

## Day 6 evidence

AC-05 has R1 coverage for 4 versus 5 failures and the inclusive 300-second boundary. AC-08 has deterministic preview IDs, rule version/parameters, reasons, and resolvable evidence references; persistent alert deduplication remains pending. AC-13 includes ties, shuffled events, grouping isolation, successes, reimports/conflicts, and episode rearming. Full suite: 83 passing tests. These component results do not complete the remaining rules or release acceptance.

## Day 7 evidence

AC-06 now has R2 tests for distinct usernames, repeats, boundaries, expiration, ties, and independent IPs. AC-07 has R3 tests for preceding failures, exact start/end behavior, matching username/IP, and multiple successes. AC-08/13 cover stable combined IDs, repeated imports/conflicts, shuffled import order, supporting failure/success references, unchanged R1 example, and one snapshot per run. Output bounds fail without partial reports. Full suite: 103 passing tests. Persistent alert deduplication, investigations, authentication, evaluation, and final release acceptance remain pending.

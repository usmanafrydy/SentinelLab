# Acceptance criteria

## Current Day 16 setup evidence

Verified all 137 baseline source blobs against published commit 834a51c1bc170c1c1f6240f72d8d02837594387b and staged only those source files into a separate ignored folder. A newly created venv passed the 193 baseline tests. Final Day 16 candidate passes 194 tests and the seven-check authenticated HTTP rehearsal: import/deduplication, saved detections/run history, case/note/decision, faithful report content, process restart/session rejection and cleanup. A header-only login test was adjusted after intermittent Windows connection-aborted errors and passed twenty targeted checks. Application code is unchanged. See SETUP_REHEARSAL.md for detailed evidence.

Fresh network acquisition failed TLS verification, so the source fallback used hash-verified local bytes. Hidden-password input automation was rejected; real account service was exercised instead. These steps remain explicitly unverified. This is one Windows environment, not a new OS, browser visual audit or public deployment. Portfolio demonstration and final release acceptance remain pending. Earlier entries below are historical.


## Current Day 15 evaluation evidence

The fixed labeled corpus exercises twelve scenarios through real import/storage/detection using isolated temporary databases. Intent scoring gives TP 3, FP 3, TN 3 and FN 3. Expected rule sets agree in all twelve cases; this is distinct from classification quality. Source/event/manifest fingerprints and deterministic JSON support reproduction. Nine new tests bring the full suite to 193 passing tests. One initial existing HTTP test hit Windows error 10053; its isolated rerun and a complete subsequent run passed. No rule was tuned on the corpus. Authored with knowledge of the rules, this is not blinded or real-world evaluation. Day 14 navigation is complete; clean setup, final demo and release acceptance remain pending. Older entries below are historical evidence.


## Day 13 report evidence

AC-10 now has bounded Markdown and JSON exports containing case state, complete history, full saved rule/alert details, first run and linked original records/provenance from one read-only snapshot. Sixteen new tests bring the suite to 184. Tests cover fidelity, large IDs, full history beyond a page, unchanged database bytes, concurrent WAL updates, hostile markup, limits, missing links, old schemas, private exclusive CLI output and authenticated/stale/invalid/expired HTTP downloads. Both actual browser downloads were checked against the saved QA database; drafts remained excluded and retained. This is component evidence, not the complete final acceptance run. Broader interface improvement, held-out evaluation and clean-setup/release demonstration remain pending. The cumulative handbook includes Day 13; Word page layout remains unverified because bundled LibreOffice is absent.

## Day 12 local access evidence

Single-account browser access uses scrypt, expiring server-side sessions, logout, per-session write tokens and server-assigned browser case authors. Eleven new tests bring the suite to 168: anonymous gates, author spoofing, cookies, invalid input, limiting, rotation, expiry, salted storage and fail-closed startup. Browser workflows and narrow login layout were checked. This does not establish public-deployment security, authenticated historical provenance, encrypted storage, multiple roles or completed release acceptance. Reports/evaluation remain pending. The cumulative Word/Markdown handbook includes Days 10-12; Word page layout remains unverified because bundled LibreOffice is missing.

## Day 10 component evidence

AC-04/09 now have local case persistence, notes, status/disposition, before/after history, immutable alert links, reasons, and stale-revision protection. Sixteen new tests cover complete lifecycle, reopen/correction, rollback including migration, concurrency, bounds, read-only behavior, and separate-process commands. Full suite: 149 passing tests. Existing event/alert web reads remain compatible with v3. Browser case controls, authenticated authors/access (AC-11), exports (AC-10), broader evaluation, and final release acceptance remain unfinished. Self-declared author labels and SQLite history are not tamper-proof auditing.

These are release targets established September 24, 2026. Dated evidence below records component progress; the full release acceptance run remains pending.

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

## Day 8 evidence

AC-08 now has persisted deduplication, immutable rule/evidence snapshots, run history, and linked originals with separate-process retrieval. Tests cover migration preservation, failed-write rollback, concurrent saves/imports, selected/empty runs, late data, and preview/history read-only behavior. AC-04 event/browser compatibility remains verified after migration; investigation persistence is pending. Full suite: 120 passing tests. AC-09 through AC-11 and final release evaluation remain unfinished.

## Day 9 evidence

Browser access now covers explicit detection/save, bounded alert/run lists, per-run findings, paged alert evidence, and originals. AC-08 snapshots/deduplication are reused without rule changes. AC-12 checks protect the new write endpoint. Full suite: 133 tests, including invalid inputs, paging, read-only GETs, and rollback. Browser verified 3 new then 0 new/3 existing, run membership, R3-to-original success, reload persistence, and desktop/narrow layouts. Investigation persistence, authentication, exports, detection evaluation, and release acceptance remain unfinished.

## Day 10 and Day 11 investigation evidence

AC-04 investigation persistence and case history now have storage and HTTP coverage. Case actions preserve originals, duplicate creation returns the existing case, and stale decisions cannot overwrite newer revisions. Day 11 adds browser workflow, bounded lists/history and safe text rendering with the existing request protections. Full suite: 157 passing tests. Browser checked creation, notes, decisions, duplicate prevention, stale recovery, original navigation, reload persistence and responsive layouts. These are component/workflow results; analyst authentication, report export, final detection evaluation and release acceptance remain unfinished.

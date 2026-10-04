# Next session Day 17

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Target release October 17, 2026. Explain in simple English and Roman Urdu when useful.

1. Read AGENTS.md, PROGRESS.md, SETUP.md, SETUP_REHEARSAL.md and DAY_16_GUIDE.md. Compare published main and local files before editing; preserve unrelated work and existing access controls.
2. Day 16 completed a fresh venv and isolated authenticated HTTP rehearsal. Baseline 137 published blobs were verified, then copied into ignored data/runtime/day16_clean after network TLS failures. Never claim fresh download/clone passed. No user data or prior environment copied. The clean copy is a rehearsal artifact, not the active project.
3. scripts/rehearse.py uses a random account, temporary DB, a separate LocalServer worker and cooperative EOF shutdown. Seven checks cover access, imports/deduplication, detection/runs, case/history/report originals, restart persistence and logout. The final clean candidate passes 194 tests; corrected header-only auth check passed twenty repetitions. No app rule/schema/GUI change. Hidden account keyboard entry remains unverified due terminal-input approval rejection; account service was tested.
4. SETUP.md now separates existing-user continuation from fresh setup. Existing user account remains secrets/analyst.json; never print its contents/password. Continue day14_demo.db on 8776. Rehearsal closes its temporary servers and does not start that daily demo. App restart may stop the daily server; check before starting.
5. Day 17 proposed: prepare a clear synthetic portfolio demo, representative screenshots, an honest case study and draft CV bullets; map actual evidence against final acceptance and list remaining blockers. Do not claim a production SIEM, real-world accuracy, complete attack coverage, or tamper-proof evidence. No public hosting/multiple roles promised.
6. Update both cumulative Word and Markdown every checkpoint. Chapter 29 current map, 31 navigation, 32 evaluation, 33 setup rehearsal. Preserve historical chapters. Word content/structure is checked; bundled LibreOffice remains unavailable, so pagination is unverified.
7. Day 15 corpus remains TP/FP/TN/FN each 3 with 12/12 expected-rule agreement. It is authored with knowledge of rules, not independent evaluation. Distinguish rule agreement from malicious-intent classification. Application code unchanged in Day 16, so saved evaluation source fingerprints remain valid.
8. One learning question: after restarting with the same database, should the saved case disappear or should only the login session need renewal? Answers go in chat. Deadline October 17; no automatic future work or reminders requested.

## Current demonstration

MSYS2 Python 3.12.7, .venv/bin/python.exe, application standard library only. Existing private usman account in secrets/analyst.json; never print hashes or request the password in chat.

scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json

Check whether the server is running before starting. PID file data/runtime/day14_server.pid may be stale after an app restart; verify process identity before stopping. App restart may stop local processes; server restart invalidates sessions. Do not stop unrelated processes.

Day 14 demo was a consistent backup of day13_demo.db: 16 events, one import, three alerts, one run, case 1 in_progress/suspicious revision 5 with five actions. User activity may change it. Older demos remain separate and do not synchronize. Continue using day14_demo.db. QA uses day14_qa.db on 8777 with existing synthetic day12_qa_account.json; QA was signed out after checks. Its case reached revision 5 through synthetic note/decision checks, not user work.

workspace.js loads before app/alerts/cases scripts. It moves existing sections once and hides parent views independently of record-panel hidden state. revealWorkspace is called before focusing opened cases/alerts/originals; leaveEvidenceWorkspace returns to the origin. Main nav uses actual links/aria-current. Unknown or unavailable record fragments fall back to Overview. The new static assets must be served by a restarted current Python server.

## Preserved data and publication contracts

Rules: one snapshot, maximum 10000 events/100000 combined references. R1 five failures/300s, R2 ten distinct accounts/600s, R3 success after five earlier failures/300s. Explicit detection saves runs and immutable alerts; case creation migrates v2 to v3 atomically. Reads never migrate; uploads never auto-detect. Browser case IDs/revisions and report database-local IDs/revisions are strings.

Reports: same read-only snapshot, 1000 actions/1000 originals, 8 MiB source/16 MiB encoded; fail whole export rather than truncate. Drafts excluded. CLI files restricted to ignored reports/generated, no overwrite. Historical/CLI authors remain self-declared; database history is not tamper-proof.

Day 16 parent: 834a51c1bc170c1c1f6240f72d8d02837594387b. Inspect subsequent verified main before editing. Local HEAD/index remain at Day 2 due existing Windows metadata restrictions. Publish via connector; verify remote ref and all file hashes. Never reset work or change deny ACLs. Exclude credentials, cookies, runtime files, downloaded/private reports and Word lock files.

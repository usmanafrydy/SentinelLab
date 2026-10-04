# Next session Day 18

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Target October 17, 2026. Use simple English and Roman Urdu where helpful.

1. Read AGENTS.md, PROGRESS.md, RELEASE_READINESS.md, SETUP.md and DAY_17_GUIDE.md. Compare current published main/local blobs before edits; preserve unrelated changes and access controls.
2. Day 17 adds docs/portfolio gallery, demo script, AI-assisted case study, CV/interview notes, three reviewed JPEG screenshots and reviewed synthetic report pair. Source demo uses existing day07 sample, not private records. Both HTML badges now say PROTOTYPE rather than DAY 14. Actual application Python/rules are unchanged; 194 tests pass.
3. Isolated capture demo: data/runtime/day17_portfolio.db, port 8778, ignored data/runtime/day17_account.json. Synthetic account portfolio_analyst, created only for capture. Case 1 is in_progress/suspicious revision 3 with three browser-authored actions and six R3 originals; 16 events, two imports, three alerts, two runs. User's private everyday account/demo remain separate. Server PID file day17_server.pid can be stale; verify before stopping. Do not publish credentials or copy private records into portfolio examples.
4. Review docs/portfolio/DEMO_SCRIPT.md before presenting; it distinguishes fresh setup from already-prepared counts. Published reports have different export timestamps but identical saved case/actions/evidence. The gallery shows viewport excerpts, not the full history or a security audit. No video, public hosting, external CV submission or final release tag exists.
5. Day 18 proposed: final acceptance preparation and remaining verification. Recheck source acquisition through an authorized working path or explicitly retain its TLS limitation; do not disable verification. Hidden password typing needs a private manual check; account service is already tested. Attempt supported Word rendering when available. Review all release criteria, distribution privacy and presentation readiness before declaring a final release.
6. Keep portfolio wording honest about substantial AI assistance and learner ownership. Do not claim production SIEM, real incidents, tamper-proof evidence or real-world accuracy. Day 15 scores remain TP/FP/TN/FN each 3 and rule agreement 12/12 on authored synthetic data.
7. Update both cumulative handbooks every checkpoint. Chapter 29 current map; 31 navigation, 32 evaluation, 33 setup, 34 portfolio presentation. Preserve historical explanations. Word content/structure is checked; bundled LibreOffice remains unavailable, so visual pagination is unverified.
8. One learning question at a time: what additional information would justify changing Suspicious to Confirmed compromise? Ask for one example; answers go in this chat. No automatic scheduling requested.

## Current demonstration

MSYS2 Python 3.12.7, .venv/bin/python.exe, application standard library only. Existing private usman account in secrets/analyst.json; never print hashes or request the password in chat.

scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json

Check whether the server is running before starting. PID file data/runtime/day14_server.pid may be stale after an app restart; verify process identity before stopping. App restart may stop local processes; server restart invalidates sessions. Do not stop unrelated processes.

Day 14 demo was a consistent backup of day13_demo.db: 16 events, one import, three alerts, one run, case 1 in_progress/suspicious revision 5 with five actions. User activity may change it. Older demos remain separate and do not synchronize. Continue using day14_demo.db. QA uses day14_qa.db on 8777 with existing synthetic day12_qa_account.json; QA was signed out after checks. Its case reached revision 5 through synthetic note/decision checks, not user work.

workspace.js loads before app/alerts/cases scripts. It moves existing sections once and hides parent views independently of record-panel hidden state. revealWorkspace is called before focusing opened cases/alerts/originals; leaveEvidenceWorkspace returns to the origin. Main nav uses actual links/aria-current. Unknown or unavailable record fragments fall back to Overview. The new static assets must be served by a restarted current Python server.

## Preserved data and publication contracts

Rules: one snapshot, maximum 10000 events/100000 combined references. R1 five failures/300s, R2 ten distinct accounts/600s, R3 success after five earlier failures/300s. Explicit detection saves runs and immutable alerts; case creation migrates v2 to v3 atomically. Reads never migrate; uploads never auto-detect. Browser case IDs/revisions and report database-local IDs/revisions are strings.

Reports: same read-only snapshot, 1000 actions/1000 originals, 8 MiB source/16 MiB encoded; fail whole export rather than truncate. Drafts excluded. CLI files restricted to ignored reports/generated, no overwrite. Historical/CLI authors remain self-declared; database history is not tamper-proof.

Day 17 parent: 7b4df5146f72894961640e29d7faef42a0a19416. Inspect subsequent verified main before editing. Local HEAD/index remain at Day 2 due existing Windows metadata restrictions. Publish via connector; verify remote ref and all file hashes. Never reset work or change deny ACLs. Exclude credentials, cookies, runtime files, downloaded/private reports and Word lock files.

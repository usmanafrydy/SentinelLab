# Next session Day 16

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Deadline October 17, 2026. Use simple English and Roman Urdu where helpful.

1. Read AGENTS.md, PROGRESS.md, EVALUATION.md, DAY_15_GUIDE.md and SETUP.md. Compare current published main with local files before edits; preserve unrelated work/access controls.
2. Day 15 adds an isolated twelve-scenario evaluation. TP/FP/TN/FN are all 3, rule agreement 12/12. Scoring unit is one scenario with any alert positive. Intent is authored story context, not inferred truth. Corpus is separate from earlier fixtures but not blinded/independent; now a regression benchmark. Never present the 50 percent metrics as real-world accuracy. No rule tuning occurred.
3. Run scripts/evaluate.py through the existing .venv/bin/python.exe; no user database or credentials. Complete JSON on stdout. Exit 0 rule agreement, 1 mismatch with report, 2 invalid run without partial stdout. Published report is reports/examples/day15_evaluation.json; fingerprints identify inputs and all package Python plus CLI. Keep source unchanged while evaluating.
4. All 193 tests pass. An initial full run hit Windows error 10053 in an existing login HTTP test; isolated rerun and full rerun passed. New evaluation tests all passed. Repeated full evaluation reports match. Existing user demo/account unchanged; no browser changes today.
5. Day 16 proposed: rehearse setup from the published source in a separate clean folder; follow setup instructions, use synthetic credentials and validate import, detection, case, notes/decision and export. Document/fix reproducible issues. Do not overwrite the user's environment, private account or database. Do not treat historical SETUP examples as current instructions.
6. Update both cumulative Word and Markdown at every checkpoint. Chapter 29 is the current map; 31 covers navigation; 32 covers evaluation. Preserve historical chapters and update front matter. Bundled LibreOffice remains absent, so Word page layout is unverified despite content checks.
7. Remaining release work: clean setup, fixes, known limits, demonstration material, portfolio case study/CV bullets and final acceptance by October 17. Public hosting/multiple roles are optional. No automatic start or reminder requested.
8. Ask one learning question at a time. Day 15: if R1 and R3 both alert on one benign scenario, does our scoring count one false-positive scenario or two? Answers go in chat.

## Current demonstration

MSYS2 Python 3.12.7, .venv/bin/python.exe, application standard library only. Existing private usman account in secrets/analyst.json; never print hashes or request the password in chat.

scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json

Check whether the server is running before starting. PID saved in data/runtime/day14_server.pid; 7776 at the last start after a session restart, but verify process identity before stopping. App restart may stop local processes; server restart invalidates sessions. Do not stop unrelated processes.

Day 14 demo was a consistent backup of day13_demo.db: 16 events, one import, three alerts, one run, case 1 in_progress/suspicious revision 5 with five actions. User activity may change it. Older demos remain separate and do not synchronize. Continue using day14_demo.db. QA uses day14_qa.db on 8777 with existing synthetic day12_qa_account.json; QA was signed out after checks. Its case reached revision 5 through synthetic note/decision checks, not user work.

workspace.js loads before app/alerts/cases scripts. It moves existing sections once and hides parent views independently of record-panel hidden state. revealWorkspace is called before focusing opened cases/alerts/originals; leaveEvidenceWorkspace returns to the origin. Main nav uses actual links/aria-current. Unknown or unavailable record fragments fall back to Overview. The new static assets must be served by a restarted current Python server.

## Preserved data and publication contracts

Rules: one snapshot, maximum 10000 events/100000 combined references. R1 five failures/300s, R2 ten distinct accounts/600s, R3 success after five earlier failures/300s. Explicit detection saves runs and immutable alerts; case creation migrates v2 to v3 atomically. Reads never migrate; uploads never auto-detect. Browser case IDs/revisions and report database-local IDs/revisions are strings.

Reports: same read-only snapshot, 1000 actions/1000 originals, 8 MiB source/16 MiB encoded; fail whole export rather than truncate. Drafts excluded. CLI files restricted to ignored reports/generated, no overwrite. Historical/CLI authors remain self-declared; database history is not tamper-proof.

Day 15 parent: 45d65162ced1d244df78c57f829dd6437cf6e72c. Inspect subsequent verified main before editing. Local HEAD/index remain at Day 2 due existing Windows metadata restrictions. Publish via connector; verify remote ref and all file hashes. Never reset work or change deny ACLs. Exclude credentials, cookies, runtime files, downloaded/private reports and Word lock files.

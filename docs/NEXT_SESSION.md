# Next session Day 15

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Deadline October 17, 2026. Use simple English and Roman Urdu when helpful.

1. Read AGENTS.md, PROGRESS.md, NAVIGATION.md, REPORTS.md, AUTHENTICATION.md, DETECTION_RULES.md and DAY_14_GUIDE.md. Compare current published main with local files before editing. Preserve unrelated changes and existing access controls.
2. Day 14 adds four focused workspaces, responsive navigation, original-evidence return, case shortcuts, fragment/Back/Forward routing and useful focus. Existing DOM forms stay in memory; switching areas preserves drafts/filters but does not save them. Reload still loses drafts. Rules, schema, report and access contracts are unchanged.
3. All 184 regression tests passed; existing asset delivery test extended. Browser checks covered drafts/filters, case-alert-original return, Back/Forward, keyboard activation, unknown/reloaded evidence fragments, note/decision saves, duplicate case recovery, actual report content, narrow layout and signed-out rejection. No claim of full accessibility certification or usability-study results.
4. Proposed Day 15: held-out labeled scenario evaluation. Define labels, unit of scoring, expected findings and evaluation procedure before implementing it. Include realistic benign alternatives, positive cases and deliberate blind spots; report false positives and misses honestly. Keep held-out evaluation separate from tuning/demo fixtures and make no real-world accuracy claim.
5. Remaining release work: evaluation, clean setup rehearsal, fixes, known limits, demonstration material, portfolio case study/CV bullets, final acceptance. Target October 17. Public hosting and multiple roles are optional, not implied.
6. Update docs/SentinelLab_Project_Handbook.docx AND docs/SENTINELLAB_HANDBOOK.md every checkpoint: concepts, all changed files, operating steps, tests, troubleshooting, limits and next work. Chapter 29 is the current completion map; chapter 31 teaches Day 14. Earlier chapters are historical. Update front matter/map/test count.
7. Word content/structure verified: 1231 paragraphs, 22 tables, prior lessons/tables preserved; 2254 words added. Canonical render attempt fails because bundled LibreOffice soffice.exe is missing. Visual pagination is unverified; do not use desktop LibreOffice or claim code tests verify Word layout.
8. One learning question at a time. Day 14 pending: does retaining a draft while switching sections mean the draft was saved to SQLite? Answers go in this chat.

## Current demonstration

MSYS2 Python 3.12.7, .venv/bin/python.exe, application standard library only. Existing private usman account in secrets/analyst.json; never print hashes or request the password in chat.

scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json

Check whether the server is running before starting. PID saved in data/runtime/day14_server.pid; 7776 at the last start after a session restart, but verify process identity before stopping. App restart may stop local processes; server restart invalidates sessions. Do not stop unrelated processes.

Day 14 demo was a consistent backup of day13_demo.db: 16 events, one import, three alerts, one run, case 1 in_progress/suspicious revision 5 with five actions. User activity may change it. Older demos remain separate and do not synchronize. Continue using day14_demo.db. QA uses day14_qa.db on 8777 with existing synthetic day12_qa_account.json; QA was signed out after checks. Its case reached revision 5 through synthetic note/decision checks, not user work.

workspace.js loads before app/alerts/cases scripts. It moves existing sections once and hides parent views independently of record-panel hidden state. revealWorkspace is called before focusing opened cases/alerts/originals; leaveEvidenceWorkspace returns to the origin. Main nav uses actual links/aria-current. Unknown or unavailable record fragments fall back to Overview. The new static assets must be served by a restarted current Python server.

## Preserved data and publication contracts

Rules: one snapshot, maximum 10000 events/100000 combined references. R1 five failures/300s, R2 ten distinct accounts/600s, R3 success after five earlier failures/300s. Explicit detection saves runs and immutable alerts; case creation migrates v2 to v3 atomically. Reads never migrate; uploads never auto-detect. Browser case IDs/revisions and report database-local IDs/revisions are strings.

Reports: same read-only snapshot, 1000 actions/1000 originals, 8 MiB source/16 MiB encoded; fail whole export rather than truncate. Drafts excluded. CLI files restricted to ignored reports/generated, no overwrite. Historical/CLI authors remain self-declared; database history is not tamper-proof.

Day 14 parent: af75e7e60b1cd041ec3c87a659df17dd7b05f0be. Inspect subsequent verified main before editing. Local HEAD/index remain at Day 2 due existing Windows metadata restrictions. Publish via connector; verify remote ref and all file hashes. Never reset work or change deny ACLs. Exclude credentials, cookies, runtime files, downloaded/private reports and Word lock files.

# Next session Day 13

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Deadline October 17, 2026. Simple English and Roman Urdu as needed.

1. Read AGENTS.md, PROGRESS.md, AUTHENTICATION.md, INVESTIGATIONS.md, WEB.md and DAY_12_GUIDE.md. Compare published main and local files before editing. Preserve unrelated work/access controls.
2. Day 12 adds single-account local sign-in using scrypt, expiring server-side sessions/logout and session-bound browser case authors. CLI/historical labels remain self-declared; direct file access is outside this boundary. No public-deployment claim. Full suite: 168 tests.
3. Proposed Day 13: faithful investigation report export. Specify content, snapshot consistency, escaping, bounds, private report handling and tests before implementation. Include alert identity, evidence references, notes, reasoned conclusions and limitations; preserve originals.
4. Broader design improvement, evaluated scenarios, clean setup, demo recording and portfolio release remain pending. Preserve existing beginner help.
5. Owner requires docs/SentinelLab_Project_Handbook.docx and docs/SENTINELLAB_HANDBOOK.md to be updated every checkpoint in easy English: concepts, file responsibilities, steps, tests, limits and next work. Chapters 26-29 add Days 10-12 and current completion map; older chapters are historical. Update the current map and test count as work progresses.
6. Word content/structure verified: 1084 paragraphs, 18 tables, earlier paragraphs/tables preserved. Canonical rendering fails because bundled LibreOffice is absent. Do not claim page-layout QA passed. Preserve historical editions and Word lock files.
7. Use one learning question at a time. Day 1/5 done; Day 6 questions 1/2 correct; later answers pending. Day 12 question: does signing out delete saved notes/original records?

## Environment and demonstration

MSYS2 Python 3.12.7, .venv/bin/python.exe; application standard library only. Owner privately created usman account in ignored secrets/analyst.json. Never print hashes or ask for the password in chat. Check if the server is already running before starting:

scripts/serve.py --database data/runtime/day12_demo.db --port 8773 --credentials secrets/analyst.json

The user signs in privately. PID saved in data/runtime/day12_server.pid. Restart invalidates sessions; do not stop unrelated processes. Day 12 database was copied from Day 11: 16 synthetic events, 1 import, 3 alerts, 1 run, case 1 in_progress/suspicious revision 5 with 5 actions at preparation. User activity may change counts. Prior demos are separate; old processes retain old Python behavior. Port 8772 and day12_qa.db/account.json are synthetic QA only.

All rules use one snapshot capped at 10000 events/100000 combined references. Explicit detection save migrates v1 to v2, preserving v3; valid case creation migrates v2 to v3 atomically. Reads never migrate. Case changes preserve originals/alerts. Upload never automatically runs detection. Browser case IDs/revisions are decimal strings for 64-bit precision.

## Publication continuity

Day 12 parent: 0167848e26cb73e2f5f24102a99e7e4434bcb6d8. Consult the subsequent verified main commit before editing. Local HEAD/index remain at Day 2 due existing Windows metadata restrictions. Publish through connector and verify remote ref and all file hashes; disclose local metadata remains unsynchronized. Never reset away work or change deny ACLs. Exclude secrets, cookies, runtime data/logs/reports and lock files.

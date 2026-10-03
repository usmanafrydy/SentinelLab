# Next session Day 14

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Deadline October 17, 2026. Simple English and Roman Urdu as needed.

1. Read AGENTS.md, PROGRESS.md, AUTHENTICATION.md, INVESTIGATIONS.md, REPORTS.md, WEB.md and DAY_13_GUIDE.md. Compare published main and local files before editing. Preserve unrelated work/access controls.
2. Day 13 adds faithful Markdown/JSON exports from one bounded read-only snapshot: full history/originals, safe fenced Markdown, authenticated attachments with expected revision, and exclusive private CLI output. Full suite: 184 passing tests. Sixteen new tests plus browser verification are documented in PROGRESS.md. No schema change.
3. Proposed Day 14: focused interface/navigation improvement. Make import, detection, investigations and reports easier to find, reduce unnecessary scrolling, preserve beginner help/accessibility, and retain auth/draft/error/evidence behavior. Define a bounded plan first. No hosting/new roles in this checkpoint.
4. Still pending: held-out scenario evaluation, fresh setup, known limits, demo recording/screenshots, portfolio case study/CV bullets and final release acceptance. AC-10 has component evidence, not complete final release acceptance.
5. Update docs/SentinelLab_Project_Handbook.docx and docs/SENTINELLAB_HANDBOOK.md EVERY checkpoint in easy English: concepts, actual changes, every changed file's role, steps, tests, troubleshooting, limits and next work. Chapter 29 is the current completion map; chapter 30 explains Day 13. Earlier chapters are historical. Update front matter/map/test count.
6. Word content/structure verified: 1162 paragraphs, 20 tables, prior lessons/tables retained, 2935 words added. Canonical rendering still fails because bundled LibreOffice soffice.exe is unavailable. Do not claim page-layout QA passed or use desktop LibreOffice. Preserve historical editions/Word lock files.
7. One learning question at a time. Day 13 pending: should an unsaved typed note appear in the downloaded report? Answer here. Earlier unanswered questions are not a reason to restart completed implementation.

## Current demonstration

MSYS2 Python 3.12.7, .venv/bin/python.exe; standard library only. Owner account usman lives in ignored secrets/analyst.json; never read/print hashes or ask for the password in chat. Check existing processes before starting:

scripts/serve.py --database data/runtime/day13_demo.db --port 8774 --credentials secrets/analyst.json

PID saved in data/runtime/day13_server.pid (14824 at preparation; verify process identity before stopping). Restart invalidates sessions. Old processes retain old Python code. Day 13 was copied consistently from Day 12: 16 events, one import, three alerts, one run, one case with five actions, case 1 in_progress/suspicious revision 5. User activity may change counts. Earlier demos remain separate; later edits do not synchronize. Use Day 13 for continued work. Synthetic QA uses day13_qa.db with existing day12_qa_account.json on 8775; QA browser signed out after testing.

Browser downloads use the browser-selected folder, usually Downloads. CLI outputs stay under ignored reports/generated, never overwrite. Limits: 1000 actions, 1000 evidence events, 8 MiB source, 16 MiB encoded output; failures never intentionally truncate. Originals/notes are not redacted. Never publish generated/private reports, credentials, cookies, runtime logs/databases or lock files.

Rules use one snapshot capped at 10000 events/100000 combined references. Explicit detection save migrates v1 to v2 preserving v3; case creation migrates v2 to v3 atomically. Reads/exports never migrate. Upload never auto-detects. Browser case IDs/revisions and exported database-local IDs/revisions are decimal strings. New browser authors come from the account; historical/CLI labels remain self-declared, and database history is not tamper-proof.

## Publication continuity

Day 13 parent: e8940b4a2f3a2b9836079dff84df6aed9c9f0c12. Consult subsequent verified main before editing. Local HEAD/index remain at Day 2 due Windows metadata restrictions. Publish through connector and verify remote ref/all file hashes; disclose unsynchronized local metadata. Never reset work or change deny ACLs. Source/docs are published; runtime/secrets excluded.

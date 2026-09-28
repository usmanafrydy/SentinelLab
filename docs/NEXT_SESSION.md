# Next session - Day 6

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Target completion October 17, 2026. Simple English and Roman Urdu as needed.

1. Read AGENTS.md, PROGRESS.md, ACCEPTANCE_CRITERIA.md, EVENT_FORMAT.md, DATABASE.md, and WEB.md.
2. Verify GitHub main and local files before editing. Preserve changes and existing permissions.
3. Review Day 5 questions; Day 1 is complete and Day 2-5 answers are unrecorded.
4. Specify alert grouping/cooldown and deterministic IDs before detection implementation. Follow documented defaults: R1 five failures for exact username/source IP within inclusive five minutes; R2 ten distinct accounts within inclusive ten minutes; R3 success after five matching failures in [t-5 minutes,t).
5. Implement and test the first repeated-failure rule as a bounded checkpoint. Sort stored event time, handle ties/out-of-order input, and link original evidence. Explain suspicious pattern versus confirmed compromise.
6. Keep current CLI/browser workflows working. Do not claim rules exist until implemented and tested.
7. Update guides, run relevant checks, and publish a verified commit.

## Environment

MSYS2 Python 3.12.7, .venv/bin/python.exe, standard library only. Suite: 67 tests. Start browser: scripts/serve.py --database data/runtime/day05_demo.db, then http://127.0.0.1:8765. It is local-only with no analyst authentication. Preview may still be running; inspect before starting another. Day 5 main demo has 3 events/2 imports. Separate day05_ui_checks files contain synthetic browser QA; all runtime files are ignored.

## Git continuity

Day 5 began with published Day 4 a80e711 and exact local file matches. Local HEAD/index remain at Day 2 because of Windows metadata write restrictions; do not confuse matching contents with reconciled history. Use the connected GitHub integration if staging remains blocked. Publication is verified and reported in the conversation. Before user-side reconciliation, compare all local changes with actual remote contents; never reset away work or alter deny ACLs.

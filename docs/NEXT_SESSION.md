# Next session - Day 9

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Deadline October 17, 2026. Simple English and Roman Urdu as needed.

1. Read AGENTS.md, PROGRESS.md, DETECTION_RULES.md, ALERT_STORAGE.md, ACCEPTANCE_CRITERIA.md, and WEB.md.
2. Compare GitHub main and local files before editing. Preserve unrelated work and access controls.
3. Day 1/5 exercises are complete. Day 6 questions 1/2 correct; question 3 explained but not independently answered. Day 7 answers and Day 8 deduplication question pending. Use small examples and one question at a time.
4. Add browser views for saved alerts, detection runs, and linked original evidence. Preserve immutable snapshots, late-import semantics, and event upload/search.
5. If adding explicit browser detection/save, reuse Host/Origin/write-token protections, bounded output, atomic save API, and clear counts/errors. Uploads should not silently execute detection.
6. Test APIs and browser interactions, paging, evidence navigation, safe rendering, repeat saves, and regressions. Keep preview mode read-only.
7. Update guides and publish a verified checkpoint. Authentication, investigations, and the full dashboard remain pending.

## Environment and current results

MSYS2 Python 3.12.7, .venv/bin/python.exe, standard library only. Full suite: 120 passing tests. scripts/detect.py --database data/runtime/day08_demo.db --save --json saves all rules; omitting --save remains read-only. --rule selects R1/R2/R3. scripts/alerts.py summary/list/runs/get reads history; get needs --alert-id. Separate day08_demo.db contains 16 synthetic events, 3 saved alerts, 2 completed runs, and 1 import. First save: 3 new; second: 0 new/3 existing. Further saves add runs. Prior Day 6/7 preview examples remain unchanged.

All rules use one snapshot capped at 10,000 events; combined evidence is capped at 100,000 references. Explicit saving migrates v1 to v2 inside the same transaction and preserves events/originals/imports. Failed saves roll back. Preview/history never migrate. Late changed evidence can add alerts while retaining old snapshots. Runtime databases are ignored.

Browser: scripts/serve.py --database data/runtime/day05_demo.db at http://127.0.0.1:8765; check whether it is already running. It shows events only. Restart after code changes before using upgraded databases. Earlier demonstration databases were not migrated during Day 8. No analyst sign-in yet.

## Git continuity

Day 8 began with verified published Day 7 commit 1eef9cde5127ec9107048a19e9db8ca56f8d17e8 and matching local contents. Local HEAD/index remain behind at Day 2 due Windows metadata restrictions. Publish through the GitHub connector and verify remote files/ref. Never alter deny ACLs or reset away work. Do not claim local Git history is synchronized. Publication is confirmed in the conversation after verification.

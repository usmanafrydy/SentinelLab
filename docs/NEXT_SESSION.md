# Next session - Day 10

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Deadline October 17, 2026. Simple English and Roman Urdu as needed.

1. Read AGENTS.md, PROGRESS.md, DETECTION_RULES.md, ALERT_STORAGE.md, ACCEPTANCE_CRITERIA.md, and WEB.md.
2. Compare GitHub main and local files before editing. Preserve unrelated work and access controls.
3. Day 1/5 exercises are complete. Day 6 questions 1/2 correct; question 3 explained but not independently answered. Day 7/8/9 answers pending. Use small examples and one question at a time.
4. Day 9 browser detection/save, paged alerts/runs, run membership, and original evidence navigation are implemented. Read DAY_09_GUIDE.md. Preserve immutable snapshots and existing workflows.
5. Proposed Day 10 scope: begin bounded investigation storage. Specify case identity, alert links, notes/status transitions, timestamps, validation, and retained history before coding. Keep analyst state separate from immutable evidence. Review the dated roadmap and remaining time.
6. Test migration, failure rollback, and a complete small backend workflow before extending the browser. Keep CLI preview/history read-only. No analyst authentication exists yet.
7. Update guides and publish a verified checkpoint. Authentication, investigations, exports, final evaluation, and portfolio release remain pending.

## Environment and current results

MSYS2 Python 3.12.7, .venv/bin/python.exe, standard library only. Full suite: 133 passing tests. scripts/detect.py --database PATH --save --json saves all rules; omitting --save remains read-only. --rule selects R1/R2/R3. scripts/alerts.py summary/list/runs/get reads history; get needs --alert-id. Separate day09_demo.db contains 16 synthetic events, 3 saved alerts, 2 completed runs, and 1 import. First save: 3 new; second: 0 new/3 existing. Further saves add runs. Previous demo databases remain separate.

All rules use one snapshot capped at 10,000 events; combined evidence is capped at 100,000 references. Explicit saving migrates v1 to v2 inside the same transaction and preserves events/originals/imports. Failed saves roll back. Preview/history never migrate. Late changed evidence can add alerts while retaining old snapshots. Runtime databases are ignored.

Browser: scripts/serve.py --database data/runtime/day09_demo.db --port 8769 at http://127.0.0.1:8769; check whether it is already running. Verified repeat saves, run filtering, R3/original-success evidence, reload persistence, and desktop/narrow layouts. API tests cover larger paging. Restart after Python changes and refresh tokens. Uploads never run detection automatically. No analyst sign-in yet.

## Git continuity

Day 9 began with verified published Day 8 commit 80e88e3344a5c6b56c573a80f796a3fb796c3ab1 and matching local contents. Local HEAD/index remain behind at Day 2 due Windows metadata restrictions. Publish through the GitHub connector and verify remote files/ref. Never alter deny ACLs or reset away work. Do not claim local Git history is synchronized. Publication is confirmed in the conversation after verification.

The handbook follow-up adds chapters 23-25 to docs/SentinelLab_Project_Handbook_Through_Day_9.docx and its Markdown companion, retaining the older Day 8 Word edition locally. Content/structure verified; Word visual pagination review is still pending because bundled LibreOffice is unavailable. Preserve any Word lock file; never publish it. Frontend now includes Start here, expandable help, and readable evidence-role labels. Full redesign is still planned. Check the subsequent verified publication in the conversation.

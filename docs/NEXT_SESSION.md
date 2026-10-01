# Next session - Day 11

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Deadline October 17, 2026. Simple English and Roman Urdu as needed.

1. Read AGENTS.md, PROGRESS.md, DETECTION_RULES.md, ALERT_STORAGE.md, ACCEPTANCE_CRITERIA.md, and WEB.md.
2. Compare GitHub main and local files before editing. Preserve unrelated work and access controls.
3. Day 1/5 exercises are complete. Day 6 questions 1/2 correct; question 3 explained but not independently answered. Day 7/8/9/10 answers pending. Use small examples and one question at a time.
4. Day 10 case storage/CLI are implemented. Read DAY_10_GUIDE.md and INVESTIGATIONS.md before changing case behavior. One case per alert; immutable alert links; append-only notes/action history; revision-checked state changes. Self-declared author labels are not authentication.
5. Proposed Day 11 scope: browser case creation from a saved alert, case detail/history, note entry, status/disposition changes with reasons, stale-revision recovery, and bounded lists. Reuse storage APIs and exact Host/Origin/token checks. Preserve original evidence and do not infer conclusions automatically.
6. Improve task navigation and clear wording while preserving the new Start here/expandable help. User finds the existing frontend basic; full design improvement remains planned. Test browser workflows, errors, keyboard/narrow layouts, safe rendering, paging, and existing regressions. No analyst authentication exists yet.
7. Update guides and publish a verified checkpoint. Authentication, exports, final evaluation, and portfolio release remain pending. Review the dated roadmap; target October 17.

## Environment and current results

MSYS2 Python 3.12.7, .venv/bin/python.exe, standard library only. Full suite: 149 passing tests. scripts/cases.py offers create/list/get/note/state/history. Separate day10_demo.db: schema 3, 16 synthetic events, 1 import, 3 alerts, 1 detection run, 1 case, 3 actions. Case 1 is in_progress/undecided, revision 3. Read with get/history --case-id 1. Prior databases remain separate. CLI detection preview remains read-only; --save explicitly saves. Existing alert history commands are unchanged.

All rules use one snapshot capped at 10,000 events; combined evidence is capped at 100,000 references. Explicit detection saving migrates v1 to v2, preserving v3 when already present. Explicit valid case creation migrates v2 to v3 atomically. Reads never migrate. Case changes preserve original events/alerts. Late changed evidence can add separate alerts; cases remain linked to their original saved alert. Runtime databases are ignored.

Browser: scripts/serve.py --database data/runtime/day09_demo.db --port 8769 at http://127.0.0.1:8769; check whether it is already running. Verified repeat saves, run filtering, R3/original-success evidence, reload persistence, and desktop/narrow layouts. API tests cover larger paging. Restart after Python changes and refresh tokens. Uploads never run detection automatically. No analyst sign-in yet.

## Git continuity

Day 10 began with verified published handbook/guidance commit 731e924042b6c86979c39cb1947de2b84b4139cf and all 89 matching local files. Local HEAD/index remain behind at Day 2 due Windows metadata restrictions. Publish through the GitHub connector and verify remote files/ref. Never alter deny ACLs or reset away work. Do not claim local Git history is synchronized. Publication is confirmed in the conversation after verification.

The handbook follow-up adds chapters 23-25 to docs/SentinelLab_Project_Handbook_Through_Day_9.docx and its Markdown companion, retaining the older Day 8 Word edition locally. Content/structure verified; Word visual pagination review is still pending because bundled LibreOffice is unavailable. Preserve any Word lock file; never publish it. Frontend now includes Start here, expandable help, and readable evidence-role labels. Full redesign is still planned. Check the subsequent verified publication in the conversation.

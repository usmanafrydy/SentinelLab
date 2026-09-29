# Next session - Day 8

Active project: C:\Users\Dell\Desktop\Projects\SentinelLab. Deadline October 17, 2026. Simple English and Roman Urdu as needed.

1. Read AGENTS.md, PROGRESS.md, DETECTION_RULES.md, ACCEPTANCE_CRITERIA.md, and DATABASE.md.
2. Compare GitHub main and local files before editing. Preserve unrelated work and access controls.
3. Day 1 and Day 5 exercises are complete. Day 6 questions 1/2 were correct; question 3 was explained but not independently answered. Day 7 answers are pending. Use small examples and one question at a time.
4. Implement permanent alert/run storage as a bounded checkpoint. Design explicit schema-version migration, preserving existing events/originals/imports and rolling back failures. Keep preview mode read-only.
5. Deduplicate saved alerts using stable identity. Store evidence references, selected rules, and completed run summaries. Define late-import behavior without deleting evidence or silently changing analyst conclusions.
6. Test repeat evaluation, migration of schema-v1 databases, preserved evidence, atomic failures, concurrent writes, and unsupported schemas. Keep CLI/browser/detector checks passing.
7. Update guides and publish a verified checkpoint. Authentication, investigations, and the full dashboard remain pending.

## Environment and current results

MSYS2 Python 3.12.7, .venv/bin/python.exe, standard library only. Full suite: 103 tests. scripts/detect.py --database data/runtime/day07_demo.db --json runs ALL rules by default; --rule R1/R2/R3 selects one. Day 7 demo has 16 events and 3 previews, one per rule. R3 references 5 failures plus 1 success. Sample output: reports/examples/day07_all_rules_preview.json. Day 6 R1 example remains unchanged when selected explicitly.

All rules use one snapshot capped at 10,000 events; combined output is capped at 100,000 evidence references and fails without partial output. No persistent alerts or schema changes yet. Runtime databases are ignored.

Browser: scripts/serve.py --database data/runtime/day05_demo.db at http://127.0.0.1:8765; check whether it is already running. It does not execute detection. No analyst sign-in yet.

## Git continuity

Day 7 began with published Day 6 commit 302be1c and matching local file contents. Local HEAD/index remain behind at Day 2 due previously observed Windows metadata restrictions. Use GitHub connector publication if staging is unavailable; verify remote files/ref. Never alter deny ACLs or reset away work. Publication outcome is confirmed in the conversation after verification.

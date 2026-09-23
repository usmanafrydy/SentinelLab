# One-month roadmap

Assumption: approximately 2-3 hours per day. Experience and available time still need confirmation.

## Week 1 - Data foundations

1. Confirm scope and acceptance criteria.
2. Prepare Python development tools and environment.
3. Learn essential Python through event records.
4. Document the event schema and synthetic scenarios.
5. Implement parsing, validation, and normalization.
6. Add SQLite storage and repeated-import handling.
7. Connect upload and event search.

## Week 2 - Detection

8. Specify rule grouping, thresholds, and time-window semantics.
9. Implement repeated account failures.
10. Implement failures across distinct accounts.
11. Implement success after a failure burst.
12. Add rule versions and alert deduplication.
13. Test benign, duplicate, unordered, and boundary cases.
14. Add alert explanations and justified ATT&CK mappings.

## Week 3 - Investigation and application security

15. Build dashboard filters and counts.
16. Add investigation status and disposition.
17. Add notes and action history.
18. Add evidence timelines.
19. Protect analyst access.
20. Check input handling, access control, session protection, and sensitive data handling.
21. Export investigation reports.

## Week 4 - Evaluation and portfolio

22. Generate logs from a local test application.
23. Exercise controlled benign and suspicious scenarios.
24. Evaluate against a separate labeled scenario set.
25. Measure performance with documented hardware and datasets.
26. Verify clean installation and backup/restore.
27. Fix defects and polish the interface.
28. Record a demo; consider restricted hosting only if feasible.
29. Write a source-grounded portfolio case study.
30. Review, tag a release, and prepare accurate CV bullets.

## Scope control

Core: one format, three rules, evidence views, investigations, reports, and meaningful tests.
Optional: second format, automatic collection, multiple roles, container packaging, and hosted demo.
Synthetic evaluation does not establish real-world detection accuracy. Adjust the schedule to actual progress.

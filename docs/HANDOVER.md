# SentinelLab project handover

Version 0.1.0 is the completed local portfolio milestone. The project folder is C:\Users\Dell\Desktop\Projects\SentinelLab. Keep this folder; the ignored rehearsal copies under data/runtime are not your everyday installation. The project is a guided AI-assisted learning prototype, not a continuously running security monitor.

## Open your existing project

Open http://127.0.0.1:8776/ and sign in with your existing usman account. If the page works, no startup command is needed. If it cannot connect, open Windows PowerShell normally, without administrator mode, and run:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
& .\.venv\bin\python.exe scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json
```

Keep that terminal open. Ctrl+C stops a server started in that terminal. Closing the app/session or restarting the computer can stop a previously background-started server. The browser page and the Python server are separate: opening the page does not start Python. After starting the server, refresh the page. Server restart invalidates sessions, so sign in again. Never send your password or credential file in chat.

The command uses the same saved database and account. Do not change the database filename merely to restart, and do not recreate the account. Different database paths are separate workspaces. The Day 18 manual test account is not the normal account. If the port is occupied, identify your own server before stopping anything; do not kill unrelated programs.

## Where work is stored

| Location | Purpose | Sharing rule |
| --- | --- | --- |
| src/sentinellab and scripts | Application and commands | Published source |
| data/runtime/day14_demo.db | Owner's ongoing saved events, alerts and cases | Keep private |
| secrets/analyst.json | Local account credential record | Never publish or paste |
| reports/generated | Normal exported investigations | Review privately before sharing |
| data/samples and data/evaluation | Fictional demonstration/evaluation records | Published synthetic material |
| docs/portfolio | Reviewed screenshots, example reports, summary and CV guidance | Public portfolio material |
| docs/SentinelLab_Project_Handbook.docx | Cumulative detailed Word explanation | Updated through Day 20; page layout unverified |
| docs/SENTINELLAB_HANDBOOK.md | Readable companion with the same daily explanation | Published documentation |

Older day databases and rehearsal environments are separate copies. Do not merge or delete them casually. A source ZIP does not include your private saved work. GitHub is a source backup, not a backup of the private database or account.

## Use the system

1. Events: import only records you are authorised to review, in the documented JSONL format. Synthetic samples are best for portfolio demonstrations.
2. Detection: explicitly run and save the selected rules. Importing records does not automatically run detection.
3. Open a finding, review its explanation and linked originals, then create or open its investigation.
4. Save observations and a reasoned decision. An alert does not prove hacking. Review current case state if a stale revision is rejected.
5. Export JSON or Markdown after saving. Draft notes are excluded. Review report contents before sharing; there is no automatic redaction.

See the five-minute demo and presentation guide in docs/portfolio. Repeating exercises is optional and does not prevent you from using this release. Do not claim a complete presentation assessment was passed merely because the software checks passed.

## Verification commands

From the project folder:

```powershell
& .\.venv\bin\python.exe scripts/run_tests.py
& .\.venv\bin\python.exe scripts/rehearse.py
& .\.venv\bin\python.exe scripts/evaluate.py
```

Expected release results: 194 passing tests; rehearsal status passed with seven checks; evaluation twelve scenarios/twelve expected rule agreements and TP/FP/TN/FN each three. These results describe tested behavior and authored scenarios, not universal security or real-world detection accuracy. Record errors rather than ignoring them. SETUP.md covers interpreter selection for a fresh Windows installation whose venv may use Scripts instead of bin.

## Protect and maintain your work

Keep private backups of your database and credential file in a location you control. For an ordinary file copy, first stop the server and any other process using that database cleanly; do not copy a live SQLite file and assume a consistent backup. Do not upload private backups to this repository. No backup was created or deletion performed as part of Day 20.

When reporting a bug, share the action, expected result, actual result and a synthetic reproduction if possible. Remove passwords, cookies, private logs and personal notes. Check the published VERSION and commit so the report refers to the right source. After a fix, run relevant checks, update the explanation and create a new version rather than moving an existing release tag.

The original local Git metadata remains restricted/behind even though published source files match. Do not reset local work, alter deny permissions or force-push to hide that difference. Word visual pagination remains unverified because the supported renderer lacks bundled LibreOffice. Read the Markdown companion if the Word layout is awkward and report the affected section for a later supported layout review.

## Portfolio wording

Use PROJECT_SUMMARY.md and CV_AND_INTERVIEW.md. Say that the project received substantial AI assistance for code, tests, documentation and debugging. Claim only the parts you can explain and demonstrate. Do not claim real incident-response employment, prevented attacks, enterprise scale, tamper-proof custody or independent authorship of every line.

Future live collection, public hosting, multiple analysts or stronger integrity controls are separate improvements. There is no automatic Day 21 task or reminder. Continue with a specific bug, learning question or requested feature when ready.

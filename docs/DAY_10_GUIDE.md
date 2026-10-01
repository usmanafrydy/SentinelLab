# Day 10 Investigation records

Completed October 1, 2026. Target completion remains October 17, 2026.

## What we built today

We added a complete local case workflow: create a case from a saved alert, add notes, change its status and conclusion with a reason, and read the history later. The data survives closing PowerShell and reopening it. Cases are available through scripts/cases.py today. Browser case controls are planned for Day 11; the existing browser still handles events, alerts, and detection history.

Roman Urdu: Alert shak wali activity dikhata hai. Case mein hum us alert ki investigation ke notes aur progress save karte hain. Aaj yeh kaam commands se hota hai; browser ke buttons aglay checkpoint mein banane hain.

No new packages were needed. We continue to use Python, SQLite, and the standard library. The prepared example uses invented login records, not a real attack or a real account investigation.

## Understand the new concepts

| Concept | Simple meaning | Example |
| --- | --- | --- |
| Case | A place to organize review of one saved alert | Review synthetic success after failures |
| Status | Where the work has reached | open, in_progress, closed |
| Disposition | Your current conclusion about the activity | undecided, benign, suspicious, confirmed_compromise |
| Note | An observation or question kept with the case | Need more context about this success |
| Action history | The sequence of creation, notes, and changes | Created, note added, review started |
| Revision | A number that increases after each saved action | 1 after creation, 2 after a note, 3 after a change |

Status and conclusion answer different questions. In progress says someone is working on the case. Undecided says there is not yet a conclusion. A closed case must have a chosen conclusion, but closing it does not make that conclusion objectively correct. The software stores the analyst's assertion; it does not independently verify a compromise.

Benign means the analyst considers the activity harmless. Suspicious means a concern remains. Confirmed compromise is a strong analyst conclusion requiring evidence beyond a threshold match. Do not select it merely because R1 or R3 triggered. Today we leave the demonstration undecided.

Roman Urdu: Status batata hai kaam kahan tak pohncha. Disposition batati hai aap ka nateeja kya hai. In progress aur undecided aik saath bilkul theek hain.

## Step 1 Open the project folder

In PowerShell:

```powershell
Set-Location 'C:\Users\Dell\Desktop\Projects\SentinelLab'
```

The assistant has already created the code, tests, documents, and demonstration. You do not need to create any folders. Commands below refer to the local Python environment already in this project.

## Step 2 Read the prepared case

```powershell
& ./.venv/bin/python.exe scripts/cases.py get --database data/runtime/day10_demo.db --case-id 1
```

Expected current demonstration: title Review synthetic success after failures, status in_progress, disposition undecided, revision 3. The alert_id starts with R3. The separate database has 16 events, 3 saved alerts, 1 detection run, and 1 case. It does not replace your Day 9 database.

This get command only reads. It does not add a note, increase the revision, or migrate the database. All case commands output JSON, which is a structured set of field names and values. The optional --json flag is accepted for consistency but is not required.

## Step 3 Read what happened

```powershell
& ./.venv/bin/python.exe scripts/cases.py history --database data/runtime/day10_demo.db --case-id 1
```

Expected: three history items. Revision 1 created the case. Revision 2 added a note saying the synthetic pattern alone does not prove compromise. Revision 3 changed status from open to in_progress and retained undecided. Each action contains a UTC time and a self-declared author label.

The before and after objects show the state around each action. A note changes the revision but leaves status and conclusion unchanged. Creation has no before-state because the case did not exist. Order is determined by revision, so a computer clock adjustment does not change action order.

## Step 4 Follow the link to evidence

```powershell
$demoCase = (& ./.venv/bin/python.exe scripts/cases.py get --database data/runtime/day10_demo.db --case-id 1) | ConvertFrom-Json
& ./.venv/bin/python.exe scripts/alerts.py get --database data/runtime/day10_demo.db --alert-id $demoCase.alert_id --json
```

ConvertFrom-Json lets PowerShell read a field by name. The command uses the case's alert_id to open the exact saved alert. Its evidence still contains five earlier failures and one successful login. Editing a case never changes those records, the alert reason, the rule version, or the original login text.

If you want to inspect these events through the existing browser, start a separate instance with the new database after stopping any instance on the chosen port:

```powershell
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day10_demo.db --port 8770
```

Open http://127.0.0.1:8770. This shows events and alerts; it does not yet show case controls. Restart old servers after Python code changes before pointing them at a version 3 database. Keep the existing Day 9 preview on its own database.

## Step 5 Add a practice note only if you want to change the demo

Reading Steps 2-4 is enough for today's first exercise. The following command writes another note:

```powershell
& ./.venv/bin/python.exe scripts/cases.py note --database data/runtime/day10_demo.db --case-id 1 --text 'Practice note: I reviewed the sample original records. More context would be needed for a real conclusion.' --author lab_analyst
```

If you have not changed the demonstration earlier, the revision becomes 4. Running it twice adds two notes; notes are deliberately separate actions and do not use alert deduplication. Corrections are new notes. Existing notes cannot be edited or removed by these commands.

The author label explains what label was entered. It is not a login or verified identity. Authentication is a later requirement. Anyone with local file access could also edit SQLite outside the application, so this history is not a tamper-proof forensic record.

## Step 6 Understand changing a conclusion

A state change requires the status, conclusion, reason, author label, and the revision you just read. The software compares that revision with the stored one. If another note or change has arrived, it rejects the stale update and asks you to refresh.

Example: you read revision 3. Someone adds a note, creating revision 4. A state change claiming revision 3 fails. Read the case again, review the new information, then make a deliberate decision. Do not automatically retry with a newer number without reviewing what changed.

Roman Urdu: Revision purani ho to software aap ki change save nahi karta. Pehle nayi information dekhein, phir faisla karein. Is se kisi aur ki nayi mehnat purani screen ki wajah se overwrite nahi hoti.

Open and in_progress cases can move between those states or close with a conclusion. A closed case can revise its conclusion while staying closed, with a new reason. To reopen it, use in_progress and undecided. Closed to open is rejected. An unchanged status/conclusion pair is also rejected; use a note if you only want to add commentary.

Notes can be added to closed cases for clarification. Reopening or correcting a conclusion keeps every earlier action in history. No state change deletes old evidence.

## Reproduce the workflow on a fresh checkout

Runtime databases are not in GitHub. The following sequence creates a new practice database. Choose a new filename if this one already has unrelated practice work. Run each command successfully before continuing.

```powershell
& ./.venv/bin/python.exe scripts/database.py import data/samples/day07_all_rules.jsonl --database data/runtime/day10_practice.db --json
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day10_practice.db --save --json
$practiceAlerts = (& ./.venv/bin/python.exe scripts/alerts.py list --database data/runtime/day10_practice.db --json) | ConvertFrom-Json
$practiceAlertId = ($practiceAlerts.items | Where-Object rule_id -eq 'R3').alert_id
$creation = (& ./.venv/bin/python.exe scripts/cases.py create --database data/runtime/day10_practice.db --alert-id $practiceAlertId --title 'Review synthetic success after failures' --author lab_analyst) | ConvertFrom-Json
$practiceCaseId = $creation.case.id
& ./.venv/bin/python.exe scripts/cases.py note --database data/runtime/day10_practice.db --case-id $practiceCaseId --text 'Synthetic exercise: inspect originals before reaching a conclusion.' --author lab_analyst
$currentCase = (& ./.venv/bin/python.exe scripts/cases.py get --database data/runtime/day10_practice.db --case-id $practiceCaseId) | ConvertFrom-Json
& ./.venv/bin/python.exe scripts/cases.py state --database data/runtime/day10_practice.db --case-id $practiceCaseId --status in_progress --disposition undecided --reason 'Begin reviewing synthetic evidence.' --expected-revision $currentCase.revision --author lab_analyst
& ./.venv/bin/python.exe scripts/cases.py history --database data/runtime/day10_practice.db --case-id $practiceCaseId
```

On a fresh database, the result is a case at revision 3 with three actions. Creating a case again for the same saved alert returns created=false and the existing case; it does not replace its title or add another creation action. Repeating the entire sequence is not a no-op: imports, runs, and notes have their own histories. Read existing state before repeating write commands.

## Files and their responsibilities

| File | Responsibility |
| --- | --- |
| src/sentinellab/storage/case_schema.py | Defines and validates the two new tables; creates them inside the case transaction |
| src/sentinellab/storage/cases.py | Validates input, creates cases, appends notes, applies state rules, checks revisions, reads bounded lists/history |
| src/sentinellab/cases_cli.py | Parses each command and calls the corresponding service; formats JSON and exit codes |
| scripts/cases.py | Finds the source package and starts the command-line program |
| src/sentinellab/storage/database.py | Accepts schema version 3 and validates required case columns while retaining older versions |
| src/sentinellab/storage/alerts.py | Reads saved alerts on version 3 and reports the actual version when saving detection |
| tests/integration/test_cases.py | Sixteen integration tests for the complete workflow, failures, concurrency, persistence, and compatibility |
| docs/INVESTIGATIONS.md | Exact state, input, migration, command, and history contract |
| docs/DAY_10_GUIDE.md | This lesson and reproducible examples |

README, setup, database/alert/web contracts, acceptance evidence, progress, and next-session notes are also updated. The Day 9 Word handbook remains a historical edition through Day 9; this new guide is the current Day 10 reference.

## Database changes explained

Schema means the database's table structure. Version 1 holds events/imports. Version 2 adds alerts and detection runs. Version 3 adds investigations and investigation_actions. A valid first case creation upgrades version 2 inside one transaction. A database without a saved alert cannot create a case. Merely reading old databases never upgrades them.

The investigations row holds the current state and permanent link to its alert. The action rows preserve how the current state was reached. Foreign keys require valid links. A unique alert_id enforces one case per saved alert. This initial scope does not group several alerts into one incident.

BEGIN IMMEDIATE makes simultaneous writers wait their turn. A transaction saves the current state and its history action together. If either write fails, both roll back. Tests force failures to verify this. Concurrent case creation produces one case; concurrent notes are both retained; competing updates based on the same revision allow only one to succeed.

## Limits and troubleshooting

Titles allow 120 characters, author labels 80, notes 4000, and reasons 1000. Blank values and unsupported control characters are rejected. Notes/reasons allow newline and tab. Lists/history default to 50 items; --limit accepts 1..200 and --offset 0..1000000. List filters accept --status. History runs oldest revision first; case lists show newest case ID first.

- Saved alert not found: save detection first and use its full alert ID in the same database.
- Case not found: use list with the same --database and copy the correct case ID.
- Refresh instruction: a newer action changed the revision. Read get and history before deciding again.
- Close error: a closed case needs a conclusion other than undecided.
- Write error: check file access, locks, and schema. A failed operation does not partly save a case action.
- Exit code 0 means success; 1 means a missing case on get/history; 2 means a validation/storage/usage error.

## What we checked

The full suite passes 149 tests: the previous 133 plus 16 investigation cases. Coverage includes migration preservation, duplicate creation, complete state history, reopened/corrected conclusions, input limits, read-only access, pagination, forced failure rollback, simultaneous actions, separate-process commands, malformed schemas, and version 3 compatibility with existing detection/import/browser reads.

These are component checks. They do not establish authenticated authors, tamper-proof storage, real-world detection accuracy, exports, or completed release acceptance.

## Your part and the next checkpoint

Run the two read-only commands for get and history, or ask me to walk through their output. Answer in this chat: if you change a case's conclusion, should its original login records change too? Explain why in your own words.

Next: Start SentinelLab Day 11. Add browser investigation controls and explain each step in simple English and Roman Urdu. Preserve the current evidence behavior and beginner guidance while making the case workflow easier to use.

# Day 8 - Keep alerts after the program closes

Today we added saved alerts and a record of each detection run. The browser still shows events; the new alert commands work in PowerShell. No extra Python packages are needed.

## 1. Understand the three records

- **Event:** one login attempt, such as a failed login at 09:01.
- **Alert:** a rule found a suspicious pattern. It includes a reason and links to the events.
- **Run:** one time we asked the rules to check the database. A run can find zero, one, or many alerts.

Roman Urdu: Event aik login ki entry hai. Alert shak wali activity ka signal hai. Run ka matlab aik dafa database ko check karna hai.

An alert does not prove that an account was hacked. We must investigate the evidence.

## 2. Open the project in PowerShell

```powershell
Set-Location "C:\Users\Dell\Desktop\Projects\SentinelLab"
```

This tells PowerShell which project folder to use. Expected: the prompt ends in SentinelLab. If it cannot find the folder, check the spelling. This laptop's Python command is `& ./.venv/bin/python.exe`; other machines should follow SETUP.md.

I created the files, ran the commands, and prepared your Day 8 demonstration. Use the following steps to understand or repeat it.

## 3. Put sample events in a separate database

```powershell
& ./.venv/bin/python.exe scripts/database.py import data/samples/day07_all_rules.jsonl --database data/runtime/day08_demo.db --json
```

The sample contains 16 invented login events. On a fresh database it saves 16 events. Repeat the import: 16 duplicates and zero new events. Repeated imports add import history, so import counts can increase. Earlier demonstration databases are separate files.

## 4. Preview before saving

```powershell
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day08_demo.db --json
```

Expected: three alerts, one each for R1, R2, and R3. This command only reads. It does not save alerts or add a run. Preview is like looking at a result before filing it.

## 5. Save the results

```powershell
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day08_demo.db --save --json
```

The `--save` option is the important difference. On a fresh demonstration it reports three new alerts and one saved run. It also upgrades the database's layout from version 1 to version 2 so the extra records have their own tables. This is a **schema migration**. Existing events, original text, and import history are preserved.

Roman Urdu: Database ke andar alerts rakhne ke liye naye tables banaye hain. Purani login entries ko badla nahi jata.

Each alert receives a stable ID based on its rule and evidence. The database uses this ID to recognize the same alert again. This is **deduplication**: avoiding repeated copies.

## 6. Save the same results again

Run the same `--save` command once more. With unchanged events:

| Result | First save | Second save |
| --- | --- | --- |
| New alerts | 3 | 0 |
| Already saved alerts | 0 | 3 |
| Total saved alerts | 3 | 3 |
| Total completed runs | 1 | 2 |

Two runs show that we checked twice. Three alerts show that we did not double the results. Your prepared Day 8 database already has these two runs. Another save adds another run while keeping three alerts.

## 7. Read saved history

```powershell
& ./.venv/bin/python.exe scripts/alerts.py summary --database data/runtime/day08_demo.db --json
& ./.venv/bin/python.exe scripts/alerts.py list --database data/runtime/day08_demo.db --json
& ./.venv/bin/python.exe scripts/alerts.py runs --database data/runtime/day08_demo.db --json
```

Summary shows totals. List shows saved alert IDs and their rules. Runs shows the rules used, their settings, how many events were checked, and how many alerts were new or already saved. These commands work after reopening PowerShell because the data is in the database file.

For one alert, replace YOUR_ALERT_ID with a full `alert_id` from the list:

```powershell
& ./.venv/bin/python.exe scripts/alerts.py get --database data/runtime/day08_demo.db --alert-id YOUR_ALERT_ID --json
```

Its evidence contains internal event IDs. To see an original event, replace 1 with an evidence `internal_id` from that same database:

```powershell
& ./.venv/bin/python.exe scripts/database.py get 1 --database data/runtime/day08_demo.db --json
```

For a smaller page, add `--limit 2` to the list command. Add `--offset 2` to skip the first two results.

## 8. What happens if something goes wrong?

Saving uses a **transaction**: changes succeed together or are undone together. If detection exceeds a limit or saving fails, the new run, its new alerts, evidence links, and any migration are rolled back. Existing results remain.

Roman Urdu: Agar beech mein error aaye, adhoora result save nahi hota. Purana record mehfooz rehta hai.

For a missing database, import the sample first. For a locked database, wait for the other operation to finish and retry. For an unsupported schema, keep the file and report the error; do not delete it. For a missing alert, copy the full ID and use the same database. Restart a running browser server after changing application code before using an upgraded database.

Late imported events may change which pattern the rules find. Changed evidence can create a new alert ID. Old saved alerts remain as historical results. The system does not automatically mark them confirmed, false positives, or resolved.

## 9. How we checked today's work

```powershell
& ./.venv/bin/python.exe scripts/run_tests.py
```

Day 8: 120 passing tests. Coverage includes migration, original preservation, repeat saves, separate-process reads, late events, concurrent operations, rollback, limits, and browser compatibility.

The demo ran in separate processes: 16 events, three new alerts on the first save, zero new alerts on the second, three saved alerts, and two runs. The database is ignored by Git; code, tests, and this guide belong on GitHub.

## One learning question

You save detection results and get **3 saved alerts**. You save detection again without changing the events. How many saved alerts should there be now?

Reply in our chat. One short sentence is enough. The next question can wait until this is clear.

Day 9 is planned to show saved alerts and evidence in the browser. Investigation notes, analyst sign-in, exports, and final portfolio evaluation remain future work. Target completion: October 17, 2026.

# Day 7: detect two more suspicious patterns

Today we added R2 and R3. All three rules now run together from one copy of the saved events. They produce read-only previews: no permanent alert table or automatic browser detection yet. Our completion target is October 17.

## 1. Understand the difference

| Rule | What it counts | Time allowed |
| --- | --- | --- |
| R1 | 5 failed logins for the same username and IP | 5 minutes |
| R2 | Failed logins for 10 different usernames from the same IP | 10 minutes |
| R3 | A successful login after 5 earlier failures for the same username and IP | Failures in the previous 5 minutes |

R2 counts different usernames. Ten failures for account_A still represent only ONE username. A failure for account_A, account_B, and account_C represents THREE usernames.

Roman Urdu: R2 mein failures ki tadaad ke bajaye alag accounts ginte hain. Ek account par das failures hon, tab bhi account ek hi gina jayega.

R3 asks whether somebody logged in successfully after repeated failures. This can happen when a user finally types the correct password. It can also be suspicious. The rule gives us a reason to investigate, not proof of hacking.

Roman Urdu: R3 dekhta hai ke baar baar failure ke baad login successful hua ya nahin. Ho sakta hai asli user ne password theek likh diya ho, is liye investigation zaroori hai.

## 2. Understand time boundaries

R2 includes failures exactly 10 minutes apart. At 09:10, an event at 09:00 still counts; one at 08:59:59 does not.

R3 includes a failure exactly 5 minutes before success, but excludes failures at the EXACT same timestamp as success. Example: for success at 10:05, failures from 10:00 onward count only if they happened before 10:05. We cannot assume a failure at 10:05:00 happened before a success at 10:05:00.

The detector uses when an event happened, not when we imported its file. It sorts the records, so shuffled file lines do not change the result.

## 3. Open PowerShell in the project

```powershell
Set-Location 'C:\Users\Dell\Desktop\Projects\SentinelLab'
```

I already created and tested today's sample. It contains 16 synthetic login records. No real login attempts or attacks were performed.

To create the demonstration on a new checkout, run:

```powershell
& ./.venv/bin/python.exe scripts/database.py import data/samples/day07_all_rules.jsonl --database data/runtime/day07_demo.db
```

Expected on an empty database: 16 inserted. On this laptop after today's test: 0 inserted and 16 duplicates if you repeat the import. Your older Day 5 and Day 6 databases are separate.

## 4. Run all three rules

```powershell
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day07_demo.db --json
```

Expected: events_scanned = 16, alert_count = 3. rules_evaluated lists R1, R2, R3. From Day 7 onward, this command runs all three by default.

Our sample has two groups of activity:

- IP 192.0.2.70 has failures for account_1 through account_10 at 09:00 through 09:09. This triggers one R2 alert.
- IP 192.0.2.71 has five failures for lab_user at 09:20 through 09:24, followed by success at 09:24:30. The failures trigger R1; the later success triggers R3.

Three alerts do not mean three confirmed attacks. R1 and R3 deliberately describe related activity using some of the same evidence.

## 5. Run one rule at a time

```powershell
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day07_demo.db --rule R2 --json
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day07_demo.db --rule R3 --json
```

Expected: one alert from each command. Use --rule R1 for the original Day 6 rule. --rule all explicitly selects the new default. --json displays named fields; leave it off for the text introduction followed by alert details.

R2's distinct_account_count is 10. Its failure_count can be higher if some accounts have repeated failures. R3's failure_count is 5, and its evidence contains SIX records: five failures plus the successful login. The role field distinguishes preceding_failure from triggering_success.

## 6. Check an original record

Copy an internal_id from the alert's evidence. In a fresh import of this sample, internal ID 16 is the success:

```powershell
& ./.venv/bin/python.exe scripts/database.py get 16 --database data/runtime/day07_demo.db --json
```

Expected: day07-success, outcome success, and original_record showing the accepted input. Use IDs from your actual output and the SAME database; IDs can differ if that database already had records.

This explains the Day 6 evidence question: an alert says something happened; original record references let you open the details and check its explanation. They do not prove that externally supplied logs are authentic or protected against later file tampering.

## 7. Understand repeated runs

Running detection twice on unchanged data gives the same alert IDs. Importing identical events again does not add new stored events. Alert previews are still not saved to a table; permanent alert deduplication is the next checkpoint.

R2 suppresses repeated alerts during one continuous burst while at least ten accounts remain in the time window. It can alert again after enough accounts expire. R3 evaluates each success separately: two successes can produce two alerts with different IDs. Success does not erase the earlier failures.

## 8. Verify and troubleshoot

```powershell
& ./.venv/bin/python.exe scripts/run_tests.py
```

Expected: 103 passing tests, including 20 new cases. They check distinct counting, exact boundaries, same-time events, account/IP separation, repeated successes, shuffled imports, stable IDs, original evidence, combined output, and limits. The saved Day 6 R1 result still matches exactly.

If the database is missing, run the import command first. If the result is empty, check that you selected the intended database and rule. An empty result does not prove safety. Exit 0 means evaluation completed, with or without alerts. Exit 2 means an error.

The input cap is 10,000 stored events. Combined previews also stop if they would exceed 100,000 evidence references, since many successes can refer to overlapping failures. A limit error produces no partial preview. Use a smaller separate lab dataset; do not delete investigation evidence to force a run through.

Your browser still imports, searches, and opens events. Running today's command does not add an alert panel to it. No new dependencies or database migrations were needed.

## Your part

Try --rule R2 and --rule R3, then explain the difference in your own words. We will ask one question at a time in the chat. First: if one username has ten failed logins from one IP, has R2 seen ten different usernames?

Next session: Start SentinelLab Day 8. Explain each step in simple English and Roman Urdu when needed.

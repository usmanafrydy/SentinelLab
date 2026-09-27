# Day 4: find saved login events

Today we added event search and original-evidence lookup. We still do not detect attacks or create alerts. Deadline remains October 17, 2026.

## 1. Why search matters

Day 2 checked records. Day 3 saved them. Day 4 lets an analyst find relevant records without reading everything. A filter is a condition, such as outcome = failure. Multiple filters must all match (AND).

Roman Urdu: Hum saved records mein se apni zaroorat ke records nikaalte hain. Agar username aur failure dono dein, to dono shartein poori honi chahiye.

## 2. Open the project

Open PowerShell and paste:

```powershell
Set-Location 'C:\Users\Dell\Desktop\Projects\SentinelLab'
$projectPython = '.venv/bin/python.exe'
```

This chooses the working Python environment on this laptop. Other computers should follow SETUP.md. I have already created and tested today's files; these commands are your practice.

## 3. Find failures

```powershell
& $projectPython scripts/database.py search --database data/runtime/day03_demo.db --outcome failure --json
```

Expected on this laptop's unchanged demo: total_matches = 2, returned = 2. These are login records, not alerts. Replace failure with success to find the one successful login. --json displays named fields in a structured format.

## 4. Combine conditions

```powershell
& $projectPython scripts/database.py search --database data/runtime/day03_demo.db --username demo_user --source-ip 192.0.2.10 --outcome failure --json
```

Expected: the same two failures, because both match all three conditions. Username matching preserves case and spaces: Demo_User differs from demo_user. An IP address identifies the recorded network source; it does not prove a particular person's identity.

## 5. Search a time interval

```powershell
& $projectPython scripts/database.py search --database data/runtime/day03_demo.db --start '2026-09-24T09:00:00Z' --end '2026-09-24T09:01:00Z' --json
```

Expected: one event, demo-001. The start is included and the end is excluded. Z means UTC. Pakistan time is UTC+05:00: 14:00+05:00 equals 09:00Z. Equivalent offsets are converted to the same UTC instant. Always supply seconds and a timezone.

Roman Urdu: Shuru ka waqt shamil hai, aakhri waqt shamil nahin. Is se lagataar do time ranges mein boundary wala record do baar nahin aata. This search convention is separate from the planned detection-rule windows.

## 6. Read results one page at a time

```powershell
& $projectPython scripts/database.py search --database data/runtime/day03_demo.db --limit 1 --offset 0 --json
& $projectPython scripts/database.py search --database data/runtime/day03_demo.db --limit 1 --offset 1 --json
```

limit is how many records to show. offset is how many matching records to skip. Expected: first demo-001, then demo-002. Results go from oldest to newest; internal ID breaks ties. Default page size is 50, maximum 200. next_offset tells you where to continue; null means there is no accessible next page. Finish paging before importing more data: new records can move page positions.

## 7. Open the original evidence

```powershell
& $projectPython scripts/database.py get 1 --database data/runtime/day03_demo.db --json
```

Use the integer id shown by search, not the source event_id string. Expected: demo-001 plus original_record, first_import_id, and first_line_number. These show what was first accepted and where it appeared in that import. Search omits the original text to keep lists smaller. Lookup retains it unchanged. This is useful provenance, not proof against someone editing the database outside the app.

## 8. How the code stays safe

- search.py opens SQLite read-only, so searches cannot update saved events or create a missing database.
- User values go into SQL placeholders. A username that looks like SQL is treated as text, never an instruction.
- Page limits keep the number of returned records bounded. They do not guarantee fast searches on a huge database.
- We tested combined filters, exact time boundaries, case/spaces, IPv6, timestamp ties, invalid filters, missing databases, evidence preservation, and CLI exit codes.

Run all checks:

```powershell
& $projectPython scripts/run_tests.py
```

Expected: 57 tests pass. A test supplies a known situation and checks that the result matches the expected behavior.

## Troubleshooting

- Missing database: run the Day 3 import command from SETUP.md. Search intentionally does not create one.
- Zero results: check spelling, username case, IP, outcome, and timezone; try fewer filters.
- Invalid time: supply the full date, time, seconds, and Z or +05:00. Start must precede end.
- get shows event: null and exits 1: that internal ID does not exist. Search first and use a returned id.
- Exit 2 means a usage/filter/database error. A successful empty search exits 0.

## Your part: answer here in the chat

1. If you search with username demo_user AND outcome failure, should a successful login appear?
2. Does the 09:00 to 09:01 search include an event at exactly 09:01?
3. Do two failed logins prove that an account was hacked? Why?

No need to memorize code. Explain the purpose in your own words. Next session: Start SentinelLab Day 5. Explain each step in simple English and Roman Urdu when needed.

# Day 6: your first detection rule

R1 now finds repeated failed logins. This is a read-only command-line preview: it reads saved events and prints alerts without saving them or changing the database. The browser still handles importing, searching, and opening evidence; it does not automatically run detection. R2/R3, permanent alerts, and an alert dashboard are future work.

Your Day 5 answers were all correct: the visible page is the frontend, identical reimports should not double saved events, and a failed login does not prove hacking.

## 1. Understand a rule

A rule is a condition we check against records. R1's condition is: at least 5 failed login events for the same username and source IP within an inclusive 5-minute window.

Threshold means the minimum count (5). Window means the time interval (300 seconds). Group means which events belong together (same username AND IP). Evidence means the records supporting an alert. These thresholds are lab choices, not a universal test for hacking.

Roman Urdu: Hum har user aur IP ke failed logins alag ginte hain. Agar paanch failures paanch minute ke andar hon, to system humein investigation ka ishara deta hai. Yeh confirmed hacking ka saboot nahin.

## 2. Follow the example

| Time (UTC) | Result | What R1 does |
| --- | --- | --- |
| 09:00 | Failure | Counts 1 |
| 09:01 | Failure | Counts 2 |
| 09:02 | Failure | Counts 3 |
| 09:03 | Failure | Counts 4 |
| 09:04 | Success | Does not count or clear the failures |
| 09:05 | Failure | Counts 5; produces an alert preview |

At 09:05, the 09:00 event is exactly five minutes old, so it is included. At 09:05:00.000001 it would fall outside the window. Unlike the Day 4 search range, R1 includes BOTH window endpoints. The success at 09:04 does not remove evidence of earlier failures.

Our sample file deliberately lists events out of time order. The detector sorts by event time, so line order does not change the result. Events with the same timestamp are counted together; we do not pretend to know which happened first.

## 3. Open PowerShell

```powershell
Set-Location 'C:\Users\Dell\Desktop\Projects\SentinelLab'
```

I already created and ran the Day 6 sample. To recreate it on a new checkout, import:

```powershell
& ./.venv/bin/python.exe scripts/database.py import data/samples/day06_repeated_failures.jsonl --database data/runtime/day06_demo.db
```

Expected on a fresh database: 6 inserted. On this laptop after today's demonstration: 0 inserted, 6 duplicates. This database is separate from your Day 5 browser demo. No real login attempts or network attacks are performed; the file is synthetic data.

## 4. Run R1

```powershell
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day06_demo.db --json
```

Expected: events_scanned = 6, alert_count = 1, failure_count = 5. Only R1 is evaluated. The success is scanned but does not contribute to failure_count. All commands work without third-party packages or environment activation on this laptop. Follow SETUP.md for other Python layouts.

Read the alert: rule_id identifies R1; rule_version states the policy version; parameters explain 5 events/300 seconds; group identifies the username and IP; triggered_at is the event time where the threshold was met. reason explains why the alert exists. evidence lists the contributing records.

The alert_id is a stable identifier built from the rule and evidence. Repeating detection on the same records returns the same ID. This does not mean alerts have been saved in a new table: persistent alert storage is still pending.

## 5. Open supporting evidence

Choose an internal_id from the evidence list and use it with the SAME database. On the freshly imported supplied sample, the first failure has internal ID 2:

```powershell
& ./.venv/bin/python.exe scripts/database.py get 2 --database data/runtime/day06_demo.db --json
```

Expected: day06-failure-1 and its original accepted text. Your own database may use different internal IDs; copy the ID actually shown by detection. Source event IDs stay separate from SQLite row IDs.

## 6. Compare normal sample activity

```powershell
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day05_demo.db --json
```

Expected for the unchanged Day 5 demo: 3 scanned, 0 alerts. It contains only 2 failures. Zero R1 alerts means this particular pattern was not found; it does not prove the system is safe.

## 7. Avoid repeated alerts for one burst

After an alert, the group is temporarily disarmed while at least 5 failures remain in its window. Further failures in that continuous burst do not produce another preview. When old failures expire and fewer than 5 remain before new arrivals, the group can trigger again.

Roman Urdu: Ek hi lagataar burst par har failure ka naya alert nahin banate. Jab purane failures window se nikal jaayen aur count kam ho, to naya burst dobara alert bana sakta hai.

An alert keeps the evidence present when it triggered. It does not grow to include the rest of a long burst. There is no separate fixed cooldown timer. Full details and planned R2/R3 policies are in DETECTION_RULES.md.

## 8. Verification and limits

```powershell
& ./.venv/bin/python.exe scripts/run_tests.py
```

Expected: 83 tests pass, including 16 new R1 tests. They cover threshold boundaries, exact time limits, ties, shuffled imports, different accounts/IPs, successes, repeated imports/conflicts, rearming, stable IDs, preserved database bytes, and command-line behavior.

Detection currently supports databases with at most 10,000 total events. Larger databases fail clearly without partial results. Missing databases are not created. Exit 0 means evaluation succeeded, with or without alerts. Exit 2 means an error; read its message. No background monitoring occurs.

Forgotten passwords and faulty clients can also trigger R1. In an investigation, check the timing, source context, successes, and account activity before deciding what happened. Do not treat this demo as measured real-world detection accuracy.

## Your part: reply in this chat

1. Would 4 failures for the same username/IP within five minutes trigger R1?
2. Would 5 failures at 09:00, 09:01, 09:02, 09:03, and 09:05 trigger it?
3. Why should an alert include the original event references?

Next session: Start SentinelLab Day 7. Explain each step in simple English and Roman Urdu when needed.

# Day 9: browser detection and saved evidence

Completed September 30, 2026. Project deadline: October 17, 2026.

## Purpose

You can now check stored events from the browser, save the findings, open an alert, and follow its evidence back to an original login record. You can also see what each completed detection run found. The existing rules have not changed.

Roman Urdu: Aaj hum ne browser ko detection aur saved alerts ke saath jora hai. Ab aap button daba kar check chala sakte hain, phir alert ki wajah aur asal login record dekh sakte hain.

## Five useful words

| Word | Meaning | Example |
| --- | --- | --- |
| Event | One recorded action | One failed login |
| Rule | A condition for a suspicious pattern | Five failures for the same account/IP in five minutes |
| Alert | A saved finding when a rule matches | R1 repeated account failures |
| Run | One completed check | One successful press of Run detection and save |
| Evidence | Records explaining the finding | The failures that caused R1 |

An alert is not proof of hacking. Someone may repeatedly enter the wrong password, then log in successfully. Investigate the evidence and surrounding context before concluding compromise. Analyst investigation decisions are not yet stored by this project.

Days 1-5 established validation, SQLite storage, search, originals, and the browser. Days 6-7 added R1/R2/R3. Day 8 saved permanent alert snapshots and run history through command-line tools. Day 9 connects those services to browser controls. No new dependencies are required.

## Step 1: open the project

In PowerShell:

```powershell
Set-Location 'C:\Users\Dell\Desktop\Projects\SentinelLab'
```

This changes the working folder. It does not move files. The project remains in Desktop > Projects > SentinelLab.

## Step 2: open the demonstration

The running demonstration uses http://127.0.0.1:8769 and the separate ignored database data/runtime/day09_demo.db. At the end of verification it has 16 synthetic events, 1 import, 3 alerts, and 2 runs. Further saves increase the run count.

If the server is not running, start it from the project folder:

```powershell
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day09_demo.db --port 8769
```

Keep PowerShell open. Ctrl+C stops a foreground server without deleting data. The assistant's server may already be running in the background. If the port is busy, first try the existing page.

For a fresh checkout, the ignored database is absent. Reproduce the example with a new practice database, importing the published sample once:

```powershell
& ./.venv/bin/python.exe scripts/database.py import data/samples/day07_all_rules.jsonl --database data/runtime/day09_practice.db
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day09_practice.db --port 8771
```

Open http://127.0.0.1:8771. A freshly imported database starts with 16 events and zero saved alerts/runs. These are synthetic records. Earlier demonstration databases remain separate.

## Step 3: understand the page

Navigation links jump to Import, Events, Detection, Saved alerts, and Run history. Event search filters only affect the event table. Detection checks the complete stored dataset, not just visible search results. Uploading records does not automatically run detection; press the explicit save button when ready.

## Step 4: run the rules

In Detection, leave Rules on All rules and press Run detection and save. Or select one rule:

| Rule | Pattern | Default threshold |
| --- | --- | --- |
| R1 | Repeated failures for the same exact username/IP | 5 failures in an inclusive 300-second window |
| R2 | Failures across distinct usernames from one IP | 10 distinct usernames in an inclusive 600-second window |
| R3 | Success after earlier failures for the same username/IP | 5 earlier failures within 300 seconds; equal-time failures excluded |

R1 counts failed events, not alerts. R2 counts distinct usernames, not repeated attempts against just one username. DETECTION_RULES.md explains timestamp ties, grouping, and episode rearming precisely.

The button saves a completed run. For an event-only database it also creates the alert/history tables in the same transaction. A transaction means the related changes succeed together or roll back together; a failed attempt must not leave half a run saved.

The first all-rules save on the fresh practice database should show 16 checked, 3 new, 0 already saved, and 3 total saved alerts. On the already verified Day 9 demo, the next save should show 0 new and 3 already saved.

## Step 5: read counts correctly

| Count | Meaning |
| --- | --- |
| Events checked | Stored events in the evaluated snapshot |
| Matched | Findings produced by this run's selected rules |
| New | Findings newly saved permanently |
| Existing | Matching findings already saved earlier |
| Total saved alerts | All unique saved findings, including historical results |
| Completed runs | Successful save operations |

Run 1 finds and saves 3 findings. Run 2 checks identical data and recognizes the same 3 findings. The result is 3 alerts and 2 runs. New + Existing equals Matched for a run. Total saved alerts need not equal the number matched by a selected-rule run.

Roman Urdu: Run aik dafa check chalane ka record hai. Alert suspicious activity ka result hai. Wohi data dobara check karne par run barhta hai, lekin wohi alert dobara save nahi hota.

A successful run may match zero alerts. This is not necessarily an error, and does not prove that every possible attack was absent. These rules cover only specific patterns.

## Step 6: open an alert

Select Open R3 alert. Its details show the stable alert ID, rule version, account, IP, threshold, failure count, first event time, trigger time, first saved run, and explanation. Times are UTC.

In this demo, R3 concerns lab_user at 192.0.2.71. It contains five preceding failures and one triggering success. The explanation notes that someone correcting a password can cause this pattern. The first saved run stays 1 even when you open the same alert from run 2. Opening details is read-only.

## Step 7: inspect original evidence

In R3's evidence table, select Original #16. The original panel shows day07-success, outcome success, lab_user, 192.0.2.71, and the exact original JSON. First import and line number show where the record entered this database.

Internal ID 16 belongs to this database. Different import orders or databases may assign another number. Source and event_id identify the synthetic source record across demonstrations.

Roman Urdu: Alert humein wajah batata hai. Original record woh asal data dikhata hai jis par alert bana. Sirf alert ka naam dekh kar hacking confirm nahi karni.

## Step 8: read run history

Run history shows time, selected rule versions/settings, scanned/matched/new/existing counts, and a findings button. Select Alerts from run 2. It still shows three findings even though that run added zero new alerts: existing alerts were found again and linked to run 2. This filter uses run membership, not the first saved run.

Show all alerts removes the run filter. Refresh history reloads counts and starts lists at their first page. Reading these views or reloading the page never creates a run. Saved data survives a browser reload.

## Step 9: pages and snapshots

The browser shows 10 alerts/runs per page and 25 evidence references per page. Previous/Next controls are disabled when there is no page in that direction. APIs allow at most 200 items per page.

A saved alert keeps the evidence present at its trigger. Late imports do not rewrite it. Changed findings may produce new alerts alongside historical ones. Retaining an old snapshot does not declare it resolved. Separate list requests use offsets, so concurrent new saves can shift positions; Refresh history starts again from the beginning. There is no continuous monitoring or automatic background refresh.

## How the code handles a click

1. The browser sends the selected rule to POST /api/detect with its write token.
2. The server checks host, origin, token, content type, and request size.
3. save_detection opens one transaction and reads one bounded event snapshot.
4. The selected rules evaluate that snapshot using unchanged policies.
5. Storage records the run, new snapshots, evidence links, and membership of every matched alert. Existing unchanged alerts are reused.
6. It commits everything together; failures roll back that attempt.
7. The browser displays counts and reads the saved lists through GET requests.
8. Alert details retrieve a bounded evidence page; Original buttons use the existing event API.

The page token helps prevent unwanted cross-site writes. It is not analyst authentication. Local users/processes able to read the page can obtain it. Accounts, roles, and public deployment remain unfinished.

## Day 9 file responsibilities

| File | Job |
| --- | --- |
| src/sentinellab/storage/alerts.py | Run-membership filter, next-page information, bounded evidence responses; existing atomic saving remains authoritative |
| src/sentinellab/web/server.py | New read APIs, protected detection POST, two additional allowlisted assets |
| src/sentinellab/web/templates/index.html | Detection form, alert/details tables, history, navigation |
| src/sentinellab/web/static/app.js | Shared busy state and focus/scroll to originals |
| src/sentinellab/web/static/alerts.js | API calls, safe text rendering, selection, paging, stale-response handling |
| src/sentinellab/web/static/alerts.css | New controls, facts, responsive tables |
| tests/integration/test_web_alerts.py | Thirteen real HTTP/SQLite integration cases |
| docs/WEB.md and docs/ALERT_STORAGE.md | API/storage behavior and limits |
| docs/DAY_09_GUIDE.md | This lesson |
| README.md, SETUP.md, PROGRESS.md, NEXT_SESSION.md, ACCEPTANCE_CRITERIA.md, DETECTION_RULES.md | Updated status, instructions, continuity, verification, and scope; these Markdown files except README are under docs |

## Verification

All 133 automated tests pass. Thirteen new tests cover repeat/selected/empty saves, no detection on upload, read-only history, list/evidence paging, original links, invalid inputs, write protection, failure rollback, bounded large evidence, and asset access.

Browser checks verified first/repeated saves, run-2 membership, R3 details, the original success, reload persistence, and desktop/narrow layouts without page-level horizontal overflow. Larger evidence/list pagination is covered by HTTP integration tests. No browser console errors were observed in this workflow. This is component verification, not production security or measured detection accuracy.

Run tests from the project folder:

```powershell
& ./.venv/bin/python.exe scripts/run_tests.py
```

## Troubleshooting

- Page unavailable: check the server and exact 127.0.0.1 port.
- Old page/token: restart after Python changes, then refresh the browser.
- Zero saved alerts: importing does not run detection; the chosen rule may also find nothing.
- Zero new and some existing: the software recognized saved findings and avoided duplicates.
- Limit error: over 10,000 events or 100,000 combined evidence references fails the complete run, not a partial save.
- Connection lost during save: Refresh history before retrying. The server may have committed even if its response was lost. Retrying can add a run while unchanged alerts remain deduplicated.
- Wide table on a narrow screen: scroll inside the table to reach remaining columns.

## Your practice and the next checkpoint

Open R3 and its successful-login original. Explain event, alert, and run in your own words. Answer directly in this project chat; no separate file is needed.

One question: a check shows 0 new alerts and 3 already saved. Did detection fail, or recognize the same findings? Explain why.

Day 10 is planned to begin investigation storage: link a saved alert to a case and preserve analyst notes/status history separately from immutable evidence. We must specify and test it first. Authentication, exports, broader evaluation, and portfolio presentation remain future work. Say: Start SentinelLab Day 10. Explain each step in simple English and Roman Urdu when needed.

GitHub publication is verified separately after checks. Local Git HEAD/index remain behind because of the existing Windows metadata restriction. Connector publication does not synchronize local Git metadata. Do not reset the working folder to resolve that mismatch.

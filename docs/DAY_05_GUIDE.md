# Day 5: SentinelLab in your browser

Today we built a local page for importing, searching, and inspecting login events. You can now use buttons and forms instead of typing a separate command for each operation. Attack detection and analyst sign-in are still future work. The project deadline remains October 17, 2026.

## 1. Understand the three parts

Frontend: the page you see, written in HTML (structure), CSS (appearance), and JavaScript (button actions and updates).

Backend: Python receives the page's requests, validates input, and calls our existing import/search functions. An API is the agreed set of requests and responses between the browser and Python.

Database: SQLite keeps the records on disk, so closing the page does not erase them.

Roman Urdu: Frontend woh page hai jo aap dekhte hain. Backend peeche kaam karta hai. Database records ko sambhal kar rakhta hai. Browser band karne se saved records delete nahin hote.

Flow: choose file -> browser sends bytes -> Python checks records -> SQLite stores accepted events -> browser shows counts.

## 2. Start the page

I created the files and tested the app. If the preview is already open and working, use it. Otherwise open PowerShell and paste:

```powershell
Set-Location 'C:\Users\Dell\Desktop\Projects\SentinelLab'
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day05_demo.db
```

Keep that PowerShell window open. Visit http://127.0.0.1:8765 in your browser. 127.0.0.1 means this computer. The page is not published on the internet. No extra packages or activation script are needed on this laptop; other computers should follow SETUP.md to choose their Python path.

Expected: SentinelLab, an import section, search filters, and an event table. Starting with a fresh database creates empty tables without adding a fake import. Today's verified demo has 3 events and 2 imports. The separate Day 3 database remains unchanged.

## 3. Import a sample

Click Choose a lab file. Select:

```text
C:\Users\Dell\Desktop\Projects\SentinelLab\data\samples\day01_login_events.jsonl
```

Click Import records. On an empty database, expected: 3 saved. On this laptop's already tested demo, expected: 0 saved and 3 duplicates. The saved-event count remains 3; the completed-import count increases by 1. An import is one completed attempt to process a file, not one event or alert.

The .jsonl file has one JSON record per line. Browser upload sends a copy to the local Python server. We do not move or edit the original sample. A temporary copy is removed after processing. Accepted original records remain in SQLite as evidence.

Roman Urdu: Same file dobara import karne par wohi events dobara save nahin hote. Duplicate ka matlab hai ke woh record pehle se mojood hai.

## 4. Find failed logins

Under Login result select Failure, then click Search events. Expected: 2 matching records. Change it to Success and search again: expected 1. You can also supply username demo_user and source IP 192.0.2.10; every supplied condition must match.

For time filtering, use From 2026-09-24T09:00:00Z and Until 2026-09-24T09:01:00Z with All results. Expected: demo-001 only. Start is included; end is excluded. Z means UTC. Read DAY_04_GUIDE.md for timezone examples.

Clear filters returns to all records. Rows per page limits how many you see at once. Previous/Next are disabled when there is no corresponding page. Finish paging before importing additional data because new records can change page positions.

## 5. Inspect evidence

Click View #1. The evidence panel shows normalized fields plus original_record, first_import_id, and first_line_number. The original lets you compare our displayed record with what was first accepted. The import ID and line number explain where it came from.

We display log values as text. Even if a username looks like HTML, the page must not run it as code. This prevents a stored log value from turning into a script in our page. Request checks and output handling are described in WEB.md.

## 6. Try an invalid line

Select data/samples/day02_mixed_events.jsonl and import it. After the Day 1 sample, expected: 0 saved, 2 duplicates, 1 rejected, 1 blank line. Open View import counts and line errors. Line 2 has an invalid outcome. Later valid records are still checked.

A rejected record is a format problem; a conflict means an event identity already exists with different values. In either case, the app preserves existing evidence. Neither count is an attack alert.

## 7. What we tested

```powershell
& ./.venv/bin/python.exe scripts/run_tests.py
```

Expected: 67 passing tests, including real local HTTP requests. Tests cover import/search/lookup, duplicates/conflicts, invalid filters, upload limits, blocked cross-site requests, original preservation, and the dropdown regression found during browser testing.

Browser checks covered good/mixed imports, failure filtering, original evidence, invalid-IP messages, 27-record pagination in a separate test database, and HTML-like text rendering without an injected image. Desktop and narrow-screen layouts were inspected. These are development checks, not a complete production security assessment.

## 8. Stop and restart

In the PowerShell window running the server, press Ctrl+C. The page stops responding, but saved events remain. Repeat the start command when needed. Do not start a second copy on the same port.

If the assistant-started preview is still running, use it; ask here to stop it when finished.

## Troubleshooting

- Cannot start: the port might already be in use. Try the existing page first. Alternatively add --port 8767 and open http://127.0.0.1:8767.
- Cannot connect: start Python and keep its terminal open. Use the displayed 127.0.0.1 address exactly.
- Refresh the local page before importing: the server restarted and its request token changed. Reload the browser.
- File too large: maximum 2 MiB, 10,000 physical lines, 16 KiB per line. Keep practice data small.
- No results: clear filters and retry; check username case, IP, and timezone.
- Choose File does nothing in an embedded preview: open the same local address in your normal browser.

## Your part today

Try Failure -> Search events -> View #1. Then answer in this chat:

1. Which part do you see: frontend, backend, or database?
2. If the same sample is imported twice, should saved events double?
3. Does a failed login automatically mean an account was hacked?

No need to memorize the code. Understand the flow and explain the evidence. Next: Start SentinelLab Day 6. Explain each step in simple English and Roman Urdu when needed.

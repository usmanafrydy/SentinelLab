# Day 13 - Exporting an investigation report

Checkpoint date: 3 October 2026. Target project completion: 17 October 2026. Today adds reports to the existing project. It does not finish the final release or prove detection accuracy on real attacks.

## 1. What we built today

You can now open a saved investigation and download it as Markdown or JSON. You can also export the same information from PowerShell. A report includes the case, its saved conclusion, complete action history, the saved alert and rule settings, and the original records linked to that alert.

Before today, those details were available in different parts of the application. Now they can travel together in one file. For example, you can review a synthetic case away from the running server or use it in a portfolio demonstration. The report remains a copy: it does not close the case, save your unfinished typing, run detection again, or edit evidence.

Roman Urdu: Report aap ki saved investigation ki copy hai. Is mein notes aur evidence aik jagah milte hain. Report banana account hack honay ka saboot nahi hai.

## 2. The concepts in simple English

**Export** means take saved information out of the program and put it in a file. It does not mean delete the information from the program. You can continue working on the case after exporting.

**Markdown** is a text format with simple headings. Our .md report has clear section headings and code-style blocks containing the exact values. A Markdown viewer can display the headings neatly. Notepad can still open the file as text. We deliberately keep stored notes and evidence inside code blocks so they do not become active HTML, links or new report headings.

**JSON** is a structured format for programs. It uses named fields, objects in curly brackets, and lists in square brackets. For example, "status": "in_progress" tells another program the saved case status. JSON is also readable by people, but the Markdown headings make navigation easier. These are investigation exports; they are separate from your Word learning handbook.

**Snapshot** means a consistent view of saved data at one moment. Imagine taking a photograph of the case and all its records together. If someone adds a note while the report is being prepared, the report must not combine the old case revision with the new history. Every report query uses the same SQLite read transaction. Roman Urdu: Aik report mein mukhtalif waqt ki aadhi aadhi information mix nahi honi chahiye.

**Revision** is the case's change number. Creating a case starts revision 1. Each saved note or decision increases it. If your page shows revision 5 but the database has revision 6, the browser export asks you to refresh and review. That prevents you from unknowingly downloading a different saved version. A concurrent change after the snapshot begins belongs to a later report.

**Serialization** means turning stored values into file text. Newlines and quotation marks may appear as escape sequences such as \n and \" in JSON. These sequences preserve the original values; a JSON reader restores them. We do not edit the underlying original_record string. Database-local identifiers and revisions become decimal strings, such as "9007199254740999", so software using JavaScript does not round large IDs.

**Provenance** means information about where a stored record came from. Each linked original has its first import ID, first line number and import time. These help you trace it within this database. They are not a legal chain of custody or proof that nobody edited the database directly.

**Bounds** are maximum allowed sizes. One export permits up to 1,000 actions and 1,000 linked events, with 8 MiB of selected source values and 16 MiB of encoded output. If a case is too large, the whole export fails with a message. It never silently drops the remaining evidence. A browser page may show only ten actions; the report still includes the full history within these limits.

## 3. What is inside the report

| Section | Meaning and purpose |
| --- | --- |
| Report details | Format version 1.0 and the UTC time the report was prepared. Export time is not the login time. |
| Case and analyst conclusion | Case ID, alert link, title, status, disposition, revision, creation time and latest update time. The conclusion is the analyst's judgment. |
| Saved alert and rule details | Alert ID, rule ID/version, threshold/window, grouping values, event interval, trigger time, reason, and complete saved evidence references. R2 account information is retained. |
| First detection run | When the alert was first saved, the rules/configurations in that run, counts and event/import high-water marks. This is not a list of every later run. |
| Complete action history | Creation, notes and reasoned decisions in revision order, including author labels and before/after state. Earlier notes remain visible after a correction. |
| Linked original evidence | Each event's normalized search values, stored original_record text, evidence position/role and first-import provenance. Unrelated database events are not included. |
| Limitations | Explains uncertainty, private content, historical labels, saved-only scope and lack of signing/encryption/tamper-proof guarantees. |

For the existing R3 sample, five earlier failures and one success explain the finding. A success after failures may mean an attacker guessed a password, but it can also mean the real user corrected a mistake. The report repeats the saved evidence and conclusion. It does not decide which story is true for you.

## 4. Every implementation step and why it matters

First, we compared all 109 published Day 12 files with the local project. They matched. This protected the work already done and established the correct parent for publishing today's changes.

Second, we wrote REPORTS.md before implementing the feature. This defines what is included, the read-only behavior, limits, privacy handling, stale-revision response and verification plan. A written contract makes it possible to test behavior rather than just check that a button exists.

Third, we created reports.py. It validates numeric input and opens the existing database read-only. Version 1 or 2 has no saved cases, so it returns no case without upgrading the database. For version 3, it reads the case, alert, first run, history and linked evidence using one connection and one transaction.

Fourth, the service checks row counts and byte sizes before loading selected data. It checks required links, evidence order and history continuity. A missing original or inconsistent history stops the export. This catches broken relationships; it cannot detect a coordinated edit that changes all related records consistently.

Fifth, we added both renderers. JSON uses reversible escaping and fixed field names. Markdown uses headings written by the application and fences longer than any run of backticks inside the data. Therefore a note containing fake headings or HTML stays report content. No HTML preview or embedded script is generated.

Sixth, we added the HTTP download route. It uses the same existing sign-in and local-request protections as the workspace. The requested case revision must match. Successful replies use attachment filenames containing only numeric case/revision values and a fixed extension. Error replies remain error messages; the browser does not save them as report files.

Seventh, we added Download Markdown and Download JSON to the case detail panel. The text explains which format to choose, what is included, and why drafts are excluded. The controls are unavailable while the case is loading or a case write is in progress. Download errors do not clear the note or reason boxes.

Eighth, we added export_report.py for PowerShell. It uses the same snapshot/renderer and creates a new file exclusively. Existing files cannot be overwritten. Output must stay under the ignored reports/generated directory. If a normal write or close fails after creation, the new incomplete file is removed. Sudden process/power failure can still leave a partial file.

Ninth, we tested the services, HTTP boundary, browser controls and actual downloaded files. We also checked the narrow layout. Finally, we updated the guides and both cumulative handbook formats. Publication uses the connected GitHub service because the existing Windows restriction still prevents synchronizing local Git metadata normally.

## 5. Files added or changed today

| File | Responsibility |
| --- | --- |
| src/sentinellab/reports.py | Reads one bounded snapshot, checks relationships, converts IDs without precision loss, renders JSON/Markdown, and creates safe attachment names. |
| scripts/export_report.py | PowerShell entry point; validates the output location, refuses overwrite and handles file-write failures. |
| src/sentinellab/web/server.py | Adds the authenticated report route, strict format/revision query checks, attachment header and HTTP 409 response. |
| src/sentinellab/web/static/cases.js | Connects buttons to downloads, handles session/errors, shows progress and preserves drafts. |
| src/sentinellab/web/templates/index.html | Adds report guidance/buttons/status text and updates the checkpoint badge. |
| src/sentinellab/web/templates/login.html | Updates the visible checkpoint badge; sign-in behavior is unchanged. |
| tests/integration/test_reports.py | Sixteen tests cover report contents, consistency, limits, hostile text, read-only behavior, CLI output and protected HTTP downloads. |
| docs/REPORTS.md | Exact report contract for future development. |
| docs/DAY_13_GUIDE.md | This easy-English lesson, concepts, operating steps and troubleshooting. |
| README.md and docs/SETUP.md | Update current capabilities, guide links and the Day 13 startup/export examples. |
| docs/WEB.md and docs/ACCEPTANCE_CRITERIA.md | Record the download API and evidence toward AC-10, without claiming the whole release is accepted. |
| docs/PROGRESS.md and docs/NEXT_SESSION.md | Record checks, current demonstration state, remaining limits and the next checkpoint. |
| docs/SENTINELLAB_HANDBOOK.md and docs/SentinelLab_Project_Handbook.docx | Update the current completion map and append the detailed Day 13 explanation, preserving earlier lessons. |

No database table was added today. The existing events, saved_alerts, detection_runs, alert_evidence, investigations and investigation_actions tables already contain the necessary information. reports/generated is an ignored local output directory; its private reports are not project source and are not published.

## 6. Your browser exercise

1. Open the Day 13 address http://127.0.0.1:8774/ while the local server is running. Sign in with your existing usman account. Do not create the account again or send the password in chat.
2. Choose Investigations in the navigation. Open case 1. Read the saved status, conclusion and revision. The prepared continuation copied Day 12's database consistently; it starts with 16 events, one import, three alerts, one run and one case at revision 5. Your later saved work can change these counts.
3. Open the linked alert and evidence if you need to remind yourself what happened. A report should be understood before it is shared.
4. Save a note or decision only if you actually want that change recorded. Text still sitting in an input box is not saved. Simply exporting does not save it.
5. In the case detail panel, choose Download Markdown. Check your browser downloads, usually the Windows Downloads directory. A filename such as sentinellab-case-1-rev-5.md identifies the saved case version.
6. Open the file in a text editor or Markdown viewer. Find the case conclusion, alert reason, notes and original evidence. Notice that all saved actions are included even if the page showed only its first history page.
7. Choose Download JSON and compare the same sections. You do not need to understand every bracket today. Start with case, actions, evidence and limitations.
8. If the page says the case changed, select Refresh selected case, review the new history and retry. Your text boxes remain in this page, but a full browser reload loses unsaved drafts.

Roman Urdu: Pehle saved status aur evidence dekhein. Phir report download karein. Agar case kisi aur jagah update hua ho, refresh karke dobara parhein. Report share karne se pehle private information check karein.

## 7. Start the server only if it is stopped

Open PowerShell. Copy the following commands. If this address already works, leave the running server alone rather than launching another copy.

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/serve.py --database data/runtime/day13_demo.db --port 8774 --credentials secrets/analyst.json
```

The local prepared Day 13 database is separate from previous demos. For continued Day 13 work, keep using day13_demo.db; changes made to old day12_demo.db afterward do not automatically copy across. Port 8775 and day13_qa.db are isolated automated/browser QA data and are not your working demo. The private credential file is reused locally and never published.

## 8. Optional PowerShell exports

The browser is enough for today's exercise. These commands show how the same service works without the browser:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/export_report.py --database data/runtime/day13_demo.db --case-id 1 --format markdown
.\.venv\bin\python.exe scripts/export_report.py --database data/runtime/day13_demo.db --case-id 1 --format json
```

--database selects your saved database, --case-id selects the investigation, and --format selects the output representation. A successful command prints the saved path, number of bytes and revision. The default filename includes the case ID and revision. An unchanged second export with that filename is refused; it will not overwrite the first report.

To deliberately create another copy, choose an unused name under the allowed directory:

```powershell
.\.venv\bin\python.exe scripts/export_report.py --database data/runtime/day13_demo.db --case-id 1 --format json --output reports/generated/my-second-review.json
```

You can add --expected-revision 5 when you specifically want revision 5. If the saved case has changed, the command fails. Without that option, CLI exports the current saved snapshot. CLI access relies on laptop file permissions; it does not ask for your browser password.

## 9. What we checked

The full suite now has 184 passing tests: the previous 168 plus sixteen report tests. Run it with .\.venv\bin\python.exe scripts/run_tests.py. The JavaScript syntax check also passed.

The new tests compare exported fields against stored alert details, history and exact original_record values; check R1/R2/R3 parameters and evidence roles; include history longer than a browser page and a closed/benign conclusion; reject stale/invalid IDs; preserve database bytes; avoid migration of older schemas; preserve very large case IDs; reject oversized and broken records; and refuse invalid formats.

A concurrent-update test uses SQLite WAL mode so another connection can add a note while export is reading. The resulting report keeps the earlier case and earlier history together. Separate tests prove that hostile Markdown/HTML text stays data, CLI cannot overwrite an existing file or write outside its private directory, and a simulated file-close failure removes the new incomplete file.

HTTP tests check authenticated attachments, fixed filenames, no-store/nosniff headers, missing cases, invalid/repeated query parameters, stale revisions, anonymous access, expired sessions and cross-site requests. Browser checks downloaded both files and compared their contents with the saved QA database. Unsaved draft text was excluded and retained in the form. A separate QA update caused the expected refresh message; signing out in another tab blocked a subsequent download and kept the draft. Desktop and 390-pixel layouts showed the controls without page-level horizontal overflow. No browser console errors were observed in the checked flow.

These tests support the local prototype's behavior. They do not establish real-world detection accuracy or public-server security. Word content/structure checks are separate from code tests; the bundled Word renderer remains unavailable because LibreOffice is missing, so page layout is not claimed as visually verified.

## 10. Common problems and their meaning

**There is no download section:** open a case, not only an alert. A report belongs to an investigation. Make sure you opened the Day 13 server address rather than an older process running previous Python code.

**Case changed:** another saved action increased the revision. Refresh the selected case and read the change before exporting again. This is protection against misunderstanding which saved version you are reviewing.

**Session ended:** use the sign-in link. Your unsaved form text remains in the existing tab. Sign-in in another tab restores access, but reload the existing page only after saving/copying any draft you want to keep.

**No file is obvious after clicking:** check the browser's download list and Downloads folder. The success text says a download was requested, not that the operating system definitely saved it. Browser settings may choose another directory or ask where to save. The automated browser download-event helper did not observe our blob download, but the files were present in Downloads and their contents were verified.

**Cannot create report in PowerShell:** the default file may already exist. Choose a new name under reports/generated and ensure its parent directory exists. Do not overwrite earlier evidence reports just to make an error disappear.

**Report exceeds a limit:** nothing was partially exported. The current report feature is deliberately bounded. Preserve the case; a reviewed larger-export design is future work, not a reason to delete evidence.

**Linked records are inconsistent:** preserve the database and investigate the problem. The exporter refuses to pretend the missing information was not needed. Do not manually edit the database to hide the error.

## 11. Remaining limits and next work

Reports contain saved originals and notes without automatic redaction. Review content before sharing. Git ignores reports/generated, reports/private, runtime databases and credentials; browser downloads are outside the repository. A public portfolio should use synthetic demonstrations only. The report is neither digitally signed nor encrypted. Anyone who can directly alter the local database can undermine its history.

Markdown renders the exact values in fenced blocks rather than a designed PDF. The Word handbook teaches how the application works; it is not generated per investigation. Multi-case report bundles, scheduled emailing, PDF report design, live collectors, multiple accounts and public hosting are not implemented by this checkpoint.

The next proposed checkpoint is a focused interface and navigation improvement: make the main workflow easier to follow, reduce scrolling and preserve beginner explanations, authentication and report behavior. After that, we still need held-out scenario evaluation, a fresh-setup rehearsal, release checks, a demonstration, portfolio write-up and honest CV bullets. The deadline remains 17 October.

## 12. One learning question

You type a new note but do not click Save note. Then you download a report. Should that unfinished note appear in the report? Explain why in your own words. You can answer in this chat, in English or Roman Urdu.

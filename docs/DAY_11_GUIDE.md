# Day 11 - Investigations in your browser

Completed October 2, 2026. Project: C:\Users\Dell\Desktop\Projects\SentinelLab.

## What you can do today

You can open a saved alert, create its investigation case, write observations, record a decision with a reason, and read the history in your browser. Day 10 built the storage and commands; Day 11 connects those same rules to buttons and forms. No detection thresholds have changed.

Roman Urdu: Alert humein shak wali activity dikhata hai. Case mein hum us activity ki jaanch, notes aur faisla record karte hain. Sirf alert aane ka matlab hacking confirm hona nahi hai.

## Step 1 - Open the demonstration

Open http://127.0.0.1:8771/ while the Day 11 server is running. This uses data/runtime/day11_demo.db, separate from older demonstrations. It contains 16 synthetic login records, one import, three saved alerts and one detection run. Browser verification created case 1 with five actions, ending In progress / Suspicious at revision 5. Your later actions will change those case counts and revisions.

If the page does not open, run these commands in PowerShell:

```powershell
Set-Location "C:\Users\Dell\Desktop\Projects\SentinelLab"
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day11_demo.db --port 8771
```

Keep that terminal running. Ctrl+C stops a server started in that terminal. If the port is already in use, open the existing page first. Do not stop unrelated programs. A restart changes the page's request token, so reload the browser before saving again.

On a new checkout, the database is not downloaded from GitHub. Import data/samples/day07_all_rules.jsonl through the browser and press Run detection and save once. Importing alone does not run detection.

## Step 2 - Read the alert and originals

Use Saved alerts in the navigation. Choose Open R3 alert. Read its explanation: five earlier failures were followed by a success for the same username and IP within the configured time window. Review its six evidence references. Original #16 opens the successful login in this demonstration; record IDs can differ in other databases.

Purpose: understand why the detector matched before writing an opinion. The rule cannot tell whether someone corrected their own password or an attacker succeeded. Other context would be needed. An original record is retained evidence; an investigation note is your interpretation.

Expected result: the saved alert and original event can be viewed without changing either one.

## Step 3 - Start or open the investigation

Choose Investigate this alert. The form shows the exact linked alert. Keep or edit the proposed short title, enter an author label such as lab_analyst, and choose Create or open case.

A new case starts Open / Undecided at revision 1. If that alert already has a case, the existing case opens with its previous title, status and notes. This does not reopen a closed case or create another copy. The demonstration's R3 case already exists, so you should see case 1.

The author label is just text supplied by the person using the application. It is not a verified account or a login. Do not describe it as authenticated identity in an interview.

## Step 4 - Add an observation

Enter an Author label for notes and decisions. In New note write a specific observation, for example:

> The alert links five failures and one successful login for lab_user from 192.0.2.71. These are synthetic records. More context is needed before confirming compromise.

Press Save note once. The note appears in Case history and the revision increases. Original events and the saved alert do not change. Notes can also be added to closed cases. You cannot edit or delete old notes through the application; add a correction as another note.

Roman Urdu: Jo cheez evidence mein nazar aati hai woh likhein. Andaza aur haqeeqat alag rakhein. Ghalti ho to naya correction note likhein; purani history rehti hai.

## Step 5 - Understand status and conclusion

| Field | Value | Meaning |
|---|---|---|
| Status | Open | A case exists and work can begin. |
| Status | In progress | Someone is investigating. |
| Status | Closed | The current review has ended with a conclusion. |
| Conclusion | Undecided | There is not enough information to decide. |
| Conclusion | Benign | The reviewer considers the activity harmless, with supporting context. |
| Conclusion | Suspicious | The activity needs concern or further investigation; compromise is not confirmed. |
| Conclusion | Confirmed compromise | The reviewer asserts compromise based on supporting evidence. Detection never selects this automatically. |

Status answers "Where is the work?" Conclusion answers "What do we currently think?" They are different. A suspicious case can remain In progress. Closing requires a conclusion other than Undecided. Reopening a closed case requires In progress and Undecided. Every change requires a reason. Saving the same status and conclusion again is rejected; use a note to add observations instead.

To practise a decision on synthetic data, choose a different valid status/conclusion, explain why in Reason for this change, and choose Save decision. Do not label compromise merely to make the portfolio look impressive. The history shows the before and after values and the supplied author label.

## Step 6 - Learn revisions and conflict recovery

A revision is a case version number. Creation is revision 1. Every saved note or decision adds one. If your page read revision 3 and another action created revision 4, saving a decision based on revision 3 must not overwrite newer work.

The browser says the case changed elsewhere and disables Save decision. Your reason is kept. Choose Refresh selected case, read the latest history, choose the appropriate status and conclusion again, then save. Refresh restores the saved dropdown values but keeps your draft note/reason. The warning itself creates no action.

Roman Urdu: Aap ke paas purana version ho to pehle taza information dekhein. System aap ka likha hua reason sambhal kar rakhta hai, lekin naya faisla karne se pehle latest history dekhni hoti hai.

Notes do not require an expected revision: two submitted notes can both be appended. Decisions do require one because an old decision can contradict newer work.

## Step 7 - Find cases and read history

Use Investigations in the navigation. Choose All cases or a status, then Refresh cases. Open case 1 to continue the demonstration. Case lists show newest case first, ten at a time. Previous cases and Next cases move between pages when available.

Inside a case, history is oldest action first, ten at a time. Next actions shows later entries. Each entry has a revision, action type, UTC time, author label, text and resulting state. Open linked alert and evidence returns to the original saved alert. All saved information survives browser reload.

Draft text is different: it exists only in the current page. Switching between cases or refreshing a selected case preserves its draft. Reloading or closing the browser loses unsaved drafts. Save observations you need to retain.

## Step 8 - Handle errors

- Empty/too-long fields: correct the field. Titles allow 120 characters, author labels 80, notes 4000, reasons 1000. Unsupported control characters are rejected.
- Case changed elsewhere: refresh the selected case and review the latest history before saving the decision again.
- Lost connection while saving: refresh and inspect history before retrying. The server may have saved the action even if the reply was lost. Notes do not have automatic retry deduplication.
- No cases match: switch to All cases and refresh. The selected case can still be visible even when it no longer matches a list filter.
- No saved alerts: import the sample and explicitly run detection/save first.
- Narrow display: tables scroll horizontally inside their own boxes. The editor stacks vertically.

## What changed in the code

| File | Responsibility |
|---|---|
| src/sentinellab/storage/cases.py | Existing transaction/state rules; adds a distinct stale-revision error that the web layer can identify. |
| src/sentinellab/web/case_api.py | Validates exact JSON fields and case query parameters, calls the existing services, and sends IDs/revisions as decimal strings to avoid JavaScript number rounding. |
| src/sentinellab/web/server.py | Routes case requests, enforces existing Host/Origin/token checks and body limits, and returns a conflict response for outdated decisions. |
| src/sentinellab/web/templates/index.html | Accessible labels, case forms, help, list and history containers. |
| src/sentinellab/web/static/cases.js | Loads cases/history, saves explicit actions, retains page drafts, and handles refresh conflicts. |
| src/sentinellab/web/static/cases.css | Case layout, editor spacing, timeline and narrow-screen adjustments. |
| src/sentinellab/web/static/alerts.js | Connects an opened saved alert to the investigation form. |
| src/sentinellab/web/static/app.js | Carries structured API error codes to the browser controls. |
| src/sentinellab/web/static/style.css | Gives tables a readable minimum width within scrollable wrappers. |
| tests/integration/test_web_cases.py | Real local HTTP tests for workflow, duplicate prevention, conflicts, rejected writes, paging, read-only requests and rollback. |

Flow: button/form -> JavaScript -> protected local HTTP request -> input validation -> case storage transaction -> SQLite -> JSON response -> updated case and history. A failed transaction rolls back its changes together. Text is displayed as text, never treated as HTML.

## Verification and limits

157 automated tests pass. Day 11 adds eight HTTP tests; earlier storage tests cover concurrent operations, state transitions, migration and process persistence. Browser verification covered creation, notes, decisions, duplicate creation, outdated-decision recovery, preserved draft reasons, linked original evidence, reload persistence, and desktop/narrow layouts. Pagination boundaries are covered by HTTP tests. No browser console errors were observed in the final check.

This remains a local learning prototype. Request tokens are cross-site request protection, not analyst authentication. History is append-only through the application, but a person directly editing the database can tamper with it. No authenticated users, roles, export workflow or final detection evaluation is complete. Runtime databases/logs stay out of GitHub.

## What comes next

Day 12 should review the web stack and define/implement appropriate analyst sign-in and session protection for this local prototype, with tests and clear limits. Reports, broader interface improvements, detection evaluation, portfolio screenshots and final release remain planned. Target completion is October 17, 2026. These are future tasks, not features already delivered.

## Your small exercise

Open case 1 and read its history. Tell me here: if your page shows revision 5 but another note has already created revision 6, what should you do before saving a decision? You can answer in simple English or Roman Urdu.

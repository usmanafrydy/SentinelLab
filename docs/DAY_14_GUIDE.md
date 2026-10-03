# Day 14 - A clearer workspace

Completed 3 October 2026. Target release: 17 October 2026.

## 1. Today's result

SentinelLab now has four main work areas instead of showing every feature in one long page. The desktop has a side navigation panel. A narrow screen has a compact navigation grid. The selected area is highlighted, the heading explains its purpose, and irrelevant sections are hidden.

This addresses the earlier feedback that the interface was basic and difficult to use. The improvement is functional as well as visual: it is easier to find a case, move to its alert, inspect an original record, return, and download a report. We have not measured usability with a group of users, so this is a tested design improvement rather than a measured productivity claim.

Roman Urdu: Pehle sab cheezein aik lambi screen par theen. Ab har kaam ka alag section hai. Jis kaam ki zaroorat ho, us section ko kholein.

## 2. Where each feature lives

| Area | What you do here |
| --- | --- |
| Overview | See saved event/import counts, read the beginner guide and follow the three starting steps. Continue an existing investigation from the highlighted link. |
| Events | Import a synthetic JSON Lines file, search by account/IP/outcome/time, and open an original record. |
| Detection | Deliberately run the rules, review saved alerts and their explanations, and inspect completed run history. |
| Investigations | Open or create cases, write notes, record decisions with reasons, read action history and download reports. |

Original evidence opens in a focused view. Close evidence takes you back to the area and control that opened it when that control is still available. It is a reading view, not an editing form. The side navigation stays associated with the originating area.

The overview counts are saved-data counts, not a live network monitor. The project still processes imported records and runs detection only when requested. Switching sections does not collect new events, run rules or create cases.

## 3. Concepts explained simply

**Navigation** is the set of controls that helps you move around the application. Clear names tell you where to go. Reports are under Investigations because a report describes a saved case.

**Frontend** means the part you see and interact with. HTML describes the content and forms. CSS controls appearance and layout. JavaScript connects interactions to application behavior. The backend remains responsible for validating requests, sign-in, evidence, rules, case changes and exports.

**DOM** is the browser's representation of the page. Think of it as a tree containing headings, forms, buttons and text boxes. We move the existing sections into containers once, then hide or show the containers. We do not destroy and recreate the forms every time you navigate. This is why a draft can remain in its text box.

**State** means the current values and selections the page remembers: a search filter, selected case, current page of history or unfinished note. State in browser memory is different from information saved in SQLite. Navigation retains the former; clicking Save note creates the latter. Reloading or closing the page still loses unsaved drafts.

Roman Urdu: Section badalne se draft rehta hai, lekin draft save nahi hota. Save note dabane par hi note database mein jata hai. Page reload karne se unsaved text khatam ho sakta hai.

**URL fragment** is the part after # in an address, such as #workspace-cases. It identifies a place in the page. The browser history remembers these moves so Back and Forward can switch areas. We use fixed section IDs, not passwords, evidence text or case contents, in these fragments. A copied evidence fragment cannot reconstruct a selected original after a fresh page load.

**Focus** is the element that keyboard input currently reaches. After navigation, focus moves to the relevant heading or control. Close evidence tries to return focus to the button that opened it. A visible focus outline helps keyboard users see where they are. The Skip to workspace link lets them avoid tabbing through the whole menu.

**Responsive layout** adapts to available width. Desktop side navigation becomes a grid below 1,000 pixels; smaller screens use two columns. Tables retain readable columns and scroll inside their own wrapper. A table's horizontal scrolling is different from the entire page overflowing sideways.

**Separation of responsibilities** means each part has a focused job. workspace.js handles navigation; app.js still handles import/search/originals; alerts.js still handles rules/alerts/runs; cases.js still handles investigations and reports. Styling does not determine whether a request is authorized.

## 4. The steps we took

First, we read the saved contracts and compared all 114 Day 13 project files with the published GitHub version. They matched. We retained the existing evidence, rule, session and report contracts.

Second, we wrote NAVIGATION.md before changing the interface. It specifies the four areas, focused evidence view, draft preservation, browser history, keyboard behavior and verification scope.

Third, we added workspace.js before the other deferred application scripts. It creates containers and moves existing sections into them. Only one workspace is displayed at a time. The original section-level hidden flags still decide whether a selected alert or case has been opened.

Fourth, we implemented link handling and Back/Forward recovery. Navigation updates the selected link and page heading. An unknown or unavailable fragment safely returns to Overview. Reloading a case-detail or evidence fragment does not invent a selected record. You reopen the case from its list.

Fifth, we connected existing programmatic actions to navigation. Opening a case reveals Investigations. Opening its linked alert reveals Detection. Opening an original reveals Evidence before moving focus. Closing the original restores its origin. The actual data requests continue using the existing APIs.

Sixth, we improved the visual hierarchy: a dark header, descriptive navigation, clearer overview cards, a highlighted continuation link, a report card and shortcuts for Write a note, Read history and Download report. Text explanations and Roman Urdu guidance remain available.

Seventh, we extended the exact server asset allowlist for workspace.js and workspace.css. This does not expose arbitrary directories. Authenticated workspace/data access and existing POST protections remain unchanged.

Eighth, we ran the regression suite and JavaScript syntax checks, then exercised navigation with the real browser using synthetic QA data. We verified draft/filter retention, browser history, focus restoration, case writes, duplicate-case handling and actual report content. The user demonstration was kept separate from these QA changes.

Finally, we updated this guide, current status, continuity notes, Word handbook and Markdown companion. GitHub publication uses the connector because the existing local Git metadata restriction remains unresolved.

## 5. Files and responsibilities

| File | Day 14 responsibility |
| --- | --- |
| src/sentinellab/web/static/workspace.js | Groups sections; switches views; manages fragments, Back/Forward, current navigation state and focus; returns from evidence. |
| src/sentinellab/web/static/workspace.css | Desktop side navigation, responsive grid, sticky header, overview cards, report card and visible keyboard focus. |
| src/sentinellab/web/templates/index.html | Loads the new assets; adds navigation, skip link, named workspace heading, continuation link and case shortcuts. |
| src/sentinellab/web/templates/login.html | Updates the checkpoint badge to Day 14. Account behavior is unchanged. |
| src/sentinellab/web/static/app.js | Reveals the evidence workspace and returns to the source when it closes. Import/search logic stays in this file. |
| src/sentinellab/web/static/alerts.js | Reveals Detection when an alert/run selection opens and restores a useful focus target when closing an alert. |
| src/sentinellab/web/static/cases.js | Reveals Investigations before focusing a case or the case-creation form. |
| src/sentinellab/web/server.py | Allows the two new static assets by exact path. |
| tests/integration/test_web.py | Extends the existing static-asset delivery check to cover the new files. |
| docs/NAVIGATION.md | Written navigation and state-preservation contract. |
| docs/DAY_14_GUIDE.md | This lesson, file map, operating steps, verification and limits. |
| README.md, docs/SETUP.md, docs/WEB.md | Current capabilities, address, startup and navigation instructions. |
| docs/PROGRESS.md, docs/NEXT_SESSION.md | Completed checks, demonstration details, remaining work and next checkpoint. |
| docs/SentinelLab_Project_Handbook.docx, docs/SENTINELLAB_HANDBOOK.md | Chapter 31 adds Day 14; front matter and chapter 29 completion map reflect the current system. |

No database schema, rule threshold, report format or account credential was changed. No frontend framework, network font, external image or analytics package was added. Existing backend safeguards still decide whether an action is allowed.

## 6. Your practical exercise

1. Open http://127.0.0.1:8776/ while the Day 14 server is running. Sign in using your existing account privately.
2. Start at Overview. Find the four navigation names and read their small descriptions. Expand the beginner explanation if needed.
3. Open Investigations, then Open case 1. The prepared user copy begins with the existing saved case, not the synthetic QA notes added during testing.
4. Choose Write a note and type a short practice draft. Do not save it yet. Switch to Events, then return to Investigations. The same draft should still be there.
5. Open linked alert and evidence. Detection appears. Open an Original button. Read the stored record and select Close evidence. You should return to its source view.
6. Return to Investigations. Save the note only if you want it permanently recorded in the case. A correction requires another note; original notes are retained.
7. Choose Read history to review saved actions. Choose Download report to reach the report card. Export only includes saved work, as explained on Day 13.
8. Try browser Back and Forward. Notice that these navigate the workspace; they do not undo saved notes or decisions.

Roman Urdu: Back dabane ka matlab pichlay section mein jana hai. Is se saved note delete ya undo nahi hota.

## 7. Startup and saved files

If the address is already working, do not start a second server. If it is stopped, open PowerShell and run:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json
```

The Day 14 demonstration is a consistent SQLite backup of day13_demo.db. At preparation it contained 16 events, one import, three alerts, one run and case 1 at revision 5, in_progress/suspicious with five actions. Later user activity can change this state. Continue using day14_demo.db; separate older databases do not synchronize automatically. QA uses port 8777 and day14_qa.db, with synthetic credentials and observations.

The project remains at C:\Users\Dell\Desktop\Projects\SentinelLab. Browser downloads go to the browser-selected folder. Private CLI reports stay below reports/generated. Credentials, runtime databases and generated reports are excluded from GitHub.

## 8. Verification results

All 184 automated tests pass. The count stays 184 because this checkpoint extends an existing asset test rather than adding tests that merely repeat the markup. JavaScript syntax checks pass. Backend regression tests remain distinct from the interactive navigation checks.

Browser verification covered the four-area layout, case-to-alert-to-original navigation, returning focus to Original #16, preserved draft note/reason, retained search filter, a six-record filtered result, Back/Forward, keyboard Enter navigation, note saving, decision saving and opening an existing case without duplication.

An actual JSON download contained the newly saved QA note at revision 4 and excluded the unsaved reason. Unknown fragments and reloaded evidence fragments returned to Overview. At 390-pixel width the report buttons and text remained usable without page-level horizontal overflow. Signing out in another tab blocked the next export, exposed the sign-in recovery message and preserved the draft. No console errors were observed in the checked flow.

These are focused checks, not a complete accessibility certification or a user study. The Word update is checked for preserved text/tables and new content. Page-layout verification remains unavailable because the bundled LibreOffice renderer is missing; passing code tests does not prove Word pagination quality.

## 9. Troubleshooting

**I still see the long old page:** use port 8776 and check the Day 14 badge. An old Python server does not acquire new backend routes automatically. A fresh server/page is required for the new assets. Copy unsaved text before reloading an older page.

**My draft is not in the report:** section switching retained it in browser memory, but you did not save it. Click Save note if appropriate, then export the new case revision.

**Back did not undo my decision:** browser history changes the displayed location. Saved decisions remain in the case history. Make a reasoned new decision through the form if you need to correct a conclusion.

**An evidence link returned to Overview after reload:** selected record data is not stored in the URL. Open the case or alert again and choose its original. This avoids guessing a private record from a section-only link.

**My session ended:** follow the global sign-in recovery instruction. Keep or copy draft text before a full reload. Hiding a workspace never grants additional access or keeps an expired session valid.

**A table scrolls sideways on a narrow screen:** that is intentional. Its wrapper lets you read complete columns without compressing them into unreadable fragments. The whole page should not require sideways scrolling.

## 10. What comes next

Day 15 is proposed for held-out scenario evaluation: define what counts as a correct finding, test labeled positive and negative scenarios, count false positives and misses honestly, and explain limits. This is different from today's layout checks. After evaluation, remaining release work includes a fresh-setup rehearsal, final fixes, demonstration material, a portfolio case study, accurate CV bullets and final acceptance checks by 17 October.

No automatic live collection, public hosting, multi-user roles or claim of real-world detection accuracy was added today. The prototype is still a local learning and investigation tool.

## 11. One learning question

If you switch from Investigations to Events and then return, your draft stays in its box. Does that mean the draft has been saved to the database? Explain why in English or Roman Urdu in this chat.

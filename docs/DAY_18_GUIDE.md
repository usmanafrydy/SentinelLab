# Day 18 Checking the complete project before release

Completed 4 October 2026. The project completion target remains 17 October. Today we checked the existing system from downloaded source, recorded the results and prepared the remaining release work. We did not add a new detection rule or change application behavior.

## What today achieved

The existing project passed all 194 automated tests. We then downloaded the exact published GitHub source, checked every one of its 152 file hashes, created a fresh Python environment and ran the tests there. That downloaded copy also passed all 194 tests. A separate rehearsal exercised the real authenticated HTTP workflow and passed its seven checks. The synthetic evaluation reproduced the previous report exactly, including its source fingerprints.

You also ran the account command in your own PowerShell window and reported that the account was created. The separate ignored test file exists. We did not read its password hash or ask for your password. This is a user-reported manual command result, separate from the automated account-service checks. The assistant did not watch your keyboard or directly observe whether characters were visible.

The main result is stronger evidence that another source copy can run the documented workflow. Final release preparation still includes presentation practice and the unresolved Word page-layout check. The original laptop copy also retains its known local Git-history restriction. We have not created a final version tag or claimed production readiness.

Roman Urdu: Aaj hum ne GitHub se project ki nayi copy download karke check ki. Maqsad yeh tha ke project sirf purani working folder mein nahi, nayi environment mein bhi sahi chale. Tests pass hona achha evidence hai, lekin har mumkin problem khatam honay ki guarantee nahi.

## Acceptance and regression in simple English

An acceptance criterion is a promise about what the project should do. For example, importing the same event twice should not save two copies. An acceptance review connects each promise to a test, demonstration or other evidence. It also states what that evidence cannot prove. The project has fifteen criteria, identified as AC-01 through AC-15.

A regression is something that used to work and stops working after a change. Regression tests help find that problem. The full suite checks parsing, storage, rules, cases, reports and access controls. Running 194 tests does not mean the system detects 194 kinds of attack. Some tests check invalid input, a boundary time, a duplicate or an error path.

An end-to-end rehearsal checks several connected parts together. Our helper starts a real server process, signs in and sends real HTTP requests. It then imports records, runs detection, changes a case and exports reports. This helps catch integration problems that a small isolated test might miss. It does not replace a person checking how the interface feels.

## Step 1 Identify exactly which source we are checking

We first read the project instructions, progress, setup guide and release-readiness list. We compared the laptop files with GitHub commit cbc94443ead66ca2268dab49968b255e463cf00e. All 152 published files matched before any Day 18 edits. That commit is the Day 17 baseline. Day 18 adds documentation and an acceptance record; application source, assets, tests and rule data remain unchanged.

A commit identifies a saved repository snapshot. A file hash is a compact fingerprint calculated from its bytes. We used Git blob hashes, which include Git's file header as well as the file bytes. Matching these hashes helps establish that we tested the intended published source. It does not establish that the source is free of bugs, and it is not a digital signature from an independent reviewer.

This comparison matters because the original laptop Git HEAD and index remain behind under existing Windows access restrictions. We do not reset those files, change their access controls or pretend that local history is synchronized. Publication uses the connected GitHub service and a comparison of every published file. The new source ZIP has no Git history; it is a source snapshot only.

## Step 2 Download the source safely

Earlier attempts with the project's Python and PowerShell encountered certificate errors. Today the bundled document/workspace Python downloaded the exact commit ZIP from GitHub using urllib with the default SSL context. Certificate verification stayed enabled. The archive was 822122 bytes. Its SHA-256 fingerprint is recorded in reports/examples/day18_acceptance.json.

TLS certificate checking helps the client establish a trusted HTTPS connection. Turning it off would remove that check, so we did not use that workaround. A successful request through a different configured runtime does not prove that the earlier runtime's certificate configuration has been repaired. We can accurately say that an authorized verified download path now worked. A fresh git clone was not tested.

Before extracting, we checked the expected archive prefix, file names, sizes, absence of parent-directory traversal and exact membership in the published inventory. Every extracted file matched its expected Git blob hash. We extracted only those 152 files into the separate ignored data/runtime/day18_clean folder. No private credentials, database, old virtual environment or generated report was copied from the everyday project.

Roman Urdu: ZIP file ko seedha har jagah extract nahi kiya. Pehle file names aur fingerprints check kiye, phir alag test folder mein rakha. Aap ka asal account aur saved investigations apni jagah par rahe.

## Step 3 Create a fresh environment and run the tests

We created a new virtual environment without pip inside the downloaded copy. A virtual environment gives this copy its own interpreter environment. SentinelLab uses the Python standard library, so we did not install third-party application packages. This test used Windows, MSYS2 UCRT Python 3.12.7 and SQLite 3.46.1 on the same laptop. It is not a test of a different operating system or a machine with no Python installed.

The existing workspace ran scripts/run_tests.py and passed 194 tests in 35.288 seconds. The downloaded fresh environment passed 194 tests in 32.519 seconds. These durations describe these two runs; they are not a speed benchmark or a response-time promise. No application fix was needed during this checkpoint.

The suite includes failure paths as well as happy paths. For example, it checks identity conflicts, stale case revisions, expired sessions, missing evidence, report limits and malformed requests. A passing error-path test means the application rejected that tested situation as intended. It does not mean arbitrary hostile input is safe under every future deployment.

## Step 4 Rehearse the complete saved workflow

We ran scripts/rehearse.py inside the freshly downloaded environment. It created a temporary synthetic account through the actual account service and started a separate server process. The helper authenticated, obtained the session protections and used the real routes. There is no command-line authentication bypass in the user-facing server.

The first sample import saved sixteen events. The second import added zero events because all sixteen were duplicates. Detection saved three findings, one for each rule. A second run recorded another check without duplicating the findings. This demonstrates why event count, import count, alert count and detection-run count are different quantities.

The helper created an R3 case, saved a session-authored note and decision, and verified complete JSON and Markdown reports. It checked saved evidence rather than relying on a screenshot. It stopped and restarted the server with the same temporary database, checked that the saved case survived and checked that old sessions were rejected. Logout also removed access. Temporary test accounts, databases and files were removed after the rehearsal.

All seven reported checks passed. These are grouped workflow checks, not seven additional tests added to the suite. The automated helper uses HTTP rather than clicking a browser. The last actual browser demonstration and screenshots are from Day 17. No new browser usability or accessibility claim is made today.

## Step 5 Repeat the evaluation honestly

We ran scripts/evaluate.py on the twelve authored scenarios. The resulting JSON matched the published Day 15 report as structured data, including input and application-source fingerprints. This is expected because the rules and evaluated application source have not changed. Terminal redirection can change text encoding or line endings; comparing parsed JSON avoids mistaking that for a different result.

There were three true positives, three false positives, three true negatives and three false negatives. Each reported classification metric was 50 percent for this deliberately balanced toy corpus. All twelve expected rule sets agreed. Rule agreement answers whether the implementation behaves as specified. Intent classification asks whether the alert matched the story's benign or suspicious label. Those are different questions.

These scenarios were authored with knowledge of the rules. They are now a repeatable regression benchmark, not a blinded independent evaluation. We did not change the labels or tune thresholds to improve the score. We cannot use this result to claim real-world attack detection accuracy.

## Step 6 Complete the manual account command

You needed help opening PowerShell. The instructions were to open ordinary Windows PowerShell, change to the Desktop project folder, then run the existing scripts/account.py with username day18_check and an explicit separate file under data/runtime. Administrator mode and execution-policy changes were unnecessary.

The program requests the same 15-to-128-character password twice. It uses hidden entry and refuses the unsafe redirected-input fallback. It does not put the password in command arguments. You replied that the account was created; we confirmed only that the separate file exists. The password and stored hash were not read or published. The normal account in secrets/analyst.json remains the everyday account.

This test file is not automatically selected by the normal server command. Creating it does not change the username used by your existing demonstration. Keep it private; do not upload it or paste its contents into chat. If the command reports an existing file on a later attempt, it preserves the existing file instead of overwriting it. There is no reason to recreate the everyday account at each checkpoint.

## Step 7 Review what will be published

We reviewed the 152 published baseline paths and the explicit Day 18 additions. Runtime folders, credentials, private data, generated private reports, virtual environments, databases and Word lock files are outside the publication allowlist. An ignored file can still be published by a careless manual upload, so .gitignore alone is not the complete check. We publish reviewed paths deliberately.

The six original records in the portfolio JSON report were rechecked against the known synthetic sample. They all matched. Those reviewed fictional examples remain suitable for the demonstration. That does not authorize publishing a later report containing real login records or personal notes. Report export has no automatic redaction.

The download ZIP and fresh rehearsal environment stay in ignored data/runtime. The test logs and editing helpers are local verification materials, not application dependencies. The public acceptance JSON contains only safe results, source identity and limitations. A targeted publication review is not a guarantee that any arbitrary future file contains no secret.

## Files changed today and why

- docs/DAY_18_GUIDE.md is this detailed lesson, including the purpose, method, results, concepts and remaining work.
- docs/FINAL_ACCEPTANCE.md is the concise technical review record. It links each acceptance criterion to the relevant automated evidence and states the release decision.
- reports/examples/day18_acceptance.json stores the source identity, acquisition method, environment, test results, evaluation comparison and qualifications in machine-readable form.
- docs/RELEASE_READINESS.md records the current state of the checklist, including the successful source download and your manual account result.
- docs/SETUP.md explains the now-tested download route while preserving the earlier TLS qualification and normal account instructions.
- README.md points a new reviewer to the latest acceptance evidence and gives the correct completion status.
- docs/ACCEPTANCE_CRITERIA.md adds Day 18 evidence above the preserved earlier checkpoint records.
- docs/PROGRESS.md and docs/NEXT_SESSION.md record completed work and the next bounded checkpoint.
- docs/SentinelLab_Project_Handbook.docx and docs/SENTINELLAB_HANDBOOK.md receive chapter 35, an updated introduction and the current chapter 29 completion map. Earlier explanations remain available.

No source module, rule, database schema, interface asset or test file changed today. We used existing verification tools rather than adding a new feature simply to increase the file count.

## Reading the final acceptance decision

The acceptance checks pass with documented qualifications. The downloaded source now reproduces the tested workflow. We still distinguish that result from a final versioned release. The fifteen criteria have evidence, but evidence has a scope: local authentication is not public hosting, saved history is not tamper-proof custody and a rule match is not proof of compromise.

The cumulative Word file has content and structure checks. The supported renderer was attempted after the update and failed because LibreOffice soffice.exe was not available in the bundled runtime path. Visual pagination remains unverified. The Markdown companion remains readable. A text-preservation check cannot detect every clipped line, awkward page break or table-layout problem in Word.

Before the final release, we should complete your presentation practice, decide how to handle any remaining document-layout limitation and record a deliberate versioned release checkpoint. We should not add optional live collection, multiple roles or public hosting just before the deadline. Those are separate future projects with additional design and security requirements.

## Your next learning step

Read the current setup guide, then walk through the five-minute demo script using synthetic data. Explain the chain in your own words: a login record is validated and stored; a rule identifies a pattern; an analyst investigates the linked evidence; a report captures saved work. Explain one false alarm and one missed scenario. Be clear about the substantial AI assistance and the parts you personally understand and operate.

For today's single practice question: give one example of additional evidence you would seek before changing an R3 case from Suspicious to Confirmed compromise. You can answer in simple English or Roman Urdu in this chat. The five failures followed by success are already known; the question asks what else you would investigate.

Roman Urdu: Sirf alert ki wajah se hacking confirm nahi hoti. Hamein mazeed maloomat chahiye jo bataye ke successful login waqai ghair-ijazati tha. Aap ek example dein; phir hum us par baat karenge.

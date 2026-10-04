# Day 20 Final release and portfolio handover

4 October 2026. Today completes the bounded SentinelLab local portfolio milestone as version 0.1.0, ahead of the October 17 target. The word final describes this project's agreed local scope. It does not mean the program is a certified production security product or that every possible future feature is finished.

## What we decided

The owner asked to continue after the release candidate and chose not to repeat the optional duplicate-upload exercise. We clarified that presentation practice is for learning, not a technical release requirement. The owner correctly said supporting evidence should be checked before deciding a case, but a complete presentation assessment has not happened. We record that distinction honestly and do not make optional exercises block delivery.

The implemented features already have automated checks, an authenticated workflow rehearsal, a downloaded-source fresh-environment run and actual synthetic browser demonstration material. We use that evidence to release the local prototype with explicit limitations. Learning and interview practice can continue afterward at the owner's pace.

Roman Urdu: Project ka local portfolio wala scope complete hai. Practice aapki learning ke liye hai; usay skip karne se software ka tested kaam undo nahi hota. Lekin apni CV par wohi understanding claim karni hai jo aap explain kar sakte hain.

## Step 1 Verify the starting snapshot

We read the project instructions and latest release/readiness records. All 159 local published files matched GitHub commit 9e2d265bbc52a97759144514445b0dd743f32ae3, the v0.1.0-rc.1 candidate. This establishes the source from which we are preparing the final release.

A Git commit identifies a source snapshot. A tag gives that snapshot a version name. A GitHub release adds a description and source downloads. The new final tag is v0.1.0. The candidate tag stays attached to its original commit. We do not silently move an old version to new content.

The original laptop Git HEAD/index remain behind under existing Windows restrictions. We preserve those controls and verify the connected publication against local file hashes. This establishes which files were published, not that the restricted local history was repaired. The release documentation keeps that limitation visible.

## Step 2 Run the final checks

The complete automated suite passed 194 tests in 28.258 seconds. It covers validation, storage, search, detection, saved alerts, cases, authentication, browser routes, reports, evaluation and rehearsal behavior. The duration is the observed time for this run, not a performance target or a comparison between computers.

The separate scripts/rehearse.py command passed all seven grouped checks. It creates a temporary account and server, signs in over real HTTP, imports and reimports synthetic events, saves and repeats detections, creates an investigation, checks JSON/Markdown reports, restarts the server, rejects old/logout sessions and cleans up temporary files. It does not edit your private account or everyday database.

We reran the twelve-scenario evaluation. Its parsed JSON matched the published earlier report exactly, including source and input fingerprints. TP, FP, TN and FN remain three each, and all twelve expected rule sets agree. A rule can be implemented correctly while producing a false alarm or missing an attack story. These authored synthetic results are not real-world detection accuracy.

Day 20 changes release metadata and documentation only. No application source, interface asset, test, rule parameter, schema or evaluation input changes. The final comparison checks that invariant. The earlier Day 18 verified ZIP download and fresh venv remain setup evidence; we do not claim a new operating-system installation or git-clone test today.

## Step 3 Resolve the release checklist honestly

The known Word limitation concerns visual page layout. We update the content, preserve earlier lessons and tables, and retry the supported renderer. Bundled LibreOffice has been unavailable, so visual pagination remains unverified if rendering still fails. We retain the readable Markdown companion and state the limitation. We do not rename an unperformed visual check as passed.

The local Git-history restriction is also retained. Private account setup has user-reported success from Day 18; the assistant did not read the password/hash or observe keyboard visibility. Source acquisition worked through a TLS-verified bundled-Python route, without claiming the earlier runtime certificate settings were repaired. These qualifications describe the actual evidence.

Presentation practice becomes optional post-release learning. The owner has given one correct investigation judgment, not a complete demonstration of every concept. The final project summary and CV wording explicitly describe substantial AI assistance and guided learning. No proficiency score or independent authorship claim is invented.

Roman Urdu: Jo cheez check hui hai usay checked likhna hai. Jo limitation abhi mojood hai usay saaf likhna hai. Version number badalne se limitation khud khatam nahi hoti.

## Step 4 Prepare the handover

The new docs/HANDOVER.md is the short operating guide for using the completed project. It tells you where the real project lives, how to start the existing server, which account/database to retain, what each important folder stores, how to run verification and what can be shared.

Your existing project is C:\Users\Dell\Desktop\Projects\SentinelLab. The usual database is data/runtime/day14_demo.db and the account is secrets/analyst.json. The browser address is http://127.0.0.1:8776/. Opening a browser does not start the Python server. If the page cannot connect after an app/computer restart, start the same server command from PowerShell and refresh the page. Restarting the server requires a new sign-in but should retain saved database records.

Use this command from the project folder:

```powershell
& .\.venv\bin\python.exe scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json
```

Keep the terminal open. You do not need administrator mode or a new account. Do not choose a different database path simply to restart, because that creates or opens a different workspace. If the server is already running, use it rather than starting another process on the same port. The setup guide explains fresh installation separately.

The handover also explains that GitHub contains source and reviewed synthetic material, not private runtime data. A source ZIP is not a backup of your investigations. For ordinary private file backups, stop database writers cleanly before copying the database. No new backup, deletion or private-data upload is performed today.

## Step 5 Finalise the portfolio description

docs/portfolio/PROJECT_SUMMARY.md gives a concise account of the problem, workflow, stack, evidence and limitations. The case study remains the more detailed architecture/design explanation. The CV page provides conservative wording appropriate to the owner's guided involvement, while retaining interview prompts for optional practice.

A useful CV line is: Completed a guided, AI-assisted implementation of a local Python and SQLite login-event investigation prototype with explained alerts, case history and JSON/Markdown reports. Supporting bullets can describe the synthetic evaluation and verified workflows without claiming independent implementation or real incident-response employment.

The final version does not justify phrases such as production SIEM, prevented attacks, enterprise-scale deployment, tamper-proof evidence or perfect detection. No job application, CV submission, public hosting or external profile edit is part of this checkpoint. The prepared wording stays in the repository for you to use and adapt honestly.

## Step 6 Publish the reviewed version

VERSION changes from 0.1.0-rc.1 to 0.1.0. The new release notes describe implemented behavior, verification, startup and retained qualifications. The new commit contains only reviewed metadata/documentation changes. Publication compares the complete remote tree and local file hashes, then creates the final GitHub release/tag at that reviewed commit. The previous candidate remains available.

The final GitHub release is a normal release for the local prototype. Its notes continue to say that it is not production-ready security infrastructure. That distinction is part of the product's scope, even without a Pre-release label. No private accounts, databases, environments, real logs or generated private reports are release assets.

The source download contains files, not your Python installation or credentials. A new user follows SETUP.md and creates their own private account. An existing user retains the current account and database. When future code changes, create a new reviewed version instead of silently altering v0.1.0.

## Files changed in this checkpoint

- VERSION identifies final local prototype version 0.1.0.
- docs/releases/v0.1.0.md records release scope, evidence, known limits and the decision that optional practice is not a blocker.
- docs/HANDOVER.md explains startup, important files, private data, verification and maintenance in simple English.
- docs/portfolio/PROJECT_SUMMARY.md provides a ready-to-read project overview.
- docs/portfolio/CV_AND_INTERVIEW.md, CASE_STUDY.md and README.md align the portfolio with the final local scope and actual owner involvement.
- reports/examples/day20_release_checks.json records safe verification facts without credentials or private records.
- docs/DAY_20_GUIDE.md is this lesson. The README, acceptance/readiness, progress and next-session pages point to current status while preserving earlier history.
- Both cumulative handbooks receive chapter 37, a current opening and the updated chapter 29 completion map. Earlier lessons are retained.

## What happens after this

There is no compulsory next daily checkpoint. You can use the project, read the handbook, practise a demonstration, ask about a concept or request a specific improvement. Optional presentation exercises remain available. A bug should include a synthetic reproduction and expected versus actual behavior; never send passwords or private account contents.

Public hosting, live event collection, multiple analysts and stronger evidence integrity are possible future projects requiring new design and testing. They are not hidden unfinished promises in this local release. The finished result is a bounded, documented, reproducible learning prototype that you can explain honestly and gradually improve.

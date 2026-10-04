# Day 19 Preparing a release candidate and explaining the project

4 October 2026. Today prepares SentinelLab version 0.1.0-rc.1 and starts presentation practice. The completion deadline remains 17 October. This is a release candidate for the local learning prototype; it is not a final stable release or a production security product.

## What a release means

A Git commit records a snapshot of project files. A tag gives a snapshot a memorable version name. A GitHub release adds a page describing that version and offering source downloads. The tag should identify the intended reviewed commit. Later corrections should use a new version instead of silently moving the old tag.

The candidate name is v0.1.0-rc.1. The rc part means release candidate and the final 1 means the first candidate for this version. It is a way to make reviewable progress while keeping unfinished presentation practice and document-layout verification visible. A version number does not mean that more attack techniques are detected or that rule thresholds changed.

The new VERSION file contains 0.1.0-rc.1. It is release metadata. It is not imported by the detector and does not change the existing rule versions or SQLite schema. GitHub should label the candidate Pre-release so a visitor can distinguish it from a finished stable release.

Roman Urdu: Version name ek nishan hai jo batata hai hum project ki kis saved copy ki baat kar rahe hain. Release candidate final review wali copy hoti hai. Is naam se software automatically production-ready nahi ban jata.

## Step 1 Check the starting point

We read the project instructions, latest progress, next-session plan and release-readiness record. All 155 local published files matched GitHub commit e3fb62ceca8e8f7d25fdd1b95c31b9c9a5a1b908 before editing. This prevents unrelated or unreviewed local changes from being mixed into the checkpoint.

The original laptop Git HEAD and index remain behind because of existing access restrictions. We preserve those restrictions and publish through the connected GitHub service. We compare file hashes and the published ref after publication. That checks file content, not synchronization of the restricted original local Git history.

The GitHub connection can create file blobs, trees and commits, but does not expose a release-creation action. The existing signed-in GitHub browser provides the release form. We inspected that form, including its tag, target, title, notes and Pre-release option. The candidate is prepared from an explicit reviewed source snapshot, not from a guessed or unrelated branch.

## Step 2 Check that the workflow still runs

We reran scripts/rehearse.py using the existing project environment. All seven grouped checks passed. It created a temporary account, ran a separate authenticated server, imported and reimported the sample, saved and repeated detection, created an investigation, checked both report formats, restarted the server, checked session rejection/logout and cleaned up its temporary files.

The most recent full suite remains the Day 18 run: 194 tests passed in the existing workspace and 194 in a newly created environment from verified downloaded source. Day 19 changes release metadata and documents only; application modules, browser assets, tests and evaluation inputs remain unchanged. We do not represent the earlier full-suite run as a new Day 19 run. A final hash comparison checks this unchanged-code claim.

This distinction is useful in an interview. Say exactly what was tested and when. Repeating a number without describing its scope can mislead a reviewer. Seven workflow checks are not seven new attack detectors, and 194 passing tests do not prove perfect security.

## Step 3 Open the owner's existing demonstration

We checked the local demo port and started the existing server with data/runtime/day14_demo.db and secrets/analyst.json. It runs on http://127.0.0.1:8776/. The returned page was the normal sign-in page. The private account content was not read. The owner signs in privately with the usual account.

Starting the server does not import another sample or change an investigation. The database and private account remain the everyday ones. Earlier demonstration databases are independent copies and do not synchronize. A restart invalidates old sessions, so seeing the sign-in screen is expected. Saved data lives in SQLite; the session lives in server memory.

The server stopped during an app/session restart. After the owner asked to run the project, it was restarted with the same database/account and HTTP 200 was verified again. The browser remained on an internal connection-error page; its security policy blocked automated refresh, so the owner was asked to press Ctrl+R. The new server process identifier was recorded in ignored data/runtime/day19_server.pid. A stored process number may become stale after restart, so future work must verify the process rather than stopping an unrelated program. No unrelated service was stopped.

## Step 4 Practise the story in simple language

Start with the purpose: SentinelLab helps turn imported login records into explained alerts, investigation notes and reports. It is a local, AI-assisted learning project. It processes files when you import them and run detection. It does not continuously monitor the laptop or network.

Follow a clear chain: input record, validation, storage, detection, investigation, report. Validation checks the expected fields and limits. Storage retains accepted originals and avoids duplicates. Detection applies a rule to stored event time. Investigation records observations and a reasoned conclusion. A report captures saved evidence and history.

The new presentation guide explains each part with examples. Use it with the existing five-minute demonstration script. The script tells you what to click; the practice guide helps you explain why that action matters. Read a short section, then say it in your own words. Memorizing difficult terminology is less useful than explaining one clear example.

Roman Urdu: Har button ka naam yaad karna zaroori nahi. Yeh samajhna zaroori hai ke data kahan se aaya, alert kyun bana, aur analyst ne kya evidence dekh kar decision liya.

## Step 5 Separate an alert from a conclusion

Our first practice question asks what additional information you would seek before calling five failed logins followed by success a confirmed compromise. The visible pattern is already known. The missing part is whether the successful access was unauthorized and who controlled the session.

An account-owner explanation can help. Authorized identity-provider, device, session or endpoint evidence may help corroborate it. These are possible external investigation sources; SentinelLab's present login format does not collect device or MFA fields. An unfamiliar IP alone is not proof, because VPNs, shared networks and travel can change context. Likewise, a rule matching does not establish who typed a password.

Record only facts supported by evidence. A benign alternative is that the owner corrected a forgotten password. Suspicious means the pattern deserves attention. Confirmed compromise requires stronger supporting evidence and a reasoned assessment. It is reasonable to leave a case In progress while more information is requested.

The owner has been invited to answer one question at a time. A guide or example is not proof that the owner has answered or completed practice. Actual responses should be discussed in chat before recording that milestone as complete.

## Step 6 Write useful release notes

The release notes explain what is included, what was checked, how to start and what is still limited. They cover the real implemented system: bounded imports, original evidence, three rules, saved alerts, local access, investigation history, reports, synthetic evaluation and portfolio material.

They also state that the application is a single-account local prototype, not a public production SIEM. Direct filesystem access can alter the database. Reports are not signed, encrypted or automatically redacted. Browser drafts require explicit saves. Synthetic evaluation is not real-world accuracy. These qualifications help a reviewer use the project appropriately.

The release should contain reviewed source and documentation only. Private account files, real logs, runtime databases, environments and generated private reports are excluded. A GitHub source archive does not contain Python or a ready-made account; a new user follows SETUP.md. Existing users should not reinstall or recreate their normal account just because a release candidate exists.

## Files added or updated

- VERSION names the candidate and is separate from rule and database versions.
- docs/releases/v0.1.0-rc.1.md contains the reviewable release notes, verification scope, startup links and known limitations.
- docs/portfolio/PRESENTATION_PRACTICE.md provides simple explanations for the owner, examples, troubleshooting and an honest practice-status description.
- docs/DAY_19_GUIDE.md explains this checkpoint, its concepts, steps and results.
- README.md, docs/RELEASE_READINESS.md, docs/PROGRESS.md and docs/NEXT_SESSION.md point to the candidate and remaining work.
- docs/portfolio/CASE_STUDY.md updates stale setup/acceptance wording to include Day 18 evidence.
- Both cumulative handbooks add chapter 36 and update the chapter 29 completion map while preserving earlier explanations.

No application feature, detection threshold, schema or browser behavior is changed today. Presentation and release work make the existing system easier to review and reproduce.

## What remains before the final version

The owner should practise explaining the purpose, duplicates, one rule, investigation judgment, report contents and limits. We will discuss the answers in this chat, one at a time. The versioned candidate can be shared as a clearly labelled prototype while that learning continues. A final stable release should record the outcome of this review rather than assuming it happened.

The Word handbook's content is checked and earlier lessons are preserved. Supported visual rendering is attempted after the update. The known absence of bundled LibreOffice means page layout remains unverified unless that render succeeds. The Markdown companion provides the same current explanation for reading. The original local Git-history limitation also remains explicit.

Future public hosting, live collection, multiple roles or stronger evidence integrity are separate design projects. They are not required additions to this bounded local portfolio release. Keep the deadline focused on a demonstrated, documented and honestly described system.

# Day 17 Presenting the project with evidence

Completed 4 October 2026. The target completion date is still 17 October. Today prepares the portfolio presentation; it does not mark the whole release complete.

## What we made today

We created a portfolio folder with a five-minute demonstration script, a project case study, CV wording, interview practice, three real application screenshots and two synthetic example reports. We also mapped the fifteen acceptance criteria to existing evidence and remaining checks. These materials help another person understand what the project does and help you explain it confidently without making claims the evidence cannot support.

Before editing, all 141 files in the Day 16 published snapshot matched the laptop source. We used a separate demo database and synthetic analyst account. Your everyday day14_demo.db and private account were not used for these screenshots or reports. The full suite passed 194 tests after today's small interface-label change. No new detection algorithm, database schema or authentication behavior was introduced.

Roman Urdu: Aaj hum ne project ko dikhane aur samjhane ke liye material banaya. Sirf screen dikhana nahi, balkay har claim ke saath evidence aur limitations batana zaroori hai.

## Why a portfolio needs a story

A portfolio is evidence of work you can explain. A large number of files is not enough by itself. A reviewer needs a clear problem, a design that addresses it, a demonstration and an honest discussion of limits. SentinelLab's story is how login records become an explained finding, then a reasoned investigation and a saved report.

The demonstration follows one R3 finding from beginning to end. This is easier to understand than clicking every feature without a purpose. We show the other rules and duplicate handling briefly, then spend most of the time explaining evidence and the decision. A useful demonstration answers what happened, why the rule matched, what is still unknown and what the analyst would do next.

The case study gives a more detailed written account. It separates implemented behavior from possible future work. The CV entry is shorter again: it names the actual technology and gives a few demonstrable outcomes. Neither should claim a real security incident, production deployment or measured business benefit that did not happen.

## The synthetic story used today

We reused data/samples/day07_all_rules.jsonl instead of inventing a new format. It contains sixteen fictional login events. Ten usernames have failures from 192.0.2.70. Another account, lab_user, has five failures from 192.0.2.71 between 09:20 and 09:24 UTC on 29 September 2026, followed by success at 09:24:30 UTC.

R2 describes failures against ten distinct accounts from the first IP. R1 describes the five failures for lab_user. R3 describes the later successful login after those failures. Three alerts do not necessarily mean three independent attackers or incidents; rules can describe overlapping activity.

The same sample was imported twice into the isolated database. The first import inserted sixteen events. The second inserted zero and reported sixteen duplicates. The database therefore showed sixteen saved events and two completed imports. This is a useful point for a demonstration: an import is an action, while an event is a saved record.

Detection was saved twice. Three alerts remained, and two runs were recorded. The second run found the existing alerts. This explains a second important distinction: keeping a history of checks is different from duplicating a finding.

These timestamps describe when the fictional login events happened. Import, run and case timestamps describe when we processed or investigated the sample. The application displays UTC. Do not describe a September event as a new attack on today's date just because it was imported today.

## What we did in the browser

We signed in with a synthetic portfolio_analyst account in the isolated demo on port 8778. Overview displayed the saved counts. Detection showed the three alerts and two runs. We opened R3 and read its explanation, account, IP, threshold, first event time, trigger time and linked records.

We inspected the success record through Original #16. It showed outcome success, the expected account/IP/time, the original accepted JSON record and first-import location. The local row number is a convenient link in this database; it is not a globally meaningful event identity. In another database the Original button may have a different row number.

Next we used Investigate this alert to create Case 1 titled Synthetic review: success after five failures. We saved a note containing only observations and a benign alternative: a legitimate owner might have corrected a password. We then chose In progress and Suspicious and saved a reason requesting account-owner confirmation and additional authentication context.

The case reached revision three: creation, note and decision. The history retained all three actions with the signed-in analyst name. We did not choose Confirmed compromise. Nothing in these sample records proves who controlled the account or whether the successful login was unauthorized.

Roman Urdu: Paanch failures ke baad success nazar aayi. Yeh suspicious pattern hai, lekin user ne apna password theek bhi kiya ho sakta hai. Is liye case ko investigate karna hai, hacking ka final faisla foran nahi karna.

## Screenshots and what they prove

The three published screenshots show the actual application using synthetic data. They were not generated as mockups. The Overview capture shows the event/import counts and beginner workflow. The R3 capture shows the explanation and rule facts. The case capture shows its title, In progress / Suspicious state, revision and report area.

We reviewed the captured images and adjusted the scroll position so important headings are visible below the fixed header. They are viewport excerpts; some tables and controls continue below the bottom of the picture. A screenshot cannot establish every stored record, every route's security or complete accessibility. The full reports and automated checks provide different types of evidence.

The header previously said LOCAL LAB and DAY 14. That old lesson number was confusing in a current presentation, so both the workspace and sign-in templates now say LOCAL LAB and PROTOTYPE. This is a small text correction. It does not imply a new product version or production readiness.

No private account file, password, session token or user investigation appears in the portfolio material. Synthetic screenshots may contain the test account name, example IP addresses and timestamps. Those values are part of the fictional demonstration, not evidence of a real person's activity.

## Reviewing the two example reports

We exported Case 1 using the existing command-line report tool with expected revision three. Exports initially went to the ignored reports/generated directory. We checked their contents before copying the synthetic examples into the public portfolio folder.

The JSON report contains the case, saved R3 alert, first detection run, three case actions, six linked original records and limitations. Every original_record matched a line in the known synthetic sample. All actions had the browser session's portfolio_analyst author. The Markdown report contained the same saved sections and values. The export timestamps differ because the two exports were produced separately; the case, action and evidence data agree.

Markdown is readable text with headings and fenced JSON sections. JSON is structured data that software can parse. Both represent saved work at an export snapshot. Downloading a report does not save an unfinished draft, confirm compromise or close a case. Real reports may contain private information, which is why normal generated reports remain ignored by Git.

Publishing these reviewed fictional examples is a specific portfolio choice. It does not change the rule that future private reports must remain outside the repository. There is no automatic redaction, signature, encryption or forensic chain-of-custody guarantee.

## How to use the demonstration script

Open docs/portfolio/DEMO_SCRIPT.md. It divides approximately five minutes into problem, import, detection, evidence, investigation and reporting. The times are a speaking plan, not measured application performance. Practice slowly first, then shorten your explanation once you understand the transitions.

For a fresh presentation, follow SETUP.md, start a new database filename with your existing private account and use an available loopback port. Do not overwrite a database to reset a demonstration. If you use today's prepared demo, explain that the two imports and two runs were already completed. Further repetitions change history counts while unchanged events and alerts remain deduplicated.

Sign in privately before recording. Show the original success record, say why it matched R3, describe the benign alternative and show the saved decision. Finish with an export and one limitation. If a browser download is unavailable, show the included example report and identify it as a previously exported synthetic example.

We did not record a video, publish a public website or submit a job application today. The materials are ready for you to practice and adapt. A live browser session can expire after inactivity; saved cases persist, but you may need to sign in again.

## Case study and CV ownership

The case study explains the problem, architecture, transaction/evidence choices, three rules, investigation workflow, evaluation and tradeoffs. It explicitly identifies the project as AI-assisted. Code, tests, documentation and debugging received substantial assistance. You should not claim independent authorship of every line or professional incident-response experience from this lab.

The suggested CV entry uses actual technologies: Python, SQLite, HTML, CSS, JavaScript and unittest. It mentions three explainable rules, deduplicated storage, investigation history, exports and synthetic verification. There are no invented incident counts, cost savings, performance improvements or enterprise deployment claims.

If your involvement is still mainly guided learning, use the conservative wording supplied in CV_AND_INTERVIEW.md. Before claiming a skill, practice explaining the relevant code and showing the feature. Honest ownership is compatible with AI assistance; understanding is the part you must be able to demonstrate yourself.

The interview section asks about duplicate identity, R1/R3 overlap, uncertainty, persistence, stale revisions, report limits, tests and AI assistance. Work through one question at a time. You do not need complicated language to give a strong explanation.

## Evaluation claims that must stay separate

The Day 15 authored corpus has twelve scenarios, with TP, FP, TN and FN each three. Its labels were defined before running the detector, but its author knew the rules. It is separate from earlier implementation fixtures, not an independent blinded evaluation. It is now a reusable benchmark.

All twelve scenarios produced their expected rule sets. That shows agreement with written behavior on those cases; it does not mean the system caught every malicious story. The 50 percent figures belong only to this deliberately balanced synthetic set. Never turn them into a real-world accuracy claim or hide the false positives and misses.

Passing 194 tests is useful evidence for checked behavior. It is not proof of universal security. Slow guessing, distributed attempts, stolen-password success, missing logs and harmless mistakes remain important limitations of these simple rules.

## Every new or changed file

docs/portfolio/README.md is the gallery and starting index. DEMO_SCRIPT.md is the ordered speaking and operating guide. CASE_STUDY.md is the written technical story. CV_AND_INTERVIEW.md provides truthful project wording and practice prompts. sample-report.json and sample-report.md are reviewed real exports containing only synthetic data.

The screenshots directory contains 01-overview.jpg, 02-alert.jpg and 03-case.jpg. They are original browser captures. docs/RELEASE_READINESS.md maps AC-01 through AC-15 to evidence and qualifications, followed by open verification items. docs/DAY_17_GUIDE.md is this lesson.

src/sentinellab/web/templates/index.html and login.html replace the obsolete day badge with Prototype. README.md now describes the implemented project and actual stack rather than calling the whole platform merely planned. It links the portfolio material. docs/ACCEPTANCE_CRITERIA.md, PROGRESS.md and NEXT_SESSION.md record evidence, continuity and remaining work.

The cumulative Word and Markdown handbooks receive chapter 34 and current-map updates while keeping earlier lessons. Helper scripts used to prepare and verify the demo stay outside the published project. The isolated runtime database/account, server logs, environment and unreviewed generated reports are excluded from GitHub.

## What remains before completion

The readiness map covers all fifteen criteria without marking the final release complete. Existing component tests and demonstrations support the implemented features. Remaining checks include an authorized working source-download path, private manual hidden-password entry, Word rendering when its supported dependency is available, the final acceptance sequence and a versioned release checkpoint.

The Day 16 source download had certificate errors; hash-verified local source was used for that rehearsal. Hidden terminal input was blocked by automatic approval review. The account service and sign-in workflow were tested, but those specific external steps remain unverified. The bundled Word renderer still has a missing LibreOffice limitation; content preservation is checked separately from page layout.

Day 18 is planned for final acceptance preparation and closing or clearly documenting these remaining items. The completion target remains 17 October. Optional new features should not distract from making the current project reproducible and explainable.

Your one practice question is: what extra information would you request before changing this synthetic case from Suspicious to Confirmed compromise? Give one example in this chat. There is no need to claim that the sample itself supplies that proof.

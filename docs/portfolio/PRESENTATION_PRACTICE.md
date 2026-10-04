# Presenting SentinelLab in simple English

Practice is optional and does not block the v0.1.0 release. Use one step at a time. This is a practice guide, not a record that the owner has already completed or passed the demonstration. The existing five-minute DEMO_SCRIPT.md contains the exact operation sequence. Your current laptop demo is at http://127.0.0.1:8776/ with your usual private account; prepared data counts may change as you use it.

## 1 Explain the purpose

Say: "SentinelLab is my AI-assisted cybersecurity learning project. It helps me turn login records into explained alerts, investigation notes and reports. I import files and run checks deliberately. It does not continuously monitor my laptop."

Explain the input and output in your own words. JSONL means one JSON event per line. SQLite stores accepted events and investigation work on the laptop. An alert is a rule finding; a case records the analyst's investigation of that finding.

Roman Urdu: Login records input hain. System un records mein patterns dhoondta hai. Phir analyst evidence dekh kar notes aur decision save karta hai.

## 2 Explain why repeated uploads do not double the data

An event is identified by source plus event_id. Importing the same accepted event again reports a duplicate instead of saving another event. If the same identity arrives with different content, it is a conflict: the original is retained. An import is an action, so import history may increase even when saved event count does not.

Example: upload the sixteen-event synthetic sample twice into an empty demonstration database. Expect sixteen saved events, not thirty-two. Do not promise those counts for a database that already contains other samples. Never delete your usual database just to make a presentation counter look tidy.

## 3 Explain one rule precisely

Use R3: a successful login has at least five earlier failures for the same account and IP in the preceding five minutes. Failures exactly at the success timestamp are excluded because equal timestamps do not tell us which came first. This rule describes a suspicious sequence; a legitimate owner correcting a password can produce it too.

R1 is five failures for the same account/IP in five minutes. R2 is failures for ten distinct usernames from one IP in ten minutes. These are lab defaults, not universal security thresholds. A shared IP can represent several people.

## 4 Explain what you would investigate

First state the facts: account, IP, timestamps, outcomes and linked originals. Then state what remains unknown: who controlled the session and whether access was authorized. Seek additional records and account-owner context. For example, ask whether the owner recognizes the successful sign-in, then compare device/session context and authorized authentication logs. No single clue automatically proves compromise.

Do not claim SentinelLab already collects device, MFA, identity-provider or endpoint records. Those are possible external investigation sources on systems you are authorized to review. The current imported schema does not contain those fields.

Roman Urdu: User se pooch sakte hain ke successful login us ne kiya tha ya nahi. Phir doosray authorized records se baat verify karni hai. Sirf unfamiliar IP ya ek jawab ko final proof nahi samajhna.

## 5 Show saved work and explain a report

Open the case linked to the alert. Describe its note, status, disposition and action history. Status describes progress; disposition records the current conclusion. A case can be In progress and Suspicious. Closed cases need a conclusion, but closing a case does not mean compromise was confirmed.

A revision helps prevent a stale page from overwriting newer decisions. Refresh and review the latest state before submitting again. Notes/history do not rewrite the original event. A report captures saved case data, actions, rule evidence and original records from one database snapshot. Unsaved drafts are excluded. The database is not tamper-proof against local file access.

## 6 Explain the evidence and limits honestly

The Day 18 suite passed 194 tests in both the usual workspace and a newly created environment from downloaded source. Tests cover particular behaviors and error paths. They are not a guarantee of perfect security. The independent HTTP rehearsal checks the connected workflow and restart behavior; it is not a browser usability score.

The twelve authored scenarios produced three true positives, three false positives, three true negatives and three misses. All expected rule sets agreed. Correctly implementing a rule can still produce a false alarm or miss an attack story. This is not an independent real-world accuracy estimate.

Say that AI provided substantial code, test, documentation and debugging assistance. Demonstrate the parts you understand rather than claiming you wrote every line independently. Your learning is shown by explaining decisions, recognizing limits and operating the system safely.

## Practice record

The first question was issued on Day 19: what extra information would you check before calling an R3 login sequence confirmed compromise? During follow-up, the owner answered that supporting evidence should be checked before deciding a case; that judgment was affirmed. The repeated duplicate-upload exercise was skipped by choice. This does not establish a full presentation assessment. Further answers and feedback belong in this chat. Continue with one question at a time: purpose, duplicates, one rule, investigation judgment, saved report and limits. Record actual responses before marking practice complete.

If the page is unavailable, start the existing demo using SETUP.md. Sign in privately. Use the labelled screenshots and sample report as an explicitly identified fallback; do not describe them as a live result. Do not reveal credentials during screen sharing.

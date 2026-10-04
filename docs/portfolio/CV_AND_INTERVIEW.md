# CV wording and interview preparation

Use these as project descriptions after you can demonstrate and explain the features. They describe an AI-assisted learning project, not employment experience, a production deployment or wholly unassisted implementation. Adapt the wording to your actual involvement; do not list tools or concepts you cannot discuss.

## Final suggested project entry

**SentinelLab v0.1.0 | Guided AI-assisted cybersecurity project**  
Python, SQLite, HTML, CSS, JavaScript, unittest  
[GitHub repository](https://github.com/usmanafrydy/SentinelLab)

- Completed a guided, AI-assisted implementation of a local login-event investigation prototype with three explained detection rules, retained original evidence and browser case management.
- Project capabilities include event/alert deduplication, revision-aware investigation history, local sign-in and Markdown/JSON reports linking findings to original records.
- Verification includes 194 passing tests, seven authenticated workflow checks and twelve authored synthetic evaluation scenarios documenting false alarms and missed cases.

These bullets describe the project and its verification, not proof that the owner independently wrote or personally assessed every component. Code, tests, documentation and debugging received substantial AI assistance. Use only claims you can explain honestly. A complete owner presentation assessment has not been performed; practice is optional and may continue after release.

Do not write perfect detection accuracy, production SIEM, prevented cyberattacks, enterprise deployment, real incident response, tamper-proof evidence or independently wrote every line. Do not turn the synthetic 50 percent metrics into a real-world claim. No external CV, job application or profile has been submitted or edited. The [project summary](PROJECT_SUMMARY.md) gives supporting context.

## A thirty second introduction

SentinelLab is my AI-assisted learning project for understanding how login records become security findings and investigations. It validates and stores events, runs three explicit rules, preserves original evidence and supports case notes and exports. The useful lesson is that an alert is only a lead: I can demonstrate a harmless password-recovery story that triggers the same pattern as guessing. I documented false alarms, blind spots and the limits of the local prototype.

## Questions to practice

1. Why does importing the same file twice not double the event count? Explain source/event_id identity and the difference between a duplicate and a conflict.
2. Why can one incident pattern produce R1 and R3? Explain the failure threshold, the later success and why the evaluation scores one scenario once.
3. Why is Suspicious different from Confirmed compromise? Explain a benign alternative and what additional evidence you would request.
4. What survives a restart? Explain SQLite persistence versus in-memory sessions and unsaved browser drafts.
5. What does a stale revision protect? Explain that a decision must be based on the current case state; refresh and review rather than overwrite.
6. What does a report preserve, and what does it not prove? Explain saved originals/history versus signatures, authenticity and direct database tampering.
7. What does 194 passing tests establish? Explain checked behavior under the tests, not universal security or real-world accuracy.
8. How did AI help? Describe code/document generation and debugging support honestly, then demonstrate your own understanding of one rule and one investigation.

Practice answering one at a time in plain language before adding more terminology to your CV. Roman Urdu: Jo cheez aap explain aur demonstrate kar sakte hain, wahi apni skill ke taur par likhein. AI ki madad aur apni learning ko sachai se batayein.

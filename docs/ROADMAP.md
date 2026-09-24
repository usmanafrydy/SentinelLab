# Delivery schedule - September 24 to October 17, 2026

Deadline: October 17, at least two days before October 19. October 18 is contingency only. Daily availability is unconfirmed; provisionally plan around 2-3 hours per day and reduce optional scope when necessary.

| Dates | Work | Completion checkpoint |
| --- | --- | --- |
| Sep 24 - Day 1 | Requirements, success criteria, event-format design, learning example | Written scope, measurable criteria, valid synthetic example |
| Sep 25-26 | Verify Python environment, introduce Python through records, implement validation | Documented setup and parser checks |
| Sep 27-28 | Normalize timestamps, persist events, handle duplicates/conflicts | Import survives restart and repeat imports |
| Sep 29-30 | Basic upload and search workflow | Import and inspect events through a local browser |
| Oct 1-3 | Specify window/grouping behavior and implement three rules | Positive, negative, and boundary checks |
| Oct 4-5 | Alert deduplication, evidence references, rule explanations | Repeatable results with traceable evidence |
| Oct 6-7 | Edge cases and detection review | Tested rules and documented limitations |
| Oct 8-9 | Dashboard, investigations, notes, timelines | Complete analyst review workflow |
| Oct 10-12 | Access protection, input security checks, report exports | Protected workflow and faithful reports |
| Oct 13-15 | Local-lab scenarios, evaluation, fixes, clean setup, documentation | Reproducible complete demonstration |
| Oct 16-17 | Demo recording, case study, accurate CV bullets, release | Portfolio package and release saved on GitHub |

## Scope priorities

Required: one format, three rules, evidence views, investigations, access protection, reports, meaningful tests, and reproducible documentation.

Optional: second format, automatic collection, multiple roles, container packaging, and hosted demo. Do not add optional work while required acceptance criteria remain unmet.

## Daily working pattern

Explain the concept; implement a bounded change; run relevant checks; have the owner review or try the result; record progress; commit and publish the checkpoint. Do not equate a scheduled date with completed work.

## Release gates

1. All required criteria in ACCEPTANCE_CRITERIA.md have results.
2. Clean setup reproduces the main workflow.
3. Known limitations and evaluation context are documented.
4. GitHub contains the final source, setup instructions, and portfolio material.

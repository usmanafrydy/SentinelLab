# SentinelLab project brief

Status: Day 1 working specification, September 24, 2026. Requirements are not implemented yet.

## Problem and user

A learner acting as a security analyst needs to review authentication records, find suspicious sequences, and explain findings with evidence. Manually reading individual records makes related activity easy to miss.

SentinelLab will provide a local web application that imports records, applies three transparent rules, and supports investigation. The first version has one analyst account and one local installation.

## Outcome and deadline

Deliver a reproducible portfolio prototype by October 17, 2026, at least two days before October 19. October 18 is contingency time, not planned feature development.

The owner has basic knowledge of Python, networking, and cybersecurity. Daily availability is unconfirmed; the schedule provisionally assumes 2-3 hours a day. Explain new concepts during implementation and adjust optional scope to actual progress.

## Main user journey

1. The analyst signs in.
2. They import a synthetic or authorized local-lab JSON Lines file.
3. The application reports accepted, rejected, and duplicate records.
4. The analyst searches normalized events and runs detections.
5. They open an alert and inspect its rule, evidence, and timeline.
6. They add notes, change workflow status, and record a disposition.
7. They export a report that separates observed facts from conclusions.

## Required features

- One input format with explicit validation, timezone handling, and import summaries.
- SQLite persistence, duplicate handling, and event search.
- Three configurable, versioned rules: repeated failures; failures across accounts; success after a failure burst.
- Alerts with stable identity and original supporting event references.
- Investigation statuses: open, investigating, closed.
- Separate dispositions: undetermined, benign, suspicious, confirmed incident. A confirmed-incident disposition requires an analyst rationale; the detector cannot assign it automatically.
- Analyst authentication and protection of state-changing actions.
- Markdown and JSON report exports with evidence, notes, and limitations.
- Meaningful automated tests, a labeled lab evaluation, setup documentation, and a recorded demo.

## Scope boundaries

No production monitoring, automatic IP blocking, malware execution, internet-wide scanning, machine learning, live threat-feed subscription, or multi-tenant service in version 1. Public hosting, multiple roles, extra log formats, and automatic collection are optional.

## Definition of done

All required acceptance criteria in ACCEPTANCE_CRITERIA.md have recorded results; a clean setup can reproduce the demo; no secrets or private evidence are committed; remaining limitations are documented; final code and documents are saved on GitHub.

## Portfolio claims

Describe the system as a local learning prototype. Report measured results with their dataset and hardware context. Synthetic test results do not establish performance or accuracy on real organizational traffic. Explain AI assistance honestly and demonstrate understanding of key decisions.

# SentinelLab portfolio summary

**SentinelLab v0.1.0 | Guided AI-assisted cybersecurity project**

SentinelLab is a local Python and SQLite prototype that turns imported login records into explained alerts, investigation notes and saved reports. It demonstrates the difference between detecting a suspicious pattern and establishing a confirmed compromise.

The system validates bounded JSONL events, normalizes timestamps, preserves accepted original text and prevents duplicate events. Three rules cover repeated account failures, failures across distinct accounts and success after earlier failures. Browser investigations retain notes, decisions and revision-aware history; JSON/Markdown reports link the saved case to its original evidence. Local sign-in protects browser access within the documented loopback-only scope.

The completed portfolio includes working source, synthetic data, reviewed screenshots and reports, a case study, setup/handover guides and a cumulative handbook. Final verification passed 194 tests and seven authenticated workflow checks. Twelve authored evaluation scenarios produced TP/FP/TN/FN each three, while all expected rule sets agreed. Those results do not estimate real-world accuracy.

Technology: Python 3.12, SQLite, standard-library HTTP server, HTML, CSS, JavaScript and unittest. No third-party application framework or live collector is part of the implementation.

The project received substantial AI assistance for implementation, tests, documentation and debugging. The owner's work includes guided operation and learning; a full presentation assessment has not been completed. Use the conservative CV wording while building confidence explaining the design.

Limitations: a single local account, no public production deployment, no cryptographic evidence integrity, no automatic report redaction, and unverified Word pagination. The original laptop's restricted local Git metadata remains separate from verified published source. These limits are documented rather than hidden by the final version number.

[Source repository](https://github.com/usmanafrydy/SentinelLab) · [v0.1.0 notes](../releases/v0.1.0.md) · [Handover](../HANDOVER.md) · [Case study](CASE_STUDY.md) · [Demonstration](DEMO_SCRIPT.md)

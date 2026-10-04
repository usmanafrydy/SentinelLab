# Release readiness after Day 19

Reviewed 4 October 2026. Target completion is 17 October. The [Day 18 acceptance review](FINAL_ACCEPTANCE.md) passed its automated checks with qualifications; Day 19 prepares v0.1.0-rc.1 as a pre-release; a final stable release remains pending. Component coverage means implementation and relevant checks exist; it does not mean all environments or risks have been tested.

| Criterion | Evidence available | Remaining qualification |
| --- | --- | --- |
| AC-01 Validation | Reader and CLI tests; bounded JSONL contract | Only the documented login format |
| AC-02 UTC normalization | Offset, boundary and invalid timestamp tests | Does not establish source clock accuracy |
| AC-03 Preserve and deduplicate | Storage tests, repeat imports, original-record review | Original text, not forensic byte-image custody |
| AC-04 Persistence and search | Search/case tests and restart rehearsal | Single local database; no distributed scale test |
| AC-05 R1 | Threshold/window/grouping/rearm tests | Fixed lab threshold, false positives possible |
| AC-06 R2 | Distinct-user/window tests | Shared IP is not one person or proof of spraying |
| AC-07 R3 | Earlier-failure/success boundary tests; demo | Equal-time failures excluded; intent unknown |
| AC-08 Explained alerts | Versioned snapshots, deduplication, linked originals | Late input can produce different recomputed IDs |
| AC-09 Investigations | Revision/history/rollback tests; browser case | Direct file access can alter history |
| AC-10 Exports | Snapshot/limits/fidelity tests; reviewed Day 17 pair | No signing, encryption or automatic redaction |
| AC-11 Analyst access | scrypt/session/logout/spoof tests; signed-in demo | Local account only; owner reported manual CLI success; visibility not independently observed |
| AC-12 Hostile inputs | Bounds, request-token, escaping and query tests | No production security audit or public hosting |
| AC-13 Edge cases | Ties, boundaries, duplicates and ordering tests | Rule-specific coverage, not all attacks |
| AC-14 Evaluation | Frozen labels, twelve scenarios, reproducible metrics | Authored with rule knowledge; not independent/blinded |
| AC-15 Reproduction and demo | Fresh venv, workflow helper, setup, screenshots and reports | Verified network ZIP and fresh venv passed; git clone not tested; presentation/final release pending |

## Remaining work before final release

1. Source acquisition: completed through a verified HTTPS ZIP route on Day 18, followed by checking all 152 blobs and running 194 tests in a fresh venv. Earlier runtime TLS setup is not claimed repaired; git clone remains untested.
2. Interactive account command: owner reported successful creation on Day 18. The separate ignored file exists and was not read. This is user-reported evidence; the assistant did not directly observe password visibility.
3. Word layout: content preservation and structure are checked. The supported Day 18 render attempt failed because bundled LibreOffice soffice.exe is missing; pagination stays unverified. Use the Markdown companion for reading meanwhile.
4. Acceptance sequence: existing and downloaded suites, seven HTTP rehearsal checks, exact evaluation comparison and distribution review completed. Day 18 edits only documentation/results; verify the final publication inventory and unchanged application files.
5. Presentation and versioned release: Day 19 prepares VERSION 0.1.0-rc.1, [candidate notes](releases/v0.1.0-rc.1.md) and [practice guide](portfolio/PRESENTATION_PRACTICE.md). The owner has been asked the first question; do not mark practice complete without actual responses. Publish the candidate as a GitHub Pre-release at the reviewed commit and verify its tag target. No final stable version or video is claimed. Retain limitations when making the final release decision.

Existing local Git metadata remains behind because of Windows restrictions; connector publication and complete blob verification are used. This is a known local-history limitation, not permission to reset work or change access controls. The deadline remains October 17. Optional new features should not displace the remaining verification and explanation work.

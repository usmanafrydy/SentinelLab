# Release readiness after Day 17

Reviewed 4 October 2026. Target completion is 17 October. This is an evidence map for final review, not a declaration that the release is complete. Component coverage means implementation and relevant checks exist; it does not mean all environments or risks have been tested.

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
| AC-11 Analyst access | scrypt/session/logout/spoof tests; signed-in demo | Local account only; hidden typing not reverified |
| AC-12 Hostile inputs | Bounds, request-token, escaping and query tests | No production security audit or public hosting |
| AC-13 Edge cases | Ties, boundaries, duplicates and ordering tests | Rule-specific coverage, not all attacks |
| AC-14 Evaluation | Frozen labels, twelve scenarios, reproducible metrics | Authored with rule knowledge; not independent/blinded |
| AC-15 Reproduction and demo | Fresh venv, workflow helper, setup, screenshots and reports | Network download/clone and final release checkpoint pending |

## Open verification items before final release

1. Recheck source acquisition through an authorized working network path, or explicitly retain the certificate/download limitation. Do not disable TLS verification.
2. Have hidden interactive account entry checked locally without exposing a password in chat. Account service and HTTP sign-in are already tested; keyboard entry is a separate boundary.
3. Render and inspect the cumulative Word handbook when the supported renderer is available. Until then, label pagination unverified and retain the readable Markdown companion.
4. Run the final acceptance sequence against the final source, review the distribution for credentials/private logs and rehearse the presentation. Record failures and outcomes; do not substitute screenshots for these checks.
5. Create the final versioned release checkpoint and ensure the user can explain the architecture, a rule, a false alarm and a report. No final release tag or video was created on Day 17.

Existing local Git metadata remains behind because of Windows restrictions; connector publication and complete blob verification are used. This is a known local-history limitation, not permission to reset work or change access controls. The deadline remains October 17. Optional new features should not displace the remaining verification and explanation work.

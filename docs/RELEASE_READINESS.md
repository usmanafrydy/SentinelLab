# Final v0.1.0 release decision

Reviewed October 4 and finalised October 5, 2026. Decision: complete the bounded local portfolio milestone as v0.1.0 with the qualifications below. The user explicitly proceeded after optional exercises were waived as a release blocker. All 159 baseline files matched the candidate; Day 20 passed 194 tests, seven HTTP rehearsal checks and exact evaluation comparison. See [final notes](releases/v0.1.0.md), [verification record](../reports/examples/day20_release_checks.json) and [handover](HANDOVER.md). This is not production certification.

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
| AC-15 Reproduction and demo | Fresh venv, workflow helper, setup, screenshots and reports | Verified ZIP/fresh venv and demo evidence; v0.1.0 release; git clone not tested; owner practice optional |

## Retained qualifications and their disposition

1. Source acquisition passed through a TLS-verified ZIP route with every blob checked on Day 18. Fresh venv passed 194 tests. Earlier runtime certificate settings, git clone and other operating systems are not claimed verified.
2. The owner reported successful separate manual account creation. Only file existence was checked; password/hash were not read and keyboard visibility was not independently observed.
3. Word content is preserved and the supported renderer is retried at this checkpoint. Missing bundled LibreOffice leaves visual pagination unverified; the Markdown companion is the readable alternative. This is a documented non-blocking layout qualification.
4. Automated acceptance and distribution checks provide evidence for the local scope. They do not certify public hosting or every hostile-input scenario. Final publication must match the reviewed complete tree and release tag target.
5. Presentation practice is optional. The owner correctly prioritised supporting evidence in one answer; no complete presentation or broad proficiency assessment is claimed. The final CV wording describes guided AI-assisted work.
6. Original local Git HEAD/index remain restricted and behind. Connector publication and complete blob comparison establish published file content, not repaired local history. No reset, ACL change or force push is authorised by this limitation.

The previous v0.1.0-rc.1 remains preserved. Publish v0.1.0 at the reviewed final commit; subsequent changes require a new version. Optional live collection, public hosting, multiple roles, stronger evidence integrity and further learning are future work, not unfinished promises in this bounded release. No compulsory Day 21 task or automation exists.

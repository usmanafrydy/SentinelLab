# Day 18 final acceptance review

## Day 20 final local release disposition

Version 0.1.0 completes the agreed local portfolio scope with documented qualifications. Final checks passed 194 tests in 28.258 seconds, seven authenticated workflow checks and an exact evaluation-report match. Application source remains unchanged from the candidate. Presentation practice is optional by the latest user direction and is not claimed complete. Word visual layout and restricted original local Git history remain non-blocking disclosed limitations. See [release decision](RELEASE_READINESS.md), [handover](HANDOVER.md) and [final notes](releases/v0.1.0.md). Earlier dated evidence below is historical, including statements that release or practice was then pending.

Reviewed 4 October 2026. Decision: the automated acceptance checks pass with documented qualifications. This is the acceptance-review checkpoint, not a final version tag, production certification or independent audit. Completion target remains 17 October.

## Exact source and method

Tested commit: cbc94443ead66ca2268dab49968b255e463cf00e (Day 17). All 152 local baseline blobs matched GitHub before edits. An HTTPS GitHub commit ZIP was downloaded with bundled Python urllib using its default SSL context; certificate checking remained enabled. The archive was 822122 bytes. Every extracted path and Git blob hash matched the published inventory. Extraction went to a new ignored folder and excluded private/runtime files. Archive SHA-256 and detailed results are in [the acceptance record](../reports/examples/day18_acceptance.json).

A fresh venv was created without pip using the existing MSYS2 UCRT Python 3.12.7 installation on Windows, with SQLite 3.46.1. No third-party application packages were installed. A new OS or fresh Git clone was not tested. The earlier MSYS2/PowerShell certificate configuration was not repaired; the bundled Python download route worked. A ZIP contains source, not Git history.

## Results

| Check | Result | Scope |
| --- | --- | --- |
| Existing workspace suite | 194 passed in 35.288 s | Existing application source |
| Downloaded fresh-environment suite | 194 passed in 32.519 s | Same source on same Windows laptop |
| Authenticated HTTP rehearsal | Seven checks passed | Separate server, temporary account/data, import through report, restart/logout and cleanup |
| Synthetic evaluation | Exact parsed-JSON match, including fingerprints | 12 scenarios; 12 rule agreements; TP/FP/TN/FN each 3 |
| Manual account command | Owner reported account created; separate ignored file exists | Assistant did not observe keyboard visibility or read credentials |
| Distribution inventory | 152 baseline paths reviewed; private/runtime paths absent | Explicit Day 18 additions reviewed before publication |
| Portfolio evidence | All six original records match synthetic sample | Published report, not private investigations |

Day 18 changes documentation and the acceptance record only. Application Python, interface assets, tests, rules and evaluation data remain unchanged from the tested commit. Publication verifies that invariant and all final file hashes. Test durations are observations, not performance targets. The last browser demonstration was Day 17; no new browser or accessibility audit is claimed today.

## Evidence for every acceptance criterion

The full suite above ran all listed modules. Paths below are repository-relative; the detailed promises remain in [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md).

| Criterion | Executed evidence | Qualification |
| --- | --- | --- |
| AC-01 Validation | tests/unit/test_reader.py; tests/integration/test_cli.py | Documented bounded JSONL format only |
| AC-02 UTC | test_reader.py; test_search.py; detection tests | Clock authenticity is not established |
| AC-03 Preserve and deduplicate | test_storage.py; HTTP reimport rehearsal | Original accepted text, not forensic disk custody |
| AC-04 Persistence and search | test_storage.py, test_search.py, test_cases.py; restart rehearsal | Single local SQLite database |
| AC-05 R1 | test_detection.py; test_detection_day07.py | Five failures/300 s; fixed lab threshold |
| AC-06 R2 | test_detection_day07.py | Ten distinct accounts/600 s; shared IP is not a person |
| AC-07 R3 | test_detection_day07.py; rehearsal | Success after earlier failures; equal-time failures excluded |
| AC-08 Explained alerts | test_alert_storage.py; test_web_alerts.py; repeat detection rehearsal | Late input can change recomputed findings; saved snapshots remain |
| AC-09 Investigations | test_cases.py; test_web_cases.py; rehearsal | Direct database access can alter history |
| AC-10 Faithful reports | test_reports.py; rehearsal; synthetic report review | No encryption, signature or automatic redaction |
| AC-11 Local access | test_auth.py; rehearsal; user-reported CLI account creation | Single local account; no independent keyboard observation |
| AC-12 Hostile input | Reader, storage, auth, web and report tests | Tested bounds/escaping/queries/session writes; not a penetration-test certificate |
| AC-13 Edge cases | Both detection modules, storage and evaluation tests | Known rule boundaries and scenarios; not all attack techniques |
| AC-14 Honest evaluation | test_evaluation.py; repeated evaluate.py report | Authored with known rules; 50% toy-corpus metrics are not real-world accuracy |
| AC-15 Reproduction and demonstration | Verified network ZIP, fresh venv, suite/rehearsal, Day 17 gallery/script | Source acquisition now exercised; owner's presentation and final versioned release remain pending |

## Publication privacy and release limits

The reviewed inventory excludes secrets, runtime folders, private/raw data, normal generated reports, environments and database files. Only explicit documentation and the safe acceptance record are added today. The six public portfolio originals match the known fictional sample. This targeted review does not promise that arbitrary future files are secret-free. No private account content was read.

Word content preservation and structural checks are separate from page-layout review. The supported renderer failed after the Day 18 update because LibreOffice soffice.exe was not found in the bundled runtime path. Visual pagination remains unverified. Content checks retained earlier explanations and all 24 tables; the handbook now has 1478 paragraphs. The original local Git HEAD/index remain behind under existing Windows restrictions. Connector publication verifies source files; it does not synchronize that local history.

The final release remains pending while we complete presentation practice, disposition the document-layout limitation and deliberately create a versioned release checkpoint. No final tag, video or public deployment was created today. The existing [demo script](portfolio/DEMO_SCRIPT.md), [case study](portfolio/CASE_STUDY.md) and [Day 18 lesson](DAY_18_GUIDE.md) support the next step.

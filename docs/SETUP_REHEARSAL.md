# Day 16 setup rehearsal record

Completed 4 October 2026; work began 3 October. Baseline published commit: 834a51c1bc170c1c1f6240f72d8d02837594387b. All 137 published blobs matched local bytes before changes. The clean rehearsal folder is ignored data/runtime/day16_clean, separate from the owner's current account/database. No private data or existing environment was copied.

## Source acquisition and environment

Direct archive acquisition from GitHub failed: Python reported CERTIFICATE_VERIFY_FAILED and PowerShell reported authentication failure during TLS. Certificate verification was not disabled. Fallback: reconstruct the source tree from local bytes individually verified against all GitHub blob hashes. This establishes equivalence to the published source, but does not verify a fresh network download or clone.

A new environment was created with Python -m venv --without-pip. It reports isolated True, Python 3.12.7, MSYS2 UCRT/GCC 14.2.0 64-bit and SQLite 3.46.1, with hashlib.scrypt available. No third-party application dependencies were installed. This is an empty project environment on the same laptop, not a clean OS or a cross-platform certification.

The untouched baseline passed all 193 tests in the new environment. Then the new rehearsal helper, its regression test and the revised login header-rejection test were copied in as explicit Day 16 candidate changes; existing application code stayed identical to the published baseline. The final candidate suite passed 194 tests. The Day 15 evaluation report remains unchanged because application Python and the evaluation CLI were not changed.

## Workflow observed

| Check | Observed result |
| --- | --- |
| Local access | Anonymous summary rejected; synthetic account can sign in and load workspace |
| Sample upload | 16 inserted; zero rejected |
| Repeated upload | Zero inserted; 16 duplicates |
| Detection | Three saved alerts covering R1, R2 and R3 |
| Repeated detection | Three alerts remain; two saved runs |
| Investigation | R3 case created, note saved, closed as suspicious with reason, revision 3 |
| Reports | JSON contains all three actions and matching original evidence; Markdown returns an attachment |
| Attribution | All three case actions use the signed-in synthetic analyst |
| Restart | Case and three alerts survive; previous session rejected |
| Logout | Access rejected after logout |
| Cleanup | Worker exits cleanly before temporary account/database directory removal |

Closing the synthetic case as suspicious is an analyst exercise, not a finding of confirmed compromise. The HTTP checks use actual routes and a separate server process. They are not a new visual browser audit. Existing frontend code is unchanged.

## Changes made because of the rehearsal

SETUP.md had accumulated multiple historical startup addresses, different database names and obsolete test counts. It now starts with the owner's continuation command, then provides one ordered fresh-install path, interpreter selection, capability checks, tests, account setup, startup, sample workflow and troubleshooting. Historical lessons remain in the daily guides and cumulative handbook.

scripts/rehearse.py provides one repeatable synthetic workflow check. It creates a random temporary account, starts the production server class in a child worker on an OS-assigned loopback port, makes authenticated HTTP requests, checks duplicates/case/export/restart/logout and then cleans up. The worker receives shutdown through its private stdin pipe; EOF also requests shutdown if the parent ends. There is no HTTP shutdown endpoint and no authentication bypass. Initial experimental process termination was unreliable in this restricted Windows environment; the final helper uses cooperative shutdown and no taskkill command.

tests/integration/test_rehearsal.py runs that helper from another working directory and checks its success result and absence of files in that directory. The helper checks actual behavior; the test ensures the shipped command stays runnable. Forced OS/process termination may still leave temporary files. A failed shutdown produces a failure rather than a false cleanup claim.

An initial candidate suite encountered Windows connection-aborted error 10053 in the existing login header-protection test. tests/integration/test_auth.py now sends an empty body for header-only rejection cases, avoiding a race between an early server close and a discarded request body. The expected 403/415 responses are unchanged; malformed JSON/body checks remain separate. Application request handling was not weakened or changed. The adjusted test passed twenty consecutive targeted runs, followed by verification of the complete suite result. This is a focused test correction, not a claim that all possible transport failures are eliminated.

A subsequent full run encountered the same error in an anonymous-write test. The shared HTTP fixture in tests/integration/test_web.py now buffers each finite test request and sends it together, avoiding a separate body send after early rejection. It never retries a POST and leaves status assertions intact. The final full run passed 194 tests in 33.611 seconds. The clean candidate therefore includes both adjusted existing test files, the new helper and its regression test; production source remains unchanged.

## Unverified steps and boundaries

Interactive account.py reached its first hidden-entry prompt, but automatic approval review rejected terminal input because sandbox_approval is disabled. No private password was requested. Final rehearsal account creation uses the real account service with a random password in memory. Hidden interactive typing remains a manual check.

The trial terminal processes did not survive the app/session restart. Later final rehearsal workers completed their cooperative exits. No unrelated server was stopped. Source download/clone, interactive keyboard input, other OS/Python distributions, installation of Python itself, browser visual usability and public hosting are outside the completed verification.

The original Desktop copy's Git metadata is still restricted and behind; publish via connector with full file-hash verification. Do not reset it or alter deny rules. The cumulative Word/Markdown lesson is updated at this checkpoint. Word page rendering remains a separate check; code tests cannot verify pagination.

# Day 15 Understanding what the rules catch and miss

Completed 3 October 2026. Release target remains 17 October 2026.

## What we built today

We added a repeatable evaluation of twelve separate, fictional login situations. The evaluation runs the real event importer, SQLite storage and all three detection rules. It compares the findings with labels written before the first run. It produces a JSON report with every scenario, the overall counts, the calculations and hashes identifying the inputs and implementation.

This work answers two different questions. First, did the program follow its written rules? All twelve scenarios produced the expected set of rule IDs. Second, did those rules separate malicious stories from harmless stories? They caught three of the six malicious stories and raised alerts in three of the six harmless stories. These findings expose the limits of simple login thresholds.

There is no new button in the browser today. Evaluation is a developer command and a published synthetic results file. Your Overview, Events, Detection and Investigations workspaces continue to work as before. Existing accounts, cases, notes, databases, sign-in and report exports were not changed by the evaluation.

Roman Urdu: Aaj hum ne system ka imtehan liya. Hum ne dekha ke kin misaalon par alert aata hai aur kin par nahi. Alert aana hacking ka pakka saboot nahi, aur alert na aana bhi safety ka pakka saboot nahi.

## Why we needed labels before running the program

A label is the answer supplied by the scenario author. Each story is labeled benign, meaning harmless in the story, or malicious, meaning an unauthorized actor is involved in the story. For example, the owner forgetting a password is benign. An attacker guessing that password is malicious. Their recorded failures may look identical.

These are fictional ground-truth labels. We know them because we wrote the stories. SentinelLab sees the event records, not the person's true intention. In a real investigation, additional evidence would be needed to support a conclusion. You must never explain these labels as if the software discovered the actor's identity.

We also wrote expected_rules for each story. This is a separate field: it says which documented rules should fire. A benign story can correctly be expected to trigger R1. If it does, the implementation followed its rule, but the scenario is still a false positive when judged against intent. Confusing these two measurements would hide the limitations.

The evaluation contract and manifest were written before the first detector run. We kept the existing rule implementation unchanged. The cases are separate from earlier samples and test fixtures, but they were authored with knowledge of the rules. Therefore this is not a blinded or independent external evaluation. Now that the cases have been run, they form a reusable benchmark; they are no longer unseen data for future tuning.

## The three rules we evaluated

R1 looks for at least five failures for the same username and source IP within an inclusive five-minute window. R2 looks for failures involving at least ten distinct usernames from one source IP within an inclusive ten-minute window. R3 looks for a successful login after at least five earlier failures for the same username and source IP within five minutes; failures at the exact success time do not count as earlier failures.

These rules find patterns worth reviewing. They cannot tell whether an owner forgot a password, software retained an old password, or an attacker guessed passwords. They also cannot observe events that were never imported. Detection runs only when requested; there is still no live collection of laptop or network activity.

We deliberately included situations that cross the thresholds and situations that avoid them. Changing a threshold just to make today's score look better would weaken the evaluation. Any later rule improvement needs a separate set of new cases as well as checks that older behavior still works.

## How one scenario becomes one score

Our scoring unit is one scenario, not one event and not one alert. If any rule raises an alert, the scenario prediction is positive. If none raises an alert, it is negative. R1 and R3 can both describe one sequence of failures followed by success. Counting that story twice would exaggerate the number of situations detected.

The four possible results form a confusion matrix. The word confusion simply means we are comparing what the story says with what the detector predicts.

| Result | Meaning | Day 15 count |
| --- | --- | --- |
| True positive or TP | Malicious story with at least one alert | 3 |
| False negative or FN | Malicious story with no alert | 3 |
| False positive or FP | Benign story with at least one alert | 3 |
| True negative or TN | Benign story with no alert | 3 |

Roman Urdu: False positive ka matlab be-zarar activity par alert. False negative ka matlab attack wali misaal par alert na aana. Dono cheezein report karna zaroori hai.

## Every scenario and its result

All filenames below are inside data/evaluation/day15. Each JSONL file contains one complete independent story. All usernames, addresses and events in these files are synthetic. The manifest holds the explanation and labels; event files contain only the event fields accepted by the application.

| JSONL filename | Story intent | Rules observed | Score |
| --- | --- | --- | --- |
| routine_success.jsonl | Benign correct sign-ins | None | TN |
| typing_errors.jsonl | Benign three mistakes then success | None | TN |
| stale_client.jsonl | Benign client retries an old password six times | R1 | FP |
| shared_gateway.jsonl | Benign ten staff accounts each make one mistake behind one IP | R2 | FP |
| owner_recovery.jsonl | Benign owner makes six mistakes then succeeds | R1 and R3 | FP |
| occasional_errors.jsonl | Benign four mistakes spread over fifteen minutes | None | TN |
| rapid_guessing.jsonl | Malicious seven rapid guesses at one account | R1 | TP |
| many_accounts.jsonl | Malicious attempts against twelve accounts | R2 | TP |
| guess_then_success.jsonl | Malicious success after six guesses | R1 and R3 | TP |
| slow_guessing.jsonl | Malicious six guesses spaced ninety seconds apart | None | FN |
| distributed_guessing.jsonl | Malicious six guesses from six IP addresses | None | FN |
| stolen_password.jsonl | Malicious first observed login using a stolen password | None | FN |

The shared gateway example explains why an IP is not the same as a person. Several legitimate people may share an address. The slow example keeps every five-minute window below five failures. The distributed example spreads the events across different IP groups. The stolen-password example has no preceding failure burst at all. These misses are documented coverage gaps, not hidden test failures.

The owner_recovery and guess_then_success stories deliberately have the same observable event pattern and different intent labels. This makes a crucial limitation visible: these login fields alone cannot distinguish the two stories. An analyst must collect context rather than treating R3 as automatic proof of compromise.

## What the percentages mean

Precision asks: among the scenarios that raised alerts, how many were malicious in the authored story? TP divided by TP plus FP is 3 divided by 6, or 50 percent. Recall asks: among the malicious scenarios, how many raised an alert? TP divided by TP plus FN is also 3 divided by 6, or 50 percent.

Specificity asks: among benign scenarios, how many stayed quiet? TN divided by TN plus FP is 3 divided by 6, or 50 percent. Accuracy counts all correct scenario predictions: TP plus TN divided by all scenarios, which is 6 divided by 12, or 50 percent. The JSON report includes every numerator and denominator, so the percentages can be checked. A zero denominator is reported as null, meaning unavailable, rather than inventing a percentage.

These values describe only this small, deliberately balanced and challenging corpus. They do not mean SentinelLab will catch half of real attacks, nor that half of your real alerts will be wrong. Actual event prevalence, missing logs, environment and attacker behavior would change results. There is no statistical confidence estimate or production accuracy claim. Twelve out of twelve expected rule sets agreeing is a different measurement from malicious-versus-benign classification.

## How the evaluation works inside the code

Step 1 is manifest validation. The evaluator reads a bounded UTF-8 JSON file and checks version, exact fields, unique scenario IDs, simple filenames, allowed labels, expected rule IDs and a short rationale. Repeated JSON keys are rejected to prevent ambiguous labels. Files must resolve inside the manifest directory. The suite supports one to one hundred scenarios.

Step 2 is input capture. Each event file is read with a two-MiB bound. The exact bytes are hashed and written into a temporary input file. A SHA-256 hash is a fingerprint that helps compare bytes between runs. It does not prove that the story is true, who wrote it, or that a file is trustworthy.

Step 3 creates a separate temporary database and uses the real import_events service. The evaluator requires nonempty input that inserts cleanly: no invalid rows, repeated identities, conflicting identities or blank lines. If a scenario cannot be imported properly, the entire evaluation fails instead of quietly excluding that scenario and making the score look better. The existing importer also enforces its line and event limits.

Step 4 calls the existing read-only detect function for all rules. It collects observed rule IDs, alert count and number of scanned events. It does not save alert runs or create investigation cases. After each scenario, the temporary database and copied input are removed during normal success or failure cleanup. A process crash may leave operating-system temporary files.

Step 5 compares predictions with intent, calculates the four counts, and separately checks observed versus expected rule sets. Step 6 returns a complete deterministic report. The report omits changing import times, machine-specific temporary paths and elapsed runtime. It includes manifest/event hashes and hashes of every Python file under src/sentinellab plus the evaluation CLI, making it possible to identify the implementation used. Source files must stay unchanged during a run for a meaningful comparison.

## What each new or updated file does

docs/EVALUATION.md defines the scoring and reproducibility contract. data/evaluation/day15/manifest.json holds twelve IDs, filenames, intent labels, expected rule sets and rationales. The twelve JSONL files listed above supply the actual login records. They are separate from the earlier demonstration samples.

src/sentinellab/evaluation.py validates the manifest, runs each isolated import and detection, calculates metrics and constructs the report. scripts/evaluate.py is the command-line entry point; it selects the manifest, prints JSON and returns a meaningful exit code. tests/integration/test_evaluation.py contains nine tests for scoring, zero denominators, repeated results, labels, malformed manifests, bad event files, byte bounds, cleanup and CLI behavior.

reports/examples/day15_evaluation.json is the saved synthetic result from the frozen corpus. It is safe to publish because it contains authored test scenarios and code fingerprints rather than personal investigation data. Generated private case reports still belong in ignored directories. docs/DAY_15_GUIDE.md is this complete lesson. README.md points readers to the current checkpoint; docs/SETUP.md adds the command; docs/ACCEPTANCE_CRITERIA.md records evaluation evidence; docs/PROGRESS.md and docs/NEXT_SESSION.md retain continuity.

docs/SentinelLab_Project_Handbook.docx and docs/SENTINELLAB_HANDBOOK.md preserve earlier lessons, add this chapter and update the current completion map. Helpers used to prepare the document or publish files stay outside the project. No new package or database migration was required.

## Run it yourself in PowerShell

Open PowerShell and enter the project folder. Run the evaluation command. These commands use the existing Python environment on your laptop.

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/evaluate.py
$LASTEXITCODE
```

You should see scenario_count 12, rule_agreement_count 12, three of each confusion category, and an exit code of 0. JSON is a structured text format: braces contain named values, and square brackets contain lists. Find the scenarios list and read one story at a time. Compare intent, observed_rules and classification before looking at percentages.

Exit code 0 means every expected rule set agreed. It does not mean there were no false positives or missed attacks. Exit code 1 means the run completed but at least one expected rule set differed. Exit code 2 means evaluation failed, for example because a manifest or event file was invalid. Invalid runs do not print a partial report to stdout.

To run all automated checks, enter the following command. The runner sets up the Python module search path for this repository.

```powershell
.\.venv\bin\python.exe scripts/run_tests.py
```

The current suite contains 193 tests, including nine evaluation tests. One initial full run encountered a Windows connection-aborted error in an existing login HTTP test; the isolated test and subsequent full-suite result are recorded in the progress log. The direct unittest command needs PYTHONPATH set to src; using scripts/run_tests.py avoids that setup mistake.

If PowerShell cannot find the Python executable, confirm the folder and environment using docs/SETUP.md. A fresh Windows Python installation normally creates .venv\Scripts\python.exe; this laptop's existing environment uses .venv\bin\python.exe. A nonzero exit code should be investigated before treating results as complete. Do not edit labels simply to make a failing check pass.

## Verification and limits

The evaluation tests check all four confusion classes using independent examples and verify formulas with unequal counts as well as zero denominators. They run the complete corpus twice and compare reports. They confirm that two rule findings in owner_recovery still count as one false-positive scenario. Tests also reject malformed labels, repeated JSON keys, path traversal, duplicate scenario IDs, invalid/repeated expected rules, oversized event input and dirty imports.

Another test simulates a detection failure and checks that the temporary database directory is removed. CLI tests run a separate Python process and check success, expected-rule mismatch and invalid-input exit codes. Existing tests continue to cover rule boundaries, evidence preservation, storage, browser access, cases and exports. Passing code tests does not verify Word page layout.

Word content and structure are checked separately while preserving prior chapters. The bundled Word renderer is attempted again for this checkpoint. If its LibreOffice executable remains missing, visual pagination remains unverified and is reported explicitly. The Markdown lesson remains directly readable.

## What happens next and how to explain this in an interview

Day 16 is planned as a clean-setup rehearsal: start from the published source in a separate clean folder, follow the documented installation and account steps with synthetic credentials, and verify the full import-to-report workflow. Record and fix reproducible setup problems. Then prepare the demonstration, an honest portfolio case study, accurate CV bullets, known limitations and release acceptance by 17 October. Public hosting and multiple user roles are not promised parts of this local prototype.

An accurate interview explanation is: I built an isolated synthetic evaluation harness for three login detection rules. I separated rule correctness from scenario intent, recorded false alarms and blind spots, and included reproducible inputs and implementation fingerprints. Avoid saying that the system proves hacking or has validated real-world accuracy.

Your practice question is: a legitimate owner forgets a password six times and then signs in; R1 and R3 both alert. Is that one false-positive scenario or two, under our scoring method? Explain your reason in this chat. We will discuss one question at a time.

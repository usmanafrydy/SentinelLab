# A five minute SentinelLab demonstration

Purpose: show how an imported login pattern becomes a traceable investigation without claiming that an alert proves hacking. Use synthetic data only. This is a suggested presentation length, not a measured performance result.

## Preparation

Follow [current setup](../SETUP.md). For a clean presentation use a new database filename, such as data/runtime/presentation.db, and your existing private account on an unused loopback port. Never overwrite an existing database or recreate its account merely to reset a demo. Start from the repository folder with the environment interpreter selected as projectPython:

```powershell
& $projectPython scripts/serve.py --database data/runtime/presentation.db --port 8780 --credentials secrets/analyst.json
```

Open http://127.0.0.1:8780/ and sign in privately before recording. Keep passwords and credentials out of screenshots. If that database already exists, continue it knowingly or choose another unused name; this command does not reset data. Stop only your own server with Ctrl+C when finished.

The Day 17 screenshots used a separate ignored day17_portfolio.db on port 8778 and a synthetic portfolio_analyst account. The owner's ongoing work remains day14_demo.db on 8776. The two databases do not synchronize. Credentials are not included in this portfolio folder; create your own account through the setup guide when reproducing from GitHub.

## 0 to 45 seconds Describe the problem

Show Overview. Say: SentinelLab is a local Python and SQLite learning project. It helps turn login records into explained alerts, investigation notes and reports. It processes uploaded files when asked; it is not a live network monitor.

State that the logs are fictional. The interface's Prototype label describes the product honestly and does not tie the display to an obsolete lesson number.

## 45 to 90 seconds Import and check duplicates

In Events choose data/samples/day07_all_rules.jsonl and import. Expect sixteen inserted and zero rejected on a new database. Import the same file again. Expect zero inserted and sixteen duplicates. Explain that source plus event_id defines identity; conflicting content is reported rather than overwriting the original.

If demonstrating the already prepared Day 17 database, both imports are already present: show the 16-event / 2-import counts rather than claiming you just made them. Further uploads add import history, so do not promise the import count always stays two.

## 90 to 150 seconds Explain detection

In Detection run All rules and save. On a fresh sample database expect three alerts, one per rule. Run again and show three existing alerts with another run recorded. A run is the check; an alert is the finding.

Say: R1 finds repeated failures for one account and IP, R2 finds failures against many accounts from one IP, and R3 finds a success after earlier failures. These thresholds are lab choices. Several people can share an IP; a forgotten password can produce the same pattern as guessing.

## 150 to 210 seconds Follow an alert to evidence

Open R3. Point to lab_user, 192.0.2.71, five failures from 09:20 to 09:24 UTC and a success at 09:24:30 UTC on 29 September 2026. Those are event timestamps, not today's import time. Open Original #16 in the prepared demo, or the success record's Original button in a fresh database where row IDs may differ. Explain original_record and first-import provenance, then Close evidence to return.

The rule includes failures at the five-minute start boundary and excludes failures at the exact success timestamp. Do not present equal timestamps as proof of ordering. The stable alert ID depends on rule/evidence identity, not the local row number.

## 210 to 270 seconds Record an investigation

Choose Investigate this alert. Create a short synthetic title or open its existing case. Save this observation:

> Five failures were followed by a successful login for the same account and IP. A corrected password is a possible benign explanation. Independent confirmation is not available in this sample.

Choose In progress and Suspicious, with a reason requesting account-owner confirmation and additional authentication context. Save and show the history. Do not choose Confirmed compromise just because the rule fired. A conclusion is an analyst judgment, and the database history is not tamper-proof against direct file access.

## 270 to 300 seconds Export and state the limits

Download Markdown or JSON from the case. Show the saved note, decision, rule facts and original records. An unsaved draft is excluded. The provided sample reports are a fallback if browser downloads are unavailable during a presentation; say they are previously exported examples.

Finish with: The twelve authored evaluation scenarios produced three true positives, three false positives, three true negatives and three misses. Every expected rule set agreed, but that is not real-world accuracy. The project also has 194 automated tests and a separate authenticated workflow rehearsal. It is a single-account local prototype with no live collector or production deployment claim.

## If something goes wrong

If signed out, sign in privately. If the page cannot connect, check the server terminal and matching port. If a case revision is stale, refresh, review the saved changes and submit your decision deliberately. Reusing an alert opens its existing case; it does not erase history. If counts differ because you already repeated steps, explain the existing state rather than resetting a database during the presentation. Use the labeled screenshots or saved synthetic report as a clearly identified fallback. No video has been recorded as part of Day 17.

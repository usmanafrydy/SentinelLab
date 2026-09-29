# Saved alerts - schema version 2

`scripts/detect.py` remains read-only by default. Explicit `--save` opens an existing database in SQLite `mode=rw`, enables foreign keys, acquires `BEGIN IMMEDIATE`, validates its schema, migrates version 1 if needed, evaluates one bounded snapshot, writes a completed run and alert links, then commits. It never creates a missing database. Imports/initialization still create version 1 and also accept version 2.

## Records

- `detection_runs`: completion time in UTC; selected rule configurations (IDs, version, threshold, window); event count; maximum event/import IDs at evaluation; matched, new, and existing counts. Even zero-alert saves record a run.
- `saved_alerts`: stable alert ID, rule/version, trigger time, first run ID, full immutable JSON result including reason, parameters, group, interval, and ordered evidence. No application operation edits these rows.
- `alert_evidence`: ordered foreign-key links to original events, with failure or R3 preceding-failure/triggering-success roles.
- `run_alerts`: which saved alerts matched each run. Old alerts need not appear in newer runs.

Events and imports remain unchanged by detection. Evidence IDs resolve only in their original database; IDs from other installations must not fetch local events. Stable alert identity excludes internal SQLite event IDs, as specified in DETECTION_RULES.md.

## Deduplication and late imports

Unchanged events/configurations create a new run, not another copy of each alert. An existing alert ID must have identical serialized content or the new run fails; historical results are never silently overwritten. A rule's ID/version/parameters and ordered evidence define identity, not its run ID.

Late events can change a window, trigger time, evidence, and alert ID. New results are saved alongside previous results; nothing deletes the old snapshot or declares it resolved. Run membership records results of a particular evaluation. Alert counts are not incident counts; rules may describe overlapping activity. Analyst conclusions/investigation history are not implemented yet.

## Atomicity and compatibility

Migration, evaluation, run insertion, alerts, evidence, and membership share one transaction and connection. Writers serialize with a five-second lock timeout. A failed migration/evaluation/write rolls back that attempt. Read-only preview/history never migrates. Unsupported versions and malformed schemas fail safely. Validation checks version and required columns, not cryptographic integrity.

Version 1 history readers report zero alerts/runs without creating tables. Version 2 supports event import, search, evidence retrieval, and the browser after its server code is restarted. No browser save-detection endpoint yet.

## Commands and bounds

`scripts/detect.py --database PATH --save [--rule R1|R2|R3|all] [--json]` returns run ID and scanned/matched/new/existing/total counts. Preview omits `--save` and returns full computed alerts. All rules is the default. Both modes exit 0 on success and 2 on fatal error.

`scripts/alerts.py summary|list|runs|get --database PATH --json` reads history. `get` needs `--alert-id` and returns evidence; a missing alert exits 1, malformed arguments/database errors exit 2. List/runs use `--limit` (1..200, default 50) and `--offset` (0..1,000,000, default 0). Alerts sort by descending trigger time then ID; runs sort by descending run ID. Human history output also uses formatted JSON.

Detection limits input to 10,000 events and combined evidence to 100,000 references. No partial saved results on limit failure. No total database retention limit; repeated saves grow run history. No background monitoring, encryption, tamper-evident storage, analyst authentication, or automatic incident confirmation is claimed.

Tests cover migration preservation; read-only versions 1/2; repeat/selected/empty runs; evidence lookup; migration conflicts; failed writes; unsupported/missing databases; late data; concurrent saves/imports; CLI persistence; bounds; and browser compatibility. See DAY_08_GUIDE.md for the walkthrough.

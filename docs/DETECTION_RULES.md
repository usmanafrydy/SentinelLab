# Detection contract - Day 7

## R1 version 1.0.0: repeated account failures

Default and currently fixed parameters: 5 distinct stored failed-login events, 300 seconds, group by exact username and canonical source_ip. Different source namespaces can contribute; source is part of event identity, not the grouping key. This assumes usernames are comparable across imported sources. Use one lab namespace if accounts differ across applications. A shared IP does not identify a person.

Evaluate stored UTC event time, not import time. Successes neither count nor reset a failure group. Sort failures by UTC time, then source and event_id. Evaluate all same-group events at an identical timestamp together: arbitrary tie order must not decide evidence membership.

At each failure timestamp t, expire events strictly older than t minus 300 seconds. Exactly 300 seconds is included. If the remaining count is below 5, arm the group. Add all failures at t. If armed and the resulting count is at least 5, emit one alert and disarm. The next alert is possible after the surviving pre-add window drops below 5. There is no separate fixed cooldown. Long sustained bursts can therefore produce only their first alert; its evidence is a snapshot at that trigger, not all later events. This is an intentional volume-control limitation.

Evidence includes every matching failure in the inclusive window at the triggering timestamp. Alert fields contain rule ID/version, parameters, group, first evidence time, trigger time, count, reason, stable alert ID, and evidence references. Internal event IDs resolve with database.py get against the same database. Alert IDs hash the rule/version/parameters/group and ordered evidence identities/timestamps; internal SQLite row IDs are excluded so import order does not change the alert ID.

Default execution is a read-only batch preview. Day 8 adds explicit --save for persistent deduplicated alerts and run history (ALERT_STORAGE.md). It does not monitor continuously or run on browser upload. Rerunning unchanged events returns identical alert IDs. Late imported events can change recomputed windows and IDs; saved historical snapshots remain. Zero alerts only means R1 did not find this pattern; it does not establish safety.

## Limits

Read at most 10,001 rows from one database snapshot. More than 10,000 events (including successes) fails the whole run without partial results. No time-filtered partial detection is offered because preceding events matter. Default preview makes no schema changes. Explicit --save upgrades existing v1 databases and saves results atomically; it never edits source events or creates a missing database. No extra dependencies.

False positives include forgotten passwords, misconfigured clients, and shared networks. Blind spots include fewer than five failures, activity spread across IPs/accounts, unavailable logs, and evidence outside the dataset. These thresholds are lab design choices, not measured real-world accuracy claims.

## R2 version 1.0.0: distinct-account failures

R2 counts 10 distinct usernames with failures per source IP in [t-600 seconds, t], batching ties. Repeated failures by one username count once toward the threshold; evidence retains every contributing failure and its username. Case and spaces remain significant. Successes do not contribute or reset the group. Source namespaces can contribute to the same IP group. This can suggest password spraying but cannot prove which passwords were attempted.

Expire failures older than 600 seconds and remove a username only when no failures for it remain. If the pre-add distinct-account count is below 10, arm the group. Add the entire timestamp batch; emit once if armed and the count reaches 10, then disarm. There is no fixed cooldown. Evidence is frozen at trigger time. Alert identity includes rule/version/parameters/IP and ordered evidence identities/timestamps/usernames, excluding internal row IDs.

## R3 version 1.0.0: success after failures

R3 evaluates each success independently, counting at least 5 matching username/IP failures in [t-300 seconds, t). Equal-time failures are excluded because logs do not establish their order relative to success. Process all successes at a timestamp before adding failures at that timestamp. Successes never clear the failure window; each qualifying success gets its own alert, including multiple successes at the same instant.

Evidence includes every contributing earlier failure plus the triggering success, with role preceding_failure or triggering_success. failure_count excludes that success. Alert identity includes rule/version/parameters/group and ordered evidence identities/timestamps/roles, excluding internal row IDs. Usernames are exact and IPs canonical; different source namespaces may contribute as for R1. A user correcting a password can trigger this rule legitimately.

## Combined engine and CLI

scripts/detect.py evaluates all three rules by default. Select --rule R1, R2, R3, or all. All selected rules use one bounded snapshot ordered by normalized UTC time/source/event_id. Preview opens read-only; --save evaluates inside the saving transaction. Output sorts by trigger time, rule ID, then alert ID. Existing detect_r1 remains available, and its valid-input behavior, version, and saved Day 6 preview are preserved.

Input is capped at 10,000 total events. Combined output is additionally capped at 100,000 evidence references across selected rules. Repeated successes can otherwise produce quadratic evidence output. Exceeding either bound fails the complete run with a safe error, with no partial report or writes. The evidence budget is checked before building R2/R3 alerts. Stored times are checked for canonical UTC formatting before evaluation.

Results are previews unless --save is supplied. Day 8 stores deduplicated alerts and run history; no continuous monitoring or browser detection yet. R1/R3 may describe the same activity; alert counts are not incident counts. Late data can change recomputed results while old saved snapshots remain. Exit 0 means successful evaluation regardless of alert count; exit 2 indicates an error. The default rule selection changed in Day 7; historical R1-only examples should use --rule R1.

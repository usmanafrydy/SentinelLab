# Detection contract - Day 6

## R1 version 1.0.0: repeated account failures

Default and currently fixed parameters: 5 distinct stored failed-login events, 300 seconds, group by exact username and canonical source_ip. Different source namespaces can contribute; source is part of event identity, not the grouping key. This assumes usernames are comparable across imported sources. Use one lab namespace if accounts differ across applications. A shared IP does not identify a person.

Evaluate stored UTC event time, not import time. Successes neither count nor reset a failure group. Sort failures by UTC time, then source and event_id. Evaluate all same-group events at an identical timestamp together: arbitrary tie order must not decide evidence membership.

At each failure timestamp t, expire events strictly older than t minus 300 seconds. Exactly 300 seconds is included. If the remaining count is below 5, arm the group. Add all failures at t. If armed and the resulting count is at least 5, emit one alert and disarm. The next alert is possible after the surviving pre-add window drops below 5. There is no separate fixed cooldown. Long sustained bursts can therefore produce only their first alert; its evidence is a snapshot at that trigger, not all later events. This is an intentional volume-control limitation.

Evidence includes every matching failure in the inclusive window at the triggering timestamp. Alert fields contain rule ID/version, parameters, group, first evidence time, trigger time, count, reason, stable alert ID, and evidence references. Internal event IDs resolve with database.py get against the same database. Alert IDs hash the rule/version/parameters/group and ordered evidence identities/timestamps; internal SQLite row IDs are excluded so import order does not change the alert ID.

This checkpoint is a read-only batch preview. It does not save alerts, monitor continuously, or run on browser upload. Rerunning unchanged events returns identical alert IDs; persistent alert deduplication and run history are future work. Late imported events can change the recomputed windows and preview IDs. Zero alerts only means R1 did not find this pattern; it does not establish safety.

## Limits

Read at most 10,001 rows from one database snapshot. A database containing more than 10,000 events (including successes) fails the whole detection run with a clear error; no partial results. The cap bounds this learning implementation's memory/evidence output. No time-filtered partial detection is offered because preceding events matter to the window. No schema changes, dependencies, source record edits, or new database files are made by detection.

False positives include forgotten passwords, misconfigured clients, and shared networks. Blind spots include fewer than five failures, activity spread across IPs/accounts, unavailable logs, and evidence outside the dataset. These thresholds are lab design choices, not measured real-world accuracy claims.

## Planned R2 and R3 (not implemented)

R2 will count 10 distinct usernames with failures per source IP in [t-600 seconds, t], batching ties. Repeated failures by one username count once toward the threshold; evidence retains contributing events. Proposed grouping mirrors R1's rearm-below-threshold behavior using distinct-account counts. This can suggest password spraying but cannot prove which passwords were attempted.

R3 will evaluate each success independently, counting at least 5 matching username/IP failures in [t-300 seconds, t). Equal-time failures are excluded because logs do not establish their order relative to success. Proposed identity includes the success and failure evidence; no cross-success cooldown. Confirm these policies with tests when implementing each rule.

# Current cumulative update through Day 20

Updated 5 October 2026. This cumulative handbook explains the completed SentinelLab v0.1.0 local portfolio scope and its retained limitations. Day 20 adds the final release decision, operating handover, project summary and conservative AI-assisted CV wording. Final checks passed 194 tests and seven authenticated workflow checks; the synthetic evaluation exactly matches prior results. Presentation practice is optional and not claimed complete. Word visual pagination and the original restricted local Git history remain disclosed qualifications. This final project milestone is not production security certification.

# SentinelLab Project Handbook

## A detailed guide to the system through Day 9

Updated 1 October 2026. Chapters 1 to 22 retain the Day 8 reference; chapters 23 to 25 add Day 9 and supersede earlier statements that browser alerts are still planned. Current core test total is 133. See the new chapters for current frontend guidance and the remaining design plan.

Prepared for the project owner on 30 September 2026. This handbook explains the working software, its files, its design decisions, its tests, and the remaining development plan. It is written for someone with basic Python, networking, and cybersecurity knowledge. Difficult concepts include short Roman Urdu explanations.

The current project can validate login records, preserve them in SQLite, search them in a browser or terminal, detect three suspicious login patterns, and save alerts without duplicating unchanged results. It is a local learning prototype. Investigation notes, analyst sign in, browser alert pages, and final report exports are still future work.

The application checkpoint covered here is GitHub commit 80e88e3344a5c6b56c573a80f796a3fb796c3ab1. The project is stored at C:\Users\Dell\Desktop\Projects\SentinelLab. Its repository is https://github.com/usmanafrydy/SentinelLab. The target completion date is 17 October 2026, at least two days before 19 October.

## How to read this handbook

Read the system overview and worked examples first. Next, follow the operating guide using synthetic samples. Use the file reference when you need to know where a feature lives. The database and rule sections explain the decisions you should be able to discuss in an interview. The test catalogue is a reference, not a list you need to memorize.

The file reference covers all 83 published files in the Day 8 checkpoint, including package markers and empty directory placeholders. Generated runtime files are explained separately because they are local data, not source code. This handbook and its Word edition are documentation added after that checkpoint.

Older daily guides describe what existed on their particular day. Some early planning files retain future wording. The current implementation and the Day 8 contracts take precedence when deciding whether a feature exists now. A learning day is a development checkpoint, not necessarily a different calendar day.

# 1 Purpose and current capabilities

## The problem SentinelLab addresses

A login log records individual attempts to access an account. One line might say that demo_user failed to log in from 192.0.2.10 at a particular time. Hundreds of separate lines are difficult to review manually. Related failures, activity across several accounts, and a success after a burst of failures can be missed.

SentinelLab organizes these records and applies transparent rules. Transparent means you can explain exactly why a rule produced an alert. The result includes the rule settings, time interval, account or IP grouping, and supporting event references. The analyst can look at the original records instead of trusting an unexplained warning.

The software does not attempt logins, attack systems, capture passwords, or scan the network. It reads files provided to it. Sample files describe invented activity; importing them does not generate that activity on a real computer.

## What works now

| Capability | Current behavior | Where you use it |
| --- | --- | --- |
| Format validation | Checks each JSON Lines record and reports safe line errors | check_events.py and imports |
| Normalization | Converts time to UTC and IP text to a canonical form | Ingestion layer |
| Event persistence | Saves accepted events and first original text in SQLite | database.py import or browser upload |
| Duplicate handling | Skips identical identities and reports changed-content conflicts | Import layer |
| Search | Combines exact account, IP, outcome, and time filters | Terminal and browser |
| Original evidence | Reads original text and first import information | Terminal get and browser View button |
| Three rules | Evaluates R1, R2, and R3 on one bounded dataset | detect.py |
| Read only preview | Shows computed alerts without saving a run | detect.py without --save |
| Saved alerts | Stores unique alerts and ordered event links | detect.py --save |
| Run history | Records each successful saved evaluation and its configuration | alerts.py runs |
| Automated checks | Day 8 suite contains 120 tests | run_tests.py |

## What is still planned

Browser alert views and a browser detection action are the next planned checkpoint. Investigation notes, workflow status, analyst disposition, action history, sign in, and report exports are not implemented. There is no continuous collector, background scheduler, machine learning model, email notification system, or automatic IP blocking.

Rule selection is configurable through --rule, but threshold and window values are currently constants in Python. Do not describe threshold editing in the interface as completed. The earlier architecture proposes broader configuration and an analyst account; these are targets.

## Events alerts runs and incidents

An event is one recorded occurrence. An alert is a pattern found by a rule. A run is one execution of detection that is explicitly saved. An incident is an analyst conclusion about harmful activity, which requires investigation beyond matching a threshold.

Five failures followed by a success may be a user correcting a forgotten password. Ten accounts failing from one IP may involve a shared network or a misconfigured application. An alert therefore means investigate, not account hacked.

Roman Urdu: Event aik entry hai. Alert shak wali activity ka signal hai. Run aik dafa checking hai. Incident ka faisla evidence dekh kar hota hai, sirf alert aane se nahi.

# 2 Architecture and the complete data journey

## The main layers

The project separates input handling, storage, detection, and presentation. Each layer has a different responsibility. This makes it possible to test the rules without using a browser, or to use the same importer from PowerShell and the browser.

```text
JSON Lines input file
        |
        v
Validation and time and IP normalization
        |
        v
SQLite events and imports
        |                         |
        v                         v
Search and original evidence     Detection snapshot
Terminal or browser              R1 plus R2 plus R3
                                  |
                         +--------+--------+
                         |                 |
                         v                 v
                    Preview only      Explicit save
                                      Alerts and runs
```

The browser branch currently stops at events and original evidence. The detection branch currently runs through terminal commands. Both can use the same database file, but starting them with different database paths gives them different datasets.

## What happens when you check a file

The wrapper scripts/check_events.py adds the src directory to Python's import path and calls the main function in sentinellab/cli.py. The CLI reads its arguments and calls read_events. The reader checks size limits, splits physical lines, decodes UTF 8, parses JSON, validates fields, and returns accepted and rejected records.

The checker prints counts and errors. It does not create a database, remove duplicate event identities, or run detection. Accepted means the record follows the format; it does not mean the login was safe or the source was authentic.

## What happens when you import a file

The import command checks that the input file is not the database itself. It parses the bounded input before writing. Then it opens SQLite, enables foreign key enforcement, and starts a write transaction. It creates the event schema only for a genuinely empty database, or validates an existing supported schema.

The importer creates one import-history row. For each valid record it computes canonical JSON and looks for its source and event_id. A missing identity is inserted. An identical identity and normalized content is counted as a duplicate. The same identity with different normalized content is reported as a conflict, preserving the first accepted record.

After processing, the importer updates its counts and safe error list, calculates total stored events, and commits. A storage failure rolls back the batch. Ordinary line rejections and identity conflicts do not prevent unrelated valid records from being saved.

## What happens when you search

The search layer validates the filter values and opens the database read only. It builds SQL conditions from fixed fragments and binds user values separately. Conditions use AND: an event must match every supplied filter. Count and page queries share one read transaction so they describe the same snapshot.

The result contains total_matches, returned, limit, offset, next_offset, and the page of events. Events are ordered by normalized timestamp and internal ID. Opening evidence returns extra fields including original_record, first_import_id, and first_line_number.

## What happens during detection

The engine validates the requested rule name. It reads at most 10,001 rows in normalized time, source, and event ID order. If there are more than 10,000 events, it rejects the whole evaluation. It validates stored timestamp formatting, passes the same snapshot to selected rules, applies a shared evidence budget, and sorts the results deterministically.

Default preview opens read only and returns results without storing anything. The --save path opens the existing database for writing, begins a transaction, upgrades schema 1 if needed, evaluates on that same connection, and saves the run and its unique alerts. The distinction is deliberate: looking at results and recording results are separate actions.

## What happens when you close the program

Closing a terminal ends that command. Stopping the browser server makes its address unavailable, but does not delete SQLite data. Stored events and saved alerts remain in the selected database file. Preview results shown only in a terminal are not automatically stored as alert history.

The browser is an interface to the local Python server. It is not the database. GitHub stores the shared source code and documents, not your ignored runtime databases. These are three different locations with different responsibilities.

# 3 Programming and security concepts

## Python modules packages and entry points

A module is usually one Python file. A package groups related modules in a directory. The __init__.py files mark these package boundaries in this project. A main function acts as the entry point for a command. The small scripts directory wrappers locate the source package and invoke that entry point without requiring a package installation.

For example, scripts/detect.py is the launcher; detection_cli.py parses options; detection/engine.py coordinates rules. Keeping these roles separate prevents terminal formatting decisions from becoming part of detection logic.

## Data classes exceptions and safe errors

The reader uses data classes to describe an Event, an AcceptedRecord, a RejectedRecord, and an ImportResult. An accepted record holds its normalized Event and original text together. Event and record objects are frozen where appropriate, reducing accidental reassignment after validation.

ValidationError means one record is unsuitable. InputFileError means the input file cannot be processed within the contract. StorageError represents a safe storage or detection failure. The distinction determines whether the program can continue to the next line or must stop the operation.

Errors describe the problem without echoing rejected input values. This helps avoid displaying an accidental secret in an error message. Original accepted evidence is available only through its deliberate evidence view.

## Dictionaries sets deques and counters

Dictionaries map keys to values, such as JSON field names or groups of events. Sets represent unique names, such as required fields. A deque is a queue that can efficiently remove the oldest item from the left and append new items on the right. R1, R2, and R3 use deques for moving time windows.

R2 also uses a Counter, which remembers how many failures for each username remain in the window. When the last failure for a username expires, the username is removed from the counter. That is why the distinct-account count can decrease correctly as time advances.

## Normalization and canonical values

Different text can describe the same meaning. The times 14:00:00+05:00 and 09:00:00Z describe the same instant. IPv6 also has multiple valid spellings. Normalization gives these values a consistent representation so comparisons work reliably.

The project stores UTC timestamps with six fractional digits and an explicit +00:00 offset. It uses Python's IP parser for canonical IP text. Username case and spaces remain significant. The system does not assume that Admin and admin are the same account.

Roman Urdu: Normalization ka matlab aik hi meaning ko aik jaisi shakal mein rakhna hai. Waqt ka format badalta hai, asal waqt nahi.

## SQL keys constraints and transactions

A primary key identifies a database row. A unique constraint prevents duplicate identities. A foreign key links a record to another table, such as an alert evidence row to an event. These are database rules, not merely comments in Python.

A transaction makes a group of changes succeed together or roll back together. BEGIN IMMEDIATE reserves the SQLite write transaction early, so another writer waits instead of racing to insert the same alert. Read operations use snapshots to avoid mixing counts and rows from different moments.

Roman Urdu: Transaction mein ya poora kaam save hota hai ya us attempt ka kuch bhi save nahi hota. Adhoori history nahi banani.

## Stable identity and hashing

Alert IDs use a SHA 256 digest of a deterministic description of the rule and evidence. The digest is a compact fingerprint for identity comparison. The R1, R2, or R3 prefix identifies the rule family. Internal database row IDs are excluded from the hashed identity, because importing the same logical records in a different order can assign different row IDs.

Hashing is not encryption. The alert still stores readable evidence. The hash does not prove the source log is genuine, does not authenticate an analyst, and does not make the database tamper proof. Its role here is deterministic identity and deduplication.

## Determinism idempotency and provenance

Determinism means the same valid data and rule settings produce the same result. Sorting events, batching equal times, and canonical identity construction support this. Idempotency here means repeated unchanged imports or alert saves do not add duplicate events or alerts. Import and run history can still grow to record repeated actions.

Provenance describes where a stored record came from. first_import_id and first_line_number identify its first accepted import location. original_record preserves its text. This supports explanation and review, but is not a complete forensic chain of custody.

## Authentication authorization and request protection

Authentication answers who you are. Authorization answers what you may do. Neither a full analyst account system nor role-based authorization exists yet. The local server's request token and origin checks reduce unwanted browser requests; they do not identify a user.

The server binds only to 127.0.0.1, so it is intended for this computer. Loopback restriction is not a replacement for authentication in a deployed service. Later access-protection work must explicitly protect evidence reads as well as writes.

# 4 Input format and validation

## JSON Lines format

A JSON Lines file contains one complete JSON object per nonblank line. There is no outer array and no comma between records. This makes line-specific feedback simple. The application accepts only a defined authentication-event format, not arbitrary CSV, Windows Event Log exports, packet captures, or every product's JSON logs.

```json
{"event_id":"example-001","source":"local-login-lab","timestamp":"2026-09-29T09:00:00Z","source_ip":"192.0.2.10","username":"demo_user","event_type":"login","outcome":"failure"}
```

| Field | Accepted value | Why it matters |
| --- | --- | --- |
| event_id | Nonblank string up to 128 characters | Identifies an event within its source namespace |
| source | Nonblank string up to 64 characters | Separates IDs from different log sources |
| timestamp | Date and time with seconds and Z or numeric offset | Establishes event time for windows |
| source_ip | Valid IPv4 or IPv6 without a zone suffix | Groups observed source activity |
| username | Nonblank string up to 128 characters | Identifies the recorded account exactly |
| event_type | login | Limits the supported event family |
| outcome | success or failure | Separates successful and failed attempts |

All seven values must be strings. Extra fields are rejected rather than ignored. Unknown-field rejection catches misspellings and discourages accidental ingestion of passwords or tokens. It does not automatically sanitize every sensitive value placed into an allowed field.

## Validation in order

First the reader requires an existing regular file and reads no more than the file limit plus one byte. Then it counts physical lines. For each line it checks length, decodes UTF 8, counts blanks, parses JSON with duplicate-key rejection, and validates the decoded object.

JSON arrays, non-object values, missing fields, unknown fields, repeated field names, nonstandard NaN or Infinity numbers, control characters, and unpaired Unicode surrogates are rejected. Dates must be valid, include an explicit timezone, and have no more than six fractional second digits. Leap seconds are not accepted by this implementation.

An invalid line normally contributes one rejection and does not stop later valid lines. A fatal file size or physical line count violation stops the whole file before results are returned. A final newline terminates the last line; it is not counted as an additional empty record.

## Limits and their meaning

| Limit | Value | Failure behavior |
| --- | --- | --- |
| Input or upload size | 2 MiB | Reject the complete input |
| Physical lines including blanks | 10000 | Reject the complete input |
| One line excluding LF | 16 KiB | Reject that line and continue |
| Stored events for detection | 10000 | Fail detection without partial results |
| Combined detection evidence references | 100000 | Fail detection without partial results |
| Search or history page size | 1 to 200 | Reject invalid request |
| Search or history offset | 0 to 1000000 | Reject invalid request |
| SQLite lock wait | 5 seconds | Fail safely if lock remains unavailable |

The import limit and detection limit are different. Several imports can produce more than 10,000 stored events, because total event storage has no retention cap. Detection then refuses to evaluate the oversized dataset. This is a bounded learning implementation, not a scalable production pipeline.

## Accepted original text

Accepted original text is kept without the LF newline terminator. A CR from CRLF can remain. The normalized representation is stored separately. This lets search use comparable values while evidence review can still show what was first accepted.

Rejected raw lines are not stored in import history. The history keeps line numbers and safe reasons. Input file paths are not stored there. The source field is a declared namespace from the record, not a filesystem path and not proof of authenticity.

# 5 Event storage and search

## Event identity and duplicate examples

The identity is the pair source and event_id. Consider source lab and ID e1. The first valid record is saved. Reimporting e1 with identical normalized fields adds no event. Reordering JSON keys or changing whitespace alone also adds no event, because equality uses canonical content.

If e1 now claims a different username, outcome, time, or other meaningful field, the importer reports a conflict and keeps the original. If another source uses e1, that is a different identity and may be inserted. In a single batch, the first valid occurrence wins; an invalid record does not reserve its ID.

## Import counts

validated equals inserted plus duplicates plus conflicts. rejected is the number of invalid nonblank records. blank_lines is tracked separately. total_events is the database's event count after the import. import_id identifies the completed import operation.

A duplicates-only import succeeds and adds an import-history row. A mixed input can save valid new records and return exit code 1 because other lines were invalid or conflicting. A fatal database failure returns exit code 2 and does not commit that import's changes.

## Search semantics

Username, source IP, and outcome filters are exact matches after relevant input validation. Username filtering is not fuzzy search and does not match substrings. Canonical IP conversion allows equivalent IP spellings to match. Time filters normalize to UTC.

The start boundary is included and the end boundary is excluded. A search from 09:00 to 09:05 includes 09:00 exactly but not 09:05 exactly. This differs from the detection windows, which have their own rules. If both boundaries are provided, start must be earlier than end.

Every supplied filter must match. For example, username lab_user, IP 192.0.2.71, and outcome failure means failure records for that exact account and IP, not any one of those conditions. Pagination lets the application return a bounded page rather than all stored rows.

## Read only guarantees

Summary, search, event lookup, preview detection, and saved-history reads open existing databases read only. They do not create a missing file or upgrade a version 1 database. Tests compare file bytes before and after read operations. The explicit --save command is the path that upgrades and records detection history.

# 6 Detection rules in detail

## Shared assumptions

Rules use event time, not the time a file was imported. Input may arrive out of order; detection sorts it. Source is part of event identity but not part of the rule grouping key. Events from different sources can therefore contribute to the same account and IP group. That is useful only when the source namespaces refer to comparable accounts.

All current rules are version 1.0.0. Thresholds are lab choices, not universal values that prove an attack. Changing rule meaning later should be treated as a versioned behavior change and tested against saved evidence and reproducibility requirements.

| Rule | Grouping | Trigger | Time window |
| --- | --- | --- | --- |
| R1 | Exact username and source IP | At least 5 failed events | Inclusive 300 seconds |
| R2 | Source IP | Failures for at least 10 distinct usernames | Inclusive 600 seconds |
| R3 | Exact username and source IP | A success after at least 5 earlier failures | Start included and success time excluded for failures |

## R1 repeated account failures

R1 keeps only failure events, groups them by username and source IP, and walks each group in time order. At a timestamp it removes failures strictly older than 300 seconds. Exactly 300 seconds old is still inside the window. It then adds every matching failure at the current timestamp as a batch.

When an armed group reaches at least five failures, it creates one alert and becomes disarmed. It can rearm when the surviving window count drops below five before adding a later timestamp batch. A success does not count as a failure and does not reset this rule.

This is not one alert for every additional failed login. A sustained burst may generate only its first alert until the window permits rearming. Saved evidence is a snapshot at the trigger, not a continuously growing list of every later failure.

Example: failures at 09:00, 09:01, 09:02, 09:03, and 09:05 for one username and IP trigger R1 at 09:05. The first event is exactly 300 seconds old and is included. Four failures do not meet the threshold. A fifth at 09:05:00.000001 would exclude the 09:00 event if those are the only records.

Roman Urdu: Paanch minute ke andar aik hi account aur IP ki kam az kam paanch failed entries chahiye. Paanch alerts nahi, paanch failed login events.

## R2 failures across accounts

R2 groups failures by source IP. It maintains all failures in a 600-second window and a count for each username. Ten repeated failures for one username still represent one distinct account. At least ten different usernames are required.

When events expire, the count for each affected username decreases. A username leaves the distinct set only when none of its failure events remain in the window. Equal-time records are processed as a batch. The same armed and rearm pattern controls repeated alerts.

The alert contains distinct_account_count, a sorted username list, failure_count, and all contributing failure references. failure_count may exceed ten because several failures can belong to the same account. R2 can suggest activity consistent with password spraying, but the format does not record passwords, so the system cannot prove that one password was tried across accounts.

Example: ten accounts fail from one IP between 09:00 and 09:09. R2 can trigger. Nine accounts plus twenty repeat failures for one of those accounts still leave nine distinct accounts and do not trigger R2 by themselves.

## R3 success after failures

R3 groups both outcomes by exact username and IP. At each timestamp it removes failures older than 300 seconds, evaluates successes against strictly earlier failures, and only then adds failures at that same timestamp.

That ordering is essential. If a failure and success have exactly the same recorded time, the log does not establish which happened first. The rule therefore excludes equal-time failures from that success's preceding-failure count. The start boundary remains included.

Every qualifying success is evaluated independently. Successes do not clear the failure window. Multiple successes can therefore create multiple alerts referencing overlapping failures. Evidence includes preceding_failure roles and one triggering_success role. failure_count does not include the successful event.

Example: failures at 09:20, 09:21, 09:22, 09:23, and 09:24 followed by a success at 09:24:30 trigger R3. The account and IP must match. A success by a different account or from another IP does not satisfy this group.

## Why equal timestamps are batched

An arbitrary file order must not change a rule's conclusion when records share the same time. R1 and R2 add all same-time failures before evaluating a threshold. R3 evaluates successes before adding same-time failures. Source and event ID provide deterministic ordering, but do not establish true subsecond event order.

## Alert fields and evidence

Every alert carries alert_id, rule_id, rule_version, title, parameters, group, failure_count, first_event_at, triggered_at, reason, and evidence. R2 adds distinct-account information. Evidence references contain the internal database ID, source, source event ID, and normalized timestamp. R2 adds username; R3 adds the evidence role.

The internal ID is useful for opening an original event from the same database. It is not portable across installations. The stable alert hash excludes that internal ID but includes meaningful ordered evidence information. Sorting and canonical serialization keep repeated results reproducible.

## Limitations of rule based detection

Slow attempts below a threshold, attempts spread across many IPs, missing logs, incorrect source timestamps, or an attacker who succeeds immediately may not trigger these rules. Shared IPs and human mistakes can produce false positives. Rules only evaluate the records supplied to this project.

Zero alerts means these particular rules found no matching pattern in the supplied dataset. It does not prove that a computer or account is safe. Three alerts may overlap and must not automatically be reported as three separate incidents.

# 7 Permanent alerts and schema migration

## Preview versus save

Without --save the detector calculates alerts and returns them. With --save it also records one completed evaluation and stores new alert identities. An unchanged evaluation adds a new run but recognizes existing alerts. That distinction allows an analyst to answer both what suspicious patterns exist and when the dataset was checked.

The Day 8 sample demonstrates this clearly: first save gives three new alerts; second save gives zero new alerts and three existing alerts. The total saved alerts stays three while completed runs becomes two.

## Explicit schema upgrade

Schema means the database's table and column layout. Version 1 has events and imports. Version 2 adds detection_runs, saved_alerts, alert_evidence, and run_alerts. New imports still create version 1. The first explicit detection save upgrades an existing version 1 database.

The upgrade occurs inside the same transaction as detection and persistence. A failed migration, failed evaluation, or failed write rolls back the upgrade and new records together. A missing database is not created by save_detection; import or initialize it first. Unsupported schema versions are rejected.

## Immutable results and late data

The application does not edit a saved alert's evidence snapshot. When its ID already exists, the serialized result must match exactly. An unexpected identity/content mismatch fails the new run instead of silently changing history.

Late imported events can change which window first reaches a threshold, which evidence participates, and the resulting alert ID. The new alert can be saved alongside the old one. Old alerts remain historical observations from earlier runs, even if the newest run no longer matches them. run_alerts preserves membership for each run.

This is not an automatic incident resolution system. The application does not assign confirmed, benign, suspicious, or resolved conclusions. Later investigation features must preserve this separation between observed evidence and human judgment.

## Concurrent actions

Two save commands can start close together. BEGIN IMMEDIATE makes their write transactions serialize. One can create the three alert records; the next observes them and records three existing alerts. Both runs can be retained without duplicate alerts.

A concurrent import also serializes with saving. The saved run evaluates one coherent snapshot: either before or after that import, rather than half of its records. Tests check the event count and maximum event/import IDs to confirm this consistency.

# 8 Database reference

## Tables and relationships

```text
imports 1 ------ many events
detection_runs 1 ------ many saved_alerts by first_run_id
saved_alerts 1 ------ many alert_evidence ------ 1 events
detection_runs many ------ run_alerts ------ many saved_alerts
```

An alert has one first saved run but can appear in many later runs. An event can support several alerts. The link tables represent these relationships without copying the entire original event into every database row that needs it.

## Events table

id is the internal integer primary key. source and event_id together are unique. timestamp_utc is the normalized time. source_ip, username, event_type, and outcome support searches and detection. CHECK constraints restrict the supported event type and outcomes.

canonical_json is the normalized serialization used for duplicate comparison. original_record is the first accepted source text. first_import_id links to imports and first_line_number identifies the source line. The events_time index uses timestamp_utc and id to support ordered event retrieval.

## Imports table

id identifies an import. imported_at is its UTC operation time. validated, inserted, duplicates, conflicts, rejected, and blank_lines record outcomes. errors_json stores safe line-specific validation and conflict information. Even an empty or duplicates-only successful import can produce a history row.

## Detection runs table

id identifies a saved evaluation. completed_at records completion time. configurations_json stores selected rule IDs, versions, thresholds, and windows, including when no alert matches. events_scanned records the evaluated dataset size. max_event_id and max_import_id record the highest IDs present at that snapshot.

matched_count is the number of results from that run. new_count counts newly saved identities. existing_count counts identities already saved. matched_count equals new_count plus existing_count for a successful run. These maximum IDs support provenance but are not a complete cryptographic snapshot or protection against outside database edits.

## Saved alerts table

alert_id is its text primary key. rule_id and rule_version identify the detection behavior. triggered_at supports ordering. first_run_id links to the first saving run. alert_json preserves the complete result, including its reason and evidence references. An index orders saved alerts by time and ID.

## Evidence and membership tables

alert_evidence has alert_id, position, event_id, and role. The combination of alert ID and position is its primary key. An additional unique constraint prevents the same event appearing twice for one alert. Foreign keys link to the saved alert and original event.

run_alerts has run_id and alert_id as a combined primary key, with foreign keys to their parent tables. This records the actual results of each run even when no new alert rows are necessary. The current history CLI shows run summaries; there is no separate per-run membership endpoint yet.

## Data integrity boundaries

The application enables foreign keys for writing, uses parameterized values, checks supported versions and required columns, and uses transactions. These protect normal application operations. Someone with direct filesystem or SQLite access can still change the file outside the application. There is no encryption at rest or tamper-evident audit chain.

# 9 Browser and HTTP behavior

## Frontend and backend

index.html supplies the page structure. style.css controls layout, colors, spacing, and responsive behavior. app.js calls the local HTTP API, updates counts, renders event rows, handles upload and filters, and opens evidence. server.py handles those requests and calls the same storage functions used by the CLI.

The server creates a random per-process request token and substitutes it into the page. JavaScript sends the token with uploads. Restarting the server changes the token, so an old page may need refreshing before it can upload again.

| Route | Method | Purpose |
| --- | --- | --- |
| / | GET | Serve the event workspace |
| /static/app.js | GET | Serve the browser logic |
| /static/style.css | GET | Serve the stylesheet |
| /api/summary | GET | Read event and import totals |
| /api/events | GET | Search and page events |
| /api/events/ID | GET | Read one event with original evidence |
| /api/import | POST | Validate and save uploaded JSON Lines |

There is currently no /api/alerts route, no login page, no saved-alert dashboard, and no automatic detection on upload. The visible badge still says Day 7 because Day 8 added command-line persistence rather than redesigning that page.

## Upload protection

The server checks exact Host and Origin expectations and rejects cross-site fetches. Uploads require the matching origin and token, one numeric Content-Length, no Transfer-Encoding, and Content-Type application/x-ndjson. Oversized requests fail before import. Incomplete content or timeouts return errors rather than saving a partial upload.

Uploaded content is written to a temporary file with a server-chosen name. The user-supplied filename does not determine a filesystem path, and the browser cannot choose an arbitrary database path. The importer processes the temporary file, after which the temporary directory is cleaned up.

## Safe rendering and browser state

The JavaScript uses textContent for record values and JSON evidence rather than treating them as HTML. A username containing HTML-like text is displayed as data. Event requests use a counter so an old response does not replace a newer evidence selection. Controls are disabled during relevant requests to reduce overlapping actions.

The browser starts with 25 rows per page. The storage API's default is 50 if no limit is supplied. Both are correct in their respective layers. Clear filters resets the browser state; it does not delete database records.

## Response protections and limits

Responses set no-store caching, nosniff, no-referrer, and a restrictive Content Security Policy. Only the two named static assets are served; there is no general directory listing or arbitrary file route. Request logging is suppressed to avoid logging search values, uploads, and tokens.

The server is a standard-library threaded development server with a ten-second connection timeout. It binds only to 127.0.0.1. The allowed CLI port range is 1024 through 65535, with 8765 as default. It is not a production deployment server and should not be described as authenticated or hardened for public hosting.

# 10 Progress through the eight learning days

| Checkpoint | Completed work | Recorded test total |
| --- | --- | --- |
| Initial scaffold | Repository and directory structure | No application suite |
| Day 1 | Scope, deadline, criteria, event design, synthetic sample | Design checks |
| Day 2 | Python environment, validation, normalization, reader CLI | 27 |
| Day 3 | SQLite events/imports, originals, duplicates, conflicts, rollback | 46 |
| Day 4 | Exact search, time filters, pagination, evidence lookup | 57 |
| Day 5 | Browser upload/search/evidence and HTTP protections | 67 |
| Day 6 | R1 preview, evidence, deterministic IDs and boundaries | 83 |
| Day 7 | R2, R3, combined engine and evidence budget | 103 |
| Day 8 | Alert persistence, runs, migration, deduplication and history CLI | 120 |

Day 1 and Day 5 learning exercises were recorded as complete. Day 6 threshold and boundary answers were correct; the evidence-reference question was explained but not independently answered. Other pending answers are learning follow-ups, not failed software tests. Implementation progress and your ability to explain it are separate things to develop together.

The original dated roadmap remains a planning document. Some features were completed earlier than their provisional dates. The remaining deadline is still 17 October. No automatic daily work or reminder was scheduled; you resume work by returning to the project conversation.

# 11 Running the software yourself

## Open PowerShell and select the folder

Open the Start menu, type PowerShell, and open Windows PowerShell. Run the following command. Do not type the prompt text such as PS C:\WINDOWS\system32> as part of a command.

```powershell
Set-Location 'C:\Users\Dell\Desktop\Projects\SentinelLab'
```

The local Python environment uses .venv/bin/python.exe because it was created with the existing MSYS2 Python 3.12.7. A normal Windows CPython environment often uses .venv/Scripts/python.exe instead. These are environment layouts, not two required copies of the application.

```powershell
$projectPython = '.venv/bin/python.exe'
& $projectPython --version
```

The ampersand tells PowerShell to run the program identified by the variable. The variable is temporary for this PowerShell session. No activation script or execution-policy change is required for these commands. On a fresh machine, follow docs/SETUP.md rather than copying this laptop's virtual environment.

## Check a sample without saving

```powershell
& $projectPython scripts/check_events.py data/samples/day01_login_events.jsonl --json
```

Expected: three accepted records, zero rejected, zero blank lines. This verifies format only. The mixed Day 2 sample has two accepted records, one rejection, and one blank line; its invalid outcome is intentional and produces exit code 1.

## Inspect existing Day 8 data without changing it

```powershell
& $projectPython scripts/database.py summary --database data/runtime/day08_demo.db --json
& $projectPython scripts/alerts.py summary --database data/runtime/day08_demo.db --json
& $projectPython scripts/alerts.py list --database data/runtime/day08_demo.db --json
& $projectPython scripts/alerts.py runs --database data/runtime/day08_demo.db --json
```

At the prepared Day 8 checkpoint, the database contains sixteen events, one import, three alerts, and two runs. Those numbers can change if you later import or save again. The summary command is the way to check present values rather than assuming they always stay fixed.

## Run a fresh demonstration

Choose a new runtime database name if you want fresh counts. The following example uses handbook_demo.db. If that file already exists, the commands reuse it and duplicate/run counts reflect its history.

```powershell
& $projectPython scripts/database.py import data/samples/day07_all_rules.jsonl --database data/runtime/handbook_demo.db --json
& $projectPython scripts/detect.py --database data/runtime/handbook_demo.db --json
& $projectPython scripts/detect.py --database data/runtime/handbook_demo.db --save --json
& $projectPython scripts/detect.py --database data/runtime/handbook_demo.db --save --json
& $projectPython scripts/alerts.py summary --database data/runtime/handbook_demo.db --json
```

On a fresh file: import inserts sixteen events; preview returns three alerts without saving; first save adds three alerts; second save adds zero new alerts; summary shows three alerts and two runs. The first save upgrades the schema. No attack is performed by these commands.

## Select a single rule

```powershell
& $projectPython scripts/detect.py --database data/runtime/day08_demo.db --rule R1 --json
& $projectPython scripts/detect.py --database data/runtime/day08_demo.db --rule R2 --json
& $projectPython scripts/detect.py --database data/runtime/day08_demo.db --rule R3 --json
```

Each is read only because --save is absent. Add --save only when you intend to add a completed run and any new alert identities. The default rule selection is all, which differs from the original Day 6 R1-only behavior.

## Search and open evidence

```powershell
& $projectPython scripts/database.py search --database data/runtime/day08_demo.db --username lab_user --outcome failure --json
& $projectPython scripts/database.py get 11 --database data/runtime/day08_demo.db --json
```

The prepared sample uses internal IDs 11 through 15 for the failure burst, but do not assume that every database has those IDs. Get the ID from a search or alert evidence result first. For saved-alert detail, replace YOUR_ALERT_ID with the full R1, R2, or R3 hash ID from alerts.py list.

```powershell
& $projectPython scripts/alerts.py get --database data/runtime/day08_demo.db --alert-id YOUR_ALERT_ID --json
```

## Open the browser

```powershell
& $projectPython scripts/serve.py --database data/runtime/day08_demo.db
```

Open http://127.0.0.1:8765 and keep that PowerShell process running. The browser shows events in the selected database, not the saved-alert history yet. Stop it with Ctrl+C. If the port is already in use, check the existing server or use --port 8767 and open that port. Do not assume that an already-running Day 5 server is using Day 8 data.

## Test and interpret exit codes

```powershell
& $projectPython scripts/run_tests.py
$LASTEXITCODE
```

The Day 8 suite has 120 tests. The test runner returns 0 on success and 1 on failure. Reader/import commands use 0 for success, 1 for completed operations with rejected/conflicting records, and 2 for fatal or usage errors. An event or saved-alert get returns 1 for a valid but missing identity. Detection returns 0 when evaluation succeeds, including zero alerts, and 2 on failure.

# 12 A worked investigation style walkthrough

## The sample has two separate patterns

The Day 7 sample contains sixteen synthetic events. Ten failures belong to ten accounts from one source IP and support R2. A separate group has five failures for lab_user from another IP, followed by a success. That group supports R1 and R3.

The combined engine returns three alerts: one per rule. This is a useful demonstration of why alert count is not incident count. R1 and R3 partly refer to the same burst. An analyst would compare their evidence before deciding whether they describe one investigation.

## Follow one result to its source

First run the preview and choose the R3 result. Read its reason, group, time interval, and failure_count. Its six evidence entries include five preceding failures and the triggering success. Then use an evidence internal_id with database.py get against that same database.

The evidence view shows the normalized fields, original_record, first_import_id, and first_line_number. Compare the source event ID and timestamp to the alert reference. That connection explains how the warning relates to the stored source record.

## Separate observation from interpretation

Observation: the stored records show five preceding failures and a success for one username and source IP within the configured window. Interpretation: the pattern deserves review because it could be suspicious. Confirmation would require additional authorized evidence such as the user's explanation, device context, or account activity.

The current file format does not contain geolocation, device fingerprint, password values, or a verified user's identity. Do not invent those details in a report. Later investigation features should make it easy to record what is known and what remains uncertain.

# 13 Tests and verification

## What the tests establish

Unit tests isolate input validation behavior. Integration tests connect real parsing, SQLite, CLI subprocesses, and local HTTP requests. They use temporary databases and synthetic records so repeated tests do not need to change your demonstration data.

Boundary tests check exact time endpoints, just-outside events, tied timestamps, limit values, and invalid inputs. Failure tests deliberately cause write errors to verify rollback. Concurrency tests run operations close together to check that duplicated data and mixed snapshots do not appear.

The suite confirms documented behavior for tested examples. It is not a measured real-world detection accuracy score, a penetration-test certification, or proof that no bug exists. A held-out labeled evaluation and clean-environment release demo remain future work.

## Why important tests exist

A test for four failures versus five protects the threshold definition. A test for exactly five minutes protects the inclusive boundary. A test that imports the same event twice protects evidence identity. A test that forces a failure after some alert writes protects atomicity, not merely a happy-path count.

Browser tests verify uploads, filters, original evidence, hostile-looking text as data, bounded requests, origin/token protections, and compatibility after schema migration. The user interface still needs another browser review when alert pages are added.

The detailed test catalogue later in this handbook lists each test method by file so you can locate its code. Descriptive test names are executable statements about expected behavior, not production functions called by the user interface.

# 14 Local folders Git and GitHub

## Source code versus runtime data

The Desktop SentinelLab directory is the active project. src contains implementation; scripts contains launchers; tests contains verification; docs contains explanations; data/samples contains shareable invented logs; reports/examples contains synthetic preview outputs.

data/runtime contains local SQLite files and demonstration material. These are ignored by Git. .venv contains the local interpreter environment and is also ignored. __pycache__ folders contain automatically generated Python bytecode and are not authored application features.

.git is Git's metadata directory: commits, refs, index, and related internal state. It is not a normal source folder to move, edit, or clean by hand. .gitignore tells Git which untracked files to exclude; it is not encryption and does not erase already tracked files. .gitattributes defines text and line-ending handling.

## The current Git history situation

The Day 8 source files were verified against GitHub commit 80e88e3344a5c6b56c573a80f796a3fb796c3ab1. Local working files are updated, but local HEAD and index remain at the earlier Day 2 checkpoint because metadata writes were restricted. Git status can therefore show many differences that were already published through the connected GitHub integration.

Do not use reset --hard or clean commands to make the status look tidy. That can destroy later local work. Reconciliation requires comparing current files, local history, and remote history, then resolving the metadata restriction through the normal permitted workflow. Publishing a GitHub commit does not itself rewrite the laptop's .git directory.

## What belongs in the portfolio repository

Source code, synthetic samples, tests, setup instructions, design explanations, and sanitized demonstration reports belong in the repository. Credentials, real personal logs, generated databases, private investigation reports, and environment binaries do not. The final portfolio should show an honest reproducible prototype with measured results and limitations.

# 15 Troubleshooting

| Symptom | Likely explanation | Next action |
| --- | --- | --- |
| Python command not found | Wrong interpreter path or missing environment | Check .venv/bin versus .venv/Scripts and SETUP.md |
| File cannot be read | Wrong current folder or path | Use Set-Location and confirm the file exists |
| Mixed sample returns code 1 | Intentional invalid record | Read the line reason and expected counts |
| Import reports duplicates | Same normalized identity already exists | This is expected; check inserted and total_events |
| Import reports conflicts | Same identity now has different values | Preserve the original and investigate the input |
| Browser shows different counts | Server points to another database | Compare its --database path with the CLI command |
| Browser cannot connect | Server stopped or wrong port | Start the server or open its displayed address |
| Port already in use | Another server owns that port | Reuse the intended server or choose another port |
| Upload requests a refresh | Page token belongs to an older process | Refresh the page after server restart |
| Unsupported schema | Wrong file or unsupported version | Keep the file and report the error; do not delete it |
| Database locked | Another writer is still running | Let it finish and retry; timeout is five seconds |
| Detection refuses dataset | Event or evidence cap exceeded | Review dataset size; no partial detection is produced |
| No alerts | Current rules do not match this dataset | Check data and rule selection; do not infer safety |
| Repeated save adds runs | History records each successful check | Expected when --save is used |
| Saved alert not found | Incorrect full ID or different database | Copy the complete ID from the same database list |
| Git shows old changes | Local metadata is behind published content | Compare history carefully before reconciliation |

When reporting a problem, share the exact command, safe error text, database filename, and whether it happened in the browser or terminal. Do not send real passwords, tokens, or private logs. A screenshot can show presentation problems, but text output is usually better for exact error diagnosis.

# 16 Work after Day 8

## Day 9 browser alert workflow

The next planned checkpoint is to show saved alerts, run history, and linked original evidence in the browser. A deliberate detection action may use the existing atomic save API. It must keep request protections, show new versus existing counts, and handle failures clearly. Uploading should not silently run detection.

Verification should cover paging, empty history, evidence navigation, repeated saving, untrusted text rendering, and consistency with terminal results. Existing event upload/search must keep working. The full regression suite should run after implementation, followed by a visual browser check.

## Investigations and analyst decisions

Next, add investigation records with notes, workflow status, disposition, and action history. Planned workflow status values include open, investigating, and closed. Planned dispositions include undetermined, benign, suspicious, and confirmed incident. A confirmed incident needs an analyst rationale rather than an automatic detector label.

Changing a note or conclusion must not modify original events or saved alert evidence. Tests should verify persistence across restart, correct relationships, and a faithful change history. These are design goals, not tables that already exist.

## Authentication and access protection

Introduce an analyst sign-in flow, appropriate password hashing, session handling, logout invalidation, and protection of reads and writes. The earlier stack proposal mentions FastAPI, but the current implementation uses the Python standard library. Any dependency and framework transition requires a deliberate compatibility and security review.

Existing loopback, token, and safe-rendering measures should be retained or replaced with explicit tested equivalents. Authentication is a feature with its own tests, not a label to add to the current token mechanism.

## Reports evaluation and release

Planned Markdown and JSON report exports should include rule settings, evidence references, UTC times, notes, disposition, and limitations. Report content must match stored data. A timeline should distinguish source event time from import time and analyst action time.

Evaluation needs labeled scenarios and a stated unit of measurement. For example, measure whether a scenario should produce a rule alert, rather than mixing event counts and incident counts. Report false positives and misses honestly. Synthetic performance does not establish accuracy on real organizational traffic.

Before release, reproduce setup on a clean environment, run required acceptance checks, record a demonstration, prepare a case study, and write CV bullets limited to implemented and understood work. Reserve time for fixes before 17 October. Optional collectors, extra formats, multiple roles, and public hosting should not displace required completion work.

## Your role in the remaining work

The assistant creates and maintains files, implementation, tests, and documentation. Your role is to understand the concepts, try the visible workflow, answer short learning questions, and explain design choices in your own words. You should be able to trace an alert to its events and explain why it is not automatic proof of compromise.

For each checkpoint, read the guide, try one normal example, try one boundary or duplicate example, and explain the result. Ask for simpler English or Roman Urdu whenever needed. You do not need to memorize every line of code to begin, but portfolio credibility grows as you can demonstrate what the code does.

# 17 Portfolio and interview preparation

## A truthful current description

SentinelLab is an AI-assisted local Python security monitoring prototype that validates and stores authentication events, applies three explainable detection rules, preserves original evidence, and saves deduplicated alerts with run history. Its current interface includes browser event search and command-line detection. The Day 8 suite contains 120 automated tests.

Use this as a starting description, adjusting it to what you personally understand and can demonstrate. Do not claim independent authorship of assistant-generated work or list unfinished authentication and incident-management features as completed.

## Questions you should be able to answer

Why preserve original records as well as normalized values? Originals support review; normalized values support reliable comparison. Why use source plus event ID? Different sources can reuse the same ID. Why not count every failure as an attack? Context and thresholds matter, and matching a rule is only an observation.

Why are repeated saves allowed to add runs? They record repeated evaluations while alert identity prevents duplicate findings. Why exclude same-time failures from R3? The records cannot prove those failures happened before the success. Why do transactions matter? A partial run would create misleading or incomplete history.

Why is the server local only? It is a learning prototype without completed analyst authentication or production deployment controls. Why are there no accuracy percentages yet? The project has behavior tests, but a held-out labeled detection evaluation has not been completed.

## A short demonstration sequence

Show a sample event and explain its fields. Import the sample and show the counts. Repeat the import to show duplicates. Search for an account and open the original. Preview all three rules and explain one result. Save twice and show three alerts with two runs in a fresh demonstration database. Finish by naming the limitations and next planned features.

# 18 Glossary

| Term | Plain English meaning |
| --- | --- |
| API | A defined way for one program part to request work from another |
| Backend | Server code that validates requests and accesses data |
| Frontend | Browser page and code the user interacts with |
| CLI | A program operated through terminal commands |
| JSON | A structured text representation of values and objects |
| JSON Lines | One complete JSON value per line; this project requires objects |
| UTC | A common time reference used for comparing events |
| SQLite | A relational database stored in a local file |
| Schema | The tables columns and constraints of a database |
| Migration | A controlled change from one schema version to another |
| Primary key | The unique identifier of a table row |
| Foreign key | A relationship from one table to a parent record |
| Canonical | A consistent representation used for comparison |
| Deduplication | Avoiding another copy of the same logical item |
| Transaction | Changes that commit together or roll back together |
| Snapshot | A consistent view of data for one operation |
| Threshold | The minimum count required by a rule |
| Window | The time interval considered at an evaluation moment |
| Evidence | The records supporting a finding |
| Provenance | Information about where a record came from |
| False positive | A suspicious result that does not represent the intended harmful case |
| False negative | A relevant harmful case that is missed |
| Regression test | A check that existing behavior still works after changes |
| Commit | A recorded source history checkpoint |
| Repository | The project files and their version history |
| Virtual environment | An isolated Python environment for a project |
| Loopback | A network address that refers to the same computer |

# 19 Complete file reference

The following catalogue describes every file published at the Day 8 checkpoint. Paths are relative to the SentinelLab project root. Package markers and placeholders are included because they explain why apparently empty files exist. Generated environment files are grouped separately rather than pretending they are authored project code.

## File 1 gitattributes

Path: `.gitattributes`

Defines Git text normalization and line-ending preferences. Markdown, Python, JSON, YAML use LF; PowerShell uses CRLF. It affects how Git stores and checks out text, not how detection rules work. A line-ending warning does not itself mean that application data was duplicated.

## File 2 gitignore

Path: `.gitignore`

Excludes virtual environments, Python caches, credentials, local configuration, databases, raw/private/runtime data, generated/private reports, and editor noise. Its purpose is repository hygiene. It does not secure a file against local readers, and a tracked secret would need separate remediation rather than merely adding a pattern.

## File 3 AGENTS md

Path: `AGENTS.md`

Records project collaboration rules: simple English and Roman Urdu, the active Desktop location, assistant-maintained files, meaningful tests and publication checkpoints, evidence preservation, and truthful claims. It is guidance for work on the project, not a Python module or configuration loaded by the running application.

## File 4 README md

Path: `README.md`

The entry point for a new repository reader. It states the current Day 8 status, stack, folder layout, setup links, browser launch, detection examples, and saved-alert commands. Read this first when returning to the project. Some deeper explanations live in linked contracts and daily guides.

## File 5 gitkeep

Path: `data/samples/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 6 day01 login events jsonl

Path: `data/samples/day01_login_events.jsonl`

Three invented login records: two failures and one success for the same account/source. All are valid format examples. They stay below the current detection thresholds, making the file useful for demonstrating import, search, evidence, duplicates, and the difference between a failure event and an alert.

## File 7 day02 mixed events jsonl

Path: `data/samples/day02_mixed_events.jsonl`

An intentionally mixed validation sample: two accepted records, one invalid outcome, and one blank line. It demonstrates line-specific rejection while later valid records continue. The checker returns exit 1 intentionally. Do not treat this fixture as a broken project file to silently repair.

## File 8 day06 repeated failures jsonl

Path: `data/samples/day06_repeated_failures.jsonl`

Six synthetic events designed to demonstrate R1: five relevant failures and a success. Input is intentionally out of event-time order to show that detection sorts correctly. The historical R1-only preview is reproduced with --rule R1; the current default all-rules evaluation may include another qualifying rule.

## File 9 day07 all rules jsonl

Path: `data/samples/day07_all_rules.jsonl`

Sixteen synthetic events covering all rules: ten distinct-account failures for R2 and a separate five-failure burst plus success for R1/R3. It is reused for the Day 8 save/deduplication demo. Importing this file does not make actual login attempts or attack any host.

## File 10 gitkeep

Path: `docs/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 11 ACCEPTANCE CRITERIA md

Path: `docs/ACCEPTANCE_CRITERIA.md`

The fifteen release targets and dated component evidence. Covers validation, normalization, persistence, rules, reproducibility, investigation history, exports, access protection, hostile input, edge cases, evaluation, and final demonstration. Passing a component test does not mean the whole release is accepted.

## File 12 ALERT STORAGE md

Path: `docs/ALERT_STORAGE.md`

The version 2 persistence contract: explicit saving, tables, immutable snapshots, run membership, late data, transaction behavior, concurrency, CLI history, and limits. Use it when modifying saved-alert behavior or designing browser alert views.

## File 13 ARCHITECTURE md

Path: `docs/ARCHITECTURE.md`

The original proposed system outline from input through investigations and reporting. Some of its pipeline is now implemented, but investigation, authorization, and configuration statements include future design. Use the current code and Day 8 contracts for precise implemented behavior.

## File 14 DATABASE md

Path: `docs/DATABASE.md`

The event/import schema, canonical duplicate policy, transactions, count meanings, limits, and version 2 compatibility pointer. Read with ALERT_STORAGE.md for saved-alert tables and explicit migration.

## File 15 DAY 01 GUIDE md

Path: `docs/DAY_01_GUIDE.md`

Beginner introduction to the problem, event versus alert reasoning, planned rules, sample records, and the learning project. Historical day-one guide rather than current feature inventory.

## File 16 DAY 02 GUIDE md

Path: `docs/DAY_02_GUIDE.md`

Teaches Python environment and JSON Lines validation, accepted/rejected counts, safe input handling, and running the format checker. Useful before learning database import.

## File 17 DAY 03 GUIDE md

Path: `docs/DAY_03_GUIDE.md`

Explains durable SQLite events, originals, imports, duplicates, conflicts, and transaction behavior through practical commands. Introduces why first accepted evidence is retained.

## File 18 DAY 04 GUIDE md

Path: `docs/DAY_04_GUIDE.md`

Explains exact search, combined filters, UTC time ranges, pagination, and original-evidence lookup. Use it to practice finding the records behind later alerts.

## File 19 DAY 05 GUIDE md

Path: `docs/DAY_05_GUIDE.md`

Introduces the local browser workspace, starting/stopping the server, uploads, event filtering, original evidence, duplicate counts, and the distinction between suspicion and confirmed compromise.

## File 20 DAY 06 GUIDE md

Path: `docs/DAY_06_GUIDE.md`

Teaches R1 repeated failures, thresholds, inclusive windows, evidence, preview commands, and interpretation. Use --rule R1 for historical examples because all rules is now the CLI default.

## File 21 DAY 07 GUIDE md

Path: `docs/DAY_07_GUIDE.md`

Teaches R2 distinct-account activity, R3 success after failures, combined previews, rule selection, event-time ordering, evidence roles, and limitations.

## File 22 DAY 08 GUIDE md

Path: `docs/DAY_08_GUIDE.md`

Teaches permanent alert storage, run versus alert counts, explicit --save, migration, duplicate prevention, read-only history, rollback, late data, and the one-question exercise. This is the shortest practical companion to the full handbook.

## File 23 DETECTION RULES md

Path: `docs/DETECTION_RULES.md`

Precise rule semantics, grouping, windows, ties, rearming, stable identity, evidence, combined execution, and limits. Day 8 updates distinguish default preview from --save. This is the primary written contract for interpreting rule output.

## File 24 EVENT FORMAT md

Path: `docs/EVENT_FORMAT.md`

The seven-field JSON Lines contract, identity policy, timezone/IP normalization, original preservation, sample explanation, and reader limits. Some historical wording predates R2/R3; all three rules now exist, while the input contract remains the same.

## File 25 NEXT SESSION md

Path: `docs/NEXT_SESSION.md`

The current handoff for Day 9, including browser alert plans, verification requirements, pending learning questions, runtime state, and Git continuity. It lets the next session continue without guessing which features are finished.

## File 26 PROGRESS md

Path: `docs/PROGRESS.md`

Historical record of scaffold and daily implementation, tests, sample results, teaching follow-ups, and Git publication constraints. Read dated entries for context; older next-step text can be superseded by newer entries and NEXT_SESSION.md.

## File 27 PROJECT BRIEF md

Path: `docs/PROJECT_BRIEF.md`

The original problem, learner audience, scope, deadline, desired user journey, required features, boundaries, definition of done, and honest portfolio claims. Its sign-in, investigation, and export journey is the intended destination, not a claim that all steps already work.

## File 28 ROADMAP md

Path: `docs/ROADMAP.md`

The provisional calendar through 17 October, scope priorities, daily working pattern, and release gates. Dates are plans rather than evidence of completion. Required work takes priority over collectors, extra formats, roles, containers, and public hosting.

## File 29 SEARCH md

Path: `docs/SEARCH.md`

The exact-filter and pagination contract, start-included/end-excluded semantics, evidence lookup, response fields, and exit codes. Its older version-1 wording is superseded by the code supporting versions 1 and 2; search still never migrates.

## File 30 SETUP md

Path: `docs/SETUP.md`

Environment requirements, interpreter selection, portable .venv instructions, command examples, exit codes, and troubleshooting. Some checkpoint descriptions still say Day 7 or preview-only; the current Day 8 guide adds persistence commands and the 120-test total.

## File 31 WEB md

Path: `docs/WEB.md`

The local browser protocol and boundaries: routes, upload flow, request protections, response behavior, frontend handling, and development limitations. It documents event browsing rather than an implemented saved-alert dashboard.

## File 32 gitkeep

Path: `reports/examples/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 33 day06 r1 preview json

Path: `reports/examples/day06_r1_preview.json`

A saved synthetic R1-only preview result from the Day 6 demonstration. It illustrates rule version, parameters, group, trigger, reason, and evidence. It is a static example file, not the live SQLite alert store. Its internal evidence IDs refer to the corresponding sample database.

## File 34 day07 all rules preview json

Path: `reports/examples/day07_all_rules_preview.json`

A static synthetic combined preview showing one alert per rule for the Day 7 sample. Useful for studying the JSON contract and comparing reproducible results. It is not a general incident report exporter, and its internal IDs should not be used against unrelated databases.

## File 35 gitkeep

Path: `scripts/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 36 alerts py

Path: `scripts/alerts.py`

Small launcher for sentinellab.alerts_cli.main. It opens saved alert totals, lists, run history, and details. It is a reader of completed results and does not execute detection or add a run.

## File 37 check events py

Path: `scripts/check_events.py`

Small launcher for sentinellab.cli.main. It computes the repository src path relative to the script rather than requiring the current directory to be src. Use it for format validation before saving. Most behavior is in the CLI and reader modules, not in this wrapper.

## File 38 database py

Path: `scripts/database.py`

Small launcher for sentinellab.storage_cli.main. It exposes import, summary, search, and get without installing SentinelLab as a package. Relative data/database paths still resolve from the shell current directory; locating the package does not automatically change where your files are resolved.

## File 39 detect py

Path: `scripts/detect.py`

Small launcher for sentinellab.detection_cli.main. It makes preview and --save detection available from PowerShell. Default rule selection is all. The wrapper does not itself implement thresholds, database migration, or alert identity.

## File 40 run tests py

Path: `scripts/run_tests.py`

Adds src to the Python import path, discovers tests under tests with unittest, runs them at verbosity 2, and returns exit 0 if all pass or 1 if any fail. It needs no third-party test framework. It is a development verification command rather than a user-facing monitoring feature.

## File 41 serve py

Path: `scripts/serve.py`

Small launcher for sentinellab.web.server.main. It runs the loopback browser workspace using the database and optional port supplied on the command line. The terminal process must keep running for the browser to connect.

## File 42 init   py

Path: `src/sentinellab/__init__.py`

A Python package marker for this directory. It lets modules or tests be organized and imported using their package path. In this project it is empty or contains only a short package description; it does not start a server, create a database, or run a rule. The real behavior is in the neighboring modules described separately.

## File 43 alerts cli py

Path: `src/sentinellab/alerts_cli.py`

Implements read-only saved-history commands summary, list, runs, and get. main validates command-line types, passes pagination to the history layer, and requires a complete alert ID for detail. A missing alert returns exit 1; a malformed ID or database failure returns exit 2. Output is formatted JSON even without --json on successful reads.

Code navigation: `main`.

## File 44 cli py

Path: `src/sentinellab/cli.py`

Implements the format-check command. main parses the input filename and --json option, calls read_events, prints a human or JSON summary, and selects the exit status. It distinguishes file-level failure from rejected individual records. This command never imports into SQLite and does not run the detector.

Code navigation: `main`.

## File 45 gitkeep

Path: `src/sentinellab/detection/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 46 init   py

Path: `src/sentinellab/detection/__init__.py`

A Python package marker for this directory. It lets modules or tests be organized and imported using their package path. In this project it is empty or contains only a short package description; it does not start a server, create a database, or run a rule. The real behavior is in the neighboring modules described separately.

## File 47 common py

Path: `src/sentinellab/detection/common.py`

Shared primitives for bounded and deterministic detection. utc_time requires canonical UTC strings. load_snapshot opens a read-only connection and delegates to read_snapshot; read_snapshot can also reuse the saving transaction connection. EvidenceBudget.consume limits the combined output references. reference creates a portable source reference plus local internal ID. alert_identity hashes the rule/version/parameters/group and ordered evidence while excluding internal_id. Input and evidence caps are defined here.

Code navigation: `utc_time`; `load_snapshot`; `read_snapshot`; `EvidenceBudget (__init__, consume)`; `reference`; `alert_identity`.

## File 48 engine py

Path: `src/sentinellab/detection/engine.py`

Coordinates all selected rules rather than implementing a particular pattern. validate_rule accepts R1, R2, R3, or all. detect loads one snapshot and delegates to evaluate_snapshot. evaluate_snapshot calls the selected evaluators with a shared evidence budget, combines and sorts their results, and returns a preview-shaped report. save_detection reuses this evaluator inside its transaction. A single snapshot prevents different rules from silently observing different database states in one run.

Code navigation: `detect`; `validate_rule`; `evaluate_snapshot`.

## File 49 r1 py

Path: `src/sentinellab/detection/r1.py`

Implements repeated failures for an exact username/IP pair. Constants define R1 version 1.0.0, five failures, and 300 seconds. evaluate_r1 groups and batches failures, expires the old window, applies armed/rearm behavior, and emits deterministic results. _alert builds the reason, parameters, evidence, and stable hash. detect_r1 preserves the earlier direct R1-only preview API; the normal Day 8 CLI uses the combined engine, which also enforces the shared output budget.

Code navigation: `_alert`; `detect_r1`; `evaluate_r1`.

## File 50 r2 py

Path: `src/sentinellab/detection/r2.py`

Implements failures across at least ten distinct accounts from one source IP in 600 seconds. evaluate_r2 uses a deque for failures and Counter for per-account frequencies. Expiration updates both, so repeated failures do not inflate the distinct account count. The evaluator batches equal times, rearms only after the surviving distinct count drops below threshold, consumes the evidence budget, and returns explanations with usernames and all contributing failure references.

Code navigation: `evaluate_r2`.

## File 51 r3 py

Path: `src/sentinellab/detection/r3.py`

Implements success after at least five earlier failures for the same username/IP in 300 seconds. evaluate_r3 keeps failures in a deque, processes same-time successes before adding same-time failures, and evaluates every success independently. It consumes the evidence budget before building each result. Evidence labels earlier failures and the triggering success explicitly. A successful login does not clear the window or prove compromise.

Code navigation: `evaluate_r3`.

## File 52 detection cli py

Path: `src/sentinellab/detection_cli.py`

Implements the detector options --database, --rule, --json, and --save. main calls detect for preview or save_detection for explicit persistence. Preview text includes each computed alert; save text summarizes new, existing, and total alerts. This is the main place where the user chooses reading versus writing.

Code navigation: `main`.

## File 53 gitkeep

Path: `src/sentinellab/ingestion/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 54 init   py

Path: `src/sentinellab/ingestion/__init__.py`

A Python package marker for this directory. It lets modules or tests be organized and imported using their package path. In this project it is empty or contains only a short package description; it does not start a server, create a database, or run a rule. The real behavior is in the neighboring modules described separately.

## File 55 reader py

Path: `src/sentinellab/ingestion/reader.py`

The input boundary for both CLI imports and browser uploads. It defines allowed fields and resource limits, normalizes time/IP, and preserves accepted original text. Event stores normalized fields; AcceptedRecord adds line number and original text; RejectedRecord stores a safe reason; ImportResult groups outcomes and produces a summary. _unique_object rejects repeated JSON keys; _reject_constant rejects nonstandard numbers; validate_event checks one decoded object; read_events processes the bounded file. ValidationError is line-level and InputFileError is fatal-file-level. This layer does not perform database deduplication.

Code navigation: `ValidationError`; `InputFileError`; `Event`; `AcceptedRecord`; `RejectedRecord`; `ImportResult (summary)`; `_unique_object`; `_reject_constant`; `validate_event`; `read_events`.

## File 56 gitkeep

Path: `src/sentinellab/storage/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 57 init   py

Path: `src/sentinellab/storage/__init__.py`

A Python package marker for this directory. It lets modules or tests be organized and imported using their package path. In this project it is empty or contains only a short package description; it does not start a server, create a database, or run a rule. The real behavior is in the neighboring modules described separately.

## File 58 alert schema py

Path: `src/sentinellab/storage/alert_schema.py`

Contains only the version 2 table/index additions and schema checks. SCHEMA declares detection_runs, saved_alerts, alert_evidence, run_alerts, and the saved-alert time index. validate_alert_schema checks required columns. migrate creates these structures only when user_version is 1 and then sets version 2. The caller owns the transaction, so migration is rolled back with a failed detection save. It does not rewrite original event rows.

Code navigation: `validate_alert_schema`; `migrate`.

## File 59 alerts py

Path: `src/sentinellab/storage/alerts.py`

Coordinates persistent detection and read-only history. save_detection validates rule selection, opens an existing writable database, starts BEGIN IMMEDIATE, migrates if needed, reads and evaluates one snapshot, writes a run, compares stable alert identities, inserts new alerts/evidence, records run membership, updates counts, and commits. Any failure rolls back the attempt. alert_summary returns totals; list_history provides bounded alert summaries or run configurations; get_alert returns one full saved result and first run. Stored results are immutable through these APIs, and late-data results do not delete earlier alerts.

Code navigation: `save_detection`; `alert_summary`; `list_history`; `get_alert`.

## File 60 database py

Path: `src/sentinellab/storage/database.py`

Creates and validates the event/import schema and performs transactional imports. canonical_event converts an Event into normalized comparable values. _check_schema checks supported versions and required columns, including alert tables on v2. initialize_database creates an empty v1 schema without inventing an import. import_events validates first, applies identity rules, preserves provenance, writes counts, and commits atomically. database_summary reads totals and the actual schema version. StorageError provides safe application-facing errors. Initial SCHEMA_VERSION remains 1 because imports create the original event schema.

Code navigation: `StorageError`; `canonical_event`; `_check_schema`; `initialize_database`; `import_events`; `database_summary`.

## File 61 search py

Path: `src/sentinellab/storage/search.py`

Read-only database access for event search and evidence lookup. _reader opens mode=ro, starts a read transaction, sets row objects, validates schema, and closes the connection. _integer rejects booleans and out-of-range integers; _timestamp validates and normalizes time filters. search_events combines exact filters with AND and returns a bounded ordered page with counts. get_event returns original evidence and provenance for one valid internal ID, or None if it is absent. Its helpers are reused by saved-alert readers.

Code navigation: `_reader`; `_integer`; `_timestamp`; `search_events`; `get_event`.

## File 62 storage cli py

Path: `src/sentinellab/storage_cli.py`

Implements database import, summary, search, and get subcommands. main defines their allowed arguments and delegates to storage functions. Import reports validated, inserted, duplicate, conflicting, and rejected records. Search/get print safe escaped JSON. A valid missing event uses exit 1; invalid usage or fatal errors use exit 2.

Code navigation: `main`.

## File 63 init   py

Path: `src/sentinellab/web/__init__.py`

A Python package marker for this directory. It lets modules or tests be organized and imported using their package path. In this project it is empty or contains only a short package description; it does not start a server, create a database, or run a rule. The real behavior is in the neighboring modules described separately.

## File 64 server py

Path: `src/sentinellab/web/server.py`

Provides the local HTTP backend. LocalServer binds to loopback, stores the selected database path, and creates a random token. Handler.setup sets a timeout; log_message suppresses potentially sensitive request logging; reply sets JSON/content and protective headers; allowed checks Host, Origin, cross-site context, and URL length. do_GET serves only named pages/assets and event read endpoints. do_POST permits only protected bounded imports using a temporary file. main validates the port, initializes the database, runs the server, and handles normal stop/startup errors. There are no alert or login endpoints yet.

Code navigation: `LocalServer (__init__)`; `Handler (setup, log_message, reply, allowed, do_GET, do_POST)`; `main`.

## File 65 gitkeep

Path: `src/sentinellab/web/static/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 66 app js

Path: `src/sentinellab/web/static/app.js`

Browser behavior built with native JavaScript. api wraps fetch and JSON errors; status safely sets text; refreshCounts reads event/import totals; toggleSearch manages controls; hideEvidence invalidates older requests; showEvidence fetches one original; search requests a bounded page and builds DOM rows with textContent. Event handlers submit filters, clear filters, page results, close evidence, and upload a bounded file with the token. It does not calculate rules or directly access SQLite.

## File 67 style css

Path: `src/sentinellab/web/static/style.css`

Presentation rules for the event workspace: fonts, colors, header, summary cards, panels, forms, tables, outcome labels, focus indicators, evidence text, and pagination. A narrow-screen media query switches filters and statistics to one column and adjusts spacing. Styling changes how information is displayed; it does not decide whether an event or alert is valid.

## File 68 gitkeep

Path: `src/sentinellab/web/templates/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 69 index html

Path: `src/sentinellab/web/templates/index.html`

The browser page structure: branding, prototype notice, saved-event/import counts, upload form, combined search filters, event table, pagination, and original-evidence panel. It includes labels and status regions for usability, a request-token placeholder filled by the server, and links to local CSS/JavaScript. It contains no backend database logic. Its current badge says Day 7 even though Day 8 added persistence behind the separate CLI.

## File 70 init   py

Path: `tests/__init__.py`

A Python package marker for this directory. It lets modules or tests be organized and imported using their package path. In this project it is empty or contains only a short package description; it does not start a server, create a database, or run a rule. The real behavior is in the neighboring modules described separately.

## File 71 gitkeep

Path: `tests/fixtures/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 72 gitkeep

Path: `tests/integration/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 73 init   py

Path: `tests/integration/__init__.py`

A Python package marker for this directory. It lets modules or tests be organized and imported using their package path. In this project it is empty or contains only a short package description; it does not start a server, create a database, or run a rule. The real behavior is in the neighboring modules described separately.

## File 74 test alert storage py

Path: `tests/integration/test_alert_storage.py`

Day 8 persistence tests. They check atomic migration without evidence loss, duplicate alert prevention with separate runs, read-only v1/v2 behavior, selected/empty runs, failure rollback, table conflicts, unsupported/missing databases, concurrent saves/imports, late data, identity conflicts, pagination bounds, and separate-process CLI persistence. These tests connect detection results to durable database history.

## File 75 test cli py

Path: `tests/integration/test_cli.py`

Runs the format checker in subprocesses. It verifies package discovery from another working directory, safe JSON output and exit codes for rejections, and missing-file handling. This catches errors that would be missed by calling reader functions directly in the same Python process.

## File 76 test detection py

Path: `tests/integration/test_detection.py`

R1-focused integration tests. It verifies thresholds, inclusive boundaries, equal-time batches, grouping, case/spaces, cross-source identities, success behavior, rearming, shuffled import order, stable evidence, read-only file bytes, input caps, and CLI output. Shared fixtures define example failure sequences and base times.

## File 77 test detection day07 py

Path: `tests/integration/test_detection_day07.py`

Tests R2/R3 and the combined engine: distinct accounts versus repeats, inclusive/exclusive boundaries, separate groups, ties, multiple successes, evidence roles, shuffled imports, unchanged R1 behavior, shared snapshot use, and combined output limits. It verifies the rule relationships introduced after the R1-only checkpoint.

## File 78 test search py

Path: `tests/integration/test_search.py`

Exercises combined exact filters, timezone normalization, time endpoints, pagination ties, missing evidence, invalid arguments, SQL-looking text as data, and read-only behavior. It verifies both search results and the storage safety assumptions reused by the browser.

## File 79 test storage py

Path: `tests/integration/test_storage.py`

Exercises real SQLite imports and summaries. It checks normalized persistence, original provenance, duplicate/conflict rules, source namespaces, empty inputs, safe CLI behavior, concurrent imports, unrelated/unsupported databases, and rollback after a deliberately forced write error. Its event helper supplies reusable synthetic records for other tests.

## File 80 test web py

Path: `tests/integration/test_web.py`

Runs a real isolated loopback HTTP server against temporary SQLite data. It checks routes, assets, import/search/evidence round trips, pagination, filter controls, safe rendering inputs, origin/token/host protections, request limits, partial uploads, and compatibility after alert schema migration. It does not establish production hosting readiness.

## File 81 gitkeep

Path: `tests/unit/.gitkeep`

An empty placeholder that makes Git retain this directory in the scaffold. Git tracks files, not empty folders. It contains no executable code, settings, data, or tests. It may remain after real files are added; it does not activate a feature.

## File 82 init   py

Path: `tests/unit/__init__.py`

A Python package marker for this directory. It lets modules or tests be organized and imported using their package path. In this project it is empty or contains only a short package description; it does not start a server, create a database, or run a rule. The real behavior is in the neighboring modules described separately.

## File 83 test reader py

Path: `tests/unit/test_reader.py`

Tests the reader in isolation using valid, invalid, hostile-looking, empty, and oversized inputs. It checks required fields, types, outcomes, timestamps, IP normalization, duplicate JSON keys, character restrictions, UTF 8, original-text handling, and resource limits. It verifies the input contract before storage or detection is involved.



# 20 Automated test catalogue

The following test names are extracted from the project tests. Each item includes a plain-language reading of the name. Tests are grouped by file. They are the detailed location guide behind the Day 8 total of 120 tests.

## test alert storage

Path: `tests/integration/test_alert_storage.py`. Test methods: 16.

- `test_migration_preserves_originals_and_links_all_evidence`: checks that migration preserves originals and links all evidence.
- `test_repeated_save_deduplicates_but_records_each_run`: checks that repeated save deduplicates but records each run.
- `test_preview_and_history_never_write_or_migrate`: checks that preview and history never write or migrate.
- `test_selected_rules_and_zero_alert_run_record_configurations`: checks that selected rules and zero alert run record configurations.
- `test_failed_evaluation_rolls_back_migration`: checks that failed evaluation rolls back migration.
- `test_partial_writes_roll_back_entire_run`: checks that partial writes roll back entire run.
- `test_event_limit_and_invalid_stored_time_leave_v1_unchanged`: checks that event limit and invalid stored time leave v1 unchanged.
- `test_concurrent_import_and_save_use_one_consistent_snapshot`: checks that concurrent import and save use one consistent snapshot.
- `test_migration_table_conflict_is_atomic`: checks that migration table conflict is atomic.
- `test_unsupported_schema_and_missing_database_not_modified`: checks that unsupported schema and missing database not modified.
- `test_concurrent_saves_share_one_set_of_alerts`: checks that concurrent saves share one set of alerts.
- `test_import_after_upgrade_keeps_deduplication_and_provenance`: checks that import after upgrade keeps deduplication and provenance.
- `test_late_data_preserves_old_alert_and_records_new_membership`: checks that late data preserves old alert and records new membership.
- `test_identity_conflict_does_not_overwrite`: checks that identity conflict does not overwrite.
- `test_history_paging_and_input_bounds`: checks that history paging and input bounds.
- `test_cli_process_persistence_and_error_codes`: checks that cli process persistence and error codes.

## test cli

Path: `tests/integration/test_cli.py`. Test methods: 3.

- `test_sample_from_another_working_directory`: checks that sample from another working directory.
- `test_rejected_input_returns_exit_one_without_leaking_contents`: checks that rejected input returns exit one without leaking contents.
- `test_missing_file_returns_exit_two`: checks that missing file returns exit two.

## test detection

Path: `tests/integration/test_detection.py`. Test methods: 16.

- `test_four_failures_and_success_are_below_threshold`: checks that four failures and success are below threshold.
- `test_exact_five_minute_boundary_and_evidence`: checks that exact five minute boundary and evidence.
- `test_one_microsecond_outside_boundary_does_not_trigger`: checks that one microsecond outside boundary does not trigger.
- `test_ties_are_batched_and_all_contribute`: checks that ties are batched and all contribute.
- `test_continuous_burst_is_one_frozen_alert`: checks that continuous burst is one frozen alert.
- `test_group_rearms_after_window_drops_below_threshold`: checks that group rearms after window drops below threshold.
- `test_success_does_not_reset_failures`: checks that success does not reset failures.
- `test_accounts_ips_case_and_spaces_do_not_mix`: checks that accounts ips case and spaces do not mix.
- `test_distinct_source_identities_contribute_to_same_group`: checks that distinct source identities contribute to same group.
- `test_timezone_and_ipv6_normalization`: checks that timezone and ipv6 normalization.
- `test_reimports_conflicts_and_reruns_do_not_inflate_results`: checks that reimports conflicts and reruns do not inflate results.
- `test_import_order_changes_row_ids_but_not_alert_identity`: checks that import order changes row ids but not alert identity.
- `test_missing_empty_and_read_only_database_behavior`: checks that missing empty and read only database behavior.
- `test_event_cap_fails_whole_run_including_successes`: checks that event cap fails whole run including successes.
- `test_minimum_supported_date_does_not_overflow`: checks that minimum supported date does not overflow.
- `test_cli_separate_process_json_and_exit_codes`: checks that cli separate process json and exit codes.

## test detection day07

Path: `tests/integration/test_detection_day07.py`. Test methods: 20.

- `test_r2_nine_accounts_and_many_repeats_do_not_trigger`: checks that r2 nine accounts and many repeats do not trigger.
- `test_r2_includes_exact_ten_minute_boundary`: checks that r2 includes exact ten minute boundary.
- `test_r2_excludes_one_microsecond_outside_boundary`: checks that r2 excludes one microsecond outside boundary.
- `test_r2_same_time_batch_retains_repeated_account_evidence`: checks that r2 same time batch retains repeated account evidence.
- `test_r2_different_ips_and_successes_do_not_mix`: checks that r2 different ips and successes do not mix.
- `test_r2_case_and_spaces_count_as_distinct_usernames`: checks that r2 case and spaces count as distinct usernames.
- `test_r2_ongoing_burst_suppressed_and_later_burst_rearms`: checks that r2 ongoing burst suppressed and later burst rearms.
- `test_r2_expiring_one_repeat_keeps_account_active`: checks that r2 expiring one repeat keeps account active.
- `test_r3_five_failures_then_success_links_both_roles`: checks that r3 five failures then success links both roles.
- `test_r3_four_failures_no_success_or_earlier_success_do_not_trigger`: checks that r3 four failures no success or earlier success do not trigger.
- `test_r3_start_inclusive_and_end_exclusive`: checks that r3 start inclusive and end exclusive.
- `test_r3_excludes_equal_time_failures_even_with_enough_earlier_ones`: checks that r3 excludes equal time failures even with enough earlier ones.
- `test_r3_username_and_ip_must_both_match`: checks that r3 username and ip must both match.
- `test_r3_each_success_has_own_identity_and_no_reset`: checks that r3 each success has own identity and no reset.
- `test_all_rules_snapshot_stable_reruns_reimports_and_shuffled_order`: checks that all rules snapshot stable reruns reimports and shuffled order.
- `test_r1_saved_day6_example_is_unchanged`: checks that r1 saved day6 example is unchanged.
- `test_combined_run_reads_snapshot_once`: checks that combined run reads snapshot once.
- `test_evidence_budget_fails_instead_of_returning_partial_results`: checks that evidence budget fails instead of returning partial results.
- `test_cli_default_all_and_rule_selection`: checks that cli default all and rule selection.
- `test_missing_database_and_invalid_rule_do_not_create_files`: checks that missing database and invalid rule do not create files.

## test search

Path: `tests/integration/test_search.py`. Test methods: 11.

- `test_default_chronological_order_and_no_original_in_list`: checks that default chronological order and no original in list.
- `test_combined_filters`: checks that combined filters.
- `test_start_inclusive_end_exclusive_at_microseconds`: checks that start inclusive end exclusive at microseconds.
- `test_equivalent_ipv6_and_exact_username`: checks that equivalent ipv6 and exact username.
- `test_pages_handle_timestamp_ties_without_overlap`: checks that pages handle timestamp ties without overlap.
- `test_invalid_filters_are_safe`: checks that invalid filters are safe.
- `test_sql_text_is_only_a_value`: checks that sql text is only a value.
- `test_lookup_retains_original_and_provenance`: checks that lookup retains original and provenance.
- `test_read_operations_leave_database_bytes_unchanged`: checks that read operations leave database bytes unchanged.
- `test_missing_or_corrupt_database_is_not_created_or_modified`: checks that missing or corrupt database is not created or modified.
- `test_cli_from_another_directory_and_exit_codes`: checks that cli from another directory and exit codes.

## test storage

Path: `tests/integration/test_storage.py`. Test methods: 19.

- `test_persists_normalized_and_original_evidence_after_reopen`: checks that persists normalized and original evidence after reopen.
- `test_reimport_is_duplicate_and_preserves_first_provenance`: checks that reimport is duplicate and preserves first provenance.
- `test_same_id_different_values_is_conflict_and_original_is_kept`: checks that same id different values is conflict and original is kept.
- `test_canonical_equivalence_ignores_offset_ip_spelling_and_key_order`: checks that canonical equivalence ignores offset ip spelling and key order.
- `test_same_event_id_from_another_source_is_new`: checks that same event id from another source is new.
- `test_same_batch_first_valid_identity_wins`: checks that same batch first valid identity wins.
- `test_case_and_spaces_are_significant`: checks that case and spaces are significant.
- `test_mixed_invalid_conflict_and_new_rows_have_separate_counts`: checks that mixed invalid conflict and new rows have separate counts.
- `test_sql_looking_username_is_stored_as_data`: checks that sql looking username is stored as data.
- `test_database_failure_rolls_back_rows_and_import_summary`: checks that database failure rolls back rows and import summary.
- `test_concurrent_reimports_do_not_duplicate_events`: checks that concurrent reimports do not duplicate events.
- `test_missing_input_does_not_create_database`: checks that missing input does not create database.
- `test_summary_does_not_create_missing_database`: checks that summary does not create missing database.
- `test_input_cannot_be_database`: checks that input cannot be database.
- `test_unrelated_database_is_not_adopted_or_changed`: checks that unrelated database is not adopted or changed.
- `test_unsupported_schema_is_not_migrated`: checks that unsupported schema is not migrated.
- `test_empty_file_creates_zero_event_import`: checks that empty file creates zero event import.
- `test_cli_across_processes_persists_and_deduplicates`: checks that cli across processes persists and deduplicates.
- `test_cli_conflict_exit_and_safe_database_error`: checks that cli conflict exit and safe database error.

## test web

Path: `tests/integration/test_web.py`. Test methods: 11.

- `test_fresh_database_home_and_static_allowlist`: checks that fresh database home and static allowlist.
- `test_import_search_lookup_and_duplicate_roundtrip`: checks that import search lookup and duplicate roundtrip.
- `test_event_browser_still_reads_and_imports_after_alert_migration`: checks that event browser still reads and imports after alert migration.
- `test_browser_result_filter_contains_all_three_real_options`: checks that browser result filter contains all three real options.
- `test_partial_import_and_conflict_keep_original`: checks that partial import and conflict keep original.
- `test_host_origin_token_and_cross_site_protections`: checks that host origin token and cross site protections.
- `test_oversized_and_wrong_content_type_do_not_write`: checks that oversized and wrong content type do not write.
- `test_incomplete_upload_does_not_write`: checks that incomplete upload does not write.
- `test_invalid_filters_and_empty_results`: checks that invalid filters and empty results.
- `test_pagination_and_untrusted_text_remain_data`: checks that pagination and untrusted text remain data.
- `test_reinitialization_preserves_data_and_rejects_unrelated_file`: checks that reinitialization preserves data and rejects unrelated file.

## test reader

Path: `tests/unit/test_reader.py`. Test methods: 24.

- `test_valid_record_preserves_identity`: checks that valid record preserves identity.
- `test_equivalent_timezones_normalize_to_same_instant`: checks that equivalent timezones normalize to same instant.
- `test_ipv6_normalizes_without_changing_address`: checks that ipv6 normalizes without changing address.
- `test_microseconds_are_preserved`: checks that microseconds are preserved.
- `test_invalid_timestamps_are_rejected`: checks that invalid timestamps are rejected.
- `test_missing_fields_have_safe_explanation`: checks that missing fields have safe explanation.
- `test_unknown_field_is_rejected_without_echoing_secret`: checks that unknown field is rejected without echoing secret.
- `test_non_string_values_are_rejected`: checks that non string values are rejected.
- `test_empty_and_oversized_identity_fields`: checks that empty and oversized identity fields.
- `test_control_characters_and_unpaired_surrogates_rejected`: checks that control characters and unpaired surrogates rejected.
- `test_invalid_outcomes_and_event_types`: checks that invalid outcomes and event types.
- `test_invalid_ips`: checks that invalid ips.
- `test_mixed_input_continues_after_errors_and_keeps_line_numbers`: checks that mixed input continues after errors and keeps line numbers.
- `test_original_text_is_preserved_but_hidden_in_repr`: checks that original text is preserved but hidden in repr.
- `test_duplicate_json_keys_rejected`: checks that duplicate json keys rejected.
- `test_non_objects_and_nonstandard_constants_rejected`: checks that non objects and nonstandard constants rejected.
- `test_invalid_utf8_does_not_hide_later_record`: checks that invalid utf8 does not hide later record.
- `test_empty_file_and_trailing_newlines`: checks that empty file and trailing newlines.
- `test_oversized_line_rejected_without_crash`: checks that oversized line rejected without crash.
- `test_oversized_file_is_fatal`: checks that oversized file is fatal.
- `test_line_count_limit`: checks that line count limit.
- `test_deep_json_is_rejected_without_traceback`: checks that deep json is rejected without traceback.
- `test_missing_file_and_directory_are_fatal`: checks that missing file and directory are fatal.
- `test_deduplication_is_not_silently_claimed`: checks that deduplication is not silently claimed.



# 21 Runtime and generated files

The following entries were observed locally while preparing this handbook. Runtime counts can change after additional commands. These files are ignored by Git and do not form part of the published source inventory.

| Local file | Purpose | Size when inspected |
| --- | --- | --- |
| data/runtime/day03_demo.db | Day 3 event-persistence demonstration database. | 20480 bytes |
| data/runtime/day05_demo.db | Day 5 browser event demonstration; an existing server may still use this file. | 20480 bytes |
| data/runtime/day05_ui_checks.db | Separate synthetic database used for browser pagination and hostile-text checks. | 32768 bytes |
| data/runtime/day05_ui_checks.jsonl | Synthetic browser-check input data, kept separate from source samples. | 4804 bytes |
| data/runtime/day06_demo.db | Day 6 R1 demonstration database. | 20480 bytes |
| data/runtime/day07_demo.db | Day 7 combined-rules demonstration database. | 28672 bytes |
| data/runtime/day08_demo.db | Day 8 version 2 demo with saved alerts and run history. | 73728 bytes |


.venv holds the local Python environment, including its configuration and interpreter files. __pycache__ and .pyc files are generated by Python imports. They can be recreated by the interpreter; they do not contain a separate implementation of a feature. SQLite journal files may appear temporarily during transactions. Do not remove a database or its active journal while an operation is using it.

The .git directory contains version-control internals. Its contents should be managed through Git rather than edited manually. This handbook does not enumerate every interpreter library, Git object, or bytecode file because those are generated infrastructure rather than the 83 authored or scaffold files in the checkpoint.

# 22 Source map and maintenance

The code is the authority for implemented behavior. README.md and NEXT_SESSION.md give current orientation. EVENT_FORMAT.md, DATABASE.md, SEARCH.md, DETECTION_RULES.md, ALERT_STORAGE.md, and WEB.md describe contracts. PROGRESS.md records development history. Daily guides teach each checkpoint. PROJECT_BRIEF.md, ROADMAP.md, ARCHITECTURE.md, and ACCEPTANCE_CRITERIA.md also contain future goals and should be read with their dates and status notes.

The Day 8 repository checkpoint is available at https://github.com/usmanafrydy/SentinelLab/commit/80e88e3344a5c6b56c573a80f796a3fb796c3ab1. Tests and example reports provide reproducible implementation evidence. No external research statistics or real-world accuracy estimates are claimed in this handbook.

When the project changes, update this handbook's status, commands, schema description, file catalogue, test total, and future-work sections together. Do not change an old historical alert explanation merely to match a newer rule. Preserve versioned behavior and clearly label the new checkpoint.


# 23 Day 9 browser detection and evidence


Completed September 30, 2026. Project deadline: October 17, 2026.

## Purpose

You can now check stored events from the browser, save the findings, open an alert, and follow its evidence back to an original login record. You can also see what each completed detection run found. The existing rules have not changed.

Roman Urdu: Aaj hum ne browser ko detection aur saved alerts ke saath jora hai. Ab aap button daba kar check chala sakte hain, phir alert ki wajah aur asal login record dekh sakte hain.

## Five useful words

| Word | Meaning | Example |
| --- | --- | --- |
| Event | One recorded action | One failed login |
| Rule | A condition for a suspicious pattern | Five failures for the same account/IP in five minutes |
| Alert | A saved finding when a rule matches | R1 repeated account failures |
| Run | One completed check | One successful press of Run detection and save |
| Evidence | Records explaining the finding | The failures that caused R1 |

An alert is not proof of hacking. Someone may repeatedly enter the wrong password, then log in successfully. Investigate the evidence and surrounding context before concluding compromise. Analyst investigation decisions are not yet stored by this project.

Days 1-5 established validation, SQLite storage, search, originals, and the browser. Days 6-7 added R1/R2/R3. Day 8 saved permanent alert snapshots and run history through command-line tools. Day 9 connects those services to browser controls. No new dependencies are required.

## Step 1: open the project

In PowerShell:

```powershell
Set-Location 'C:\Users\Dell\Desktop\Projects\SentinelLab'
```

This changes the working folder. It does not move files. The project remains in Desktop > Projects > SentinelLab.

## Step 2: open the demonstration

The running demonstration uses http://127.0.0.1:8769 and the separate ignored database data/runtime/day09_demo.db. At the end of verification it has 16 synthetic events, 1 import, 3 alerts, and 2 runs. Further saves increase the run count.

If the server is not running, start it from the project folder:

```powershell
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day09_demo.db --port 8769
```

Keep PowerShell open. Ctrl+C stops a foreground server without deleting data. The assistant's server may already be running in the background. If the port is busy, first try the existing page.

For a fresh checkout, the ignored database is absent. Reproduce the example with a new practice database, importing the published sample once:

```powershell
& ./.venv/bin/python.exe scripts/database.py import data/samples/day07_all_rules.jsonl --database data/runtime/day09_practice.db
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day09_practice.db --port 8771
```

Open http://127.0.0.1:8771. A freshly imported database starts with 16 events and zero saved alerts/runs. These are synthetic records. Earlier demonstration databases remain separate.

## Step 3: understand the page

Navigation links jump to Import, Events, Detection, Saved alerts, and Run history. Event search filters only affect the event table. Detection checks the complete stored dataset, not just visible search results. Uploading records does not automatically run detection; press the explicit save button when ready.

## Step 4: run the rules

In Detection, leave Rules on All rules and press Run detection and save. Or select one rule:

| Rule | Pattern | Default threshold |
| --- | --- | --- |
| R1 | Repeated failures for the same exact username/IP | 5 failures in an inclusive 300-second window |
| R2 | Failures across distinct usernames from one IP | 10 distinct usernames in an inclusive 600-second window |
| R3 | Success after earlier failures for the same username/IP | 5 earlier failures within 300 seconds; equal-time failures excluded |

R1 counts failed events, not alerts. R2 counts distinct usernames, not repeated attempts against just one username. DETECTION_RULES.md explains timestamp ties, grouping, and episode rearming precisely.

The button saves a completed run. For an event-only database it also creates the alert/history tables in the same transaction. A transaction means the related changes succeed together or roll back together; a failed attempt must not leave half a run saved.

The first all-rules save on the fresh practice database should show 16 checked, 3 new, 0 already saved, and 3 total saved alerts. On the already verified Day 9 demo, the next save should show 0 new and 3 already saved.

## Step 5: read counts correctly

| Count | Meaning |
| --- | --- |
| Events checked | Stored events in the evaluated snapshot |
| Matched | Findings produced by this run's selected rules |
| New | Findings newly saved permanently |
| Existing | Matching findings already saved earlier |
| Total saved alerts | All unique saved findings, including historical results |
| Completed runs | Successful save operations |

Run 1 finds and saves 3 findings. Run 2 checks identical data and recognizes the same 3 findings. The result is 3 alerts and 2 runs. New + Existing equals Matched for a run. Total saved alerts need not equal the number matched by a selected-rule run.

Roman Urdu: Run aik dafa check chalane ka record hai. Alert suspicious activity ka result hai. Wohi data dobara check karne par run barhta hai, lekin wohi alert dobara save nahi hota.

A successful run may match zero alerts. This is not necessarily an error, and does not prove that every possible attack was absent. These rules cover only specific patterns.

## Step 6: open an alert

Select Open R3 alert. Its details show the stable alert ID, rule version, account, IP, threshold, failure count, first event time, trigger time, first saved run, and explanation. Times are UTC.

In this demo, R3 concerns lab_user at 192.0.2.71. It contains five preceding failures and one triggering success. The explanation notes that someone correcting a password can cause this pattern. The first saved run stays 1 even when you open the same alert from run 2. Opening details is read-only.

## Step 7: inspect original evidence

In R3's evidence table, select Original #16. The original panel shows day07-success, outcome success, lab_user, 192.0.2.71, and the exact original JSON. First import and line number show where the record entered this database.

Internal ID 16 belongs to this database. Different import orders or databases may assign another number. Source and event_id identify the synthetic source record across demonstrations.

Roman Urdu: Alert humein wajah batata hai. Original record woh asal data dikhata hai jis par alert bana. Sirf alert ka naam dekh kar hacking confirm nahi karni.

## Step 8: read run history

Run history shows time, selected rule versions/settings, scanned/matched/new/existing counts, and a findings button. Select Alerts from run 2. It still shows three findings even though that run added zero new alerts: existing alerts were found again and linked to run 2. This filter uses run membership, not the first saved run.

Show all alerts removes the run filter. Refresh history reloads counts and starts lists at their first page. Reading these views or reloading the page never creates a run. Saved data survives a browser reload.

## Step 9: pages and snapshots

The browser shows 10 alerts/runs per page and 25 evidence references per page. Previous/Next controls are disabled when there is no page in that direction. APIs allow at most 200 items per page.

A saved alert keeps the evidence present at its trigger. Late imports do not rewrite it. Changed findings may produce new alerts alongside historical ones. Retaining an old snapshot does not declare it resolved. Separate list requests use offsets, so concurrent new saves can shift positions; Refresh history starts again from the beginning. There is no continuous monitoring or automatic background refresh.

## How the code handles a click

1. The browser sends the selected rule to POST /api/detect with its write token.
2. The server checks host, origin, token, content type, and request size.
3. save_detection opens one transaction and reads one bounded event snapshot.
4. The selected rules evaluate that snapshot using unchanged policies.
5. Storage records the run, new snapshots, evidence links, and membership of every matched alert. Existing unchanged alerts are reused.
6. It commits everything together; failures roll back that attempt.
7. The browser displays counts and reads the saved lists through GET requests.
8. Alert details retrieve a bounded evidence page; Original buttons use the existing event API.

The page token helps prevent unwanted cross-site writes. It is not analyst authentication. Local users/processes able to read the page can obtain it. Accounts, roles, and public deployment remain unfinished.

## Day 9 file responsibilities

| File | Job |
| --- | --- |
| src/sentinellab/storage/alerts.py | Run-membership filter, next-page information, bounded evidence responses; existing atomic saving remains authoritative |
| src/sentinellab/web/server.py | New read APIs, protected detection POST, two additional allowlisted assets |
| src/sentinellab/web/templates/index.html | Detection form, alert/details tables, history, navigation |
| src/sentinellab/web/static/app.js | Shared busy state and focus/scroll to originals |
| src/sentinellab/web/static/alerts.js | API calls, safe text rendering, selection, paging, stale-response handling |
| src/sentinellab/web/static/alerts.css | New controls, facts, responsive tables |
| tests/integration/test_web_alerts.py | Thirteen real HTTP/SQLite integration cases |
| docs/WEB.md and docs/ALERT_STORAGE.md | API/storage behavior and limits |
| docs/DAY_09_GUIDE.md | This lesson |
| README.md, SETUP.md, PROGRESS.md, NEXT_SESSION.md, ACCEPTANCE_CRITERIA.md, DETECTION_RULES.md | Updated status, instructions, continuity, verification, and scope; these Markdown files except README are under docs |

## Verification

All 133 automated tests pass. Thirteen new tests cover repeat/selected/empty saves, no detection on upload, read-only history, list/evidence paging, original links, invalid inputs, write protection, failure rollback, bounded large evidence, and asset access.

Browser checks verified first/repeated saves, run-2 membership, R3 details, the original success, reload persistence, and desktop/narrow layouts without page-level horizontal overflow. Larger evidence/list pagination is covered by HTTP integration tests. No browser console errors were observed in this workflow. This is component verification, not production security or measured detection accuracy.

Run tests from the project folder:

```powershell
& ./.venv/bin/python.exe scripts/run_tests.py
```

## Troubleshooting

- Page unavailable: check the server and exact 127.0.0.1 port.
- Old page/token: restart after Python changes, then refresh the browser.
- Zero saved alerts: importing does not run detection; the chosen rule may also find nothing.
- Zero new and some existing: the software recognized saved findings and avoided duplicates.
- Limit error: over 10,000 events or 100,000 combined evidence references fails the complete run, not a partial save.
- Connection lost during save: Refresh history before retrying. The server may have committed even if its response was lost. Retrying can add a run while unchanged alerts remain deduplicated.
- Wide table on a narrow screen: scroll inside the table to reach remaining columns.

## Your practice and the next checkpoint

Open R3 and its successful-login original. Explain event, alert, and run in your own words. Answer directly in this project chat; no separate file is needed.

One question: a check shows 0 new alerts and 3 already saved. Did detection fail, or recognize the same findings? Explain why.

Day 10 is planned to begin investigation storage: link a saved alert to a case and preserve analyst notes/status history separately from immutable evidence. We must specify and test it first. Authentication, exports, broader evaluation, and portfolio presentation remain future work. Say: Start SentinelLab Day 10. Explain each step in simple English and Roman Urdu when needed.

GitHub publication is verified separately after checks. Local Git HEAD/index remain behind because of the existing Windows metadata restriction. Connector publication does not synchronize local Git metadata. Do not reset the working folder to resolve that mismatch.


# 24 Interface guidance and the planned design

## The current appearance is an early version

The current browser is a working local prototype. Its first job was to connect event imports, searches, detection, and original evidence correctly. It is not the final intended portfolio design. A useful security interface must help someone decide what to do next, understand a result, and find its evidence. Visual styling should make those tasks easier.

On 1 October 2026 we added a Start here section with three linked steps: add login records, check for patterns, and review evidence. The links take you to the right section. If Saved events is already above zero, you can check those records without importing them again. The prepared sample is day07_all_rules.jsonl under data/samples.

Expandable help now explains event, alert, and run; each detection rule; new versus existing counts; history columns; and UTC times. Expand only the explanation you need. This keeps help available without forcing every user to read all of it each time. Roman Urdu explanations support the main English instructions.

Evidence labels now use Failed login, Earlier failure, and Successful login. The API still preserves its original machine-readable roles. Only the visible wording changed. This makes it easier to understand which event supports a pattern and which successful event triggered R3.

Roman Urdu: Frontend sirf khoobsurat hona kaafi nahi. User ko samajh aana chahiye ke agla step kya hai aur result ka matlab kya hai. Ab page par madad maujood hai; mazeed design ka kaam final release se pehle planned hai.

## How to use the new help

Begin with Start here. Follow Add login records if your database is empty. Choose a sample, then Import records. Read the result before continuing: inserted events were saved, duplicates were already present, and rejected records need correction. Detection does not begin automatically.

Next follow Check for patterns. Open What do R1, R2, and R3 check if the rule names are unfamiliar. Choose All rules for the complete current check. Press Run detection and save once, wait for its response, then read the counts. Open How do I read the result if you are unsure why there are zero new alerts.

Finally follow Review the evidence. Open a saved alert and read its reason. Inspect its originals. A success after failures may be a corrected password; record a conclusion only after sufficient investigation. The application cannot yet store investigation notes or analyst conclusions, so do not mistake the detail view for a completed case-management system.

In Run history, open Understand the history columns and times. Trigger time describes the event pattern; completed time describes the check you ran. Pakistan is UTC plus five hours, so 09:00 UTC is 14:00 in Pakistan. The project still displays UTC consistently rather than silently mixing timezones.

## Frontend and backend

The frontend is what the user sees and operates: the page, buttons, explanations, forms, tables, spacing, and navigation. HTML defines structure, CSS defines appearance, and JavaScript reacts to user actions and displays server results. The backend is Python and SQLite: it validates records, runs rules, stores results, and returns data through the API.

A clearer label or an expandable explanation does not change a detection threshold. Separating presentation from detection lets us improve usability while retaining tested rule behavior. UI means user interface. UX means the user's experience of completing a task, including confusion, errors, waiting, and recovery.

## What a later interface improvement should achieve

The next design pass should give frequent tasks clear places: an overview, events, alerts, detection history, and investigations when implemented. Alert lists should expose useful context such as account, source IP, reason, and relevant time without requiring unnecessary clicks. Evidence should remain one obvious action away.

We should use consistent spacing, legible type, clear button hierarchy, visible keyboard focus, and colors that reinforce meaning alongside text. Small screens need usable controls and scrollable tables. Empty states should explain the next action, loading states should say what is happening, and errors should suggest a recovery step. Charts should be added only when they answer a real question from stored data.

These are planned improvements, not completed screens. We will check them with actual workflows: a first-time user imports a sample, understands the result, checks rules, opens an alert, and finds the original event. We should also check keyboard operation, narrow layouts, empty data, rejected imports, and zero-match runs. Passing automated tests alone does not establish that an interface is easy to use.

## How you participate in building the project

The assistant creates and edits the project files, explains important choices, runs checks, and publishes verified checkpoints. Your part is to try the interface, identify confusing words or steps, answer short learning questions, and say what you expected when something feels wrong. You do not need to create folders manually.

Useful feedback is specific: I do not know what Matched means; I cannot find how to open evidence; or I expected my search filter to control detection. These examples let us change wording or behavior deliberately. Do not upload private login logs or passwords for a demonstration; the project already includes synthetic samples.

For interviews, explain the flow in your own words: input records are validated and normalized, preserved in SQLite, checked against deterministic rules, and linked to immutable alert evidence. Explain why an alert is not proof of compromise and why repeating a run does not duplicate unchanged alerts.

# 25 Day 9 implementation details and continuation

## Browser and server responsibilities

index.html contains the detection form, saved-alert list, details, original-evidence panel, and run history. The guidance follow-up adds the starting journey and explanatory details elements. These details controls are standard HTML and do not need a new framework or package.

alerts.css formats the new controls, facts, guidance, and responsive layout. app.js still handles imports, event search, and originals. It also shares the busy state with detection. alerts.js calls the new APIs, builds rows with textContent, pages through results, filters by run, and opens original records. TextContent treats log text as data rather than executing HTML within it.

server.py allowlists the added assets and routes. GET /api/alerts/summary reads totals. GET /api/alerts lists saved findings and accepts a run_id membership filter. GET /api/runs lists completed checks and their settings. GET /api/alerts/ID returns metadata and a bounded evidence page. POST /api/detect deliberately saves a run. GET requests do not save or migrate history.

storage/alerts.py adds next_offset to lists, optional run membership filtering, and get_alert_page. It retains the atomic Day 8 save service. Evidence pagination limits the HTTP response, but internally still decodes the existing saved JSON before slicing. Do not claim that it streams directly from storage.

## Important boundaries

The history lists default to 50 items in the API; the browser requests 10. Evidence defaults to 25. Requests accept 1 to 200 items and offsets from 0 to 1000000. A missing valid run ID returns no findings. A malformed ID or query is rejected. Separate list requests may shift if new saves arrive between pages; refreshing starts from the beginning.

The detection form body is capped at 128 bytes and accepts exactly one supported rule value. It uses the same host, origin, and per-process token checks as imports. These checks help prevent unwanted requests from another site but do not provide analyst sign in. A local user who can read the page can obtain its token.

The browser suppresses duplicate in-page submissions while a save is active. This is not request-level idempotency. If a connection fails after the database committed, a retry can create another run. Refresh history before retrying. Existing unchanged alerts remain deduplicated by stable identity.

## Verification and accurate claims

The Day 9 core checkpoint passed 133 automated tests. Thirteen new HTTP integration cases cover saves, selected rules, zero matches, pagination, original links, invalid inputs, request protection, read-only history, and rollback. The browser demonstrated 3 new alerts on its first save and 0 new with 3 existing on its second, then opened R3 and its original successful login. Reload persistence and desktop/narrow layouts were checked.

The demonstration has 16 synthetic events, 1 import, 3 alerts, and 2 runs at that checkpoint. A user's later clicks can change run counts. Runtime databases are ignored and are not the same as published source code. The Day 9 source checkpoint is 2590afae7f03145f4873a800af9b161108dd0c1e in the usmanafrydy/SentinelLab repository.

## Next development steps

Day 10 is planned to begin investigation storage with alert links, notes, and status history kept separate from immutable evidence. Design validation and transaction behavior first, then test a small complete workflow. Analyst authentication, report exports, broader detection evaluation, and portfolio presentation remain unfinished. A more polished frontend is part of the remaining plan; no final design or production readiness is claimed here. The target remains 17 October 2026.

The local Git metadata remains behind the published branch because of the previously encountered Windows restriction. Connector publication must be verified independently and does not synchronize the local index. Do not reset the working folder to hide that difference.


# 26 Investigation storage and case concepts

This chapter records the Day 10 checkpoint. Later chapters describe subsequent changes. Browser startup now requires the Day 12 account setup, and new browser author labels come from the signed-in account.

Completed October 1, 2026. Target completion remains October 17, 2026.

## What we built today

We added a complete local case workflow: create a case from a saved alert, add notes, change its status and conclusion with a reason, and read the history later. The data survives closing PowerShell and reopening it. Cases are available through scripts/cases.py today. Browser case controls are planned for Day 11; the existing browser still handles events, alerts, and detection history.

Roman Urdu: Alert shak wali activity dikhata hai. Case mein hum us alert ki investigation ke notes aur progress save karte hain. Aaj yeh kaam commands se hota hai; browser ke buttons aglay checkpoint mein banane hain.

No new packages were needed. We continue to use Python, SQLite, and the standard library. The prepared example uses invented login records, not a real attack or a real account investigation.

## Understand the new concepts

| Concept | Simple meaning | Example |
| --- | --- | --- |
| Case | A place to organize review of one saved alert | Review synthetic success after failures |
| Status | Where the work has reached | open, in_progress, closed |
| Disposition | Your current conclusion about the activity | undecided, benign, suspicious, confirmed_compromise |
| Note | An observation or question kept with the case | Need more context about this success |
| Action history | The sequence of creation, notes, and changes | Created, note added, review started |
| Revision | A number that increases after each saved action | 1 after creation, 2 after a note, 3 after a change |

Status and conclusion answer different questions. In progress says someone is working on the case. Undecided says there is not yet a conclusion. A closed case must have a chosen conclusion, but closing it does not make that conclusion objectively correct. The software stores the analyst's assertion; it does not independently verify a compromise.

Benign means the analyst considers the activity harmless. Suspicious means a concern remains. Confirmed compromise is a strong analyst conclusion requiring evidence beyond a threshold match. Do not select it merely because R1 or R3 triggered. Today we leave the demonstration undecided.

Roman Urdu: Status batata hai kaam kahan tak pohncha. Disposition batati hai aap ka nateeja kya hai. In progress aur undecided aik saath bilkul theek hain.

## Step 1 Open the project folder

In PowerShell:

```powershell
Set-Location 'C:\Users\Dell\Desktop\Projects\SentinelLab'
```

The assistant has already created the code, tests, documents, and demonstration. You do not need to create any folders. Commands below refer to the local Python environment already in this project.

## Step 2 Read the prepared case

```powershell
& ./.venv/bin/python.exe scripts/cases.py get --database data/runtime/day10_demo.db --case-id 1
```

Expected current demonstration: title Review synthetic success after failures, status in_progress, disposition undecided, revision 3. The alert_id starts with R3. The separate database has 16 events, 3 saved alerts, 1 detection run, and 1 case. It does not replace your Day 9 database.

This get command only reads. It does not add a note, increase the revision, or migrate the database. All case commands output JSON, which is a structured set of field names and values. The optional --json flag is accepted for consistency but is not required.

## Step 3 Read what happened

```powershell
& ./.venv/bin/python.exe scripts/cases.py history --database data/runtime/day10_demo.db --case-id 1
```

Expected: three history items. Revision 1 created the case. Revision 2 added a note saying the synthetic pattern alone does not prove compromise. Revision 3 changed status from open to in_progress and retained undecided. Each action contains a UTC time and a self-declared author label.

The before and after objects show the state around each action. A note changes the revision but leaves status and conclusion unchanged. Creation has no before-state because the case did not exist. Order is determined by revision, so a computer clock adjustment does not change action order.

## Step 4 Follow the link to evidence

```powershell
$demoCase = (& ./.venv/bin/python.exe scripts/cases.py get --database data/runtime/day10_demo.db --case-id 1) | ConvertFrom-Json
& ./.venv/bin/python.exe scripts/alerts.py get --database data/runtime/day10_demo.db --alert-id $demoCase.alert_id --json
```

ConvertFrom-Json lets PowerShell read a field by name. The command uses the case's alert_id to open the exact saved alert. Its evidence still contains five earlier failures and one successful login. Editing a case never changes those records, the alert reason, the rule version, or the original login text.

If you want to inspect these events through the existing browser, start a separate instance with the new database after stopping any instance on the chosen port:

```powershell
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day10_demo.db --port 8770
```

Open http://127.0.0.1:8770. This shows events and alerts; it does not yet show case controls. Restart old servers after Python code changes before pointing them at a version 3 database. Keep the existing Day 9 preview on its own database.

## Step 5 Add a practice note only if you want to change the demo

Reading Steps 2-4 is enough for today's first exercise. The following command writes another note:

```powershell
& ./.venv/bin/python.exe scripts/cases.py note --database data/runtime/day10_demo.db --case-id 1 --text 'Practice note: I reviewed the sample original records. More context would be needed for a real conclusion.' --author lab_analyst
```

If you have not changed the demonstration earlier, the revision becomes 4. Running it twice adds two notes; notes are deliberately separate actions and do not use alert deduplication. Corrections are new notes. Existing notes cannot be edited or removed by these commands.

The author label explains what label was entered. It is not a login or verified identity. Authentication is a later requirement. Anyone with local file access could also edit SQLite outside the application, so this history is not a tamper-proof forensic record.

## Step 6 Understand changing a conclusion

A state change requires the status, conclusion, reason, author label, and the revision you just read. The software compares that revision with the stored one. If another note or change has arrived, it rejects the stale update and asks you to refresh.

Example: you read revision 3. Someone adds a note, creating revision 4. A state change claiming revision 3 fails. Read the case again, review the new information, then make a deliberate decision. Do not automatically retry with a newer number without reviewing what changed.

Roman Urdu: Revision purani ho to software aap ki change save nahi karta. Pehle nayi information dekhein, phir faisla karein. Is se kisi aur ki nayi mehnat purani screen ki wajah se overwrite nahi hoti.

Open and in_progress cases can move between those states or close with a conclusion. A closed case can revise its conclusion while staying closed, with a new reason. To reopen it, use in_progress and undecided. Closed to open is rejected. An unchanged status/conclusion pair is also rejected; use a note if you only want to add commentary.

Notes can be added to closed cases for clarification. Reopening or correcting a conclusion keeps every earlier action in history. No state change deletes old evidence.

## Reproduce the workflow on a fresh checkout

Runtime databases are not in GitHub. The following sequence creates a new practice database. Choose a new filename if this one already has unrelated practice work. Run each command successfully before continuing.

```powershell
& ./.venv/bin/python.exe scripts/database.py import data/samples/day07_all_rules.jsonl --database data/runtime/day10_practice.db --json
& ./.venv/bin/python.exe scripts/detect.py --database data/runtime/day10_practice.db --save --json
$practiceAlerts = (& ./.venv/bin/python.exe scripts/alerts.py list --database data/runtime/day10_practice.db --json) | ConvertFrom-Json
$practiceAlertId = ($practiceAlerts.items | Where-Object rule_id -eq 'R3').alert_id
$creation = (& ./.venv/bin/python.exe scripts/cases.py create --database data/runtime/day10_practice.db --alert-id $practiceAlertId --title 'Review synthetic success after failures' --author lab_analyst) | ConvertFrom-Json
$practiceCaseId = $creation.case.id
& ./.venv/bin/python.exe scripts/cases.py note --database data/runtime/day10_practice.db --case-id $practiceCaseId --text 'Synthetic exercise: inspect originals before reaching a conclusion.' --author lab_analyst
$currentCase = (& ./.venv/bin/python.exe scripts/cases.py get --database data/runtime/day10_practice.db --case-id $practiceCaseId) | ConvertFrom-Json
& ./.venv/bin/python.exe scripts/cases.py state --database data/runtime/day10_practice.db --case-id $practiceCaseId --status in_progress --disposition undecided --reason 'Begin reviewing synthetic evidence.' --expected-revision $currentCase.revision --author lab_analyst
& ./.venv/bin/python.exe scripts/cases.py history --database data/runtime/day10_practice.db --case-id $practiceCaseId
```

On a fresh database, the result is a case at revision 3 with three actions. Creating a case again for the same saved alert returns created=false and the existing case; it does not replace its title or add another creation action. Repeating the entire sequence is not a no-op: imports, runs, and notes have their own histories. Read existing state before repeating write commands.

## Files and their responsibilities

| File | Responsibility |
| --- | --- |
| src/sentinellab/storage/case_schema.py | Defines and validates the two new tables; creates them inside the case transaction |
| src/sentinellab/storage/cases.py | Validates input, creates cases, appends notes, applies state rules, checks revisions, reads bounded lists/history |
| src/sentinellab/cases_cli.py | Parses each command and calls the corresponding service; formats JSON and exit codes |
| scripts/cases.py | Finds the source package and starts the command-line program |
| src/sentinellab/storage/database.py | Accepts schema version 3 and validates required case columns while retaining older versions |
| src/sentinellab/storage/alerts.py | Reads saved alerts on version 3 and reports the actual version when saving detection |
| tests/integration/test_cases.py | Sixteen integration tests for the complete workflow, failures, concurrency, persistence, and compatibility |
| docs/INVESTIGATIONS.md | Exact state, input, migration, command, and history contract |
| docs/DAY_10_GUIDE.md | This lesson and reproducible examples |

README, setup, database/alert/web contracts, acceptance evidence, progress, and next-session notes are also updated. The Day 9 Word handbook remains a historical edition through Day 9; this new guide is the current Day 10 reference.

## Database changes explained

Schema means the database's table structure. Version 1 holds events/imports. Version 2 adds alerts and detection runs. Version 3 adds investigations and investigation_actions. A valid first case creation upgrades version 2 inside one transaction. A database without a saved alert cannot create a case. Merely reading old databases never upgrades them.

The investigations row holds the current state and permanent link to its alert. The action rows preserve how the current state was reached. Foreign keys require valid links. A unique alert_id enforces one case per saved alert. This initial scope does not group several alerts into one incident.

BEGIN IMMEDIATE makes simultaneous writers wait their turn. A transaction saves the current state and its history action together. If either write fails, both roll back. Tests force failures to verify this. Concurrent case creation produces one case; concurrent notes are both retained; competing updates based on the same revision allow only one to succeed.

## Limits and troubleshooting

Titles allow 120 characters, author labels 80, notes 4000, and reasons 1000. Blank values and unsupported control characters are rejected. Notes/reasons allow newline and tab. Lists/history default to 50 items; --limit accepts 1..200 and --offset 0..1000000. List filters accept --status. History runs oldest revision first; case lists show newest case ID first.

- Saved alert not found: save detection first and use its full alert ID in the same database.
- Case not found: use list with the same --database and copy the correct case ID.
- Refresh instruction: a newer action changed the revision. Read get and history before deciding again.
- Close error: a closed case needs a conclusion other than undecided.
- Write error: check file access, locks, and schema. A failed operation does not partly save a case action.
- Exit code 0 means success; 1 means a missing case on get/history; 2 means a validation/storage/usage error.

## What we checked

The full suite passes 149 tests: the previous 133 plus 16 investigation cases. Coverage includes migration preservation, duplicate creation, complete state history, reopened/corrected conclusions, input limits, read-only access, pagination, forced failure rollback, simultaneous actions, separate-process commands, malformed schemas, and version 3 compatibility with existing detection/import/browser reads.

These are component checks. They do not establish authenticated authors, tamper-proof storage, real-world detection accuracy, exports, or completed release acceptance.

## Your part and the next checkpoint

Run the two read-only commands for get and history, or ask me to walk through their output. Answer in this chat: if you change a case's conclusion, should its original login records change too? Explain why in your own words.

Next: Start SentinelLab Day 11. Add browser investigation controls and explain each step in simple English and Roman Urdu. Preserve the current evidence behavior and beginner guidance while making the case workflow easier to use.

# 27 Investigations in the browser

This chapter records the Day 11 checkpoint. Later chapters describe subsequent changes. Browser startup now requires the Day 12 account setup, and new browser author labels come from the signed-in account.

Completed October 2, 2026. Project: C:\Users\Dell\Desktop\Projects\SentinelLab.

## What you can do today

You can open a saved alert, create its investigation case, write observations, record a decision with a reason, and read the history in your browser. Day 10 built the storage and commands; Day 11 connects those same rules to buttons and forms. No detection thresholds have changed.

Roman Urdu: Alert humein shak wali activity dikhata hai. Case mein hum us activity ki jaanch, notes aur faisla record karte hain. Sirf alert aane ka matlab hacking confirm hona nahi hai.

## Step 1 - Open the demonstration

Open http://127.0.0.1:8771/ while the Day 11 server is running. This uses data/runtime/day11_demo.db, separate from older demonstrations. It contains 16 synthetic login records, one import, three saved alerts and one detection run. Browser verification created case 1 with five actions, ending In progress / Suspicious at revision 5. Your later actions will change those case counts and revisions.

If the page does not open, run these commands in PowerShell:

```powershell
Set-Location "C:\Users\Dell\Desktop\Projects\SentinelLab"
& ./.venv/bin/python.exe scripts/serve.py --database data/runtime/day11_demo.db --port 8771
```

Keep that terminal running. Ctrl+C stops a server started in that terminal. If the port is already in use, open the existing page first. Do not stop unrelated programs. A restart changes the page's request token, so reload the browser before saving again.

On a new checkout, the database is not downloaded from GitHub. Import data/samples/day07_all_rules.jsonl through the browser and press Run detection and save once. Importing alone does not run detection.

## Step 2 - Read the alert and originals

Use Saved alerts in the navigation. Choose Open R3 alert. Read its explanation: five earlier failures were followed by a success for the same username and IP within the configured time window. Review its six evidence references. Original #16 opens the successful login in this demonstration; record IDs can differ in other databases.

Purpose: understand why the detector matched before writing an opinion. The rule cannot tell whether someone corrected their own password or an attacker succeeded. Other context would be needed. An original record is retained evidence; an investigation note is your interpretation.

Expected result: the saved alert and original event can be viewed without changing either one.

## Step 3 - Start or open the investigation

Choose Investigate this alert. The form shows the exact linked alert. Keep or edit the proposed short title, enter an author label such as lab_analyst, and choose Create or open case.

A new case starts Open / Undecided at revision 1. If that alert already has a case, the existing case opens with its previous title, status and notes. This does not reopen a closed case or create another copy. The demonstration's R3 case already exists, so you should see case 1.

The author label is just text supplied by the person using the application. It is not a verified account or a login. Do not describe it as authenticated identity in an interview.

## Step 4 - Add an observation

Enter an Author label for notes and decisions. In New note write a specific observation, for example:

> The alert links five failures and one successful login for lab_user from 192.0.2.71. These are synthetic records. More context is needed before confirming compromise.

Press Save note once. The note appears in Case history and the revision increases. Original events and the saved alert do not change. Notes can also be added to closed cases. You cannot edit or delete old notes through the application; add a correction as another note.

Roman Urdu: Jo cheez evidence mein nazar aati hai woh likhein. Andaza aur haqeeqat alag rakhein. Ghalti ho to naya correction note likhein; purani history rehti hai.

## Step 5 - Understand status and conclusion

| Field | Value | Meaning |
|---|---|---|
| Status | Open | A case exists and work can begin. |
| Status | In progress | Someone is investigating. |
| Status | Closed | The current review has ended with a conclusion. |
| Conclusion | Undecided | There is not enough information to decide. |
| Conclusion | Benign | The reviewer considers the activity harmless, with supporting context. |
| Conclusion | Suspicious | The activity needs concern or further investigation; compromise is not confirmed. |
| Conclusion | Confirmed compromise | The reviewer asserts compromise based on supporting evidence. Detection never selects this automatically. |

Status answers "Where is the work?" Conclusion answers "What do we currently think?" They are different. A suspicious case can remain In progress. Closing requires a conclusion other than Undecided. Reopening a closed case requires In progress and Undecided. Every change requires a reason. Saving the same status and conclusion again is rejected; use a note to add observations instead.

To practise a decision on synthetic data, choose a different valid status/conclusion, explain why in Reason for this change, and choose Save decision. Do not label compromise merely to make the portfolio look impressive. The history shows the before and after values and the supplied author label.

## Step 6 - Learn revisions and conflict recovery

A revision is a case version number. Creation is revision 1. Every saved note or decision adds one. If your page read revision 3 and another action created revision 4, saving a decision based on revision 3 must not overwrite newer work.

The browser says the case changed elsewhere and disables Save decision. Your reason is kept. Choose Refresh selected case, read the latest history, choose the appropriate status and conclusion again, then save. Refresh restores the saved dropdown values but keeps your draft note/reason. The warning itself creates no action.

Roman Urdu: Aap ke paas purana version ho to pehle taza information dekhein. System aap ka likha hua reason sambhal kar rakhta hai, lekin naya faisla karne se pehle latest history dekhni hoti hai.

Notes do not require an expected revision: two submitted notes can both be appended. Decisions do require one because an old decision can contradict newer work.

## Step 7 - Find cases and read history

Use Investigations in the navigation. Choose All cases or a status, then Refresh cases. Open case 1 to continue the demonstration. Case lists show newest case first, ten at a time. Previous cases and Next cases move between pages when available.

Inside a case, history is oldest action first, ten at a time. Next actions shows later entries. Each entry has a revision, action type, UTC time, author label, text and resulting state. Open linked alert and evidence returns to the original saved alert. All saved information survives browser reload.

Draft text is different: it exists only in the current page. Switching between cases or refreshing a selected case preserves its draft. Reloading or closing the browser loses unsaved drafts. Save observations you need to retain.

## Step 8 - Handle errors

- Empty/too-long fields: correct the field. Titles allow 120 characters, author labels 80, notes 4000, reasons 1000. Unsupported control characters are rejected.
- Case changed elsewhere: refresh the selected case and review the latest history before saving the decision again.
- Lost connection while saving: refresh and inspect history before retrying. The server may have saved the action even if the reply was lost. Notes do not have automatic retry deduplication.
- No cases match: switch to All cases and refresh. The selected case can still be visible even when it no longer matches a list filter.
- No saved alerts: import the sample and explicitly run detection/save first.
- Narrow display: tables scroll horizontally inside their own boxes. The editor stacks vertically.

## What changed in the code

| File | Responsibility |
|---|---|
| src/sentinellab/storage/cases.py | Existing transaction/state rules; adds a distinct stale-revision error that the web layer can identify. |
| src/sentinellab/web/case_api.py | Validates exact JSON fields and case query parameters, calls the existing services, and sends IDs/revisions as decimal strings to avoid JavaScript number rounding. |
| src/sentinellab/web/server.py | Routes case requests, enforces existing Host/Origin/token checks and body limits, and returns a conflict response for outdated decisions. |
| src/sentinellab/web/templates/index.html | Accessible labels, case forms, help, list and history containers. |
| src/sentinellab/web/static/cases.js | Loads cases/history, saves explicit actions, retains page drafts, and handles refresh conflicts. |
| src/sentinellab/web/static/cases.css | Case layout, editor spacing, timeline and narrow-screen adjustments. |
| src/sentinellab/web/static/alerts.js | Connects an opened saved alert to the investigation form. |
| src/sentinellab/web/static/app.js | Carries structured API error codes to the browser controls. |
| src/sentinellab/web/static/style.css | Gives tables a readable minimum width within scrollable wrappers. |
| tests/integration/test_web_cases.py | Real local HTTP tests for workflow, duplicate prevention, conflicts, rejected writes, paging, read-only requests and rollback. |

Flow: button/form -> JavaScript -> protected local HTTP request -> input validation -> case storage transaction -> SQLite -> JSON response -> updated case and history. A failed transaction rolls back its changes together. Text is displayed as text, never treated as HTML.

## Verification and limits

157 automated tests pass. Day 11 adds eight HTTP tests; earlier storage tests cover concurrent operations, state transitions, migration and process persistence. Browser verification covered creation, notes, decisions, duplicate creation, outdated-decision recovery, preserved draft reasons, linked original evidence, reload persistence, and desktop/narrow layouts. Pagination boundaries are covered by HTTP tests. No browser console errors were observed in the final check.

This remains a local learning prototype. Request tokens are cross-site request protection, not analyst authentication. History is append-only through the application, but a person directly editing the database can tamper with it. No authenticated users, roles, export workflow or final detection evaluation is complete. Runtime databases/logs stay out of GitHub.

## What comes next

Day 12 should review the web stack and define/implement appropriate analyst sign-in and session protection for this local prototype, with tests and clear limits. Reports, broader interface improvements, detection evaluation, portfolio screenshots and final release remain planned. Target completion is October 17, 2026. These are future tasks, not features already delivered.

## Your small exercise

Open case 1 and read its history. Tell me here: if your page shows revision 5 but another note has already created revision 6, what should you do before saving a decision? You can answer in simple English or Roman Urdu.

# 28 Local sign in and session protection

This chapter records the Day 12 checkpoint. Later chapters describe subsequent changes. This chapter describes the current browser access behavior.

Completed October 2, 2026. Project folder: C:\Users\Dell\Desktop\Projects\SentinelLab.

## What we built and why

The browser now asks you to sign in before it shows saved login events, alerts, detection runs or investigation cases. Signing out removes the session on the server. New browser case actions use the signed-in account name; changing a form value cannot impersonate a different author.

Before today, the request token stopped unwanted cross-site writes, but anyone who could open the local page could read data and obtain that token. Authentication adds a separate check: the browser must have a valid session created after password verification. The existing request protections still apply.

Roman Urdu: Pehle page kholne se data nazar aa jata tha. Ab pehle local account se login karna hota hai. Login aap ko pehchanta hai; request token doosri website se aane wali unwanted request ko rokne mein madad karta hai.

This is a one-account, local learning prototype. It is not ready for public hosting. Browser sign-in does not encrypt SQLite or stop someone who already has access to the project files. Command-line tools rely on local filesystem access and do not ask for this browser password.

## Step 1 Open PowerShell

Press the Windows key, type PowerShell, and open it. You do not need an Administrator window. Enter:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
```

This changes the terminal's working folder. The next commands can now find this project's scripts and Python environment.

## Step 2 Create your private local account once

```powershell
.\.venv\bin\python.exe scripts/account.py --username usman
```

Choose a password containing 15 to 128 characters. A long phrase that you can remember is easier than trying to satisfy arbitrary punctuation rules. Enter the same password twice. Nothing appears while typing; that is intentional hidden entry. Do not paste the password into chat or include it in a command argument. Success says Local account created.

Roman Urdu: Password screen par nazar nahi aayega, lekin type ho raha hota hai. Dono dafa bilkul aik jaisa password likhein. Password kisi ko chat mein na bhejein.

The account is saved in secrets/analyst.json. This file is ignored by Git and must stay private. It holds your username, a salt and a password hash, not the original password. The setup command refuses to overwrite an existing file. There is no browser password-reset feature. If you later need a new account file, stop the server and use a different --file path deliberately, then restart with that --credentials path. Do not delete evidence to recover an account.

For this checkpoint, the owner created the usman account privately. No password is recorded in this guide or in GitHub.

## Step 3 Start the Day 12 server

The prepared Day 12 workspace is http://127.0.0.1:8773/. It uses a separate data/runtime/day12_demo.db created from the Day 11 demonstration. The original Day 11 database is preserved. At preparation time it contained 16 synthetic events, one import, three alerts, one detection run, one investigation case and five actions. Later practice changes those counts.

If the server is not running, enter:

```powershell
.\.venv\bin\python.exe scripts/serve.py --database data/runtime/day12_demo.db --port 8773 --credentials secrets/analyst.json
```

Keep the terminal open. Ctrl+C stops a foreground server. If the port is busy, try opening the existing workspace before starting another process. Missing or malformed credentials prevent startup; the program does not silently run without sign-in.

On a fresh checkout, runtime databases and credentials are absent. Create your own account, start the server, sign in, upload data/samples/day07_all_rules.jsonl and explicitly run detection/save. No private account file or generated database is downloaded from GitHub.

## Step 4 Sign in and investigate

Open the workspace. Enter your username and password, then choose Sign in. The server checks the password and creates a temporary session. You should see Signed in as usman and the existing workspace. A wrong username or password gives the same generic error, so the page does not identify which half was correct.

Use Saved alerts, open R3 and choose Investigate this alert. Its existing case opens without duplicating it. Author fields are filled automatically and are read-only. New notes and decisions submitted from this browser are assigned to the session account by the Python server, even if someone modifies a browser field manually.

The older case history still contains its original labels. Those labels were entered before authentication, and the CLI can still supply its own labels. The stored schema does not mark their origin. Therefore, do not claim that every historical action has authenticated identity or that a username proves a person's real-world identity.

## Step 5 Sign out

Save any work you want to retain, then choose Sign out. The server removes that session and clears the cookie. A page open in another tab may still display data it already loaded, but new API requests using the revoked session fail. Logging out cannot erase information already shown on a screen.

If you try to save from another tab after logout, a sign-in message appears and the draft text stays in that page. Open the sign-in link in a new tab, sign in, copy any unsaved draft you need, then reload the original tab to obtain a fresh request token. A full reload discards page-only drafts. Always review case history before retrying after a lost response.

## Step 6 Understand the new concepts

Authentication means checking that the supplied password matches this local account. Authorization means checking whether a request is allowed to access a resource. Our one-account prototype gives its signed-in account access to the whole local workspace. It does not yet have administrator/read-only roles or separate access per case.

A password hash is a one-way derived value used for comparison. A salt is random data used alongside a password so that two equal passwords do not produce the same stored value. We use Python's established scrypt function with fixed settings: N 131072, r 8, p 1, a 16-byte random salt and a 64-byte result. Hashing deliberately costs memory and processing time, making offline guessing more expensive. It is not a guarantee against weak passwords or a stolen computer.

A session is the server's temporary memory of a successful login. The browser receives a random 256-bit identifier in a cookie, while the server keeps the account and expiry information in memory. The cookie does not contain the password. Signing in again rotates the identifier and invalidates the presented previous session. Restarting the server loses all sessions and requires another sign-in.

HttpOnly means browser JavaScript cannot directly read the session cookie. SameSite Strict restricts when the browser sends it from another site's context. The cookie is host-only with Path / and a name containing the server's port. Cookies are not isolated by port: the naming helps avoid accidental demo collisions, but does not protect against a malicious local service. This HTTP loopback demo does not use the Secure cookie flag; a hosted version needs HTTPS and deployment changes.

CSRF is an attempt to make your browser perform an unwanted action from another website. Each signed-in session has a separate random request token, and writes require the exact local Origin and Host. This is why knowing the address or the login-page token is insufficient to save changes as a signed-in user.

Roman Urdu: Session login ke baad server ki temporary yaad hoti hai. Cookie us session ki pehchan hai. Logout ya expiry ke baad purani pehchan se naya data access nahi hota.

## Step 7 Understand expiry and login limits

A session expires after 15 minutes without a request, or after eight hours regardless of activity. The server checks these limits using a monotonic clock, which measures elapsed time. Typing into a form alone does not contact the server and does not extend the session.

The app allows up to ten live sessions. It admits at most ten password-verification attempts in a rolling minute and temporarily blocks attempts after five failures in that window. Only one password hash is checked at a time; simultaneous attempts receive a retry message. Wait one minute rather than repeatedly clicking. These are bounded local protections, not a complete internet-scale denial-of-service defense. Restart resets these in-memory limits.

## What each new or changed file does

| File | Purpose |
| --- | --- |
| scripts/account.py | Gets a password privately twice, validates it and creates a new account file without overwriting one. |
| src/sentinellab/web/auth.py | Uses scrypt to check passwords; controls login limits, session creation, expiry and revocation. |
| src/sentinellab/web/server.py | Requires account configuration, gates workspace/data requests, handles login/logout, verifies session request tokens and supplies the real session author to case services. |
| src/sentinellab/web/case_api.py | Accepts a server-supplied author override for authenticated browser case actions. |
| src/sentinellab/web/templates/login.html | Contains the sign-in fields, messages and first-time help. |
| src/sentinellab/web/static/auth.js | Sends login/logout requests and fills read-only author fields. |
| src/sentinellab/web/templates/index.html | Shows the signed-in account, sign-out button, expiry recovery and historical-author explanation. |
| src/sentinellab/web/static/app.js | Recognizes a 401 response and displays the sign-in recovery link while keeping the page open. |
| src/sentinellab/web/static/style.css | Styles the login panel and session controls for desktop and narrow displays. |
| tests/integration/test_auth.py | Exercises real HTTP requests and credential/session invariants. |
| tests/integration/test_web.py and test_cases.py | Explicitly isolate the older non-authentication fixtures; production startup has no unauthenticated command-line option. |
| docs/AUTHENTICATION.md | Records the exact access contract, stack decision, limits and references. |
| docs/SentinelLab_Project_Handbook.docx | The cumulative Word explanation through Day 12, including previously missing Days 10 and 11. |
| docs/SENTINELLAB_HANDBOOK.md | The readable text companion to the cumulative handbook. |
| AGENTS.md | Now requires a Word and Markdown handbook update at every future checkpoint. |

The flow is: login form -> bounded JSON request -> request checks -> password verification -> new session cookie -> protected workspace. A case write adds the session check and per-session request token before calling the existing case service. Original evidence and detection rules are unchanged.

## What we tested

The full suite passes 168 tests: the previous 157 plus eleven authentication tests. New coverage includes anonymous read/write denial, wrong credentials, rate limits, malformed login bodies, cookie flags, session rotation/logout, idle/absolute expiry, duplicate cookies, bounded sessions and hashing, salted storage, fail-closed startup and spoofed-author rejection. Existing ingestion, detection, storage and investigation tests still pass.

Browser checks used a separate synthetic QA account and database. We checked wrong-password feedback, successful sign-in, read-only account fields, case creation/note author, logout, another tab's rejected save with retained draft, and desktop/390-pixel login layout. No console errors were observed in the checked login flow. The private user account is separate from QA credentials.

## Common problems and their meaning

- Account file already exists: setup preserved it. Sign in with that account rather than repeatedly creating it.
- No characters appear when entering a terminal password: normal hidden entry.
- Username or password is incorrect: check both values; the app deliberately gives one message.
- Too many attempts or busy: wait a minute and retry once.
- Cannot start: confirm the credential path, database access and whether the selected port is already in use.
- Session ended: sign in again and obtain a new page token. Preserve unsaved drafts before a full reload.
- An older demo still opens without login: it is an older running process. Use the new Day 12 address; old processes do not automatically reload Python code.

## What remains and how to explain this in an interview

A fair description is: I built a local security monitoring prototype with deterministic rules, retained original evidence, investigation history and a single-account browser login using scrypt and expiring server-side sessions. I tested access checks and recovery behavior. Do not call it a production SIEM, tamper-proof forensic system, multi-user platform or proven attack detector.

Day 13 is proposed to add faithful investigation report exports: include source alert identity, evidence references, notes, conclusions and limitations without changing the originals. Broader visual improvements, detection evaluation, clean-setup rehearsal, demo recording and final portfolio/CV material remain planned. Target completion is October 17, 2026.

From now on, every checkpoint must update this Word handbook and its Markdown companion with completed work, easy explanations, file responsibilities, usage steps, tests, limits and next steps. Earlier chapters remain historical and the newest chapter explains current behavior.

## Sources for the access design

OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

OWASP Session Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

## One small learning question

If signing out removes your session, does it delete your saved case notes or original login records? Explain your answer in this chat, in English or Roman Urdu.

# 29 Completion map and continuing this handbook

## What is completed through Day 20

Event validation and normalization reject malformed records and preserve valid originals. SQLite stores imports and events with duplicate and conflict handling. Searches filter stored records and original evidence is available from the browser. The detector implements R1 repeated account failures, R2 failures across accounts and R3 success after preceding failures, with tested grouping and time-window boundaries.

Explicit detection saving records runs and immutable alerts. Repeated checks do not duplicate unchanged alerts. Each alert links to its original evidence. Cases retain notes and reasoned decisions separately from evidence, with a revision number to reject outdated decisions. Browser forms connect these pieces into a review workflow.

Day 12 adds a single local account, scrypt password verification, bounded sign-in attempts, expiring server-side sessions and logout. New browser case actions use the session account. Older and CLI labels remain self-declared; direct database access is outside browser access protection. The system is a learning prototype, not a production monitoring service.

Day 13 adds complete bounded reports containing the saved case, action history, original evidence, alert/rule details and first detection run from one read-only snapshot. Authenticated browser downloads check the displayed revision and preserve drafts on failure. CLI exports stay below reports/generated and never overwrite existing files. JSON and Markdown preserve the same data, with explicit limitations. There are now 184 passing tests; chapter 30 explains how to use and verify exports.

Day 14 organizes the interface into Overview, Events, Detection and Investigations, with a focused original-evidence view and return navigation. Existing DOM forms stay in memory so area changes preserve draft text and filters. Desktop side navigation becomes a compact grid on narrow screens. Case shortcuts lead to notes, history and reports. Keyboard focus and browser Back/Forward are supported; navigation never saves drafts. All 184 regression tests pass alongside focused browser checks.

Day 15 adds a twelve-scenario synthetic evaluation through real import and detection in temporary databases. Intent classification gives TP 3, FP 3, TN 3 and FN 3. All twelve expected rule sets agree; rule agreement differs from attack coverage. Inputs and implementation have SHA-256 fingerprints, reports repeat exactly, and nine added tests bring the total to 193. Rules were not tuned. The corpus is authored with knowledge of the rules, so it does not establish independent or real-world accuracy.

Day 16 verifies source files against the published commit, creates a fresh isolated environment and adds a seven-check authenticated HTTP rehearsal with temporary synthetic account/data and cooperative worker shutdown. Setup now separates existing-user continuation from a fresh install. The final suite passes 194 tests; test transport was corrected for Windows early-rejection races without changing application security checks. Download TLS and interactive terminal-input limitations are explicit. This is one Windows environment, not a new OS or production certification.

Day 17 adds a five-minute demo plan, an honest AI-assisted case study and CV/interview notes, three real synthetic screenshots, a reviewed JSON/Markdown report pair and an evidence map for all fifteen acceptance criteria. A browser-created R3 case is In progress / Suspicious at revision three with three actions and six linked originals. Both HTML badges now say Prototype. All 194 tests pass. This prepares the portfolio; it does not declare the final release complete or claim real-world security accuracy.

Day 18 verifies a GitHub commit ZIP over HTTPS with certificate checks enabled and all 152 source blobs matching. A newly created environment passes 194 tests; seven authenticated workflow checks and the exact evaluation comparison pass. The owner reports successful separate manual account creation. The acceptance review maps all fifteen criteria to evidence and limitations. Only documentation and a safe result record change today. Final presentation practice and a versioned release remain pending; Word visual pagination and local Git metadata restrictions remain explicit.

Day 19 adds the VERSION marker, release-candidate notes and a simple presentation practice guide. All 155 baseline files match GitHub; seven authenticated HTTP rehearsal checks pass again with unchanged application source. The owner demo was started and later restarted after a session interruption, retaining the same account/database. Owner practice is not yet claimed complete. Candidate publication is a pre-release; the final stable release remains pending.

Day 20 provides final version metadata and release notes, an operating handover, project summary, conservative AI-assisted CV wording and a verification record. All 159 candidate baseline files matched; 194 tests pass in 28.258 seconds, seven HTTP rehearsal checks pass and evaluation exactly matches the prior report. Application source, assets, tests and evaluation data are unchanged. The owner correctly prioritised supporting evidence in one practice answer and chose to skip repeated exercises; optional practice does not block release.

## How the pieces work together

First the account gates access to the browser workspace. Then the user imports a synthetic file. The parser validates each line and normalizes supported values. The storage service saves accepted records and retains their originals. The user deliberately runs detection; the rules examine one consistent set of events and the save transaction records alerts and evidence links. The user opens a finding, reads its originals and creates or continues a case. Case notes and decisions append history without rewriting the finding. Signing out ends access to new browser requests, not the saved investigation.

The frontend communicates using local HTTP requests. The backend validates requests and permissions, then calls focused services. SQLite transactions keep related writes together. Unit and integration tests check the behaviors; browser checks confirm that visible controls actually connect to them. The cumulative handbook explains each checkpoint and its remaining limits.

## What remains before the portfolio release

Day 20 completes the bounded v0.1.0 local portfolio milestone. The owner authorised final release after optional practice was clarified as non-blocking. Further learning, interview practice and bug fixes can happen after release; no complete owner presentation assessment is claimed. Word visual pagination and restricted original local Git history remain documented limitations. Public hosting, live collection, multiple roles and stronger evidence integrity are separate future designs. The October 17 completion target is met by this October 5 local release checkpoint.

## Rules for future updates

At each meaningful checkpoint, append the easy-English explanation to the Word file and Markdown companion. Explain the purpose, concepts, actual code changes, every new or changed file's responsibility, operating steps, expected results, tests, troubleshooting, remaining limitations and next planned step. Update this current completion map and test count when behavior changes. Keep historical chapters readable and label them by day so old plans are not confused with present capabilities.

Never include passwords, hashes, session cookies, request tokens or private login records in the handbook or published repository. Demonstrations use synthetic data. A successful code test does not automatically mean the Word layout has been visually checked; report document verification separately.


# 30 Investigation reports and the Day 13 workflow

Checkpoint date: 3 October 2026. Target project completion: 17 October 2026. Today adds reports to the existing project. It does not finish the final release or prove detection accuracy on real attacks.

## 1. What we built today

You can now open a saved investigation and download it as Markdown or JSON. You can also export the same information from PowerShell. A report includes the case, its saved conclusion, complete action history, the saved alert and rule settings, and the original records linked to that alert.

Before today, those details were available in different parts of the application. Now they can travel together in one file. For example, you can review a synthetic case away from the running server or use it in a portfolio demonstration. The report remains a copy: it does not close the case, save your unfinished typing, run detection again, or edit evidence.

Roman Urdu: Report aap ki saved investigation ki copy hai. Is mein notes aur evidence aik jagah milte hain. Report banana account hack honay ka saboot nahi hai.

## 2. The concepts in simple English

**Export** means take saved information out of the program and put it in a file. It does not mean delete the information from the program. You can continue working on the case after exporting.

**Markdown** is a text format with simple headings. Our .md report has clear section headings and code-style blocks containing the exact values. A Markdown viewer can display the headings neatly. Notepad can still open the file as text. We deliberately keep stored notes and evidence inside code blocks so they do not become active HTML, links or new report headings.

**JSON** is a structured format for programs. It uses named fields, objects in curly brackets, and lists in square brackets. For example, "status": "in_progress" tells another program the saved case status. JSON is also readable by people, but the Markdown headings make navigation easier. These are investigation exports; they are separate from your Word learning handbook.

**Snapshot** means a consistent view of saved data at one moment. Imagine taking a photograph of the case and all its records together. If someone adds a note while the report is being prepared, the report must not combine the old case revision with the new history. Every report query uses the same SQLite read transaction. Roman Urdu: Aik report mein mukhtalif waqt ki aadhi aadhi information mix nahi honi chahiye.

**Revision** is the case's change number. Creating a case starts revision 1. Each saved note or decision increases it. If your page shows revision 5 but the database has revision 6, the browser export asks you to refresh and review. That prevents you from unknowingly downloading a different saved version. A concurrent change after the snapshot begins belongs to a later report.

**Serialization** means turning stored values into file text. Newlines and quotation marks may appear as escape sequences such as \n and \" in JSON. These sequences preserve the original values; a JSON reader restores them. We do not edit the underlying original_record string. Database-local identifiers and revisions become decimal strings, such as "9007199254740999", so software using JavaScript does not round large IDs.

**Provenance** means information about where a stored record came from. Each linked original has its first import ID, first line number and import time. These help you trace it within this database. They are not a legal chain of custody or proof that nobody edited the database directly.

**Bounds** are maximum allowed sizes. One export permits up to 1,000 actions and 1,000 linked events, with 8 MiB of selected source values and 16 MiB of encoded output. If a case is too large, the whole export fails with a message. It never silently drops the remaining evidence. A browser page may show only ten actions; the report still includes the full history within these limits.

## 3. What is inside the report

| Section | Meaning and purpose |
| --- | --- |
| Report details | Format version 1.0 and the UTC time the report was prepared. Export time is not the login time. |
| Case and analyst conclusion | Case ID, alert link, title, status, disposition, revision, creation time and latest update time. The conclusion is the analyst's judgment. |
| Saved alert and rule details | Alert ID, rule ID/version, threshold/window, grouping values, event interval, trigger time, reason, and complete saved evidence references. R2 account information is retained. |
| First detection run | When the alert was first saved, the rules/configurations in that run, counts and event/import high-water marks. This is not a list of every later run. |
| Complete action history | Creation, notes and reasoned decisions in revision order, including author labels and before/after state. Earlier notes remain visible after a correction. |
| Linked original evidence | Each event's normalized search values, stored original_record text, evidence position/role and first-import provenance. Unrelated database events are not included. |
| Limitations | Explains uncertainty, private content, historical labels, saved-only scope and lack of signing/encryption/tamper-proof guarantees. |

For the existing R3 sample, five earlier failures and one success explain the finding. A success after failures may mean an attacker guessed a password, but it can also mean the real user corrected a mistake. The report repeats the saved evidence and conclusion. It does not decide which story is true for you.

## 4. Every implementation step and why it matters

First, we compared all 109 published Day 12 files with the local project. They matched. This protected the work already done and established the correct parent for publishing today's changes.

Second, we wrote REPORTS.md before implementing the feature. This defines what is included, the read-only behavior, limits, privacy handling, stale-revision response and verification plan. A written contract makes it possible to test behavior rather than just check that a button exists.

Third, we created reports.py. It validates numeric input and opens the existing database read-only. Version 1 or 2 has no saved cases, so it returns no case without upgrading the database. For version 3, it reads the case, alert, first run, history and linked evidence using one connection and one transaction.

Fourth, the service checks row counts and byte sizes before loading selected data. It checks required links, evidence order and history continuity. A missing original or inconsistent history stops the export. This catches broken relationships; it cannot detect a coordinated edit that changes all related records consistently.

Fifth, we added both renderers. JSON uses reversible escaping and fixed field names. Markdown uses headings written by the application and fences longer than any run of backticks inside the data. Therefore a note containing fake headings or HTML stays report content. No HTML preview or embedded script is generated.

Sixth, we added the HTTP download route. It uses the same existing sign-in and local-request protections as the workspace. The requested case revision must match. Successful replies use attachment filenames containing only numeric case/revision values and a fixed extension. Error replies remain error messages; the browser does not save them as report files.

Seventh, we added Download Markdown and Download JSON to the case detail panel. The text explains which format to choose, what is included, and why drafts are excluded. The controls are unavailable while the case is loading or a case write is in progress. Download errors do not clear the note or reason boxes.

Eighth, we added export_report.py for PowerShell. It uses the same snapshot/renderer and creates a new file exclusively. Existing files cannot be overwritten. Output must stay under the ignored reports/generated directory. If a normal write or close fails after creation, the new incomplete file is removed. Sudden process/power failure can still leave a partial file.

Ninth, we tested the services, HTTP boundary, browser controls and actual downloaded files. We also checked the narrow layout. Finally, we updated the guides and both cumulative handbook formats. Publication uses the connected GitHub service because the existing Windows restriction still prevents synchronizing local Git metadata normally.

## 5. Files added or changed today

| File | Responsibility |
| --- | --- |
| src/sentinellab/reports.py | Reads one bounded snapshot, checks relationships, converts IDs without precision loss, renders JSON/Markdown, and creates safe attachment names. |
| scripts/export_report.py | PowerShell entry point; validates the output location, refuses overwrite and handles file-write failures. |
| src/sentinellab/web/server.py | Adds the authenticated report route, strict format/revision query checks, attachment header and HTTP 409 response. |
| src/sentinellab/web/static/cases.js | Connects buttons to downloads, handles session/errors, shows progress and preserves drafts. |
| src/sentinellab/web/templates/index.html | Adds report guidance/buttons/status text and updates the checkpoint badge. |
| src/sentinellab/web/templates/login.html | Updates the visible checkpoint badge; sign-in behavior is unchanged. |
| tests/integration/test_reports.py | Sixteen tests cover report contents, consistency, limits, hostile text, read-only behavior, CLI output and protected HTTP downloads. |
| docs/REPORTS.md | Exact report contract for future development. |
| docs/DAY_13_GUIDE.md | This easy-English lesson, concepts, operating steps and troubleshooting. |
| README.md and docs/SETUP.md | Update current capabilities, guide links and the Day 13 startup/export examples. |
| docs/WEB.md and docs/ACCEPTANCE_CRITERIA.md | Record the download API and evidence toward AC-10, without claiming the whole release is accepted. |
| docs/PROGRESS.md and docs/NEXT_SESSION.md | Record checks, current demonstration state, remaining limits and the next checkpoint. |
| docs/SENTINELLAB_HANDBOOK.md and docs/SentinelLab_Project_Handbook.docx | Update the current completion map and append the detailed Day 13 explanation, preserving earlier lessons. |

No database table was added today. The existing events, saved_alerts, detection_runs, alert_evidence, investigations and investigation_actions tables already contain the necessary information. reports/generated is an ignored local output directory; its private reports are not project source and are not published.

## 6. Your browser exercise

1. Open the Day 13 address http://127.0.0.1:8774/ while the local server is running. Sign in with your existing usman account. Do not create the account again or send the password in chat.
2. Choose Investigations in the navigation. Open case 1. Read the saved status, conclusion and revision. The prepared continuation copied Day 12's database consistently; it starts with 16 events, one import, three alerts, one run and one case at revision 5. Your later saved work can change these counts.
3. Open the linked alert and evidence if you need to remind yourself what happened. A report should be understood before it is shared.
4. Save a note or decision only if you actually want that change recorded. Text still sitting in an input box is not saved. Simply exporting does not save it.
5. In the case detail panel, choose Download Markdown. Check your browser downloads, usually the Windows Downloads directory. A filename such as sentinellab-case-1-rev-5.md identifies the saved case version.
6. Open the file in a text editor or Markdown viewer. Find the case conclusion, alert reason, notes and original evidence. Notice that all saved actions are included even if the page showed only its first history page.
7. Choose Download JSON and compare the same sections. You do not need to understand every bracket today. Start with case, actions, evidence and limitations.
8. If the page says the case changed, select Refresh selected case, review the new history and retry. Your text boxes remain in this page, but a full browser reload loses unsaved drafts.

Roman Urdu: Pehle saved status aur evidence dekhein. Phir report download karein. Agar case kisi aur jagah update hua ho, refresh karke dobara parhein. Report share karne se pehle private information check karein.

## 7. Start the server only if it is stopped

Open PowerShell. Copy the following commands. If this address already works, leave the running server alone rather than launching another copy.

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/serve.py --database data/runtime/day13_demo.db --port 8774 --credentials secrets/analyst.json
```

The local prepared Day 13 database is separate from previous demos. For continued Day 13 work, keep using day13_demo.db; changes made to old day12_demo.db afterward do not automatically copy across. Port 8775 and day13_qa.db are isolated automated/browser QA data and are not your working demo. The private credential file is reused locally and never published.

## 8. Optional PowerShell exports

The browser is enough for today's exercise. These commands show how the same service works without the browser:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/export_report.py --database data/runtime/day13_demo.db --case-id 1 --format markdown
.\.venv\bin\python.exe scripts/export_report.py --database data/runtime/day13_demo.db --case-id 1 --format json
```

--database selects your saved database, --case-id selects the investigation, and --format selects the output representation. A successful command prints the saved path, number of bytes and revision. The default filename includes the case ID and revision. An unchanged second export with that filename is refused; it will not overwrite the first report.

To deliberately create another copy, choose an unused name under the allowed directory:

```powershell
.\.venv\bin\python.exe scripts/export_report.py --database data/runtime/day13_demo.db --case-id 1 --format json --output reports/generated/my-second-review.json
```

You can add --expected-revision 5 when you specifically want revision 5. If the saved case has changed, the command fails. Without that option, CLI exports the current saved snapshot. CLI access relies on laptop file permissions; it does not ask for your browser password.

## 9. What we checked

The full suite now has 184 passing tests: the previous 168 plus sixteen report tests. Run it with .\.venv\bin\python.exe scripts/run_tests.py. The JavaScript syntax check also passed.

The new tests compare exported fields against stored alert details, history and exact original_record values; check R1/R2/R3 parameters and evidence roles; include history longer than a browser page and a closed/benign conclusion; reject stale/invalid IDs; preserve database bytes; avoid migration of older schemas; preserve very large case IDs; reject oversized and broken records; and refuse invalid formats.

A concurrent-update test uses SQLite WAL mode so another connection can add a note while export is reading. The resulting report keeps the earlier case and earlier history together. Separate tests prove that hostile Markdown/HTML text stays data, CLI cannot overwrite an existing file or write outside its private directory, and a simulated file-close failure removes the new incomplete file.

HTTP tests check authenticated attachments, fixed filenames, no-store/nosniff headers, missing cases, invalid/repeated query parameters, stale revisions, anonymous access, expired sessions and cross-site requests. Browser checks downloaded both files and compared their contents with the saved QA database. Unsaved draft text was excluded and retained in the form. A separate QA update caused the expected refresh message; signing out in another tab blocked a subsequent download and kept the draft. Desktop and 390-pixel layouts showed the controls without page-level horizontal overflow. No browser console errors were observed in the checked flow.

These tests support the local prototype's behavior. They do not establish real-world detection accuracy or public-server security. Word content/structure checks are separate from code tests; the bundled Word renderer remains unavailable because LibreOffice is missing, so page layout is not claimed as visually verified.

## 10. Common problems and their meaning

**There is no download section:** open a case, not only an alert. A report belongs to an investigation. Make sure you opened the Day 13 server address rather than an older process running previous Python code.

**Case changed:** another saved action increased the revision. Refresh the selected case and read the change before exporting again. This is protection against misunderstanding which saved version you are reviewing.

**Session ended:** use the sign-in link. Your unsaved form text remains in the existing tab. Sign-in in another tab restores access, but reload the existing page only after saving/copying any draft you want to keep.

**No file is obvious after clicking:** check the browser's download list and Downloads folder. The success text says a download was requested, not that the operating system definitely saved it. Browser settings may choose another directory or ask where to save. The automated browser download-event helper did not observe our blob download, but the files were present in Downloads and their contents were verified.

**Cannot create report in PowerShell:** the default file may already exist. Choose a new name under reports/generated and ensure its parent directory exists. Do not overwrite earlier evidence reports just to make an error disappear.

**Report exceeds a limit:** nothing was partially exported. The current report feature is deliberately bounded. Preserve the case; a reviewed larger-export design is future work, not a reason to delete evidence.

**Linked records are inconsistent:** preserve the database and investigate the problem. The exporter refuses to pretend the missing information was not needed. Do not manually edit the database to hide the error.

## 11. Remaining limits and next work

Reports contain saved originals and notes without automatic redaction. Review content before sharing. Git ignores reports/generated, reports/private, runtime databases and credentials; browser downloads are outside the repository. A public portfolio should use synthetic demonstrations only. The report is neither digitally signed nor encrypted. Anyone who can directly alter the local database can undermine its history.

Markdown renders the exact values in fenced blocks rather than a designed PDF. The Word handbook teaches how the application works; it is not generated per investigation. Multi-case report bundles, scheduled emailing, PDF report design, live collectors, multiple accounts and public hosting are not implemented by this checkpoint.

The next proposed checkpoint is a focused interface and navigation improvement: make the main workflow easier to follow, reduce scrolling and preserve beginner explanations, authentication and report behavior. After that, we still need held-out scenario evaluation, a fresh-setup rehearsal, release checks, a demonstration, portfolio write-up and honest CV bullets. The deadline remains 17 October.

## 12. One learning question

You type a new note but do not click Save note. Then you download a report. Should that unfinished note appear in the report? Explain why in your own words. You can answer in this chat, in English or Roman Urdu.


# 31 A clearer workspace and the Day 14 workflow

Completed 3 October 2026. Target release: 17 October 2026.

## 1. Today's result

SentinelLab now has four main work areas instead of showing every feature in one long page. The desktop has a side navigation panel. A narrow screen has a compact navigation grid. The selected area is highlighted, the heading explains its purpose, and irrelevant sections are hidden.

This addresses the earlier feedback that the interface was basic and difficult to use. The improvement is functional as well as visual: it is easier to find a case, move to its alert, inspect an original record, return, and download a report. We have not measured usability with a group of users, so this is a tested design improvement rather than a measured productivity claim.

Roman Urdu: Pehle sab cheezein aik lambi screen par theen. Ab har kaam ka alag section hai. Jis kaam ki zaroorat ho, us section ko kholein.

## 2. Where each feature lives

| Area | What you do here |
| --- | --- |
| Overview | See saved event/import counts, read the beginner guide and follow the three starting steps. Continue an existing investigation from the highlighted link. |
| Events | Import a synthetic JSON Lines file, search by account/IP/outcome/time, and open an original record. |
| Detection | Deliberately run the rules, review saved alerts and their explanations, and inspect completed run history. |
| Investigations | Open or create cases, write notes, record decisions with reasons, read action history and download reports. |

Original evidence opens in a focused view. Close evidence takes you back to the area and control that opened it when that control is still available. It is a reading view, not an editing form. The side navigation stays associated with the originating area.

The overview counts are saved-data counts, not a live network monitor. The project still processes imported records and runs detection only when requested. Switching sections does not collect new events, run rules or create cases.

## 3. Concepts explained simply

**Navigation** is the set of controls that helps you move around the application. Clear names tell you where to go. Reports are under Investigations because a report describes a saved case.

**Frontend** means the part you see and interact with. HTML describes the content and forms. CSS controls appearance and layout. JavaScript connects interactions to application behavior. The backend remains responsible for validating requests, sign-in, evidence, rules, case changes and exports.

**DOM** is the browser's representation of the page. Think of it as a tree containing headings, forms, buttons and text boxes. We move the existing sections into containers once, then hide or show the containers. We do not destroy and recreate the forms every time you navigate. This is why a draft can remain in its text box.

**State** means the current values and selections the page remembers: a search filter, selected case, current page of history or unfinished note. State in browser memory is different from information saved in SQLite. Navigation retains the former; clicking Save note creates the latter. Reloading or closing the page still loses unsaved drafts.

Roman Urdu: Section badalne se draft rehta hai, lekin draft save nahi hota. Save note dabane par hi note database mein jata hai. Page reload karne se unsaved text khatam ho sakta hai.

**URL fragment** is the part after # in an address, such as #workspace-cases. It identifies a place in the page. The browser history remembers these moves so Back and Forward can switch areas. We use fixed section IDs, not passwords, evidence text or case contents, in these fragments. A copied evidence fragment cannot reconstruct a selected original after a fresh page load.

**Focus** is the element that keyboard input currently reaches. After navigation, focus moves to the relevant heading or control. Close evidence tries to return focus to the button that opened it. A visible focus outline helps keyboard users see where they are. The Skip to workspace link lets them avoid tabbing through the whole menu.

**Responsive layout** adapts to available width. Desktop side navigation becomes a grid below 1,000 pixels; smaller screens use two columns. Tables retain readable columns and scroll inside their own wrapper. A table's horizontal scrolling is different from the entire page overflowing sideways.

**Separation of responsibilities** means each part has a focused job. workspace.js handles navigation; app.js still handles import/search/originals; alerts.js still handles rules/alerts/runs; cases.js still handles investigations and reports. Styling does not determine whether a request is authorized.

## 4. The steps we took

First, we read the saved contracts and compared all 114 Day 13 project files with the published GitHub version. They matched. We retained the existing evidence, rule, session and report contracts.

Second, we wrote NAVIGATION.md before changing the interface. It specifies the four areas, focused evidence view, draft preservation, browser history, keyboard behavior and verification scope.

Third, we added workspace.js before the other deferred application scripts. It creates containers and moves existing sections into them. Only one workspace is displayed at a time. The original section-level hidden flags still decide whether a selected alert or case has been opened.

Fourth, we implemented link handling and Back/Forward recovery. Navigation updates the selected link and page heading. An unknown or unavailable fragment safely returns to Overview. Reloading a case-detail or evidence fragment does not invent a selected record. You reopen the case from its list.

Fifth, we connected existing programmatic actions to navigation. Opening a case reveals Investigations. Opening its linked alert reveals Detection. Opening an original reveals Evidence before moving focus. Closing the original restores its origin. The actual data requests continue using the existing APIs.

Sixth, we improved the visual hierarchy: a dark header, descriptive navigation, clearer overview cards, a highlighted continuation link, a report card and shortcuts for Write a note, Read history and Download report. Text explanations and Roman Urdu guidance remain available.

Seventh, we extended the exact server asset allowlist for workspace.js and workspace.css. This does not expose arbitrary directories. Authenticated workspace/data access and existing POST protections remain unchanged.

Eighth, we ran the regression suite and JavaScript syntax checks, then exercised navigation with the real browser using synthetic QA data. We verified draft/filter retention, browser history, focus restoration, case writes, duplicate-case handling and actual report content. The user demonstration was kept separate from these QA changes.

Finally, we updated this guide, current status, continuity notes, Word handbook and Markdown companion. GitHub publication uses the connector because the existing local Git metadata restriction remains unresolved.

## 5. Files and responsibilities

| File | Day 14 responsibility |
| --- | --- |
| src/sentinellab/web/static/workspace.js | Groups sections; switches views; manages fragments, Back/Forward, current navigation state and focus; returns from evidence. |
| src/sentinellab/web/static/workspace.css | Desktop side navigation, responsive grid, sticky header, overview cards, report card and visible keyboard focus. |
| src/sentinellab/web/templates/index.html | Loads the new assets; adds navigation, skip link, named workspace heading, continuation link and case shortcuts. |
| src/sentinellab/web/templates/login.html | Updates the checkpoint badge to Day 14. Account behavior is unchanged. |
| src/sentinellab/web/static/app.js | Reveals the evidence workspace and returns to the source when it closes. Import/search logic stays in this file. |
| src/sentinellab/web/static/alerts.js | Reveals Detection when an alert/run selection opens and restores a useful focus target when closing an alert. |
| src/sentinellab/web/static/cases.js | Reveals Investigations before focusing a case or the case-creation form. |
| src/sentinellab/web/server.py | Allows the two new static assets by exact path. |
| tests/integration/test_web.py | Extends the existing static-asset delivery check to cover the new files. |
| docs/NAVIGATION.md | Written navigation and state-preservation contract. |
| docs/DAY_14_GUIDE.md | This lesson, file map, operating steps, verification and limits. |
| README.md, docs/SETUP.md, docs/WEB.md | Current capabilities, address, startup and navigation instructions. |
| docs/PROGRESS.md, docs/NEXT_SESSION.md | Completed checks, demonstration details, remaining work and next checkpoint. |
| docs/SentinelLab_Project_Handbook.docx, docs/SENTINELLAB_HANDBOOK.md | Chapter 31 adds Day 14; front matter and chapter 29 completion map reflect the current system. |

No database schema, rule threshold, report format or account credential was changed. No frontend framework, network font, external image or analytics package was added. Existing backend safeguards still decide whether an action is allowed.

## 6. Your practical exercise

1. Open http://127.0.0.1:8776/ while the Day 14 server is running. Sign in using your existing account privately.
2. Start at Overview. Find the four navigation names and read their small descriptions. Expand the beginner explanation if needed.
3. Open Investigations, then Open case 1. The prepared user copy begins with the existing saved case, not the synthetic QA notes added during testing.
4. Choose Write a note and type a short practice draft. Do not save it yet. Switch to Events, then return to Investigations. The same draft should still be there.
5. Open linked alert and evidence. Detection appears. Open an Original button. Read the stored record and select Close evidence. You should return to its source view.
6. Return to Investigations. Save the note only if you want it permanently recorded in the case. A correction requires another note; original notes are retained.
7. Choose Read history to review saved actions. Choose Download report to reach the report card. Export only includes saved work, as explained on Day 13.
8. Try browser Back and Forward. Notice that these navigate the workspace; they do not undo saved notes or decisions.

Roman Urdu: Back dabane ka matlab pichlay section mein jana hai. Is se saved note delete ya undo nahi hota.

## 7. Startup and saved files

If the address is already working, do not start a second server. If it is stopped, open PowerShell and run:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json
```

The Day 14 demonstration is a consistent SQLite backup of day13_demo.db. At preparation it contained 16 events, one import, three alerts, one run and case 1 at revision 5, in_progress/suspicious with five actions. Later user activity can change this state. Continue using day14_demo.db; separate older databases do not synchronize automatically. QA uses port 8777 and day14_qa.db, with synthetic credentials and observations.

The project remains at C:\Users\Dell\Desktop\Projects\SentinelLab. Browser downloads go to the browser-selected folder. Private CLI reports stay below reports/generated. Credentials, runtime databases and generated reports are excluded from GitHub.

## 8. Verification results

All 184 automated tests pass. The count stays 184 because this checkpoint extends an existing asset test rather than adding tests that merely repeat the markup. JavaScript syntax checks pass. Backend regression tests remain distinct from the interactive navigation checks.

Browser verification covered the four-area layout, case-to-alert-to-original navigation, returning focus to Original #16, preserved draft note/reason, retained search filter, a six-record filtered result, Back/Forward, keyboard Enter navigation, note saving, decision saving and opening an existing case without duplication.

An actual JSON download contained the newly saved QA note at revision 4 and excluded the unsaved reason. Unknown fragments and reloaded evidence fragments returned to Overview. At 390-pixel width the report buttons and text remained usable without page-level horizontal overflow. Signing out in another tab blocked the next export, exposed the sign-in recovery message and preserved the draft. No console errors were observed in the checked flow.

These are focused checks, not a complete accessibility certification or a user study. The Word update is checked for preserved text/tables and new content. Page-layout verification remains unavailable because the bundled LibreOffice renderer is missing; passing code tests does not prove Word pagination quality.

## 9. Troubleshooting

**I still see the long old page:** use port 8776 and check the Day 14 badge. An old Python server does not acquire new backend routes automatically. A fresh server/page is required for the new assets. Copy unsaved text before reloading an older page.

**My draft is not in the report:** section switching retained it in browser memory, but you did not save it. Click Save note if appropriate, then export the new case revision.

**Back did not undo my decision:** browser history changes the displayed location. Saved decisions remain in the case history. Make a reasoned new decision through the form if you need to correct a conclusion.

**An evidence link returned to Overview after reload:** selected record data is not stored in the URL. Open the case or alert again and choose its original. This avoids guessing a private record from a section-only link.

**My session ended:** follow the global sign-in recovery instruction. Keep or copy draft text before a full reload. Hiding a workspace never grants additional access or keeps an expired session valid.

**A table scrolls sideways on a narrow screen:** that is intentional. Its wrapper lets you read complete columns without compressing them into unreadable fragments. The whole page should not require sideways scrolling.

## 10. What comes next

Day 15 is proposed for held-out scenario evaluation: define what counts as a correct finding, test labeled positive and negative scenarios, count false positives and misses honestly, and explain limits. This is different from today's layout checks. After evaluation, remaining release work includes a fresh-setup rehearsal, final fixes, demonstration material, a portfolio case study, accurate CV bullets and final acceptance checks by 17 October.

No automatic live collection, public hosting, multi-user roles or claim of real-world detection accuracy was added today. The prototype is still a local learning and investigation tool.

## 11. One learning question

If you switch from Investigations to Events and then return, your draft stays in its box. Does that mean the draft has been saved to the database? Explain why in English or Roman Urdu in this chat.


# 32 Evaluating detection and the Day 15 workflow

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


# 33 Repeatable setup and the Day 16 workflow

Completed 4 October 2026. Work began on 3 October. The planned completion date remains 17 October, at least two days before 19 October.

## What we achieved

Today we checked whether the project can work without relying on your existing virtual environment, private account or demonstration database. We prepared a separate source folder, created a fresh Python environment, ran the tests and exercised the complete synthetic login-to-report workflow. The unchanged Day 15 source passed 193 tests. After adding today's reusable rehearsal command and regression test, the clean candidate passed 194 tests.

We also repaired the setup documentation. Earlier daily instructions had accumulated in one page, with several ports, database names and old test counts. Those commands were useful at their original checkpoints, but confusing for someone installing the project now. SETUP.md now has one section for continuing your own laptop project and a separate ordered path for a fresh copy.

The main application has no new detection rule, database schema or browser screen today. The value is that another person has a clearer way to install and check it. A portfolio project needs to be understandable and repeatable, as well as working on its owner's machine.

Roman Urdu: Sirf apne laptop par chalna kafi nahi. Doosra banda bhi instructions follow karke project chala sake. Aaj hum ne nayi environment mein check kiya aur setup ke confusing steps saaf kiye.

## A fresh environment in easy English

A Python interpreter is the program that runs Python code. A virtual environment, often called a venv, gives a project its own interpreter entry point and package area. This helps keep project dependencies separate from other work. It does not create another operating system, virtual machine or strong security boundary.

Your existing environment is .venv/bin/python.exe because this laptop uses MSYS2 UCRT Python. Other Windows Python installations commonly use .venv/Scripts/python.exe. A guide that assumes only one layout may fail even when Python is installed correctly. The new setup page checks both locations and assigns the working path to a PowerShell variable named projectPython.

The ampersand before that variable tells PowerShell to run the executable whose path the variable contains. This avoids needing an activation script or changing Windows execution policy. The variable exists only in that terminal; a new terminal needs the selection step again. The fresh environment was made without pip because the application currently needs only Python's standard library.

SQLite stores the project records. hashlib.scrypt supports the existing password hashing. We checked that both are available. The environment reported Python 3.12.7, SQLite 3.46.1, scrypt available and Isolated True. These are observations about this laptop. We did not certify every Python distribution or install Python on a new computer.

## How we obtained the source for the check

The published starting commit was 834a51c1bc170c1c1f6240f72d8d02837594387b. A commit identifies a particular Git history snapshot. Before changing anything, we compared all 137 published file hashes with the local source files. Every file matched.

We attempted to obtain a new archive from GitHub. The Python download failed because its TLS certificate chain could not be verified, and PowerShell's download also failed during the TLS connection. TLS is the protection used for HTTPS connections. We did not turn off certificate checking just to make the download succeed.

Instead, we copied only the source files that matched the published GitHub blob hashes into the separate rehearsal folder. A Git blob hash identifies the stored bytes of a file, including its Git object header. Matching every file establishes that the staged source equals that published snapshot. It does not turn a failed network download into a successful one. The record explicitly says the download and clone path remains unverified.

The clean folder is data/runtime/day16_clean inside the active project. It is ignored by Git and used only for the rehearsal. Your working project remains C:\Users\Dell\Desktop\Projects\SentinelLab. We did not copy your private account, saved cases, original investigation database or existing environment into the clean folder.

## What the new rehearsal command does

The command is scripts/rehearse.py. A rehearsal means a practice run that checks the important steps before presenting the system to someone else. It is also a broad smoke check: if a basic integration is broken, it should fail visibly. It complements the detailed unit and integration tests rather than replacing them.

First, it makes a temporary directory. Inside that directory it creates a new synthetic account and a new database path. The password is generated randomly and held in memory; it is not printed, passed as a command-line argument or saved in Git. Account creation uses the same application service as the existing setup command.

Second, it starts a child Python process. That worker uses the real LocalServer class, real authentication and a port assigned by the operating system on 127.0.0.1. A port is the local number used to reach a service. Choosing an unused port automatically avoids changing your usual demonstration port. Authentication stays enabled throughout the exercise.

Third, it connects over HTTP, which is the same request-and-response protocol used by the browser. It gets the sign-in token, signs in, receives the session cookie and reads the authenticated workspace token. Those tokens stay inside the helper. It checks that an anonymous request is rejected. The helper does not bypass the sign-in checks or write directly into database tables to pretend a workflow succeeded.

Fourth, it uploads the existing synthetic sample, explicitly saves detection, creates a case, saves a note and records a decision. Fifth, it downloads JSON and Markdown reports and checks their contents. Sixth, it stops the worker, starts a new process with the same temporary database and checks persistence. Finally, it logs out, checks access rejection, stops the worker and removes its temporary files.

The command returns JSON containing status, seven completed checks, Python version, environment isolation and limitations. An exit code of zero means the rehearsal passed. An exit code of one means it failed. Read the failure reason and fix the problem before relying on the result. This command does not start your everyday demonstration server permanently.

## The workflow and results step by step

The sample day07_all_rules.jsonl contains sixteen synthetic login events. The first upload inserted sixteen and rejected zero. The second upload inserted zero and identified sixteen duplicates. This confirms that repeated upload does not double the saved evidence. An import record can still be created to record the second attempt; import counts and event counts are different things.

Running all three rules saved three alerts, one for R1, one for R2 and one for R3. Running detection again left three alerts and recorded a second run. A run records the act of checking; an alert records a finding. Repeating an unchanged check should not invent new copies of the same finding.

We selected the R3 alert and created a synthetic case. The case received a note explaining that the alert needs context. It was closed with a suspicious disposition and an explicit reason. Its revision became three: creation, note and decision each advanced the saved history. This was an exercise, not confirmation that a real account was compromised.

The JSON report contained the case at revision three, all three actions and original event text matching the sample. Every action carried the signed-in rehearsal analyst name. The client supplied a different author label, but the server correctly used the session identity. The Markdown endpoint returned an attachment with the report heading. Reports include saved work, not browser drafts.

After restarting the worker, the case and three alerts still existed. The previous session was rejected and a new sign-in worked. This demonstrates the difference between persistence and session memory. SQLite data survives process restart. In-memory authentication sessions do not. Logout also caused the protected summary request to be rejected.

Roman Urdu: Server band hone se saved records delete nahi hote. Lekin login session khatam ho jata hai. Dobara server chalane par sign in karein; pehle se saved case phir milna chahiye.

## Why shutdown needed attention on Windows

The first helper experiment used ordinary process termination. Windows virtual environments can involve a launcher process and a child interpreter, and forced tree termination was unreliable in this restricted session. A rehearsal must not report success while silently leaving a test server running.

The final helper uses cooperative shutdown. The parent owns a private input pipe to the worker. Closing that pipe tells the worker that no more input will arrive. The worker then calls server.shutdown, joins its serving thread and closes the server before exiting. The parent waits for a clean exit before claiming cleanup. There is no public HTTP shutdown route and no taskkill command in the final helper.

Normal completion and Python exceptions go through cleanup. If shutdown times out, the helper reports failure. A forced operating-system failure, process termination or machine crash can still leave temporary files; this is not a promise that cleanup succeeds after every possible failure. The earlier trial terminal processes ended with the app/session restart. The final workers were observed to finish their cooperative exits.

## What we could not verify today

The interactive account command reached its first hidden-password prompt. However, automatic approval review blocked sending terminal input because sandbox_approval is disabled in this session. We did not ask you to reveal a password. The final rehearsal exercises account creation through the actual account service with a random test password, so hidden keyboard entry remains a separate manual check.

The source download encountered certificate errors. The source itself was verified against published hashes, but a fresh network download or clone was not completed. No certificate setting was weakened. A person following the new guide can use Git or a downloaded ZIP once their machine's trust/network setup permits it.

This is a fresh virtual environment on the same Windows laptop, not a fresh operating system. We did not run a new visual browser audit because today's application HTML, CSS and JavaScript were unchanged. Real HTTP requests tested the workflow, but they cannot prove button layout, keyboard focus or screen-reader usability. Earlier browser checks remain historical evidence.

We also keep the existing Word rendering limitation separate. The cumulative Word content is updated and checked for preservation and structure, but the bundled renderer requires a LibreOffice executable that has been unavailable. A test count is not proof that Word pages look right. The final status reports the renderer result explicitly.

## Every file changed today

scripts/rehearse.py is the new reusable workflow command. It contains the worker startup/shutdown, HTTP helpers, synthetic exercise, result checks and cleanup. tests/integration/test_rehearsal.py runs that command from another working directory, checks successful JSON output and confirms it did not create files in that calling directory. Running outside the repository checks that the helper locates its source and sample from its own file path.

tests/integration/test_auth.py received a focused correction after Windows error 10053 interrupted a header-rejection check. The header-only cases now send an empty body; malformed-body cases remain separate. This tests the expected rejection without racing an early connection close against a discarded upload. The security requirements and application code are unchanged. The corrected check passed twenty targeted runs, and the full suite result was checked separately.

The same transport error subsequently appeared in an anonymous-request check. tests/integration/test_web.py now buffers each complete finite test request before sending it, instead of sending headers and body separately. This shared test client does not retry writes or change expected response statuses. After this adjustment, the complete clean-environment suite passed all 194 tests. This transport correction is limited to test infrastructure.

docs/SETUP.md replaces the accumulated historical startup sequence with current instructions for both existing and fresh users. docs/SETUP_REHEARSAL.md is the technical evidence record: source commit, environment, checks, limitations and fixes. docs/DAY_16_GUIDE.md is this plain-English lesson.

README.md reports the current checkpoint and links the setup/rehearsal material. docs/ACCEPTANCE_CRITERIA.md adds today's evidence without claiming that the whole release is finished. docs/PROGRESS.md records what happened. docs/NEXT_SESSION.md gives the next checkpoint and the current demonstration details.

docs/SentinelLab_Project_Handbook.docx and docs/SENTINELLAB_HANDBOOK.md receive chapter 33 and a refreshed current completion map. Earlier chapters remain as historical explanations. Temporary source folders, test databases, account files and authoring helpers are not published. No detection-engine source, authentication contract, existing case schema or event format changed today.

## Your commands and your part

For your existing laptop project, open PowerShell and run:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/rehearse.py
$LASTEXITCODE
```

Expect status passed, seven checks and exit code zero. You do not need to create another private account or import records into your current database for this command. It takes care of its own synthetic data and temporary account. Your task is to read each check and understand why it matters, rather than just looking for the word passed.

To run the full test suite, use .\.venv\bin\python.exe scripts/run_tests.py. For a fresh installation, follow docs/SETUP.md in order. Do not apply its clone or account-creation steps over your existing project. If the command cannot find Python, check the bin versus Scripts location as the guide explains.

For your ordinary interface, continue using day14_demo.db, port 8776 and your existing account. Start it only when stopped using the existing-project section of SETUP.md. Keep the terminal open while using it. The rehearsal command starts and closes temporary servers; it does not leave the everyday interface running.

When presenting the project, you can say: I verified the source files against a published commit, created a clean Python environment and built an isolated authenticated workflow rehearsal that checks deduplication, case history, reports and restart persistence. Also state the boundaries: the network download and interactive hidden entry were not reverified, and this was one Windows environment.

## What comes next

Day 17 is planned for the portfolio demonstration and release preparation: create a clear synthetic story, decide the presentation sequence, gather representative screenshots, draft a truthful case study and CV bullets, and map completed work against final acceptance. Any remaining release blockers should be recorded and handled before claiming the project complete. The target remains 17 October.

Your one practice question is: after restarting SentinelLab with the same database, should your saved case disappear, or should only your login session need renewal? Explain why in this chat. A short answer is enough.


# 34 Portfolio presentation and the Day 17 workflow

Completed 4 October 2026. The target completion date is still 17 October. Today prepares the portfolio presentation; it does not mark the whole release complete.

## What we made today

We created a portfolio folder with a five-minute demonstration script, a project case study, CV wording, interview practice, three real application screenshots and two synthetic example reports. We also mapped the fifteen acceptance criteria to existing evidence and remaining checks. These materials help another person understand what the project does and help you explain it confidently without making claims the evidence cannot support.

Before editing, all 141 files in the Day 16 published snapshot matched the laptop source. We used a separate demo database and synthetic analyst account. Your everyday day14_demo.db and private account were not used for these screenshots or reports. The full suite passed 194 tests after today's small interface-label change. No new detection algorithm, database schema or authentication behavior was introduced.

Roman Urdu: Aaj hum ne project ko dikhane aur samjhane ke liye material banaya. Sirf screen dikhana nahi, balkay har claim ke saath evidence aur limitations batana zaroori hai.

## Why a portfolio needs a story

A portfolio is evidence of work you can explain. A large number of files is not enough by itself. A reviewer needs a clear problem, a design that addresses it, a demonstration and an honest discussion of limits. SentinelLab's story is how login records become an explained finding, then a reasoned investigation and a saved report.

The demonstration follows one R3 finding from beginning to end. This is easier to understand than clicking every feature without a purpose. We show the other rules and duplicate handling briefly, then spend most of the time explaining evidence and the decision. A useful demonstration answers what happened, why the rule matched, what is still unknown and what the analyst would do next.

The case study gives a more detailed written account. It separates implemented behavior from possible future work. The CV entry is shorter again: it names the actual technology and gives a few demonstrable outcomes. Neither should claim a real security incident, production deployment or measured business benefit that did not happen.

## The synthetic story used today

We reused data/samples/day07_all_rules.jsonl instead of inventing a new format. It contains sixteen fictional login events. Ten usernames have failures from 192.0.2.70. Another account, lab_user, has five failures from 192.0.2.71 between 09:20 and 09:24 UTC on 29 September 2026, followed by success at 09:24:30 UTC.

R2 describes failures against ten distinct accounts from the first IP. R1 describes the five failures for lab_user. R3 describes the later successful login after those failures. Three alerts do not necessarily mean three independent attackers or incidents; rules can describe overlapping activity.

The same sample was imported twice into the isolated database. The first import inserted sixteen events. The second inserted zero and reported sixteen duplicates. The database therefore showed sixteen saved events and two completed imports. This is a useful point for a demonstration: an import is an action, while an event is a saved record.

Detection was saved twice. Three alerts remained, and two runs were recorded. The second run found the existing alerts. This explains a second important distinction: keeping a history of checks is different from duplicating a finding.

These timestamps describe when the fictional login events happened. Import, run and case timestamps describe when we processed or investigated the sample. The application displays UTC. Do not describe a September event as a new attack on today's date just because it was imported today.

## What we did in the browser

We signed in with a synthetic portfolio_analyst account in the isolated demo on port 8778. Overview displayed the saved counts. Detection showed the three alerts and two runs. We opened R3 and read its explanation, account, IP, threshold, first event time, trigger time and linked records.

We inspected the success record through Original #16. It showed outcome success, the expected account/IP/time, the original accepted JSON record and first-import location. The local row number is a convenient link in this database; it is not a globally meaningful event identity. In another database the Original button may have a different row number.

Next we used Investigate this alert to create Case 1 titled Synthetic review: success after five failures. We saved a note containing only observations and a benign alternative: a legitimate owner might have corrected a password. We then chose In progress and Suspicious and saved a reason requesting account-owner confirmation and additional authentication context.

The case reached revision three: creation, note and decision. The history retained all three actions with the signed-in analyst name. We did not choose Confirmed compromise. Nothing in these sample records proves who controlled the account or whether the successful login was unauthorized.

Roman Urdu: Paanch failures ke baad success nazar aayi. Yeh suspicious pattern hai, lekin user ne apna password theek bhi kiya ho sakta hai. Is liye case ko investigate karna hai, hacking ka final faisla foran nahi karna.

## Screenshots and what they prove

The three published screenshots show the actual application using synthetic data. They were not generated as mockups. The Overview capture shows the event/import counts and beginner workflow. The R3 capture shows the explanation and rule facts. The case capture shows its title, In progress / Suspicious state, revision and report area.

We reviewed the captured images and adjusted the scroll position so important headings are visible below the fixed header. They are viewport excerpts; some tables and controls continue below the bottom of the picture. A screenshot cannot establish every stored record, every route's security or complete accessibility. The full reports and automated checks provide different types of evidence.

The header previously said LOCAL LAB and DAY 14. That old lesson number was confusing in a current presentation, so both the workspace and sign-in templates now say LOCAL LAB and PROTOTYPE. This is a small text correction. It does not imply a new product version or production readiness.

No private account file, password, session token or user investigation appears in the portfolio material. Synthetic screenshots may contain the test account name, example IP addresses and timestamps. Those values are part of the fictional demonstration, not evidence of a real person's activity.

## Reviewing the two example reports

We exported Case 1 using the existing command-line report tool with expected revision three. Exports initially went to the ignored reports/generated directory. We checked their contents before copying the synthetic examples into the public portfolio folder.

The JSON report contains the case, saved R3 alert, first detection run, three case actions, six linked original records and limitations. Every original_record matched a line in the known synthetic sample. All actions had the browser session's portfolio_analyst author. The Markdown report contained the same saved sections and values. The export timestamps differ because the two exports were produced separately; the case, action and evidence data agree.

Markdown is readable text with headings and fenced JSON sections. JSON is structured data that software can parse. Both represent saved work at an export snapshot. Downloading a report does not save an unfinished draft, confirm compromise or close a case. Real reports may contain private information, which is why normal generated reports remain ignored by Git.

Publishing these reviewed fictional examples is a specific portfolio choice. It does not change the rule that future private reports must remain outside the repository. There is no automatic redaction, signature, encryption or forensic chain-of-custody guarantee.

## How to use the demonstration script

Open docs/portfolio/DEMO_SCRIPT.md. It divides approximately five minutes into problem, import, detection, evidence, investigation and reporting. The times are a speaking plan, not measured application performance. Practice slowly first, then shorten your explanation once you understand the transitions.

For a fresh presentation, follow SETUP.md, start a new database filename with your existing private account and use an available loopback port. Do not overwrite a database to reset a demonstration. If you use today's prepared demo, explain that the two imports and two runs were already completed. Further repetitions change history counts while unchanged events and alerts remain deduplicated.

Sign in privately before recording. Show the original success record, say why it matched R3, describe the benign alternative and show the saved decision. Finish with an export and one limitation. If a browser download is unavailable, show the included example report and identify it as a previously exported synthetic example.

We did not record a video, publish a public website or submit a job application today. The materials are ready for you to practice and adapt. A live browser session can expire after inactivity; saved cases persist, but you may need to sign in again.

## Case study and CV ownership

The case study explains the problem, architecture, transaction/evidence choices, three rules, investigation workflow, evaluation and tradeoffs. It explicitly identifies the project as AI-assisted. Code, tests, documentation and debugging received substantial assistance. You should not claim independent authorship of every line or professional incident-response experience from this lab.

The suggested CV entry uses actual technologies: Python, SQLite, HTML, CSS, JavaScript and unittest. It mentions three explainable rules, deduplicated storage, investigation history, exports and synthetic verification. There are no invented incident counts, cost savings, performance improvements or enterprise deployment claims.

If your involvement is still mainly guided learning, use the conservative wording supplied in CV_AND_INTERVIEW.md. Before claiming a skill, practice explaining the relevant code and showing the feature. Honest ownership is compatible with AI assistance; understanding is the part you must be able to demonstrate yourself.

The interview section asks about duplicate identity, R1/R3 overlap, uncertainty, persistence, stale revisions, report limits, tests and AI assistance. Work through one question at a time. You do not need complicated language to give a strong explanation.

## Evaluation claims that must stay separate

The Day 15 authored corpus has twelve scenarios, with TP, FP, TN and FN each three. Its labels were defined before running the detector, but its author knew the rules. It is separate from earlier implementation fixtures, not an independent blinded evaluation. It is now a reusable benchmark.

All twelve scenarios produced their expected rule sets. That shows agreement with written behavior on those cases; it does not mean the system caught every malicious story. The 50 percent figures belong only to this deliberately balanced synthetic set. Never turn them into a real-world accuracy claim or hide the false positives and misses.

Passing 194 tests is useful evidence for checked behavior. It is not proof of universal security. Slow guessing, distributed attempts, stolen-password success, missing logs and harmless mistakes remain important limitations of these simple rules.

## Every new or changed file

docs/portfolio/README.md is the gallery and starting index. DEMO_SCRIPT.md is the ordered speaking and operating guide. CASE_STUDY.md is the written technical story. CV_AND_INTERVIEW.md provides truthful project wording and practice prompts. sample-report.json and sample-report.md are reviewed real exports containing only synthetic data.

The screenshots directory contains 01-overview.jpg, 02-alert.jpg and 03-case.jpg. They are original browser captures. docs/RELEASE_READINESS.md maps AC-01 through AC-15 to evidence and qualifications, followed by open verification items. docs/DAY_17_GUIDE.md is this lesson.

src/sentinellab/web/templates/index.html and login.html replace the obsolete day badge with Prototype. README.md now describes the implemented project and actual stack rather than calling the whole platform merely planned. It links the portfolio material. docs/ACCEPTANCE_CRITERIA.md, PROGRESS.md and NEXT_SESSION.md record evidence, continuity and remaining work.

The cumulative Word and Markdown handbooks receive chapter 34 and current-map updates while keeping earlier lessons. Helper scripts used to prepare and verify the demo stay outside the published project. The isolated runtime database/account, server logs, environment and unreviewed generated reports are excluded from GitHub.

## What remains before completion

The readiness map covers all fifteen criteria without marking the final release complete. Existing component tests and demonstrations support the implemented features. Remaining checks include an authorized working source-download path, private manual hidden-password entry, Word rendering when its supported dependency is available, the final acceptance sequence and a versioned release checkpoint.

The Day 16 source download had certificate errors; hash-verified local source was used for that rehearsal. Hidden terminal input was blocked by automatic approval review. The account service and sign-in workflow were tested, but those specific external steps remain unverified. The bundled Word renderer still has a missing LibreOffice limitation; content preservation is checked separately from page layout.

Day 18 is planned for final acceptance preparation and closing or clearly documenting these remaining items. The completion target remains 17 October. Optional new features should not distract from making the current project reproducible and explainable.

Your one practice question is: what extra information would you request before changing this synthetic case from Suspicious to Confirmed compromise? Give one example in this chat. There is no need to claim that the sample itself supplies that proof.


# 35 Acceptance verification and the Day 18 workflow

Completed 4 October 2026. The project completion target remains 17 October. Today we checked the existing system from downloaded source, recorded the results and prepared the remaining release work. We did not add a new detection rule or change application behavior.

## What today achieved

The existing project passed all 194 automated tests. We then downloaded the exact published GitHub source, checked every one of its 152 file hashes, created a fresh Python environment and ran the tests there. That downloaded copy also passed all 194 tests. A separate rehearsal exercised the real authenticated HTTP workflow and passed its seven checks. The synthetic evaluation reproduced the previous report exactly, including its source fingerprints.

You also ran the account command in your own PowerShell window and reported that the account was created. The separate ignored test file exists. We did not read its password hash or ask for your password. This is a user-reported manual command result, separate from the automated account-service checks. The assistant did not watch your keyboard or directly observe whether characters were visible.

The main result is stronger evidence that another source copy can run the documented workflow. Final release preparation still includes presentation practice and the unresolved Word page-layout check. The original laptop copy also retains its known local Git-history restriction. We have not created a final version tag or claimed production readiness.

Roman Urdu: Aaj hum ne GitHub se project ki nayi copy download karke check ki. Maqsad yeh tha ke project sirf purani working folder mein nahi, nayi environment mein bhi sahi chale. Tests pass hona achha evidence hai, lekin har mumkin problem khatam honay ki guarantee nahi.

## Acceptance and regression in simple English

An acceptance criterion is a promise about what the project should do. For example, importing the same event twice should not save two copies. An acceptance review connects each promise to a test, demonstration or other evidence. It also states what that evidence cannot prove. The project has fifteen criteria, identified as AC-01 through AC-15.

A regression is something that used to work and stops working after a change. Regression tests help find that problem. The full suite checks parsing, storage, rules, cases, reports and access controls. Running 194 tests does not mean the system detects 194 kinds of attack. Some tests check invalid input, a boundary time, a duplicate or an error path.

An end-to-end rehearsal checks several connected parts together. Our helper starts a real server process, signs in and sends real HTTP requests. It then imports records, runs detection, changes a case and exports reports. This helps catch integration problems that a small isolated test might miss. It does not replace a person checking how the interface feels.

## Step 1 Identify exactly which source we are checking

We first read the project instructions, progress, setup guide and release-readiness list. We compared the laptop files with GitHub commit cbc94443ead66ca2268dab49968b255e463cf00e. All 152 published files matched before any Day 18 edits. That commit is the Day 17 baseline. Day 18 adds documentation and an acceptance record; application source, assets, tests and rule data remain unchanged.

A commit identifies a saved repository snapshot. A file hash is a compact fingerprint calculated from its bytes. We used Git blob hashes, which include Git's file header as well as the file bytes. Matching these hashes helps establish that we tested the intended published source. It does not establish that the source is free of bugs, and it is not a digital signature from an independent reviewer.

This comparison matters because the original laptop Git HEAD and index remain behind under existing Windows access restrictions. We do not reset those files, change their access controls or pretend that local history is synchronized. Publication uses the connected GitHub service and a comparison of every published file. The new source ZIP has no Git history; it is a source snapshot only.

## Step 2 Download the source safely

Earlier attempts with the project's Python and PowerShell encountered certificate errors. Today the bundled document/workspace Python downloaded the exact commit ZIP from GitHub using urllib with the default SSL context. Certificate verification stayed enabled. The archive was 822122 bytes. Its SHA-256 fingerprint is recorded in reports/examples/day18_acceptance.json.

TLS certificate checking helps the client establish a trusted HTTPS connection. Turning it off would remove that check, so we did not use that workaround. A successful request through a different configured runtime does not prove that the earlier runtime's certificate configuration has been repaired. We can accurately say that an authorized verified download path now worked. A fresh git clone was not tested.

Before extracting, we checked the expected archive prefix, file names, sizes, absence of parent-directory traversal and exact membership in the published inventory. Every extracted file matched its expected Git blob hash. We extracted only those 152 files into the separate ignored data/runtime/day18_clean folder. No private credentials, database, old virtual environment or generated report was copied from the everyday project.

Roman Urdu: ZIP file ko seedha har jagah extract nahi kiya. Pehle file names aur fingerprints check kiye, phir alag test folder mein rakha. Aap ka asal account aur saved investigations apni jagah par rahe.

## Step 3 Create a fresh environment and run the tests

We created a new virtual environment without pip inside the downloaded copy. A virtual environment gives this copy its own interpreter environment. SentinelLab uses the Python standard library, so we did not install third-party application packages. This test used Windows, MSYS2 UCRT Python 3.12.7 and SQLite 3.46.1 on the same laptop. It is not a test of a different operating system or a machine with no Python installed.

The existing workspace ran scripts/run_tests.py and passed 194 tests in 35.288 seconds. The downloaded fresh environment passed 194 tests in 32.519 seconds. These durations describe these two runs; they are not a speed benchmark or a response-time promise. No application fix was needed during this checkpoint.

The suite includes failure paths as well as happy paths. For example, it checks identity conflicts, stale case revisions, expired sessions, missing evidence, report limits and malformed requests. A passing error-path test means the application rejected that tested situation as intended. It does not mean arbitrary hostile input is safe under every future deployment.

## Step 4 Rehearse the complete saved workflow

We ran scripts/rehearse.py inside the freshly downloaded environment. It created a temporary synthetic account through the actual account service and started a separate server process. The helper authenticated, obtained the session protections and used the real routes. There is no command-line authentication bypass in the user-facing server.

The first sample import saved sixteen events. The second import added zero events because all sixteen were duplicates. Detection saved three findings, one for each rule. A second run recorded another check without duplicating the findings. This demonstrates why event count, import count, alert count and detection-run count are different quantities.

The helper created an R3 case, saved a session-authored note and decision, and verified complete JSON and Markdown reports. It checked saved evidence rather than relying on a screenshot. It stopped and restarted the server with the same temporary database, checked that the saved case survived and checked that old sessions were rejected. Logout also removed access. Temporary test accounts, databases and files were removed after the rehearsal.

All seven reported checks passed. These are grouped workflow checks, not seven additional tests added to the suite. The automated helper uses HTTP rather than clicking a browser. The last actual browser demonstration and screenshots are from Day 17. No new browser usability or accessibility claim is made today.

## Step 5 Repeat the evaluation honestly

We ran scripts/evaluate.py on the twelve authored scenarios. The resulting JSON matched the published Day 15 report as structured data, including input and application-source fingerprints. This is expected because the rules and evaluated application source have not changed. Terminal redirection can change text encoding or line endings; comparing parsed JSON avoids mistaking that for a different result.

There were three true positives, three false positives, three true negatives and three false negatives. Each reported classification metric was 50 percent for this deliberately balanced toy corpus. All twelve expected rule sets agreed. Rule agreement answers whether the implementation behaves as specified. Intent classification asks whether the alert matched the story's benign or suspicious label. Those are different questions.

These scenarios were authored with knowledge of the rules. They are now a repeatable regression benchmark, not a blinded independent evaluation. We did not change the labels or tune thresholds to improve the score. We cannot use this result to claim real-world attack detection accuracy.

## Step 6 Complete the manual account command

You needed help opening PowerShell. The instructions were to open ordinary Windows PowerShell, change to the Desktop project folder, then run the existing scripts/account.py with username day18_check and an explicit separate file under data/runtime. Administrator mode and execution-policy changes were unnecessary.

The program requests the same 15-to-128-character password twice. It uses hidden entry and refuses the unsafe redirected-input fallback. It does not put the password in command arguments. You replied that the account was created; we confirmed only that the separate file exists. The password and stored hash were not read or published. The normal account in secrets/analyst.json remains the everyday account.

This test file is not automatically selected by the normal server command. Creating it does not change the username used by your existing demonstration. Keep it private; do not upload it or paste its contents into chat. If the command reports an existing file on a later attempt, it preserves the existing file instead of overwriting it. There is no reason to recreate the everyday account at each checkpoint.

## Step 7 Review what will be published

We reviewed the 152 published baseline paths and the explicit Day 18 additions. Runtime folders, credentials, private data, generated private reports, virtual environments, databases and Word lock files are outside the publication allowlist. An ignored file can still be published by a careless manual upload, so .gitignore alone is not the complete check. We publish reviewed paths deliberately.

The six original records in the portfolio JSON report were rechecked against the known synthetic sample. They all matched. Those reviewed fictional examples remain suitable for the demonstration. That does not authorize publishing a later report containing real login records or personal notes. Report export has no automatic redaction.

The download ZIP and fresh rehearsal environment stay in ignored data/runtime. The test logs and editing helpers are local verification materials, not application dependencies. The public acceptance JSON contains only safe results, source identity and limitations. A targeted publication review is not a guarantee that any arbitrary future file contains no secret.

## Files changed today and why

- docs/DAY_18_GUIDE.md is this detailed lesson, including the purpose, method, results, concepts and remaining work.
- docs/FINAL_ACCEPTANCE.md is the concise technical review record. It links each acceptance criterion to the relevant automated evidence and states the release decision.
- reports/examples/day18_acceptance.json stores the source identity, acquisition method, environment, test results, evaluation comparison and qualifications in machine-readable form.
- docs/RELEASE_READINESS.md records the current state of the checklist, including the successful source download and your manual account result.
- docs/SETUP.md explains the now-tested download route while preserving the earlier TLS qualification and normal account instructions.
- README.md points a new reviewer to the latest acceptance evidence and gives the correct completion status.
- docs/ACCEPTANCE_CRITERIA.md adds Day 18 evidence above the preserved earlier checkpoint records.
- docs/PROGRESS.md and docs/NEXT_SESSION.md record completed work and the next bounded checkpoint.
- docs/SentinelLab_Project_Handbook.docx and docs/SENTINELLAB_HANDBOOK.md receive chapter 35, an updated introduction and the current chapter 29 completion map. Earlier explanations remain available.

No source module, rule, database schema, interface asset or test file changed today. We used existing verification tools rather than adding a new feature simply to increase the file count.

## Reading the final acceptance decision

The acceptance checks pass with documented qualifications. The downloaded source now reproduces the tested workflow. We still distinguish that result from a final versioned release. The fifteen criteria have evidence, but evidence has a scope: local authentication is not public hosting, saved history is not tamper-proof custody and a rule match is not proof of compromise.

The cumulative Word file has content and structure checks. The supported renderer was attempted after the update and failed because LibreOffice soffice.exe was not available in the bundled runtime path. Visual pagination remains unverified. The Markdown companion remains readable. A text-preservation check cannot detect every clipped line, awkward page break or table-layout problem in Word.

Before the final release, we should complete your presentation practice, decide how to handle any remaining document-layout limitation and record a deliberate versioned release checkpoint. We should not add optional live collection, multiple roles or public hosting just before the deadline. Those are separate future projects with additional design and security requirements.

## Your next learning step

Read the current setup guide, then walk through the five-minute demo script using synthetic data. Explain the chain in your own words: a login record is validated and stored; a rule identifies a pattern; an analyst investigates the linked evidence; a report captures saved work. Explain one false alarm and one missed scenario. Be clear about the substantial AI assistance and the parts you personally understand and operate.

For today's single practice question: give one example of additional evidence you would seek before changing an R3 case from Suspicious to Confirmed compromise. You can answer in simple English or Roman Urdu in this chat. The five failures followed by success are already known; the question asks what else you would investigate.

Roman Urdu: Sirf alert ki wajah se hacking confirm nahi hoti. Hamein mazeed maloomat chahiye jo bataye ke successful login waqai ghair-ijazati tha. Aap ek example dein; phir hum us par baat karenge.


# 36 Release preparation and the Day 19 workflow

4 October 2026. Today prepares SentinelLab version 0.1.0-rc.1 and starts presentation practice. The completion deadline remains 17 October. This is a release candidate for the local learning prototype; it is not a final stable release or a production security product.

## What a release means

A Git commit records a snapshot of project files. A tag gives a snapshot a memorable version name. A GitHub release adds a page describing that version and offering source downloads. The tag should identify the intended reviewed commit. Later corrections should use a new version instead of silently moving the old tag.

The candidate name is v0.1.0-rc.1. The rc part means release candidate and the final 1 means the first candidate for this version. It is a way to make reviewable progress while keeping unfinished presentation practice and document-layout verification visible. A version number does not mean that more attack techniques are detected or that rule thresholds changed.

The new VERSION file contains 0.1.0-rc.1. It is release metadata. It is not imported by the detector and does not change the existing rule versions or SQLite schema. GitHub should label the candidate Pre-release so a visitor can distinguish it from a finished stable release.

Roman Urdu: Version name ek nishan hai jo batata hai hum project ki kis saved copy ki baat kar rahe hain. Release candidate final review wali copy hoti hai. Is naam se software automatically production-ready nahi ban jata.

## Step 1 Check the starting point

We read the project instructions, latest progress, next-session plan and release-readiness record. All 155 local published files matched GitHub commit e3fb62ceca8e8f7d25fdd1b95c31b9c9a5a1b908 before editing. This prevents unrelated or unreviewed local changes from being mixed into the checkpoint.

The original laptop Git HEAD and index remain behind because of existing access restrictions. We preserve those restrictions and publish through the connected GitHub service. We compare file hashes and the published ref after publication. That checks file content, not synchronization of the restricted original local Git history.

The GitHub connection can create file blobs, trees and commits, but does not expose a release-creation action. The existing signed-in GitHub browser provides the release form. We inspected that form, including its tag, target, title, notes and Pre-release option. The candidate is prepared from an explicit reviewed source snapshot, not from a guessed or unrelated branch.

## Step 2 Check that the workflow still runs

We reran scripts/rehearse.py using the existing project environment. All seven grouped checks passed. It created a temporary account, ran a separate authenticated server, imported and reimported the sample, saved and repeated detection, created an investigation, checked both report formats, restarted the server, checked session rejection/logout and cleaned up its temporary files.

The most recent full suite remains the Day 18 run: 194 tests passed in the existing workspace and 194 in a newly created environment from verified downloaded source. Day 19 changes release metadata and documents only; application modules, browser assets, tests and evaluation inputs remain unchanged. We do not represent the earlier full-suite run as a new Day 19 run. A final hash comparison checks this unchanged-code claim.

This distinction is useful in an interview. Say exactly what was tested and when. Repeating a number without describing its scope can mislead a reviewer. Seven workflow checks are not seven new attack detectors, and 194 passing tests do not prove perfect security.

## Step 3 Open the owner's existing demonstration

We checked the local demo port and started the existing server with data/runtime/day14_demo.db and secrets/analyst.json. It runs on http://127.0.0.1:8776/. The returned page was the normal sign-in page. The private account content was not read. The owner signs in privately with the usual account.

Starting the server does not import another sample or change an investigation. The database and private account remain the everyday ones. Earlier demonstration databases are independent copies and do not synchronize. A restart invalidates old sessions, so seeing the sign-in screen is expected. Saved data lives in SQLite; the session lives in server memory.

The server stopped during an app/session restart. After the owner asked to run the project, it was restarted with the same database/account and HTTP 200 was verified again. The browser remained on an internal connection-error page; its security policy blocked automated refresh, so the owner was asked to press Ctrl+R. The new server process identifier was recorded in ignored data/runtime/day19_server.pid. A stored process number may become stale after restart, so future work must verify the process rather than stopping an unrelated program. No unrelated service was stopped.

## Step 4 Practise the story in simple language

Start with the purpose: SentinelLab helps turn imported login records into explained alerts, investigation notes and reports. It is a local, AI-assisted learning project. It processes files when you import them and run detection. It does not continuously monitor the laptop or network.

Follow a clear chain: input record, validation, storage, detection, investigation, report. Validation checks the expected fields and limits. Storage retains accepted originals and avoids duplicates. Detection applies a rule to stored event time. Investigation records observations and a reasoned conclusion. A report captures saved evidence and history.

The new presentation guide explains each part with examples. Use it with the existing five-minute demonstration script. The script tells you what to click; the practice guide helps you explain why that action matters. Read a short section, then say it in your own words. Memorizing difficult terminology is less useful than explaining one clear example.

Roman Urdu: Har button ka naam yaad karna zaroori nahi. Yeh samajhna zaroori hai ke data kahan se aaya, alert kyun bana, aur analyst ne kya evidence dekh kar decision liya.

## Step 5 Separate an alert from a conclusion

Our first practice question asks what additional information you would seek before calling five failed logins followed by success a confirmed compromise. The visible pattern is already known. The missing part is whether the successful access was unauthorized and who controlled the session.

An account-owner explanation can help. Authorized identity-provider, device, session or endpoint evidence may help corroborate it. These are possible external investigation sources; SentinelLab's present login format does not collect device or MFA fields. An unfamiliar IP alone is not proof, because VPNs, shared networks and travel can change context. Likewise, a rule matching does not establish who typed a password.

Record only facts supported by evidence. A benign alternative is that the owner corrected a forgotten password. Suspicious means the pattern deserves attention. Confirmed compromise requires stronger supporting evidence and a reasoned assessment. It is reasonable to leave a case In progress while more information is requested.

The owner has been invited to answer one question at a time. A guide or example is not proof that the owner has answered or completed practice. Actual responses should be discussed in chat before recording that milestone as complete.

## Step 6 Write useful release notes

The release notes explain what is included, what was checked, how to start and what is still limited. They cover the real implemented system: bounded imports, original evidence, three rules, saved alerts, local access, investigation history, reports, synthetic evaluation and portfolio material.

They also state that the application is a single-account local prototype, not a public production SIEM. Direct filesystem access can alter the database. Reports are not signed, encrypted or automatically redacted. Browser drafts require explicit saves. Synthetic evaluation is not real-world accuracy. These qualifications help a reviewer use the project appropriately.

The release should contain reviewed source and documentation only. Private account files, real logs, runtime databases, environments and generated private reports are excluded. A GitHub source archive does not contain Python or a ready-made account; a new user follows SETUP.md. Existing users should not reinstall or recreate their normal account just because a release candidate exists.

## Files added or updated

- VERSION names the candidate and is separate from rule and database versions.
- docs/releases/v0.1.0-rc.1.md contains the reviewable release notes, verification scope, startup links and known limitations.
- docs/portfolio/PRESENTATION_PRACTICE.md provides simple explanations for the owner, examples, troubleshooting and an honest practice-status description.
- docs/DAY_19_GUIDE.md explains this checkpoint, its concepts, steps and results.
- README.md, docs/RELEASE_READINESS.md, docs/PROGRESS.md and docs/NEXT_SESSION.md point to the candidate and remaining work.
- docs/portfolio/CASE_STUDY.md updates stale setup/acceptance wording to include Day 18 evidence.
- Both cumulative handbooks add chapter 36 and update the chapter 29 completion map while preserving earlier explanations.

No application feature, detection threshold, schema or browser behavior is changed today. Presentation and release work make the existing system easier to review and reproduce.

## What remains before the final version

The owner should practise explaining the purpose, duplicates, one rule, investigation judgment, report contents and limits. We will discuss the answers in this chat, one at a time. The versioned candidate can be shared as a clearly labelled prototype while that learning continues. A final stable release should record the outcome of this review rather than assuming it happened.

The Word handbook's content is checked and earlier lessons are preserved. Supported visual rendering is attempted after the update. The known absence of bundled LibreOffice means page layout remains unverified unless that render succeeds. The Markdown companion provides the same current explanation for reading. The original local Git-history limitation also remains explicit.

Future public hosting, live collection, multiple roles or stronger evidence integrity are separate design projects. They are not required additions to this bounded local portfolio release. Keep the deadline focused on a demonstrated, documented and honestly described system.


# 37 Final release and the Day 20 handover

Prepared and tested 4 October 2026; final publication continued 5 October 2026. This checkpoint completes the bounded SentinelLab local portfolio milestone as version 0.1.0, ahead of the October 17 target. The word final describes this project's agreed local scope. It does not mean the program is a certified production security product or that every possible future feature is finished.

## What we decided

The owner asked to continue after the release candidate and chose not to repeat the optional duplicate-upload exercise. We clarified that presentation practice is for learning, not a technical release requirement. The owner correctly said supporting evidence should be checked before deciding a case, but a complete presentation assessment has not happened. We record that distinction honestly and do not make optional exercises block delivery.

The implemented features already have automated checks, an authenticated workflow rehearsal, a downloaded-source fresh-environment run and actual synthetic browser demonstration material. We use that evidence to release the local prototype with explicit limitations. Learning and interview practice can continue afterward at the owner's pace.

Roman Urdu: Project ka local portfolio wala scope complete hai. Practice aapki learning ke liye hai; usay skip karne se software ka tested kaam undo nahi hota. Lekin apni CV par wohi understanding claim karni hai jo aap explain kar sakte hain.

## Step 1 Verify the starting snapshot

We read the project instructions and latest release/readiness records. All 159 local published files matched GitHub commit 9e2d265bbc52a97759144514445b0dd743f32ae3, the v0.1.0-rc.1 candidate. This establishes the source from which we are preparing the final release.

A Git commit identifies a source snapshot. A tag gives that snapshot a version name. A GitHub release adds a description and source downloads. The new final tag is v0.1.0. The candidate tag stays attached to its original commit. We do not silently move an old version to new content.

The original laptop Git HEAD/index remain behind under existing Windows restrictions. We preserve those controls and verify the connected publication against local file hashes. This establishes which files were published, not that the restricted local history was repaired. The release documentation keeps that limitation visible.

## Step 2 Run the final checks

The complete automated suite passed 194 tests in 28.258 seconds. It covers validation, storage, search, detection, saved alerts, cases, authentication, browser routes, reports, evaluation and rehearsal behavior. The duration is the observed time for this run, not a performance target or a comparison between computers.

The separate scripts/rehearse.py command passed all seven grouped checks. It creates a temporary account and server, signs in over real HTTP, imports and reimports synthetic events, saves and repeats detections, creates an investigation, checks JSON/Markdown reports, restarts the server, rejects old/logout sessions and cleans up temporary files. It does not edit your private account or everyday database.

We reran the twelve-scenario evaluation. Its parsed JSON matched the published earlier report exactly, including source and input fingerprints. TP, FP, TN and FN remain three each, and all twelve expected rule sets agree. A rule can be implemented correctly while producing a false alarm or missing an attack story. These authored synthetic results are not real-world detection accuracy.

Day 20 changes release metadata and documentation only. No application source, interface asset, test, rule parameter, schema or evaluation input changes. The final comparison checks that invariant. The earlier Day 18 verified ZIP download and fresh venv remain setup evidence; we do not claim a new operating-system installation or git-clone test today.

## Step 3 Resolve the release checklist honestly

The known Word limitation concerns visual page layout. We update the content, preserve earlier lessons and tables, and retry the supported renderer. Bundled LibreOffice has been unavailable, so visual pagination remains unverified if rendering still fails. We retain the readable Markdown companion and state the limitation. We do not rename an unperformed visual check as passed.

The local Git-history restriction is also retained. Private account setup has user-reported success from Day 18; the assistant did not read the password/hash or observe keyboard visibility. Source acquisition worked through a TLS-verified bundled-Python route, without claiming the earlier runtime certificate settings were repaired. These qualifications describe the actual evidence.

Presentation practice becomes optional post-release learning. The owner has given one correct investigation judgment, not a complete demonstration of every concept. The final project summary and CV wording explicitly describe substantial AI assistance and guided learning. No proficiency score or independent authorship claim is invented.

Roman Urdu: Jo cheez check hui hai usay checked likhna hai. Jo limitation abhi mojood hai usay saaf likhna hai. Version number badalne se limitation khud khatam nahi hoti.

## Step 4 Prepare the handover

The new docs/HANDOVER.md is the short operating guide for using the completed project. It tells you where the real project lives, how to start the existing server, which account/database to retain, what each important folder stores, how to run verification and what can be shared.

Your existing project is C:\Users\Dell\Desktop\Projects\SentinelLab. The usual database is data/runtime/day14_demo.db and the account is secrets/analyst.json. The browser address is http://127.0.0.1:8776/. Opening a browser does not start the Python server. If the page cannot connect after an app/computer restart, start the same server command from PowerShell and refresh the page. Restarting the server requires a new sign-in but should retain saved database records.

Use this command from the project folder:

```powershell
& .\.venv\bin\python.exe scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json
```

Keep the terminal open. You do not need administrator mode or a new account. Do not choose a different database path simply to restart, because that creates or opens a different workspace. If the server is already running, use it rather than starting another process on the same port. The setup guide explains fresh installation separately.

The handover also explains that GitHub contains source and reviewed synthetic material, not private runtime data. A source ZIP is not a backup of your investigations. For ordinary private file backups, stop database writers cleanly before copying the database. No new backup, deletion or private-data upload is performed today.

## Step 5 Finalise the portfolio description

docs/portfolio/PROJECT_SUMMARY.md gives a concise account of the problem, workflow, stack, evidence and limitations. The case study remains the more detailed architecture/design explanation. The CV page provides conservative wording appropriate to the owner's guided involvement, while retaining interview prompts for optional practice.

A useful CV line is: Completed a guided, AI-assisted implementation of a local Python and SQLite login-event investigation prototype with explained alerts, case history and JSON/Markdown reports. Supporting bullets can describe the synthetic evaluation and verified workflows without claiming independent implementation or real incident-response employment.

The final version does not justify phrases such as production SIEM, prevented attacks, enterprise-scale deployment, tamper-proof evidence or perfect detection. No job application, CV submission, public hosting or external profile edit is part of this checkpoint. The prepared wording stays in the repository for you to use and adapt honestly.

## Step 6 Publish the reviewed version

VERSION changes from 0.1.0-rc.1 to 0.1.0. The new release notes describe implemented behavior, verification, startup and retained qualifications. The new commit contains only reviewed metadata/documentation changes. Publication compares the complete remote tree and local file hashes, then creates the final GitHub release/tag at that reviewed commit. The previous candidate remains available.

The final GitHub release is a normal release for the local prototype. Its notes continue to say that it is not production-ready security infrastructure. That distinction is part of the product's scope, even without a Pre-release label. No private accounts, databases, environments, real logs or generated private reports are release assets.

The source download contains files, not your Python installation or credentials. A new user follows SETUP.md and creates their own private account. An existing user retains the current account and database. When future code changes, create a new reviewed version instead of silently altering v0.1.0.

## Files changed in this checkpoint

- VERSION identifies final local prototype version 0.1.0.
- docs/releases/v0.1.0.md records release scope, evidence, known limits and the decision that optional practice is not a blocker.
- docs/HANDOVER.md explains startup, important files, private data, verification and maintenance in simple English.
- docs/portfolio/PROJECT_SUMMARY.md provides a ready-to-read project overview.
- docs/portfolio/CV_AND_INTERVIEW.md, CASE_STUDY.md and README.md align the portfolio with the final local scope and actual owner involvement.
- reports/examples/day20_release_checks.json records safe verification facts without credentials or private records.
- docs/DAY_20_GUIDE.md is this lesson. The README, acceptance/readiness, progress and next-session pages point to current status while preserving earlier history.
- Both cumulative handbooks receive chapter 37, a current opening and the updated chapter 29 completion map. Earlier lessons are retained.

## What happens after this

There is no compulsory next daily checkpoint. You can use the project, read the handbook, practise a demonstration, ask about a concept or request a specific improvement. Optional presentation exercises remain available. A bug should include a synthetic reproduction and expected versus actual behavior; never send passwords or private account contents.

Public hosting, live event collection, multiple analysts and stronger evidence integrity are possible future projects requiring new design and testing. They are not hidden unfinished promises in this local release. The finished result is a bounded, documented, reproducible learning prototype that you can explain honestly and gradually improve.

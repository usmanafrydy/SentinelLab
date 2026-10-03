# Current cumulative update through Day 12

Updated 2 October 2026. The project now has browser investigations and local sign in with 168 passing tests. Chapters 26 to 29 add Days 10 to 12 and the current completion map. Earlier chapters are historical; the latest chapter supersedes older startup, authentication and author-label statements. Continue updating docs/SentinelLab_Project_Handbook.docx and this companion every checkpoint.

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

## What is completed through Day 12

Event validation and normalization reject malformed records and preserve valid originals. SQLite stores imports and events with duplicate and conflict handling. Searches filter stored records and original evidence is available from the browser. The detector implements R1 repeated account failures, R2 failures across accounts and R3 success after preceding failures, with tested grouping and time-window boundaries.

Explicit detection saving records runs and immutable alerts. Repeated checks do not duplicate unchanged alerts. Each alert links to its original evidence. Cases retain notes and reasoned decisions separately from evidence, with a revision number to reject outdated decisions. Browser forms connect these pieces into a review workflow.

Day 12 adds a single local account, scrypt password verification, bounded sign-in attempts, expiring server-side sessions and logout. New browser case actions use the session account. Older and CLI labels remain self-declared; direct database access is outside browser access protection. The system is a learning prototype, not a production monitoring service.

## How the pieces work together

First the account gates access to the browser workspace. Then the user imports a synthetic file. The parser validates each line and normalizes supported values. The storage service saves accepted records and retains their originals. The user deliberately runs detection; the rules examine one consistent set of events and the save transaction records alerts and evidence links. The user opens a finding, reads its originals and creates or continues a case. Case notes and decisions append history without rewriting the finding. Signing out ends access to new browser requests, not the saved investigation.

The frontend communicates using local HTTP requests. The backend validates requests and permissions, then calls focused services. SQLite transactions keep related writes together. Unit and integration tests check the behaviors; browser checks confirm that visible controls actually connect to them. The cumulative handbook explains each checkpoint and its remaining limits.

## What remains before the portfolio release

Day 13 is proposed to add investigation report export with faithful evidence references and clear limits. We still need a broader interface improvement, evaluated positive and negative scenarios, a fresh-setup rehearsal, known-limit documentation, demonstration screenshots or video, an accurate case study and CV bullets, and final release checks. Optional public hosting and multiple roles are not required to claim this local prototype works. Target completion remains 17 October 2026.

## Rules for future updates

At each meaningful checkpoint, append the easy-English explanation to the Word file and Markdown companion. Explain the purpose, concepts, actual code changes, every new or changed file's responsibility, operating steps, expected results, tests, troubleshooting, remaining limitations and next planned step. Update this current completion map and test count when behavior changes. Keep historical chapters readable and label them by day so old plans are not confused with present capabilities.

Never include passwords, hashes, session cookies, request tokens or private login records in the handbook or published repository. Demonstrations use synthetic data. A successful code test does not automatically mean the Word layout has been visually checked; report document verification separately.

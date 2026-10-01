# Investigation storage contract

Day 10 is a local command-line checkpoint. Browser case controls and authenticated analyst identity are not implemented yet.

## Identity and evidence

One case links to one existing saved alert in the same database. A unique alert_id prevents duplicate cases; creating it again returns the existing case without changing its title/history. This is a focused first workflow, not multi-alert incident grouping. A case cannot be relinked or deleted through the application. Original events, alerts, and evidence remain unchanged.

Create requires a title (1..120 characters) and an author label (1..80). Labels are self-declared local annotations, not verified identity. Text must not be blank; lengths apply before whitespace trimming. Notes permit 1..4000 characters and newline/tab. State-change reasons permit 1..1000 and newline/tab. Other controls, format characters, and unpaired surrogates are rejected. SQL values are bound; CLI output is JSON-escaped.

## States and conclusions

New cases start open with disposition undecided and revision 1. Allowed statuses: open, in_progress, closed. Allowed dispositions: undecided, benign, suspicious, confirmed_compromise. These are analyst assertions, never assigned by detection.

Open and in_progress may change to each other or closed; either may revise a disposition. Closed must have a disposition other than undecided. A closed case can revise its conclusion while remaining closed, or reopen to in_progress with undecided. Closed to open is rejected. Every state/disposition change requires a reason and the expected current revision. An unchanged pair is rejected rather than recording a fake change.

Notes can be appended in any status, including closed. Notes cannot be edited/deleted; corrections are new notes. Each note or state change increments the revision and appends an action in the same transaction. A stale state revision is rejected with a refresh instruction. Notes serialize and do not require a prior revision, so concurrent notes are both retained. Action order is per-case revision, not wall-clock ordering.

## Storage and compatibility

Explicit case creation migrates schema v2 to v3 inside its transaction. Missing/invalid alerts cannot migrate. Version 1 has no saved alerts and requires an explicit detection save first. Read-only case commands on v1/v2 return empty lists or no case without migrating. Missing/unsupported/malformed databases fail safely. Writes use mode=rw, foreign keys, BEGIN IMMEDIATE, and a five-second lock timeout.

investigations stores ID, unique alert_id, immutable title, current status/disposition/revision, and UTC created/updated times. investigation_actions stores case ID/revision, kind (created, note, state_changed), UTC time, author label, text, and before/after state JSON. Each case/revision pair is unique. All action types retain their after-state; creation has no before-state. State snapshots include status, disposition, revision. Failure rolls back schema, case, current state, and action together.

Existing imports/search/previews/saved detections/browser history support v3. Saving detection on v3 reports v3 and does not downgrade. No automatic migration during read-only requests. Application history is append-only by API convention, not tamper-proof storage against someone editing SQLite directly.

## Commands and limits

scripts/cases.py has create, list, get, note, state, history subcommands. Every command requires --database. Create uses --alert-id, --title, --author. Note uses --case-id, --text, --author. State uses --case-id, --status, --disposition, --reason, --expected-revision, --author. Get/history use --case-id. List optionally filters --status. List/history accept --limit 1..200 (default 50), --offset 0..1000000. Case IDs/revisions are positive integers through 2^63-1 (revision increment overflow is rejected).

List sorts newest case ID first; history sorts ascending revision. Responses contain total/items/limit/offset/next_offset; get returns current case metadata only. A missing get/history case exits 1; validation/storage failures exit 2; completed commands exit 0. All outputs are JSON; --json is accepted for consistency. No total-retention cap, automatic note redaction, authenticated authors, export, or case web API is claimed.

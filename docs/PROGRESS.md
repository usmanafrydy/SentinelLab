# Progress

## September 23, 2026 - Initial structure

Created and published the scaffold to the private usmanafrydy/SentinelLab repository. Initial verified main commit: 3bf77df194b503dead7040d68073637ea3b3b326. Local and remote contents and history were aligned. Command-line Git authentication was unavailable; the connected GitHub integration was used.

## September 24, 2026 - Day 1

- Owner resumed work and reported basic Python, networking, and cybersecurity knowledge.
- Replaced the original 30-day roadmap with a dated schedule ending October 17.
- Wrote a project brief, 15 measurable release criteria, an initial JSON Lines event specification, and a beginner learning guide.
- Added three synthetic login events for the learning exercise; these are below the proposed detection thresholds.
- Updated README, project instructions, and next-session notes.
- Verified sample parsing, field names, unique IDs, timestamps, IP addresses, expected outcome counts, README links, and diff whitespace.
- Git and a Python executable under MSYS2 were found. The Windows Python launcher reports no registered Python installations. Select and verify a suitable interpreter on Day 2 before installing project dependencies.
- No application implementation or executable application test suite yet. All release acceptance criteria remain pending.

## Owner's next actions

Day 1 exercise completed: owner correctly explained that exceeding the failed-login threshold triggers investigation, not proof of compromise. Current exercise: docs/DAY_05_GUIDE.md. Day 2-4 answers have not been recorded. Daily availability remains unconfirmed.

## Next implementation checkpoint

Day 6: specify detection grouping/window behavior and implement the first repeated-failure rule. See docs/NEXT_SESSION.md. Publication status is confirmed in the conversation and GitHub history after verification.

## September 26, 2026 - Day 2

- Verified the Desktop project matched GitHub before editing; active path is C:\Users\Dell\Desktop\Projects\SentinelLab.
- Created an isolated .venv using the existing MSYS2 UCRT Python 3.12.7, with no third-party package installation. Isolation and required standard-library modules were checked.
- Built a bounded JSON Lines reader with required-field/type/value checks, safe line-specific errors, UTC timestamp normalization, canonical IP text, and retained original accepted records in memory.
- Added a command-line checker with text/JSON summaries and documented exit codes.
- Passed 27 unit/integration tests covering positive, negative, boundary, resource-limit, and command-line cases.
- Good sample: 3 accepted, 0 rejected. Mixed sample: 2 accepted, 1 rejected, 1 blank; line 2 is intentionally invalid.
- Added portable setup instructions and a simple English/Roman Urdu Day 2 guide. Saved the owner's language preference in AGENTS.md.
- No database writes, cross-file duplicate checking, attack detection, dashboard, or production deployment yet.
- Delivery target remains October 17. The daily learning session number does not imply that work ran on September 25.

- Local Git metadata writes are blocked by an explicit Windows deny entry. Files are saved locally; Day 2 publication uses the GitHub connector. Local HEAD/index reconciliation remains pending, as documented in NEXT_SESSION.md.

## Day 3 learning session - September 26, 2026

- Verified that the user reconciled Day 2 local history: clean branch at 3d997d734b4a18a3747c367f462681c9f3747b88 matching GitHub.
- Added SQLite events/imports tables, preserving normalized and original first-accepted evidence.
- Added atomic imports, canonical duplicate skipping, conflict reporting without overwrites, and persisted safe summaries.
- Added import and read-only summary commands.
- All 46 tests passed, including 19 new storage/integration tests. Corrected test connection cleanup on Windows and checked original-text preservation against CRLF bytes during development.
- Separate-process demo: first import inserted 3; second inserted 0 and skipped 3 duplicates; reopening shows 3 events and 2 completed imports.
- Local data/runtime/day03_demo.db is excluded from Git. No extra dependencies installed.
- Added simple English/Roman Urdu learning guide and updated setup/design/continuation notes.
- Assistant-side staging still hit a Windows metadata permission error. Connected GitHub publication is available; compare local history with the published commit before further reconciliation.
- Event search, detection, web interface, and analyst authentication remain unimplemented. Target remains October 17.

## Day 4 learning session - September 27, 2026

- All published Day 3 files matched local files before editing.
- Added read-only account/IP/outcome/time search with bounded pages and deterministic time/ID ordering; original evidence lookup by internal ID.
- No schema migration or extra dependencies. Search intervals include start and exclude end.
- All 57 tests passed, including 11 new search tests for combined filters, boundaries, paging ties, invalid input, SQL-looking text, evidence, unchanged database bytes, and CLI behavior.
- Existing demo search returns 2 failures; lookup ID 1 returns demo-001 and original evidence.
- Added simple English/Roman Urdu Day 4 guide, search contract, and continuation notes.
- Local Git metadata remains behind published content; connector publication outcome is confirmed in the conversation after verification.
- Detection, browser interface, investigations, and analyst authentication remain pending. October 17 remains the target.

## Day 5 learning session - September 28, 2026

- Verified all published Day 4 files against local content before editing; local metadata still shows Day 2.
- Built a loopback-only browser workspace for JSONL upload, counts, combined event filters, paging, and original-evidence lookup. Reused existing parsing/storage/search; no third-party dependencies.
- Added explicit empty-schema initialization without fake import history. Uploads use bounded bodies and temporary files, preserving originals and duplicate/conflict behavior.
- Added exact Host/Origin checks, per-process write token, allowlisted assets, safe text rendering, and restrictive response headers. No analyst authentication or production deployment claims.
- Browser-tested good/mixed imports, 2-failure filtering, evidence, invalid IP errors, pagination with separate 27-event QA data, and literal HTML-like usernames without HTML execution. Checked desktop/narrow layouts.
- Fixed malformed Failure option found through browser testing and added a regression test. Full suite: 67 passing tests.
- Normal day05_demo.db has 3 events and 2 imports; Day 3 demo is unchanged. Separate ignored QA files retain only synthetic test data.
- Added Day 5 learning guide and web contract. Detection/investigations/sign-in remain pending; target remains October 17.
- Publish through the GitHub connector because local metadata writes remain restricted. Verify publication separately before claiming completion.

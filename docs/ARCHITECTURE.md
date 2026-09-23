# Proposed architecture

Status: design outline only.

Sample logs -> validation and normalization -> SQLite event storage -> detection rules -> evidence-backed alerts -> investigation -> report.

- Ingestion preserves the original record and a normalized representation.
- Detection uses explicit grouping keys and event-time windows.
- Alerts retain rule version and supporting event references.
- Investigations retain status, disposition, notes, and action history.
- The web interface reads and updates records through server-side validation and authorization.

Detailed schemas, API contracts, authentication design, and dependency versions will be selected during implementation.

## Planned rule families

1. Repeated failures for an account and source.
2. Failures across multiple accounts from a source.
3. Successful login following a matching failure burst.

Thresholds will be configurable and evaluated in the lab. An alert is a request for investigation, not proof of compromise. Account-wide failure patterns alone cannot prove that the same password was attempted.

"""R3: a success after five earlier matching failures; equal-time failures excluded."""
from collections import defaultdict, deque
from datetime import timedelta
from itertools import groupby

from sentinellab.detection.common import alert_identity, reference, utc_time

THRESHOLD = 5
WINDOW_SECONDS = 300


def evaluate_r3(rows, budget):
    groups = defaultdict(list)
    for row in rows:
        if row["event_type"] == "login":
            groups[(row["username"], row["source_ip"])].append(row)
    alerts = []
    for (username, source_ip), records in sorted(groups.items()):
        window = deque()
        for timestamp, iterator in groupby(records, key=lambda row: row["timestamp_utc"]):
            batch, moment = list(iterator), utc_time(timestamp)
            while window and moment - window[0][0] > timedelta(seconds=WINDOW_SECONDS):
                window.popleft()
            # All successes see only strictly earlier failures, regardless of tie order.
            for success in (row for row in batch if row["outcome"] == "success"):
                if len(window) < THRESHOLD:
                    continue
                budget.consume(len(window) + 1)
                evidence = [dict(reference(row), role="preceding_failure") for _, row in window]
                evidence.append(dict(reference(success), role="triggering_success"))
                parameters = {"threshold": THRESHOLD, "window_seconds": WINDOW_SECONDS}
                group = {"username": username, "source_ip": source_ip}
                alerts.append({
                    "alert_id": alert_identity("R3", parameters, group, evidence),
                    "rule_id": "R3", "rule_version": "1.0.0",
                    "title": "Successful login after repeated failures", "parameters": parameters,
                    "group": group, "failure_count": len(window),
                    "first_event_at": evidence[0]["timestamp_utc"], "triggered_at": timestamp,
                    "reason": f"A successful login followed {len(window)} earlier failures for the same username and source IP within 300 seconds. Equal-time failures are excluded. Investigate; the user may simply have corrected a password.",
                    "evidence": evidence,
                })
            window.extend((moment, row) for row in batch if row["outcome"] == "failure")
    return alerts

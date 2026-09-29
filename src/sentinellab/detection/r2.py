"""R2: failures across at least ten distinct accounts from one source IP."""
from collections import Counter, defaultdict, deque
from datetime import timedelta
from itertools import groupby

from sentinellab.detection.common import alert_identity, reference, utc_time

THRESHOLD = 10
WINDOW_SECONDS = 600


def evaluate_r2(rows, budget):
    groups = defaultdict(list)
    for row in rows:
        if row["event_type"] == "login" and row["outcome"] == "failure":
            groups[row["source_ip"]].append(row)
    alerts = []
    for source_ip, records in sorted(groups.items()):
        window, accounts, armed = deque(), Counter(), True
        for timestamp, batch in groupby(records, key=lambda row: row["timestamp_utc"]):
            moment = utc_time(timestamp)
            while window and moment - window[0][0] > timedelta(seconds=WINDOW_SECONDS):
                _, expired = window.popleft()
                accounts[expired["username"]] -= 1
                if accounts[expired["username"]] == 0:
                    del accounts[expired["username"]]
            if len(accounts) < THRESHOLD:
                armed = True
            for row in batch:
                window.append((moment, row))
                accounts[row["username"]] += 1
            if armed and len(accounts) >= THRESHOLD:
                budget.consume(len(window))
                evidence = [dict(reference(row), username=row["username"]) for _, row in window]
                parameters = {"threshold": THRESHOLD, "window_seconds": WINDOW_SECONDS}
                group = {"source_ip": source_ip}
                alerts.append({
                    "alert_id": alert_identity("R2", parameters, group, evidence),
                    "rule_id": "R2", "rule_version": "1.0.0",
                    "title": "Failed logins across multiple accounts", "parameters": parameters,
                    "group": group, "distinct_account_count": len(accounts),
                    "usernames": sorted(accounts), "failure_count": len(window),
                    "first_event_at": evidence[0]["timestamp_utc"], "triggered_at": timestamp,
                    "reason": f"Failed logins for {len(accounts)} distinct usernames from one source IP within an inclusive 600-second window. Investigate; this does not prove password spraying or compromise.",
                    "evidence": evidence,
                })
                armed = False
    return alerts

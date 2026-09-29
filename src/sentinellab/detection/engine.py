"""Evaluate selected rules against the same bounded read-only snapshot."""
from sentinellab.detection.common import EvidenceBudget, load_snapshot
from sentinellab.detection.r1 import evaluate_r1
from sentinellab.detection.r2 import evaluate_r2
from sentinellab.detection.r3 import evaluate_r3
from sentinellab.storage.database import StorageError

RULES = ("R1", "R2", "R3")


def detect(database_path, rule="all"):
    validate_rule(rule)
    return evaluate_snapshot(load_snapshot(database_path), rule)


def validate_rule(rule):
    if rule not in (*RULES, "all"):
        raise StorageError("rule must be R1, R2, R3, or all.")


def evaluate_snapshot(rows, rule="all"):
    validate_rule(rule)
    selected = RULES if rule == "all" else (rule,)
    budget, alerts = EvidenceBudget(), []
    if "R1" in selected:
        first = evaluate_r1(rows)
        budget.consume(sum(len(alert["evidence"]) for alert in first))
        alerts.extend(first)
    if "R2" in selected:
        alerts.extend(evaluate_r2(rows, budget))
    if "R3" in selected:
        alerts.extend(evaluate_r3(rows, budget))
    alerts.sort(key=lambda item: (item["triggered_at"], item["rule_id"], item["alert_id"]))
    return {"mode": "read_only_preview", "rules_evaluated": list(selected),
            "events_scanned": len(rows), "alert_count": len(alerts), "alerts": alerts}

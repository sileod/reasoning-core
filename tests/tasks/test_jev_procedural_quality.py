import json

from reasoning_core.tasks.generated.jev.multi_view_adjudication import JevMultiViewAdjudication
from reasoning_core.tasks.generated.jev.state_perturbation import JevStatePerturbation


def _intent_from_state(state):
    if any(state["billing"].values()):
        return "billing"
    account = state["account"]
    if account["active"] and (account["auth_failures"] >= 2 or account["permission_mismatch"]):
        return "access"
    telemetry = state["telemetry"]
    if telemetry["integration_failures"] >= 2 or telemetry["error_rate_percent"] >= 20:
        return "technical"
    return "other"


def _urgency_from_state(state):
    timeline = state["timeline"]
    deadline = timeline["deadline_hours"]
    return timeline["executive_escalation"] or (deadline is not None and deadline <= 24)


def _impact_from_state(state):
    workflow = state["workflow"]
    if workflow["core_blocked"] and not workflow["workaround_available"]:
        return 2
    if workflow["degraded"] or (workflow["core_blocked"] and workflow["workaround_available"]):
        return 1
    return 0


def _risk_from_state(record, rule):
    return (
        (0 if record["authorized"] else rule["unauthorized_points"])
        + (rule["blocked_status_points"] if record["status"] == "blocked" else rule["otherwise_points"])
        + (
            rule["amount_threshold_points"]
            if record["amount"] >= rule["amount_threshold"]
            else rule["otherwise_points"]
        )
        + (
            rule["unassigned_owner_points"]
            if record["owner"] == "unassigned"
            else rule["otherwise_points"]
        )
    )


def test_multi_view_gold_is_derived_from_joined_state_rules():
    task = JevMultiViewAdjudication()
    for _ in range(200):
        entry = task.generate_entry()
        state = entry.metadata.state
        answer = json.loads(entry.answer)

        assert "adjudication_rules" in state
        assert state["ticket"]["message"] == (
            "The user reports an operational issue requiring adjudication from the joined records."
        )
        assert answer["intent"]["choice"] == _intent_from_state(state)
        assert bool(answer["is_urgent"]["noul"]) == _urgency_from_state(state)
        assert int(answer["workflow_impact"]["score"]) == _impact_from_state(state)


def test_state_perturbation_exposes_and_uses_risk_rule():
    task = JevStatePerturbation()
    for _ in range(200):
        entry = task.generate_entry()
        state = entry.metadata.state
        answer = json.loads(entry.answer)
        rule = state["risk_rule"]

        before = _risk_from_state(state["before"], rule)
        after = _risk_from_state(state["after"], rule)
        expected = 0 if after < before else 2 if after > before else 1

        assert "state.risk_rule" in entry.metadata.questions["risk_direction"]["instructions"]
        assert int(answer["risk_direction"]["score"]) == expected

from ontology.civilizational_metrics_synthesizer import (
    ecological_self_revision_recommendations,
)
from ontology.trajectory_policy_update import TrajectoryPolicyUpdate

class AutonomousDecisionEngine:
    PRIMITIVE_NAME = "AUTONOMOUS_DECISION_ENGINE"

    def __init__(self, user_name="User"):
        self.user_name = user_name

    def step(
        self,
        opportunities=None,
        constraint_monitoring=None,
        rebalanced_schedule=None,
        strategic_schedule=None,
        policy_update=None,
    ):
        opportunities = opportunities or {}
        constraint_monitoring = constraint_monitoring or {}
        rebalanced_schedule = rebalanced_schedule or {}
        strategic_schedule = strategic_schedule or {}
        policy_update = policy_update or {}

        top_opportunity = opportunities.get("top_opportunity")
        monitoring_score = constraint_monitoring.get("monitoring_score", 0.5)
        adaptability_score = rebalanced_schedule.get("adaptability_score", 0.5)
        continuity_score = strategic_schedule.get("strategy_continuity_score", 0.5)

        decision_confidence = (
            monitoring_score + adaptability_score + continuity_score
        ) / 3.0

        policy_bias = float(policy_update.get("policy_bias", 0.0))
        decision_confidence = max(0.0, min(1.0, decision_confidence + policy_bias))

        ecological = ecological_self_revision_recommendations()
        recommendations = ecological.get("recommendations", [])

        decision = (
            f"Prioriser: {top_opportunity}"
            if top_opportunity
            else "Maintenir la trajectoire actuelle"
        )

        if recommendations:
            decision += " | Ecological: " + ",".join(recommendations[:3])

        return {
            "primitive": self.PRIMITIVE_NAME,
            "decision": decision,
            "decision_confidence": round(decision_confidence, 4),
            "policy_bias": policy_bias,
            "decision_ready": True,
        }


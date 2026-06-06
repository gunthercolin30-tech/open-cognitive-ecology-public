
"""Adaptive Priority Rebalancer"""

class AdaptivePriorityRebalancer:
    PRIMITIVE_NAME = "ADAPTIVE_PRIORITY_REBALANCER"

    def __init__(self, user_name="User"):
        self.user_name = user_name

    def step(
        self,
        strategic_schedule=None,
        emerging_constraints=None,
        emerging_opportunities=None,
        governance_metrics=None,
    ):
        strategic_schedule = strategic_schedule or []
        emerging_constraints = emerging_constraints or []
        emerging_opportunities = emerging_opportunities or []
        governance_metrics = governance_metrics or {}

        adjusted = []
        opportunity_bonus = 0.05 * len(emerging_opportunities)
        constraint_penalty = 0.03 * len(emerging_constraints)

        for item in strategic_schedule:
            base = float(item.get("priority_score", 0.5))
            new_score = max(
                0.1,
                min(1.0, round(base + opportunity_bonus - constraint_penalty, 4))
            )
            updated = dict(item)
            updated["rebalanced_priority_score"] = new_score
            adjusted.append(updated)

        adaptability_score = round(
            min(1.0, 0.8 + 0.02 * len(emerging_opportunities)),
            4
        )

        return {
            "primitive": self.PRIMITIVE_NAME,
            "rebalanced_schedule": adjusted,
            "constraints_count": len(emerging_constraints),
            "opportunities_count": len(emerging_opportunities),
            "adaptability_score": adaptability_score,
            "priority_rebalancing_ready": True,
        }

if __name__ == "__main__":
    engine = AdaptivePriorityRebalancer(user_name="Colin")
    print(engine.step(
        strategic_schedule=[
            {"day": 1, "priority_score": 0.4, "focus": "Maintenir la trajectoire actuelle"}
        ],
        emerging_constraints=["Délai réduit"],
        emerging_opportunities=["Nouvelle publication"],
        governance_metrics={"global_viability_score": 0.92457},
    ))

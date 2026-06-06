
"""Constraint Monitoring System"""

class ConstraintMonitoringSystem:
    PRIMITIVE_NAME = "CONSTRAINT_MONITORING_SYSTEM"

    def __init__(self, user_name="User"):
        self.user_name = user_name

    def step(
        self,
        internal_constraints=None,
        external_constraints=None,
        governance_metrics=None,
    ):
        internal_constraints = internal_constraints or []
        external_constraints = external_constraints or []
        governance_metrics = governance_metrics or {}

        all_constraints = list(internal_constraints) + list(external_constraints)
        pressure_score = round(min(1.0, 0.1 * len(all_constraints)), 4)

        alerts = []
        for constraint in all_constraints:
            alerts.append({
                "constraint": constraint,
                "severity": "moderate" if pressure_score < 0.5 else "high",
            })

        viability = governance_metrics.get("global_viability_score", 1.0)
        monitoring_score = round((1.0 - pressure_score + viability) / 2.0, 4)

        return {
            "primitive": self.PRIMITIVE_NAME,
            "constraint_count": len(all_constraints),
            "pressure_score": pressure_score,
            "alerts": alerts,
            "monitoring_score": monitoring_score,
            "constraint_monitoring_ready": True,
        }

if __name__ == "__main__":
    engine = ConstraintMonitoringSystem(user_name="Colin")
    print(engine.step(
        internal_constraints=["Temps limité"],
        external_constraints=["Nouvelle échéance"],
        governance_metrics={"global_viability_score": 0.92457},
    ))

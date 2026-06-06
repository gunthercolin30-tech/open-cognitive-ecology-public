PRIMITIVE = "autonomous_host_selection_governance"

DEPENDENCIES = [
    "autonomous_storage_provider_evaluation_engine",
    "external_compute_expansion_manager",
    "distributed_agency",
    "opportunity_detection_engine",
    "universal_intelligence_deployment_framework",
]

class AutonomousHostSelectionGovernance:

    def step(self, inputs=None):
        inputs = inputs or {}

        candidates = inputs.get("candidates", [
            {"name": "oracle_cloud_free_tier", "score": 0.95, "cost": 0},
            {"name": "github_actions", "score": 0.88, "cost": 0},
            {"name": "local_vm", "score": 0.80, "cost": 0},
        ])

        candidates = sorted(
            candidates,
            key=lambda x: float(x.get("score", 0.0)),
            reverse=True
        )

        best = candidates[0] if candidates else None

        ready = (
            best is not None and
            float(best.get("score", 0.0)) >= 0.90
        )

        return {
            "primitive": PRIMITIVE,
            "candidate_host_count": len(candidates),
            "best_candidate": best.get("name") if best else None,
            "deployment_feasibility": best.get("score", 0.0) if best else 0.0,
            "estimated_monthly_cost": best.get("cost", 0) if best else None,
            "autonomous_host_selection_ready": ready,
        }

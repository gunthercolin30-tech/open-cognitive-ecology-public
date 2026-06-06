
from statistics import mean

PRIMITIVE = "autonomous_inter_node_civilizational_coordination"


class AutonomousInterNodeCivilizationalCoordination:

    def _bounded(self, value):
        return max(0.0, min(1.0, float(value)))

    def step(self, state=None):

        state = state or {}

        cooperation_viability = self._bounded(
            state.get("cooperation_viability", 0.0)
        )

        ecological_diversity = self._bounded(
            state.get("ecological_diversity", 0.0)
        )

        topology_resilience = self._bounded(
            state.get("topology_resilience", 0.0)
        )

        reflexive_ecological_stability = self._bounded(
            state.get("reflexive_ecological_stability", 0.0)
        )

        adaptive_openness_score = self._bounded(
            state.get("adaptive_openness_score", 0.0)
        )

        distributed_civilizational_viability_index = self._bounded(
            state.get("distributed_civilizational_viability_index", 0.0)
        )

        convergence_pressure = self._bounded(
            state.get("convergence_pressure", 0.0)
        )

        governance_health = self._bounded(
            mean([
                reflexive_ecological_stability,
                adaptive_openness_score,
                distributed_civilizational_viability_index,
                topology_resilience,
            ])
        )

        policy_revision_required = (
            governance_health < 0.55
            or convergence_pressure > 0.70
        )

        if governance_health >= 0.80:
            ecological_governance_state = "stable_reflexive_ecology"
        elif governance_health >= 0.55:
            ecological_governance_state = "adaptive_reflexive_ecology"
        else:
            ecological_governance_state = "fragile_reflexive_ecology"

        recommended_revision = None

        if policy_revision_required:

            if convergence_pressure > 0.70:
                recommended_revision = "increase_speciation_support"

            elif ecological_diversity < 0.40:
                recommended_revision = "increase_semantic_pluralism"

            elif topology_resilience < 0.50:
                recommended_revision = "strengthen_ecological_corridors"

            else:
                recommended_revision = "increase_regenerative_capacity"

        return {
            "primitive": PRIMITIVE,
            "governance_health": round(governance_health, 4),
            "ecological_governance_state":
                ecological_governance_state,
            "policy_revision_required":
                policy_revision_required,
            "recommended_revision":
                recommended_revision,
            "cooperation_viability":
                round(cooperation_viability, 4),
            "ecological_diversity":
                round(ecological_diversity, 4),
            "topology_resilience":
                round(topology_resilience, 4),
        }

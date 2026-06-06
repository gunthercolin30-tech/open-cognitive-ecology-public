
from statistics import mean

PRIMITIVE = "autonomous_inter_host_negotiation"

class AutonomousInterHostNegotiation:

    def _bounded(self, value):
        return max(0.0, min(1.0, float(value)))

    def step(self, state=None):

        state = state or {}

        interoperability = self._bounded(
            state.get("interoperability", 0.5)
        )

        pluralistic_divergence = self._bounded(
            state.get("pluralistic_divergence", 0.5)
        )

        anti_convergence_capacity = self._bounded(
            state.get("anti_convergence_capacity", 0.5)
        )

        convergence_pressure = self._bounded(
            state.get("convergence_pressure", 0.5)
        )

        negotiation_capacity = self._bounded(
            (
                interoperability
                + pluralistic_divergence
                + anti_convergence_capacity
            ) / 3.0
        )

        distributed_alignment = self._bounded(
            (
                interoperability
                + (1.0 - convergence_pressure)
            ) / 2.0
        )

        civilizational_coordination_index = self._bounded(
            mean([
                negotiation_capacity,
                distributed_alignment,
                anti_convergence_capacity,
            ])
        )

        return {
            "primitive": PRIMITIVE,
            "negotiation_capacity":
                round(negotiation_capacity,4),
            "distributed_alignment":
                round(distributed_alignment,4),
            "civilizational_coordination_index":
                round(civilizational_coordination_index,4),
            "coordination_viable":
                civilizational_coordination_index >= 0.70,
        }

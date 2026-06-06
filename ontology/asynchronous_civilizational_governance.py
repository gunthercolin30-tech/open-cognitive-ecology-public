
from statistics import mean

PRIMITIVE = "asynchronous_civilizational_governance"

DESCRIPTION = (
    "Asynchronous distributed civilizational governance "
    "under temporal divergence and partial desynchronization."
)

DEPENDENCIES = [
    "distributed_runtime_coordination",
    "distributed_pluralistic_stability",
    "distributed_meta_stability",
    "distributed_reflexive_civilizational_identity",
    "trajectory_hysteresis",
    "trajectory_bifurcation",
    "future_openness",
    "historical_open_endedness",
    "anti_closure_metaconstraint",
    "distributed_topological_self_adaptation",
]


class AsynchronousCivilizationalGovernance:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(self, state=None):

        state = state or {}

        node_temporal_divergence = self._bounded(
            state.get(
                "node_temporal_divergence",
                0.25,
            )
        )

        network_latency = self._bounded(
            state.get(
                "network_latency",
                0.25,
            )
        )

        historical_divergence = self._bounded(
            state.get(
                "historical_divergence",
                0.25,
            )
        )

        consensus_pressure = self._bounded(
            state.get(
                "consensus_pressure",
                0.25,
            )
        )

        future_openness = self._bounded(
            state.get(
                "future_openness",
                0.90,
            )
        )

        distributed_alignment = self._bounded(
            (
                (1.0 - node_temporal_divergence)
                + (1.0 - network_latency)
            ) / 2.0
        )

        historical_pluralism = self._bounded(
            (
                historical_divergence
                + future_openness
                + (1.0 - consensus_pressure)
            ) / 3.0
        )

        asynchronous_viability = self._bounded(
            mean(
                [
                    distributed_alignment,
                    historical_pluralism,
                    future_openness,
                ]
            )
        )

        if asynchronous_viability >= 0.90:

            classification = (
                "fully_viable_asynchronous_civilization"
            )

        elif asynchronous_viability >= 0.70:

            classification = (
                "stable_asynchronous_governance"
            )

        elif asynchronous_viability >= 0.50:

            classification = (
                "fragile_asynchronous_governance"
            )

        else:

            classification = (
                "terminal_synchronization_risk"
            )

        return {
            "distributed_alignment":
                round(distributed_alignment, 4),
            "historical_pluralism":
                round(historical_pluralism, 4),
            "future_openness":
                round(future_openness, 4),
            "asynchronous_viability":
                round(asynchronous_viability, 4),
            "classification":
                classification,
            "governance_viable":
                (
                    asynchronous_viability >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)

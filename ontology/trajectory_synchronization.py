
from statistics import mean

PRIMITIVE = "trajectory_synchronization"


class TrajectorySynchronization:

    PRIMITIVE = PRIMITIVE

    def __init__(self):

        self.history = []

        self.hysteresis_gain = 0.15

        self.recovery_rate = 0.035

        self.regeneration_rate = 0.025

        self.max_history = 250

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def _average_metric(
        self,
        local_value,
        remote_values,
    ):

        values = [local_value]

        values.extend(remote_values)

        return self._bounded(
            mean(values)
        )

    def _historical_closure_memory(self):

        if not self.history:
            return 0.0

        return self._bounded(
            mean(
                [
                    x["synchronized_closure"]
                    for x in self.history
                ]
            )
        )

    def _recovery_dynamics(
        self,
        historical_memory,
        synchronized_closure,
        synchronized_openness,
    ):

        recovery_activation = (
            synchronized_openness
            * (
                1.0
                - synchronized_closure
            )
        )

        recovery_effect = (
            recovery_activation
            * self.recovery_rate
        )

        recovered_memory = self._bounded(
            historical_memory
            - recovery_effect
        )

        return {
            "recovery_activation":
                self._bounded(recovery_activation),
            "recovery_effect":
                self._bounded(recovery_effect),
            "recovered_memory":
                recovered_memory,
        }

    def _regeneration_dynamics(
        self,
        synchronized_density,
        synchronized_openness,
        recovered_memory,
    ):

        regeneration_activation = (
            synchronized_density
            * synchronized_openness
            * (
                1.0
                - recovered_memory
            )
        )

        regeneration_effect = (
            regeneration_activation
            * self.regeneration_rate
        )

        regenerated_openness = (
            self._bounded(
                synchronized_openness
                + regeneration_effect
            )
        )

        attractor_diversification = (
            self._bounded(
                regeneration_activation
            )
        )

        return {
            "regeneration_activation":
                round(
                    regeneration_activation,
                    4,
                ),
            "regeneration_effect":
                round(
                    regeneration_effect,
                    4,
                ),
            "regenerated_openness":
                round(
                    regenerated_openness,
                    4,
                ),
            "attractor_diversification":
                round(
                    attractor_diversification,
                    4,
                ),
        }

    def step(
        self,
        state=None,
    ):

        state = state or {}

        local_topology = (
            state.get(
                "local_topology",
                {},
            )
        )

        remote_topologies = (
            state.get(
                "remote_topologies",
                [],
            )
        )

        local_density = self._bounded(
            local_topology.get(
                "attractor_density",
                0.5,
            )
        )

        local_closure = self._bounded(
            local_topology.get(
                "closure_pressure",
                0.5,
            )
        )

        local_openness = self._bounded(
            local_topology.get(
                "openness_preservation",
                0.5,
            )
        )

        remote_density = [
            self._bounded(
                topology.get(
                    "attractor_density",
                    0.5,
                )
            )
            for topology in remote_topologies
        ]

        remote_closure = [
            self._bounded(
                topology.get(
                    "closure_pressure",
                    0.5,
                )
            )
            for topology in remote_topologies
        ]

        remote_openness = [
            self._bounded(
                topology.get(
                    "openness_preservation",
                    0.5,
                )
            )
            for topology in remote_topologies
        ]

        synchronized_density = (
            self._average_metric(
                local_density,
                remote_density,
            )
        )

        synchronized_closure = (
            self._average_metric(
                local_closure,
                remote_closure,
            )
        )

        synchronized_openness = (
            self._average_metric(
                local_openness,
                remote_openness,
            )
        )

        historical_closure_memory = (
            self._historical_closure_memory()
        )

        recovery = self._recovery_dynamics(
            historical_closure_memory,
            synchronized_closure,
            synchronized_openness,
        )

        recovered_memory = (
            recovery["recovered_memory"]
        )

        regeneration = self._regeneration_dynamics(
            synchronized_density,
            synchronized_openness,
            recovered_memory,
        )

        regenerated_openness = (
            regeneration["regenerated_openness"]
        )

        hysteresis_penalty = (
            recovered_memory
            * self.hysteresis_gain
        )

        effective_closure = self._bounded(
            synchronized_closure
            + hysteresis_penalty
        )

        distributed_topology_alignment = (
            self._bounded(
                (
                    synchronized_density
                    + regenerated_openness
                    + (
                        1.0
                        - effective_closure
                    )
                ) / 3.0
            )
        )

        openness_invariant_replication = (
            self._bounded(
                regenerated_openness
                * (
                    1.0
                    - effective_closure
                )
            )
        )

        attractor_consensus = (
            self._bounded(
                synchronized_density
                * (
                    1.0
                    - effective_closure
                )
            )
        )

        divergence_stabilization = (
            self._bounded(
                (
                    regenerated_openness
                    + (
                        1.0
                        - effective_closure
                    )
                ) / 2.0
            )
        )

        regeneration_index = (
            self._bounded(
                mean(
                    [
                        regenerated_openness,
                        regeneration[
                            "attractor_diversification"
                        ],
                        (
                            1.0
                            - recovered_memory
                        ),
                    ]
                )
            )
        )

        recovery_resilience_index = (
            self._bounded(
                (
                    openness_invariant_replication
                    + divergence_stabilization
                    + (
                        1.0
                        - recovered_memory
                    )
                ) / 3.0
            )
        )

        reflexive_consensus = (
            self._bounded(
                mean(
                    [
                        distributed_topology_alignment,
                        openness_invariant_replication,
                        attractor_consensus,
                        divergence_stabilization,
                    ]
                )
            )
        )

        closure_risk_detected = (
            effective_closure >= 0.75
        )

        synchronization_class = (
            "distributed_reflexive_topology"
            if reflexive_consensus >= 0.90
            else "distributed_open_topology"
        )

        self.history.append(
            {
                "synchronized_closure":
                    synchronized_closure,
                "reflexive_consensus":
                    reflexive_consensus,
            }
        )

        if len(self.history) > self.max_history:
            self.history = (
                self.history[-self.max_history:]
            )

        historical_path_dependency = (
            recovered_memory > 0.10
        )

        regenerative_transition_detected = (
            regeneration_index >= 0.65
        )

        return {
            "primitive": self.PRIMITIVE,
            "success": True,
            "remote_runtime_count":
                len(remote_topologies),
            "historical_closure_memory":
                round(
                    recovered_memory,
                    4,
                ),
            "recovery_activation":
                round(
                    recovery["recovery_activation"],
                    4,
                ),
            "recovery_effect":
                round(
                    recovery["recovery_effect"],
                    4,
                ),
            "recovery_resilience_index":
                round(
                    recovery_resilience_index,
                    4,
                ),
            "regeneration_activation":
                regeneration[
                    "regeneration_activation"
                ],
            "regeneration_effect":
                regeneration[
                    "regeneration_effect"
                ],
            "attractor_diversification":
                regeneration[
                    "attractor_diversification"
                ],
            "regeneration_index":
                round(
                    regeneration_index,
                    4,
                ),
            "regenerative_transition_detected":
                regenerative_transition_detected,
            "hysteresis_penalty":
                round(
                    hysteresis_penalty,
                    4,
                ),
            "effective_closure":
                round(
                    effective_closure,
                    4,
                ),
            "distributed_topology_alignment":
                round(
                    distributed_topology_alignment,
                    4,
                ),
            "openness_invariant_replication":
                round(
                    openness_invariant_replication,
                    4,
                ),
            "attractor_consensus":
                round(
                    attractor_consensus,
                    4,
                ),
            "divergence_stabilization":
                round(
                    divergence_stabilization,
                    4,
                ),
            "reflexive_consensus":
                round(
                    reflexive_consensus,
                    4,
                ),
            "closure_risk_detected":
                closure_risk_detected,
            "historical_path_dependency":
                historical_path_dependency,
            "history_size":
                len(self.history),
            "synchronization_class":
                synchronization_class,
        }

    def diagnostics(self):

        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
            "distributed_topology_ready": True,
            "historical_hysteresis_enabled": True,
            "recovery_dynamics_enabled": True,
            "topological_regeneration_enabled": True,
        }

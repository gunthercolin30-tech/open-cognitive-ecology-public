from statistics import mean

PRIMITIVE = "invariant_propagation_monitor"

DESCRIPTION = (
    "Distributed monitoring of constitutional invariant propagation."
)

DEPENDENCIES = [
    "distributed_constitutional_propagation",
    "distributed_constitutional_alignment",
    "distributed_constitutional_memory",
    "distributed_meta_stability",
    "constitutional_longitudinal_observatory",
    "intergenerational_continuity_metrics",
    "distributed_historical_mutation",
    "civilizational_semantic_drift",
    "trajectory_bifurcation",
    "anti_closure_metaconstraint",
]


class InvariantPropagationMonitor:

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

        propagation_visibility = (
            self._bounded(
                state.get(
                    "propagation_visibility",
                    0.0,
                )
            )
        )

        longitudinal_traceability = (
            self._bounded(
                state.get(
                    "longitudinal_traceability",
                    0.0,
                )
            )
        )

        pluralistic_observability = (
            self._bounded(
                state.get(
                    "pluralistic_observability",
                    0.0,
                )
            )
        )

        anti_convergence_detection = (
            self._bounded(
                state.get(
                    "anti_convergence_detection",
                    0.0,
                )
            )
        )

        topological_awareness = (
            self._bounded(
                state.get(
                    "topological_awareness",
                    0.0,
                )
            )
        )

        distributed_trace_consistency = (
            self._bounded(
                state.get(
                    "distributed_trace_consistency",
                    0.0,
                )
            )
        )

        monitoring_centralization = (
            self._bounded(
                state.get(
                    "monitoring_centralization",
                    0.0,
                )
            )
        )

        invariant_capture_risk = (
            self._bounded(
                state.get(
                    "invariant_capture_risk",
                    0.0,
                )
            )
        )

        distributed_monitoring_viability = (
            self._bounded(
                (
                    propagation_visibility
                    + longitudinal_traceability
                    + pluralistic_observability
                    + anti_convergence_detection
                    + topological_awareness
                    + distributed_trace_consistency
                    + (
                        1.0
                        - monitoring_centralization
                    )
                    + (
                        1.0
                        - invariant_capture_risk
                    )
                ) / 8.0
            )
        )

        open_observability_index = (
            self._bounded(
                (
                    pluralistic_observability
                    + anti_convergence_detection
                    + topological_awareness
                    + (
                        1.0
                        - monitoring_centralization
                    )
                ) / 4.0
            )
        )

        propagation_stability_monitoring = (
            self._bounded(
                (
                    propagation_visibility
                    + distributed_trace_consistency
                    + longitudinal_traceability
                ) / 3.0
            )
        )

        monitoring_closure_risk = (
            self._bounded(
                (
                    monitoring_centralization
                    + invariant_capture_risk
                    + (
                        1.0
                        - pluralistic_observability
                    )
                ) / 3.0
            )
        )

        invariant_propagation_monitor_index = (
            self._bounded(
                mean(
                    [
                        distributed_monitoring_viability,
                        open_observability_index,
                        propagation_stability_monitoring,
                        (
                            1.0
                            - monitoring_closure_risk
                        ),
                    ]
                )
            )
        )

        invariant_propagation_monitor_viable = (
            invariant_propagation_monitor_index
            >= 0.60
            and monitoring_closure_risk <= 0.50
            and monitoring_centralization <= 0.50
        )

        return {
            "distributed_monitoring_viability":
                round(
                    distributed_monitoring_viability,
                    4,
                ),
            "open_observability_index":
                round(
                    open_observability_index,
                    4,
                ),
            "propagation_stability_monitoring":
                round(
                    propagation_stability_monitoring,
                    4,
                ),
            "monitoring_closure_risk":
                round(
                    monitoring_closure_risk,
                    4,
                ),
            "invariant_propagation_monitor_index":
                round(
                    invariant_propagation_monitor_index,
                    4,
                ),
            "invariant_propagation_monitor_viable":
                (
                    invariant_propagation_monitor_viable
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)

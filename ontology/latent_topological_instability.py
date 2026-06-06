from __future__ import annotations

from statistics import mean

PRIMITIVE = "latent_topological_instability"

DEPENDENCIES = [
    "structural_anomaly_detection",
    "topology_self_diagnostics",
    "trajectory_metastability",
    "trajectory_criticality",
    "trajectory_phase_transition",
    "trajectory_hysteresis",
    "trajectory_path_dependency",
    "trajectory_irreversibility",
    "distributed_meta_stability",
    "trajectory_regime",
    "trajectory_cascade",
    "semantic_density_tracker",
    "unstable_configuration_principle",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class LatentTopologicalInstability:

    def __init__(
        self,
        latent_instability_threshold: float = 0.62,
        fossilization_threshold: float = 0.78,
    ):
        self.latent_instability_threshold = (
            latent_instability_threshold
        )

        self.fossilization_threshold = (
            fossilization_threshold
        )

        self.history = []

    def step(
        self,
        state=None,
    ):

        state = state or {}

        metastability = _bounded(
            state.get(
                "trajectory_metastability",
                0.0,
            )
        )

        criticality = _bounded(
            state.get(
                "trajectory_criticality",
                0.0,
            )
        )

        phase_transition_pressure = _bounded(
            state.get(
                "trajectory_phase_transition_pressure",
                0.0,
            )
        )

        hysteresis = _bounded(
            state.get(
                "trajectory_hysteresis",
                0.0,
            )
        )

        path_dependency = _bounded(
            state.get(
                "trajectory_path_dependency",
                0.0,
            )
        )

        irreversibility = _bounded(
            state.get(
                "trajectory_irreversibility",
                0.0,
            )
        )

        distributed_meta_stability = _bounded(
            state.get(
                "distributed_meta_stability",
                0.0,
            )
        )

        semantic_density = _bounded(
            state.get(
                "semantic_density",
                0.0,
            )
        )

        rigidity_risk = _bounded(
            state.get(
                "rigidity_risk",
                0.0,
            )
        )

        cascade_risk = _bounded(
            state.get(
                "trajectory_cascade_risk",
                0.0,
            )
        )

        instability_pressure = _bounded(
            mean(
                [
                    criticality,
                    phase_transition_pressure,
                    hysteresis,
                    path_dependency,
                    irreversibility,
                    semantic_density,
                    rigidity_risk,
                    cascade_risk,
                ]
            )
        )

        latent_rigidity = _bounded(
            mean(
                [
                    hysteresis,
                    path_dependency,
                    irreversibility,
                    rigidity_risk,
                ]
            )
        )

        adaptive_plasticity = _bounded(
            mean(
                [
                    metastability,
                    distributed_meta_stability,
                    1.0 - semantic_density,
                    1.0 - rigidity_risk,
                ]
            )
        )

        pre_attractor_formation = _bounded(
            mean(
                [
                    instability_pressure,
                    latent_rigidity,
                    1.0 - adaptive_plasticity,
                ]
            )
        )

        future_space_contraction = _bounded(
            mean(
                [
                    latent_rigidity,
                    semantic_density,
                    path_dependency,
                    irreversibility,
                ]
            )
        )

        latent_topological_instability_index = (
            _bounded(
                mean(
                    [
                        instability_pressure,
                        pre_attractor_formation,
                        future_space_contraction,
                    ]
                )
            )
        )

        instability_state = {
            "latent_topological_instability_index":
                round(
                    latent_topological_instability_index,
                    4,
                ),
            "future_space_contraction":
                round(
                    future_space_contraction,
                    4,
                ),
            "pre_attractor_formation":
                round(
                    pre_attractor_formation,
                    4,
                ),
        }

        self.history.append(
            instability_state
        )

        if len(self.history) > 1000:
            self.history = self.history[-1000:]

        latent_instability_detected = (
            latent_topological_instability_index
            >= self.latent_instability_threshold
        )

        fossilization_risk_detected = (
            future_space_contraction
            >= self.fossilization_threshold
        )

        future_openness_preserved = (
            adaptive_plasticity >= 0.70
        )

        if fossilization_risk_detected:

            classification = (
                "silent_fossilization_risk"
            )

        elif latent_instability_detected:

            classification = (
                "latent_pre_critical_instability"
            )

        elif adaptive_plasticity >= 0.70:

            classification = (
                "open_metastable_viability"
            )

        else:

            classification = (
                "adaptive_transitional_regime"
            )

        return {
            "primitive": PRIMITIVE,
            "classification":
                classification,
            "latent_instability_detected":
                latent_instability_detected,
            "fossilization_risk_detected":
                fossilization_risk_detected,
            "latent_topological_instability_index":
                round(
                    latent_topological_instability_index,
                    4,
                ),
            "future_space_contraction":
                round(
                    future_space_contraction,
                    4,
                ),
            "adaptive_plasticity":
                round(
                    adaptive_plasticity,
                    4,
                ),
            "latent_rigidity":
                round(
                    latent_rigidity,
                    4,
                ),
            "pre_attractor_formation":
                round(
                    pre_attractor_formation,
                    4,
                ),
            "instability_pressure":
                round(
                    instability_pressure,
                    4,
                ),
            "future_openness_preserved":
                future_openness_preserved,
            "history_size":
                len(self.history),
        }

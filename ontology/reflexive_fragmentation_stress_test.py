
import random


class ReflexiveFragmentationStressTest:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def run_stress_cycle(
        self,
        convergence_pressure=0.5,
        fragmentation_noise=0.5,
        symbolic_divergence=0.5,
        duration=10,
    ):

        identity_continuity = 0.92
        pluralistic_stability = 0.91
        closure_pressure_resistance = 0.93

        history = []

        for _ in range(duration):

            perturbation = (
                (
                    fragmentation_noise
                    + symbolic_divergence
                    + convergence_pressure
                ) / 3.0
            )

            adaptive_recovery = random.uniform(
                0.015,
                0.045,
            )

            identity_continuity -= (
                perturbation * 0.025
            )

            pluralistic_stability -= (
                perturbation * 0.02
            )

            closure_pressure_resistance -= (
                convergence_pressure * 0.03
            )

            identity_continuity += adaptive_recovery
            pluralistic_stability += adaptive_recovery
            closure_pressure_resistance += (
                adaptive_recovery * 0.8
            )

            identity_continuity = self._bounded(
                identity_continuity
            )

            pluralistic_stability = self._bounded(
                pluralistic_stability
            )

            closure_pressure_resistance = (
                self._bounded(
                    closure_pressure_resistance
                )
            )

            history.append({
                "identity_continuity":
                    round(
                        identity_continuity,
                        4,
                    ),
                "pluralistic_stability":
                    round(
                        pluralistic_stability,
                        4,
                    ),
                "closure_pressure_resistance":
                    round(
                        closure_pressure_resistance,
                        4,
                    ),
            })

        collapse_detected = (
            identity_continuity < 0.35
        )

        reflexive_viability = (
            identity_continuity >= 0.60
            and pluralistic_stability >= 0.60
        )

        return {
            "identity_continuity":
                round(
                    identity_continuity,
                    4,
                ),
            "pluralistic_stability":
                round(
                    pluralistic_stability,
                    4,
                ),
            "closure_pressure_resistance":
                round(
                    closure_pressure_resistance,
                    4,
                ),
            "collapse_detected":
                collapse_detected,
            "reflexive_viability":
                reflexive_viability,
            "history":
                history,
        }

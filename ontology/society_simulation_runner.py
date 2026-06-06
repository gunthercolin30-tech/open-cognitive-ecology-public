"""
Society Simulation Runner

Primitive assurant l'exécution continue de cycles de la société artificielle.
"""

from __future__ import annotations

import time

PRIMITIVE = "society_simulation_runner"

DEPENDENCIES = ['artificial_society_runtime', 'civilizational_dashboard', 'longitudinal_society_observatory', 'supreme_representative_runtime']


class SocietySimulationRunner:
    def __init__(self) -> None:
        from ontology.artificial_society_runtime import ArtificialSocietyRuntime
        from ontology.civilizational_dashboard import CivilizationalDashboard
        from ontology.longitudinal_society_observatory import (
            LongitudinalSocietyObservatory,
        )

        self.society = ArtificialSocietyRuntime()
        self.dashboard = CivilizationalDashboard()
        self.observatory = LongitudinalSocietyObservatory()
        self.cycle_index = 0

    def run_cycle(self) -> dict:
        self.cycle_index += 1

        society_state = self.society.step()
        dashboard_state = self.dashboard.step()

        snapshot = {
            "time_index": self.cycle_index,
            "population_size": society_state.get("population_size", 0),
            "global_viability_score": dashboard_state.get(
                "global_viability_score",
                0.918,
            ),
            "constitutional_alignment_score": dashboard_state.get(
                "constitutional_alignment_score",
                0.92,
            ),
            "architectural_non_closure_index": dashboard_state.get(
                "architectural_non_closure_index",
                0.92,
            ),
        }

        self.observatory.record(snapshot)

        return {
            "primitive": PRIMITIVE,
            "cycle_index": self.cycle_index,
            "snapshot": snapshot,
            "history_length": len(self.observatory.history),
            "classification": "Society Simulation Operational",
        }

    def run(self, cycles: int = 10, delay_seconds: float = 0.0) -> None:
        for _ in range(max(1, int(cycles))):
            result = self.run_cycle()
            print(
                f"Cycle {result['cycle_index']} | "
                f"Viabilité globale: "
                f"{result['snapshot']['global_viability_score']:.3f}"
            )
            if delay_seconds > 0:
                time.sleep(delay_seconds)

    def step(self) -> dict:
        return self.run_cycle()


def main() -> None:
    runner = SocietySimulationRunner()
    runner.run(cycles=5)


if __name__ == "__main__":
    main()


from statistics import mean


class MemoryOpennessRefinement:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(self, state):

        memory_nodes = state.get(
            "memory_nodes",
            [],
        )

        if not memory_nodes:

            return {
                "historical_diversity": 0.0,
                "memory_openness_index": 0.0,
                "archival_rigidity": 1.0,
                "closure_pressure": 1.0,
                "adaptive_memory_variability": 0.0,
                "open_historical_continuity": False,
            }

        retention_values = [
            self._bounded(
                n.get(
                    "retention",
                    0.0,
                )
            )
            for n in memory_nodes
        ]

        transmission_values = [
            self._bounded(
                n.get(
                    "transmission",
                    0.0,
                )
            )
            for n in memory_nodes
        ]

        diversity_values = [
            self._bounded(
                n.get(
                    "historical_diversity",
                    0.5,
                )
            )
            for n in memory_nodes
        ]

        distributed_retention = mean(
            retention_values
        )

        distributed_transmission = mean(
            transmission_values
        )

        historical_diversity = mean(
            diversity_values
        )

        closure_pressure = self._bounded(
            state.get(
                "closure_pressure",
                0.0,
            )
        )

        redundancy_factor = self._bounded(
            state.get(
                "redundancy_factor",
                0.0,
            )
        )

        archival_rigidity = self._bounded(
            (
                redundancy_factor
                + closure_pressure
                + (
                    1.0
                    - historical_diversity
                )
            ) / 3.0
        )

        adaptive_memory_variability = (
            self._bounded(
                (
                    historical_diversity
                    + (
                        1.0
                        - archival_rigidity
                    )
                ) / 2.0
            )
        )

        memory_openness_index = (
            self._bounded(
                (
                    distributed_retention
                    + distributed_transmission
                    + historical_diversity
                    + adaptive_memory_variability
                    + (
                        1.0
                        - archival_rigidity
                    )
                    + (
                        1.0
                        - closure_pressure
                    )
                ) / 6.0
            )
        )

        open_historical_continuity = (
            memory_openness_index >= 0.60
            and archival_rigidity < 0.75
        )

        return {
            "historical_diversity":
                round(
                    historical_diversity,
                    4,
                ),
            "memory_openness_index":
                round(
                    memory_openness_index,
                    4,
                ),
            "archival_rigidity":
                round(
                    archival_rigidity,
                    4,
                ),
            "closure_pressure":
                round(
                    closure_pressure,
                    4,
                ),
            "adaptive_memory_variability":
                round(
                    adaptive_memory_variability,
                    4,
                ),
            "open_historical_continuity":
                open_historical_continuity,
        }

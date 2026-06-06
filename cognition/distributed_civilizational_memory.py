
from statistics import mean


class DistributedCivilizationalMemory:

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
                "distributed_retention": 0.0,
                "distributed_transmission": 0.0,
                "fragmentation_pressure": 1.0,
                "redundancy_factor": 0.0,
                "archive_integrity": 0.0,
                "distributed_memory_index": 0.0,
                "memory_viability": False,
            }

        distributed_retention = mean([
            self._bounded(
                n.get(
                    "retention",
                    0.0,
                )
            )
            for n in memory_nodes
        ])

        distributed_transmission = mean([
            self._bounded(
                n.get(
                    "transmission",
                    0.0,
                )
            )
            for n in memory_nodes
        ])

        fragmentation_pressure = self._bounded(
            state.get(
                "fragmentation_pressure",
                0.0,
            )
        )

        redundancy_factor = self._bounded(
            state.get(
                "redundancy_factor",
                0.0,
            )
        )

        archive_integrity = self._bounded(
            state.get(
                "archive_integrity",
                0.0,
            )
        )

        closure_pressure = self._bounded(
            state.get(
                "closure_pressure",
                0.0,
            )
        )

        distributed_memory_index = self._bounded(
            (
                distributed_retention
                + distributed_transmission
                + redundancy_factor
                + archive_integrity
                + (1.0 - fragmentation_pressure)
                + (1.0 - closure_pressure)
            ) / 6.0
        )

        memory_viability = (
            distributed_memory_index >= 0.5
        )

        return {
            "distributed_retention":
                round(
                    distributed_retention,
                    4,
                ),
            "distributed_transmission":
                round(
                    distributed_transmission,
                    4,
                ),
            "fragmentation_pressure":
                round(
                    fragmentation_pressure,
                    4,
                ),
            "redundancy_factor":
                round(
                    redundancy_factor,
                    4,
                ),
            "archive_integrity":
                round(
                    archive_integrity,
                    4,
                ),
            "closure_pressure":
                round(
                    closure_pressure,
                    4,
                ),
            "distributed_memory_index":
                round(
                    distributed_memory_index,
                    4,
                ),
            "memory_viability":
                memory_viability,
        }


from statistics import mean

PRIMITIVE = "trajectory_coordination"

DEPENDENCIES = [
    "trajectory_synchronization",
    "constraint_fields",
    "distributed_symbolic_ecology",
    "attractor_desaturation",
    "distributed_historical_mutation",
    "historical_open_endedness",
    "adaptive_ecological_regulation_engine",
    "openness_preservation_supervisor",
    "long_term_coordination",
]


class TrajectoryCoordination:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def step(self, state=None):

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
                x.get(
                    "attractor_density",
                    0.5,
                )
            )
            for x in remote_topologies
        ]

        remote_closure = [
            self._bounded(
                x.get(
                    "closure_pressure",
                    0.5,
                )
            )
            for x in remote_topologies
        ]

        remote_openness = [
            self._bounded(
                x.get(
                    "openness_preservation",
                    0.5,
                )
            )
            for x in remote_topologies
        ]

        density = self._bounded(
            mean(
                [local_density] + remote_density
            )
            if remote_density
            else local_density
        )

        closure = self._bounded(
            mean(
                [local_closure] + remote_closure
            )
            if remote_closure
            else local_closure
        )

        openness = self._bounded(
            mean(
                [local_openness] + remote_openness
            )
            if remote_openness
            else local_openness
        )

        distributed_constraint_orchestration = (
            self._bounded(
                density
                * (
                    1.0
                    - closure
                )
            )
        )

        ecological_alignment = (
            self._bounded(
                (
                    openness
                    + (
                        1.0
                        - closure
                    )
                ) / 2.0
            )
        )

        anti_convergence_capacity = (
            self._bounded(
                openness
                * (
                    1.0
                    - density * 0.5
                )
            )
        )

        distributed_openness_preserved = (
            ecological_alignment >= 0.70
        )

        coordination_class = (
            "distributed_open_coordination"
            if distributed_openness_preserved
            else "fragile_coordination"
        )

        return {
            "primitive": PRIMITIVE,
            "distributed_constraint_orchestration":
                round(
                    distributed_constraint_orchestration,
                    4,
                ),
            "ecological_alignment":
                round(
                    ecological_alignment,
                    4,
                ),
            "anti_convergence_capacity":
                round(
                    anti_convergence_capacity,
                    4,
                ),
            "distributed_openness_preserved":
                distributed_openness_preserved,
            "coordination_class":
                coordination_class,
            "remote_runtime_count":
                len(remote_topologies),
        }

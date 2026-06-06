from runtime.runtime_scheduler_registry import (
    SCHEDULER_REGISTRY,
)

from runtime.scheduler_interaction_registry import (
    SCHEDULER_INTERACTION_REGISTRY,
)


class DistributedSchedulerEcology:

    def list_scheduler_ecology(self):

        return sorted(
            SCHEDULER_REGISTRY.keys()
        )

    def get_interactions(
        self,
        scheduler_name,
    ):

        return (
            SCHEDULER_INTERACTION_REGISTRY.get(
                scheduler_name,
                {},
            )
        )

    def evaluate_ecology(
        self,
        active_schedulers=None,
    ):

        active_schedulers = (
            active_schedulers or []
        )

        interaction_matrix = {}

        coexistence_score = 0.0

        for scheduler in active_schedulers:

            interactions = (
                self.get_interactions(
                    scheduler
                )
            )

            compatible = interactions.get(
                "compatible_with",
                []
            )

            interaction_matrix[
                scheduler
            ] = compatible

            local_score = 0.0

            for other in active_schedulers:

                if other == scheduler:
                    continue

                if other in compatible:
                    local_score += 1.0

            if active_schedulers:

                local_score = (
                    local_score /
                    max(
                        1,
                        len(active_schedulers) - 1
                    )
                )

            coexistence_score += local_score

        if active_schedulers:

            coexistence_score = (
                coexistence_score /
                len(active_schedulers)
            )

        ecological_viability = (
            coexistence_score >= 0.50
        )

        if coexistence_score >= 0.85:

            classification = (
                "fully_pluralistic_scheduler_ecology"
            )

        elif coexistence_score >= 0.50:

            classification = (
                "stable_scheduler_pluralism"
            )

        else:

            classification = (
                "scheduler_fragmentation_risk"
            )

        return {
            "active_schedulers":
                active_schedulers,

            "interaction_matrix":
                interaction_matrix,

            "coexistence_score":
                round(
                    coexistence_score,
                    4
                ),

            "ecological_viability":
                ecological_viability,

            "classification":
                classification,
        }


if __name__ == "__main__":

    ecology = (
        DistributedSchedulerEcology()
    )

    print(
        ecology.list_scheduler_ecology()
    )

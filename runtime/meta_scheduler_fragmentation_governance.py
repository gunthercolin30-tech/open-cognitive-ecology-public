from runtime.meta_scheduler_conflict_registry import (
    META_SCHEDULER_CONFLICT_REGISTRY,
)


class MetaSchedulerFragmentationGovernance:

    def evaluate_conflicts(
        self,
        active_schedulers=None,
    ):

        active_schedulers = (
            active_schedulers or []
        )

        detected_conflicts = []

        coexistence_viability = 1.0

        fragmentation_preserved = True

        for pair, metadata in (
            META_SCHEDULER_CONFLICT_REGISTRY.items()
        ):

            scheduler_a, scheduler_b = pair

            if (
                scheduler_a in active_schedulers
                and scheduler_b in active_schedulers
            ):

                detected_conflicts.append(
                    {
                        "pair": pair,
                        "metadata": metadata,
                    }
                )

                if metadata.get(
                    "forced_unification"
                ):

                    fragmentation_preserved = False

                    coexistence_viability *= 0.25

                else:

                    coexistence_viability *= 0.85

        coexistence_viability = max(
            0.0,
            min(
                1.0,
                coexistence_viability,
            ),
        )

        if coexistence_viability >= 0.85:

            classification = (
                "stable_meta_scheduler_pluralism"
            )

        elif coexistence_viability >= 0.50:

            classification = (
                "viable_fragmented_scheduler_ecology"
            )

        else:

            classification = (
                "meta_scheduler_fragmentation_risk"
            )

        return {
            "active_schedulers":
                active_schedulers,

            "detected_conflicts":
                detected_conflicts,

            "coexistence_viability":
                round(
                    coexistence_viability,
                    4,
                ),

            "fragmentation_preserved":
                fragmentation_preserved,

            "classification":
                classification,
        }


if __name__ == "__main__":

    governance = (
        MetaSchedulerFragmentationGovernance()
    )

    print(
        governance.evaluate_conflicts(
            [
                "fragmented_resilience_scheduler",
                "historical_divergence_scheduler",
            ]
        )
    )

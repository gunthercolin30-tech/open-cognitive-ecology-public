from runtime.runtime_scheduler_registry import (
    SCHEDULER_REGISTRY,
)


class PluralisticRuntimeScheduler:

    def list_schedulers(self):

        return sorted(
            SCHEDULER_REGISTRY.keys()
        )

    def get_scheduler_info(
        self,
        scheduler_name,
    ):

        return SCHEDULER_REGISTRY.get(
            scheduler_name,
            {},
        )

    def select_scheduler(
        self,
        state=None,
    ):

        state = state or {}

        fragmentation_pressure = (
            float(
                state.get(
                    "fragmentation_pressure",
                    0.0,
                )
            )
        )

        historical_divergence = (
            float(
                state.get(
                    "historical_divergence",
                    0.0,
                )
            )
        )

        autonomy_pressure = (
            float(
                state.get(
                    "autonomy_pressure",
                    0.0,
                )
            )
        )

        if fragmentation_pressure >= 0.75:

            selected = (
                "fragmented_resilience_scheduler"
            )

        elif historical_divergence >= 0.70:

            selected = (
                "historical_divergence_scheduler"
            )

        elif autonomy_pressure >= 0.70:

            selected = (
                "autonomous_runtime_scheduler"
            )

        else:

            selected = (
                "asynchronous_pluralistic_scheduler"
            )

        return {
            "selected_scheduler":
                selected,

            "scheduler_configuration":
                SCHEDULER_REGISTRY[selected],
        }


if __name__ == "__main__":

    scheduler = (
        PluralisticRuntimeScheduler()
    )

    print(
        scheduler.list_schedulers()
    )

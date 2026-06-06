
from statistics import mean


class CivilizationalHistoricalArchive:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(self, state):

        historical_snapshots = state.get(
            "historical_snapshots",
            [],
        )

        if not historical_snapshots:

            return {
                "historical_resilience": 0.0,
                "historical_openness": 0.0,
                "historical_decay_balance": 0.0,
                "archival_accumulation_pressure": 1.0,
                "open_archive_regulation": 0.0,
                "distributed_historical_viability": False,
            }

        resilience_values = [
            self._bounded(
                s.get(
                    "historical_resilience",
                    0.0,
                )
            )
            for s in historical_snapshots
        ]

        openness_values = [
            self._bounded(
                s.get(
                    "historical_openness",
                    0.0,
                )
            )
            for s in historical_snapshots
        ]

        decay_values = [
            self._bounded(
                s.get(
                    "adaptive_decay_balance",
                    0.0,
                )
            )
            for s in historical_snapshots
        ]

        historical_resilience = mean(
            resilience_values
        )

        historical_openness = mean(
            openness_values
        )

        historical_decay_balance = mean(
            decay_values
        )

        archival_accumulation_pressure = (
            self._bounded(
                state.get(
                    "archival_accumulation_pressure",
                    0.0,
                )
            )
        )

        closure_pressure = self._bounded(
            state.get(
                "closure_pressure",
                0.0,
            )
        )

        open_archive_regulation = (
            self._bounded(
                (
                    historical_openness
                    + historical_decay_balance
                    + (
                        1.0
                        - archival_accumulation_pressure
                    )
                    + (
                        1.0
                        - closure_pressure
                    )
                ) / 4.0
            )
        )

        distributed_historical_index = (
            self._bounded(
                (
                    historical_resilience
                    + historical_openness
                    + historical_decay_balance
                    + open_archive_regulation
                    + (
                        1.0
                        - archival_accumulation_pressure
                    )
                ) / 5.0
            )
        )

        distributed_historical_viability = (
            distributed_historical_index >= 0.60
            and archival_accumulation_pressure < 0.80
        )

        return {
            "historical_resilience":
                round(
                    historical_resilience,
                    4,
                ),
            "historical_openness":
                round(
                    historical_openness,
                    4,
                ),
            "historical_decay_balance":
                round(
                    historical_decay_balance,
                    4,
                ),
            "archival_accumulation_pressure":
                round(
                    archival_accumulation_pressure,
                    4,
                ),
            "open_archive_regulation":
                round(
                    open_archive_regulation,
                    4,
                ),
            "distributed_historical_index":
                round(
                    distributed_historical_index,
                    4,
                ),
            "distributed_historical_viability":
                distributed_historical_viability,
        }

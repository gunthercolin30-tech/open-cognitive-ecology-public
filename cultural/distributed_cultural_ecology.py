# cultural/distributed_cultural_ecology.py

from cultural.local_cultural_regime import (
    LocalCulturalRegime,
)


class DistributedCulturalEcology:
    """
    Distributed ecology of local cultural regimes.

    This module models:

    - multiple local cultures
    - coexistence of incompatible narratives
    - uneven symbolic transmission
    - asynchronous innovation
    - cultural divergence
    - fragmentation and disappearance

    There is:
    - no universal culture
    - no global synthesis
    - no final convergence
    """

    def __init__(
        self,
        culture_count=4,
    ):
        self.cultural_regimes = []

        # =====================================================
        # DISTRIBUTED CULTURAL ECOLOGY
        # =====================================================

        for i in range(culture_count):
            regime = LocalCulturalRegime(
                name=f"culture_{i}"
            )
            self.cultural_regimes.append(regime)

    # =========================================================
    # GLOBAL STEP
    # =========================================================

    def step(self):
        """
        Advance all local cultural regimes independently.
        """

        for regime in self.cultural_regimes:
            regime.step()

    # =========================================================
    # STATE ACCESS
    # =========================================================

    def get_states(self):
        return [
            regime.get_state()
            for regime in self.cultural_regimes
        ]

    def get_alive_count(self):
        return sum(
            1
            for regime in self.cultural_regimes
            if regime.alive
        )

    def get_average_fragmentation(self):
        if not self.cultural_regimes:
            return 0.0

        return (
            sum(
                regime.fragmentation
                for regime in self.cultural_regimes
            )
            / len(self.cultural_regimes)
        )

    def get_average_memory(self):
        if not self.cultural_regimes:
            return 0.0

        return (
            sum(
                regime.cultural_memory
                for regime in self.cultural_regimes
            )
            / len(self.cultural_regimes)
        )

    # =========================================================
    # DEBUG
    # =========================================================

    def debug_print(self):
        print(
            "[DISTRIBUTED_CULTURAL_ECOLOGY]",
            f"alive={self.get_alive_count()}",
            f"fragmentation={self.get_average_fragmentation():.2f}",
            f"memory={self.get_average_memory():.2f}",
        )
# economy/distributed_economic_ecology.py

import random

from economy.local_resource_regime import (
    LocalResourceRegime,
)


class DistributedEconomicEcology:
    """
    Distributed economic ecology.

    This structure contains multiple incompatible local
    economic regimes.

    There is:
    - no global market
    - no universal currency
    - no central regulator
    - only partial and unstable interdependencies
    """

    def __init__(
        self,
        regime_count=4,
    ):
        # =====================================================
        # LOCAL ECONOMIC REGIMES
        # =====================================================

        self.resource_regimes = []

        for i in range(regime_count):
            regime = LocalResourceRegime(
                resource_name=f"resource_{i}"
            )
            self.resource_regimes.append(regime)

        # =====================================================
        # DISTRIBUTED HISTORY
        # =====================================================

        self.age = 0
        self.last_crisis = False
        self.crisis_count = 0

    # =========================================================
    # LOCAL UPDATES
    # =========================================================

    def update_regimes(self):
        """
        Update every local economic regime independently.
        """

        for regime in self.resource_regimes:
            regime.update()

    # =========================================================
    # ASYMMETRIC EXCHANGES
    # =========================================================

    def apply_exchanges(self):
        """
        Partial and unstable exchanges between regimes.
        No universal market exists.
        """

        n = len(self.resource_regimes)

        if n < 2:
            return

        for _ in range(n):
            source = random.choice(
                self.resource_regimes
            )
            target = random.choice(
                self.resource_regimes
            )

            if source is target:
                continue

            source_state = source.get_state()
            target_state = target.get_state()

            abundance_gap = (
                source_state["abundance"]
                - target_state["abundance"]
            )

            if abundance_gap <= 0.05:
                continue

            transfer = min(
                source.resource_stock
                * random.uniform(0.01, 0.05),
                source.resource_stock,
            )

            source.resource_stock -= transfer
            target.resource_stock += transfer

            target.resource_stock = min(
                target.resource_stock,
                target.max_resource_stock,
            )

    # =========================================================
    # ECONOMIC PREDATION
    # =========================================================

    def apply_predation(self):
        """
        Scarce regimes may aggressively extract resources
        from more abundant neighbors.
        """

        n = len(self.resource_regimes)

        if n < 2:
            return

        for regime in self.resource_regimes:
            state = regime.get_state()

            if state["scarcity"] < 0.75:
                continue

            prey = random.choice(
                self.resource_regimes
            )

            if prey is regime:
                continue

            prey_state = prey.get_state()

            if prey_state["abundance"] < 0.35:
                continue

            stolen = min(
                prey.resource_stock
                * random.uniform(0.02, 0.08),
                prey.resource_stock,
            )

            prey.resource_stock -= stolen
            regime.resource_stock += stolen

            regime.resource_stock = min(
                regime.resource_stock,
                regime.max_resource_stock,
            )

    # =========================================================
    # DISTRIBUTED CRISES
    # =========================================================

    def update_crisis(self):
        """
        Detect emergent distributed crises.
        """

        self.last_crisis = False

        if not self.resource_regimes:
            return

        collapse_count = sum(
            1
            for regime in self.resource_regimes
            if regime.last_collapse
        )

        if collapse_count >= max(
            1,
            len(self.resource_regimes) // 2,
        ):
            self.last_crisis = True
            self.crisis_count += 1

            for regime in self.resource_regimes:
                regime.economic_fragility = (
                    regime._clamp(
                        regime.economic_fragility
                        + 0.05,
                        0.0,
                        1.0,
                    )
                )

    # =========================================================
    # MAIN UPDATE
    # =========================================================

    def update(self):
        """
        Execute one distributed economic cycle.
        """

        self.age += 1

        self.update_regimes()
        self.apply_exchanges()
        self.apply_predation()
        self.update_crisis()

    # =========================================================
    # STATE EXPORT
    # =========================================================

    def get_state(self):
        """
        Export distributed economic state.
        """

        return {
            "age": self.age,
            "regime_count": len(
                self.resource_regimes
            ),
            "last_crisis": self.last_crisis,
            "crisis_count": self.crisis_count,
            "regimes": [
                regime.get_state()
                for regime in self.resource_regimes
            ],
        }
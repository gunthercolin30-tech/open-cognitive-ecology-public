# economy/local_resource_regime.py

import random


class LocalResourceRegime:
    """
    Local economic regime.

    This object models a strictly local and historically unstable
    resource organization.

    It contains:
    - local resource stocks
    - abundance and scarcity
    - extraction and regeneration
    - production and consumption
    - economic tensions and collapses

    There is:
    - no central bank
    - no universal currency
    - no global market
    - no stable equilibrium
    - no guaranteed prosperity
    """

    def __init__(self, resource_name="generic_resource"):
        # =====================================================
        # RESOURCE IDENTITY
        # =====================================================

        self.resource_name = resource_name

        # =====================================================
        # RESOURCE STOCK
        # =====================================================

        self.resource_stock = random.uniform(40.0, 120.0)
        self.max_resource_stock = random.uniform(120.0, 250.0)

        # =====================================================
        # LOCAL ECONOMIC FLOWS
        # =====================================================

        self.extraction_rate = random.uniform(0.5, 3.0)
        self.regeneration_rate = random.uniform(0.2, 2.0)

        self.production_rate = random.uniform(0.3, 2.5)
        self.consumption_rate = random.uniform(0.3, 2.5)

        # =====================================================
        # ECONOMIC CONDITIONS
        # =====================================================

        self.abundance = 0.0
        self.scarcity = 0.0

        self.resource_pressure = 0.0
        self.economic_stress = 0.0
        self.economic_fragility = random.uniform(0.1, 0.5)

        # =====================================================
        # COLLAPSE DYNAMICS
        # =====================================================

        self.collapse_risk = 0.0
        self.collapse_count = 0
        self.last_collapse = False

        # =====================================================
        # DISSIPATIVE HISTORY
        # =====================================================

        self.age = 0
        self.total_extracted = 0.0
        self.total_regenerated = 0.0
        self.total_produced = 0.0
        self.total_consumed = 0.0

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================

    def _clamp(self, value, minimum, maximum):
        return max(minimum, min(maximum, value))
        # =========================================================
    # RESOURCE REGENERATION
    # =========================================================

    def regenerate(self):
        """
        Local resources regenerate according to:
        - environmental capacity
        - depletion level
        - historical instability
        """

        regeneration_efficiency = 1.0 - (
            self.resource_stock / max(self.max_resource_stock, 1e-6)
        )
        regeneration_efficiency = self._clamp(
            regeneration_efficiency,
            0.0,
            1.0,
        )

        regenerated = (
            self.regeneration_rate
            * regeneration_efficiency
            * random.uniform(0.7, 1.3)
        )

        self.resource_stock += regenerated
        self.resource_stock = self._clamp(
            self.resource_stock,
            0.0,
            self.max_resource_stock,
        )

        self.total_regenerated += regenerated

    # =========================================================
    # RESOURCE EXTRACTION
    # =========================================================

    def extract(self):
        """
        Local actors extract resources under scarcity pressure.
        """

        scarcity_pressure = 1.0 + self.scarcity * 1.5

        extracted = (
            self.extraction_rate
            * scarcity_pressure
            * random.uniform(0.7, 1.3)
        )

        extracted = min(extracted, self.resource_stock)

        self.resource_stock -= extracted
        self.total_extracted += extracted

        return extracted

    # =========================================================
    # PRODUCTION
    # =========================================================

    def produce(self, extracted):
        """
        Production transforms extracted resources into usable output.
        """

        efficiency = random.uniform(0.5, 1.5)

        produced = extracted * self.production_rate * 0.3 * efficiency

        self.total_produced += produced

        return produced

    # =========================================================
    # CONSUMPTION
    # =========================================================

    def consume(self, produced):
        """
        Local consumption dissipates produced wealth.
        """

        demand_pressure = 1.0 + self.economic_stress

        consumed = (
            self.consumption_rate
            * demand_pressure
            * random.uniform(0.7, 1.3)
        )

        consumed = min(consumed, produced)

        self.total_consumed += consumed

        return consumed
        # =========================================================
    # ECONOMIC CONDITIONS
    # =========================================================

    def update_conditions(self):
        """
        Compute local abundance, scarcity and systemic stress.
        """

        stock_ratio = self.resource_stock / max(
            self.max_resource_stock,
            1e-6,
        )

        self.abundance = self._clamp(stock_ratio, 0.0, 1.0)
        self.scarcity = 1.0 - self.abundance

        self.resource_pressure = self.scarcity

        flow_imbalance = abs(
            self.total_produced - self.total_consumed
        ) / max(self.total_produced + 1.0, 1.0)

        self.economic_stress = self._clamp(
            (
                0.45 * self.scarcity
                + 0.35 * flow_imbalance
                + 0.20 * self.economic_fragility
            ),
            0.0,
            1.0,
        )

        self.collapse_risk = self._clamp(
            (
                0.55 * self.scarcity
                + 0.30 * self.economic_stress
                + 0.15 * self.economic_fragility
            ),
            0.0,
            1.0,
        )

    # =========================================================
    # ECONOMIC COLLAPSE
    # =========================================================

    def check_collapse(self):
        """
        Local regimes may collapse under scarcity and stress.
        """

        self.last_collapse = False

        collapse_threshold = 0.82

        if self.collapse_risk > collapse_threshold:
            probability = (
                (self.collapse_risk - collapse_threshold)
                / (1.0 - collapse_threshold)
            )

            if random.random() < probability:
                self.last_collapse = True
                self.collapse_count += 1

                self.resource_stock *= random.uniform(0.15, 0.45)
                self.max_resource_stock *= random.uniform(0.85, 0.98)

                self.extraction_rate *= random.uniform(0.6, 0.9)
                self.production_rate *= random.uniform(0.5, 0.85)
                self.consumption_rate *= random.uniform(0.6, 0.9)

                self.economic_fragility = self._clamp(
                    self.economic_fragility
                    + random.uniform(0.05, 0.20),
                    0.0,
                    1.0,
                )

    # =========================================================
    # MAIN UPDATE
    # =========================================================

    def update(self):
        """
        Execute one local economic cycle.
        """

        self.age += 1

        self.regenerate()

        extracted = self.extract()
        produced = self.produce(extracted)
        self.consume(produced)

        self.update_conditions()
        self.check_collapse()

        self.economic_fragility = self._clamp(
            self.economic_fragility
            + random.uniform(-0.01, 0.01),
            0.0,
            1.0,
        )

    # =========================================================
    # STATE EXPORT
    # =========================================================

    def get_state(self):
        """
        Export current regime state.
        """

        return {
            "resource_name": self.resource_name,
            "age": self.age,
            "resource_stock": self.resource_stock,
            "max_resource_stock": self.max_resource_stock,
            "abundance": self.abundance,
            "scarcity": self.scarcity,
            "resource_pressure": self.resource_pressure,
            "economic_stress": self.economic_stress,
            "economic_fragility": self.economic_fragility,
            "collapse_risk": self.collapse_risk,
            "collapse_count": self.collapse_count,
            "last_collapse": self.last_collapse,
            "total_extracted": self.total_extracted,
            "total_regenerated": self.total_regenerated,
            "total_produced": self.total_produced,
            "total_consumed": self.total_consumed,
        }
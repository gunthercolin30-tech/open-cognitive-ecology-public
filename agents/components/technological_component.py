# agents/components/technological_component.py

import random


class TechnologicalComponent:
    """
    Local technological ecology.

    This component models:
    - tool accumulation
    - infrastructure dependence
    - innovation potential
    - technological obsolescence
    - adoption dynamics
    - interoperability
    - technical fragility
    - lock-in effects

    No universal technology.
    No final platform.
    No globally stable infrastructure.
    """

    def __init__(self):
        # =====================================================
        # TECHNOLOGICAL CAPITAL
        # =====================================================

        self.technological_capital = random.uniform(
            0.2,
            1.0,
        )

        self.infrastructure_dependence = random.uniform(
            0.0,
            1.0,
        )

        self.innovation_potential = random.uniform(
            0.0,
            1.0,
        )

        self.obsolescence = random.uniform(
            0.0,
            0.3,
        )

        self.adoption_capacity = random.uniform(
            0.0,
            1.0,
        )

        self.interoperability = random.uniform(
            0.0,
            1.0,
        )

        self.technical_fragility = random.uniform(
            0.0,
            1.0,
        )

        self.lock_in = random.uniform(
            0.0,
            1.0,
        )

        # =====================================================
        # DERIVED DYNAMICS
        # =====================================================

        self.technological_stability = 1.0
        self.technological_pressure = 0.0
        self.innovation_flow = 0.0
        self.upgrade_need = 0.0
        self.infrastructure_resilience = 1.0

    # =========================================================
    # UPDATE
    # =========================================================

    def update_technological_dynamics(self):
        """
        Update local technological variables.
        """

        self.obsolescence += random.uniform(
            -0.01,
            0.03,
        )
        self.obsolescence = max(
            0.0,
            min(
                1.0,
                self.obsolescence,
            ),
        )

        self.innovation_flow = (
            self.innovation_potential
            * self.adoption_capacity
            * (1.0 - self.lock_in)
        )

        self.upgrade_need = (
            self.obsolescence
            * self.infrastructure_dependence
        )

        self.technological_pressure = (
            self.upgrade_need
            + self.technical_fragility
            + self.lock_in * 0.5
        )

        self.infrastructure_resilience = max(
            0.0,
            1.0
            - (
                self.technical_fragility * 0.5
                + self.obsolescence * 0.4
            ),
        )

        self.technological_stability = max(
            0.0,
            self.technological_capital
            + self.innovation_flow * 0.5
            + self.interoperability * 0.3
            + self.infrastructure_resilience * 0.4
            - self.technological_pressure * 0.4,
        )
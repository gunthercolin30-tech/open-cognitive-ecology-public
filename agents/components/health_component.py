# agents/components/health_component.py

import random


class HealthComponent:
    """
    Local health and biological dynamics.

    This component encapsulates:
    - health state
    - immunity
    - physiological fatigue
    - contagion load
    - healthcare access
    - biological resilience
    - mortality risk
    - health fragmentation
    - local health collapses

    No perfect health.
    No universal immunity.
    No guaranteed survival.
    """

    def __init__(self):
        # =====================================================
        # CORE HEALTH VARIABLES
        # =====================================================

        # General health condition
        self.health_state = random.uniform(0.6, 1.0)

        # Immune efficiency
        self.immunity = random.uniform(0.3, 1.0)

        # Physiological exhaustion
        self.physiological_fatigue = random.uniform(0.0, 0.3)

        # Infectious burden
        self.contagion_load = random.uniform(0.0, 0.1)

        # Access to local care structures
        self.healthcare_access = random.uniform(0.2, 1.0)

        # Capacity to recover from perturbations
        self.biological_resilience = random.uniform(0.3, 1.0)

        # Probability-like mortality indicator
        self.mortality_risk = 0.0

        # Degree of sanitary instability
        self.health_fragmentation = 0.0

        # Number of severe collapses
        self.health_collapses = 0

    def update(self):
        """
        Update local health dynamics.
        """

        # =====================================================
        # FATIGUE EVOLUTION
        # =====================================================

        fatigue_delta = (
            0.05 * self.contagion_load
            - 0.03 * self.biological_resilience
        )

        self.physiological_fatigue += fatigue_delta
        self.physiological_fatigue = max(
            0.0,
            min(1.0, self.physiological_fatigue),
        )

        # =====================================================
        # IMMUNITY EVOLUTION
        # =====================================================

        immunity_delta = (
            0.02 * self.biological_resilience
            + 0.01 * self.healthcare_access
            - 0.04 * self.physiological_fatigue
        )

        self.immunity += immunity_delta
        self.immunity = max(
            0.0,
            min(1.0, self.immunity),
        )

        # =====================================================
        # CONTAGION EVOLUTION
        # =====================================================

        contagion_delta = (
            0.05 * (1.0 - self.immunity)
            - 0.03 * self.healthcare_access
            + random.uniform(-0.01, 0.01)
        )

        self.contagion_load += contagion_delta
        self.contagion_load = max(
            0.0,
            min(1.0, self.contagion_load),
        )

        # =====================================================
        # HEALTH STATE EVOLUTION
        # =====================================================

        health_delta = (
            0.03 * self.immunity
            + 0.03 * self.healthcare_access
            + 0.03 * self.biological_resilience
            - 0.05 * self.contagion_load
            - 0.05 * self.physiological_fatigue
        )

        self.health_state += health_delta
        self.health_state = max(
            0.0,
            min(1.0, self.health_state),
        )

        # =====================================================
        # MORTALITY RISK
        # =====================================================

        self.mortality_risk = max(
            0.0,
            min(
                1.0,
                (
                    0.5 * (1.0 - self.health_state)
                    + 0.3 * self.contagion_load
                    + 0.2 * self.physiological_fatigue
                ),
            ),
        )

        # =====================================================
        # HEALTH FRAGMENTATION
        # =====================================================

        self.health_fragmentation = max(
            0.0,
            min(
                1.0,
                (
                    0.4 * self.contagion_load
                    + 0.3 * self.physiological_fatigue
                    + 0.3 * self.mortality_risk
                ),
            ),
        )

        # =====================================================
        # COLLAPSE DETECTION
        # =====================================================

        if (
            self.health_state < 0.15
            and self.mortality_risk > 0.85
        ):
            self.health_collapses += 1

            self.health_state = random.uniform(0.2, 0.5)
            self.immunity = random.uniform(0.1, 0.4)
            self.physiological_fatigue = random.uniform(0.4, 0.8)
            self.contagion_load = random.uniform(0.1, 0.5)
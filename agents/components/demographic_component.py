# agents/components/demographic_component.py

import random


class DemographicComponent:
    """
    Local demographic dynamics.

    This component models:
    - age
    - ageing
    - fertility
    - reproductive maturity
    - mortality risk
    - birth potential
    - generation turnover
    - population pressure

    No immortal agents.
    No fixed population.
    No stable demographic equilibrium.
    """

    def __init__(self):
        # =====================================================
        # AGE STRUCTURE
        # =====================================================

        # Biological age in years.
        self.age = random.uniform(0.0, 80.0)

        # Expected lifespan.
        self.life_expectancy = random.uniform(60.0, 95.0)

        # Age increment per simulation cycle.
        # One cycle represents a fraction of a year.
        self.ageing_rate = random.uniform(0.05, 0.20)

        # =====================================================
        # REPRODUCTIVE PARAMETERS
        # =====================================================

        # Reproductive age interval.
        self.reproductive_age_min = random.uniform(16.0, 22.0)
        self.reproductive_age_max = random.uniform(35.0, 50.0)

        # Intrinsic fertility.
        self.fertility = random.uniform(0.2, 1.0)

        # Probability scale for births.
        self.base_birth_rate = random.uniform(0.001, 0.02)

        # =====================================================
        # DEMOGRAPHIC INDICATORS
        # =====================================================

        # Instantaneous mortality risk.
        self.mortality_risk = 0.0

        # Current birth potential.
        self.birth_potential = 0.0

        # Generation number estimate.
        self.generation_index = int(self.age // 25)

        # Local demographic pressure.
        self.population_pressure = random.uniform(0.0, 1.0)

        # Number of offspring produced.
        self.offspring_count = 0

        # Whether the agent is alive.
        self.is_alive = True

        # Whether the agent can reproduce.
        self.is_reproductive = False

        # =====================================================
        # HISTORY
        # =====================================================

        self.demographic_fragility = 0.0
        self.longevity_margin = 0.0

    # =========================================================
    # CORE UPDATE
    # =========================================================

    def update(self):
        """
        Update local demographic state.
        """

        if not self.is_alive:
            return

        # -----------------------------------------------------
        # AGEING
        # -----------------------------------------------------

        self.age += self.ageing_rate

        # -----------------------------------------------------
        # REPRODUCTIVE STATUS
        # -----------------------------------------------------

        self.is_reproductive = (
            self.reproductive_age_min
            <= self.age
            <= self.reproductive_age_max
        )

        # -----------------------------------------------------
        # LONGEVITY MARGIN
        # -----------------------------------------------------

        self.longevity_margin = (
            self.life_expectancy - self.age
        )

        # -----------------------------------------------------
        # MORTALITY RISK
        # -----------------------------------------------------

        if self.age < self.life_expectancy:
            ratio = self.age / max(self.life_expectancy, 1e-6)
            self.mortality_risk = ratio ** 4
        else:
            excess = self.age - self.life_expectancy
            self.mortality_risk = min(
                1.0,
                0.5 + 0.1 * excess,
            )

        # -----------------------------------------------------
        # BIRTH POTENTIAL
        # -----------------------------------------------------

        if self.is_reproductive:
            age_center = (
                self.reproductive_age_min
                + self.reproductive_age_max
            ) / 2.0

            age_span = max(
                (
                    self.reproductive_age_max
                    - self.reproductive_age_min
                )
                / 2.0,
                1e-6,
            )

            age_factor = max(
                0.0,
                1.0
                - abs(self.age - age_center)
                / age_span,
            )

            self.birth_potential = (
                self.fertility
                * self.base_birth_rate
                * age_factor
                * (1.0 - self.population_pressure)
            )
        else:
            self.birth_potential = 0.0

        # -----------------------------------------------------
        # GENERATION INDEX
        # -----------------------------------------------------

        self.generation_index = int(self.age // 25)

        # -----------------------------------------------------
        # FRAGILITY
        # -----------------------------------------------------

        self.demographic_fragility = (
            self.mortality_risk
            + max(0.0, -self.longevity_margin / 10.0)
        )

        # -----------------------------------------------------
        # DEATH
        # -----------------------------------------------------

        if random.random() < self.mortality_risk:
            self.is_alive = False

    # =========================================================
    # BIRTH DECISION
    # =========================================================

    def can_give_birth(self):
        """
        Determine whether a birth occurs during this cycle.
        """

        if not self.is_alive:
            return False

        if self.birth_potential <= 0.0:
            return False

        if random.random() < self.birth_potential:
            self.offspring_count += 1
            return True

        return False

    # =========================================================
    # PRESSURE UPDATE
    # =========================================================

    def set_population_pressure(self, pressure):
        """
        Update local population pressure.
        """

        self.population_pressure = max(
            0.0,
            min(1.0, pressure),
        )

    # =========================================================
    # LIFE RESET
    # =========================================================

    def reset_as_newborn(self):
        """
        Reinitialize this component as a newborn agent.
        """

        self.age = 0.0
        self.life_expectancy = random.uniform(60.0, 95.0)
        self.ageing_rate = random.uniform(0.05, 0.20)

        self.reproductive_age_min = random.uniform(16.0, 22.0)
        self.reproductive_age_max = random.uniform(35.0, 50.0)

        self.fertility = random.uniform(0.2, 1.0)
        self.base_birth_rate = random.uniform(0.001, 0.02)

        self.mortality_risk = 0.0
        self.birth_potential = 0.0
        self.generation_index = 0
        self.population_pressure = 0.0
        self.offspring_count = 0

        self.is_alive = True
        self.is_reproductive = False

        self.demographic_fragility = 0.0
        self.longevity_margin = self.life_expectancy
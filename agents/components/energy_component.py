# agents/components/energy_component.py


class EnergyComponent:
    """
    Agent-level energetic dynamics.

    Tracks:
    - available energy reserve
    - fatigue accumulation
    - exhaustion
    - survival under energetic stress
    - depletion state

    All values are normalized in [0, 1] whenever possible.
    """

    def __init__(
        self,
        initial_energy=1.0,
        initial_fatigue=0.0,
    ):
        # Core energetic variables
        self.energy_reserve = max(
            0.0,
            min(1.0, initial_energy),
        )

        self.fatigue = max(
            0.0,
            min(1.0, initial_fatigue),
        )

        self.exhaustion = 0.0

        # Resource accessibility
        self.resource_access = 1.0

        # External pressure
        self.energy_pressure = 0.0

        # State indicators
        self.is_energy_depleted = False
        self.is_alive = True

    # =====================================================
    # MAIN UPDATE
    # =====================================================

    def update(
        self,
        metabolic_cost=0.02,
        environmental_gain=0.01,
        recovery_factor=0.02,
    ):
        """
        Update energetic state.
        """

        if not self.is_alive:
            return

        # Net balance
        net_gain = (
            environmental_gain
            * self.resource_access
        )

        net_cost = (
            metabolic_cost
            * (1.0 + self.energy_pressure)
        )

        self.energy_reserve += net_gain
        self.energy_reserve -= net_cost

        # Clamp reserve
        self.energy_reserve = max(
            0.0,
            min(1.0, self.energy_reserve),
        )

        # Fatigue dynamics
        if self.energy_reserve < 0.3:
            self.fatigue += (
                0.05
                + self.energy_pressure * 0.05
            )
        else:
            self.fatigue -= recovery_factor

        self.fatigue = max(
            0.0,
            min(1.0, self.fatigue),
        )

        # Exhaustion synthesis
        self.exhaustion = min(
            1.0,
            0.6 * self.fatigue
            + 0.4 * (1.0 - self.energy_reserve),
        )

        # Depletion flag
        self.is_energy_depleted = (
            self.energy_reserve <= 0.05
        )

        # Energetic death condition
        if (
            self.energy_reserve <= 0.0
            and self.fatigue >= 1.0
        ):
            self.is_alive = False

    # =====================================================
    # ENVIRONMENTAL COUPLING
    # =====================================================

    def set_resource_access(
        self,
        value,
    ):
        """
        Set resource accessibility in [0, 1].
        """

        self.resource_access = max(
            0.0,
            min(1.0, value),
        )

    def set_energy_pressure(
        self,
        value,
    ):
        """
        Set energetic pressure in [0, 1].
        """

        self.energy_pressure = max(
            0.0,
            min(1.0, value),
        )

    def apply_resource_constraint(
        self,
        environment_factor,
    ):
        """
        Compatibility method used by
        EnergyEcologyProcess.

        environment_factor:
        - 1.0 = normal conditions
        - <1.0 = scarcity
        - >1.0 = abundance
        """

        environment_factor = max(
            0.0,
            min(2.0, environment_factor),
        )

        # Convert to normalized resource accessibility
        self.set_resource_access(
            min(1.0, environment_factor)
        )

        # Scarcity increases pressure
        if environment_factor < 1.0:
            self.set_energy_pressure(
                1.0 - environment_factor
            )
        else:
            self.set_energy_pressure(0.0)

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):
        """
        Restore a healthy energetic state.
        """

        self.energy_reserve = 1.0
        self.fatigue = 0.0
        self.exhaustion = 0.0
        self.resource_access = 1.0
        self.energy_pressure = 0.0
        self.is_energy_depleted = False
        self.is_alive = True
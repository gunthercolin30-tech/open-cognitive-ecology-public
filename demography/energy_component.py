# agents/components/demography/energy_component.py


class EnergyComponent:
    """
    Local energetic state of an agent.

    This component models:
    - internal energy reserves
    - consumption dynamics
    - recovery processes
    - fatigue accumulation
    - resource access constraints
    - exhaustion thresholds
    - energy-related mortality condition
    """

    def __init__(
        self,
        energy_reserve: float = 1.0,
        max_energy: float = 1.0,
        energy_consumption: float = 0.01,
        energy_recovery: float = 0.005,
        resource_access: float = 1.0,
        exhaustion_threshold: float = 0.05,
    ):
        # Core energetic state
        self.energy_reserve = energy_reserve
        self.max_energy = max_energy

        # Dynamics
        self.energy_consumption = energy_consumption
        self.energy_recovery = energy_recovery

        # Access to external energy sources
        self.resource_access = resource_access

        # Derived state variables
        self.fatigue = 0.0
        self.energy_stress = 0.0
        self.exhaustion = 0.0

        # Thresholds
        self.exhaustion_threshold = exhaustion_threshold

        # State flags
        self.is_energy_depleted = False
        self.is_alive = True

    # ---------------------------------------------------------
    # Core update dynamics
    # ---------------------------------------------------------

    def consume(self, activity_intensity: float = 1.0):
        """
        Energy consumption due to activity.
        """
        if not self.is_alive:
            return

        cost = self.energy_consumption * activity_intensity
        self.energy_reserve -= cost

        if self.energy_reserve < 0:
            self.energy_reserve = 0

        self._update_state_after_consumption()

    def recover(self, environment_energy_factor: float = 1.0):
        """
        Energy recovery from environment/resources.
        """
        if not self.is_alive:
            return

        gain = self.energy_recovery * self.resource_access * environment_energy_factor
        self.energy_reserve += gain

        if self.energy_reserve > self.max_energy:
            self.energy_reserve = self.max_energy

        self._update_state_after_recovery()

    # ---------------------------------------------------------
    # Internal state dynamics
    # ---------------------------------------------------------

    def _update_state_after_consumption(self):
        self._update_fatigue()
        self._update_exhaustion()
        self._check_depletion()

    def _update_state_after_recovery(self):
        self._update_fatigue(recovery=True)
        self._update_exhaustion()
        self._check_depletion()

    def _update_fatigue(self, recovery: bool = False):
        if recovery:
            self.fatigue *= 0.98
        else:
            self.fatigue += (1.0 - self.energy_reserve) * 0.02

        self.fatigue = max(0.0, min(1.0, self.fatigue))

    def _update_exhaustion(self):
        self.exhaustion = (1.0 - self.energy_reserve) * self.fatigue

    def _check_depletion(self):
        if self.energy_reserve <= self.exhaustion_threshold:
            self.is_energy_depleted = True
        else:
            self.is_energy_depleted = False

        if self.energy_reserve <= 0.0:
            self.is_alive = False

    # ---------------------------------------------------------
    # External modifiers
    # ---------------------------------------------------------

    def apply_resource_constraint(self, factor: float):
        """
        Modify access to energy resources (environmental constraint).
        """
        self.resource_access *= factor
        self.resource_access = max(0.0, min(1.0, self.resource_access))

    def get_state_vector(self):
        """
        Compact representation for ecological systems.
        """
        return {
            "energy_reserve": self.energy_reserve,
            "fatigue": self.fatigue,
            "exhaustion": self.exhaustion,
            "resource_access": self.resource_access,
            "is_depleted": self.is_energy_depleted,
            "is_alive": self.is_alive,
        }
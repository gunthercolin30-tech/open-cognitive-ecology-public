# ecologies/energy/energy_ecology_process.py

from typing import Dict, List


class EnergyEcologyProcess:
    """
    Global ecological process for energy dynamics.

    This system aggregates individual energy states and
    applies systemic constraints (resource scarcity,
    environmental stress, collective depletion).
    """

    def __init__(
        self,
        base_environment_energy: float = 1.0,
        global_resource_factor: float = 1.0,
        scarcity_amplification: float = 1.0,
    ):
        self.base_environment_energy = base_environment_energy
        self.global_resource_factor = global_resource_factor
        self.scarcity_amplification = scarcity_amplification

        # Global indicators
        self.total_energy = 0.0
        self.average_fatigue = 0.0
        self.depleted_agents_ratio = 0.0
        self.system_stress = 0.0

    # ---------------------------------------------------------
    # Main update
    # ---------------------------------------------------------

    def step(self, agents: List) -> Dict:
        """
        Compute global energy dynamics and propagate
        environmental constraints back to agents.
        """

        if not agents:
            return self._empty_state()

        total_energy = 0.0
        total_fatigue = 0.0
        depleted_count = 0

        # -----------------------------------------------------
        # Aggregate agent states
        # -----------------------------------------------------
        for agent in agents:
            energy = agent.energy_component

            total_energy += energy.energy_reserve
            total_fatigue += energy.fatigue

            if energy.is_energy_depleted:
                depleted_count += 1

        n = len(agents)

        avg_energy = total_energy / n
        avg_fatigue = total_fatigue / n
        depleted_ratio = depleted_count / n

        # -----------------------------------------------------
        # Compute system-level stress
        # -----------------------------------------------------
        self.system_stress = (
            (1.0 - avg_energy)
            * avg_fatigue
            * (1.0 + depleted_ratio * self.scarcity_amplification)
        )

        # -----------------------------------------------------
        # Update global indicators
        # -----------------------------------------------------
        self.total_energy = total_energy
        self.average_fatigue = avg_fatigue
        self.depleted_agents_ratio = depleted_ratio

        # -----------------------------------------------------
        # Propagate environmental constraints
        # -----------------------------------------------------
        environment_factor = self._compute_environment_factor()

        for agent in agents:
            agent.energy_component.apply_resource_constraint(environment_factor)

        return self.get_state()

    # ---------------------------------------------------------
    # Environment dynamics
    # ---------------------------------------------------------

    def _compute_environment_factor(self) -> float:
        """
        Energy availability modulation based on system stress.
        """
        factor = self.base_environment_energy - self.system_stress
        return max(0.1, min(1.0, factor * self.global_resource_factor))

    # ---------------------------------------------------------
    # Output
    # ---------------------------------------------------------

    def get_state(self) -> Dict:
        return {
            "total_energy": self.total_energy,
            "average_fatigue": self.average_fatigue,
            "depleted_agents_ratio": self.depleted_agents_ratio,
            "system_stress": self.system_stress,
        }

    def _empty_state(self):
        return {
            "total_energy": 0.0,
            "average_fatigue": 0.0,
            "depleted_agents_ratio": 0.0,
            "system_stress": 0.0,
        }
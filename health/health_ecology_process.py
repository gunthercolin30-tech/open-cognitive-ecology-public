# health/health_ecology_process.py

import random


class HealthEcologyProcess:
    """
    Distributed health ecology.

    This process models:
    - contagion between agents
    - immune protection
    - healthcare buffering
    - biological resilience
    - aggregate sanitary indicators

    No universal immunity.
    No guaranteed survival.
    No centralized health control.
    """

    def __init__(self):
        self.average_health_state = 1.0
        self.average_immunity = 1.0
        self.average_contagion_load = 0.0
        self.average_mortality_risk = 0.0
        self.health_fragmentation = 0.0
        self.alive_count = 0

    def update(
        self,
        agents,
    ):
        """
        Update distributed health ecology.

        The graph stores nodes in a dictionary.
        This method accepts either:
        - a list of agent objects
        - a dict of {id: agent}
        """

        # =====================================================
        # NORMALIZATION OF INPUT
        # =====================================================

        if isinstance(
            agents,
            dict,
        ):
            agents = list(
                agents.values()
            )

        else:
            agents = list(
                agents
            )

        # Keep only objects exposing health indicators.
        agents = [
            agent
            for agent in agents
            if hasattr(
                agent,
                "contagion_load",
            )
        ]

        if not agents:
            return

        # =====================================================
        # CONTAGION PROPAGATION
        # =====================================================

        infectious_agents = [
            agent
            for agent in agents
            if agent.contagion_load > 0.05
        ]

        local_pressure = 0.0

        if infectious_agents:
            local_pressure = (
                len(infectious_agents)
                / len(agents)
            )

        for agent in agents:

            contagion_increase = (
                0.08
                * local_pressure
                * (1.0 - agent.immunity)
                * (1.0 - agent.healthcare_access)
            )

            resilience_protection = (
                0.03
                * agent.biological_resilience
            )

            stochastic_noise = (
                random.uniform(
                    -0.01,
                    0.01,
                )
            )

            agent.contagion_load += (
                contagion_increase
                - resilience_protection
                + stochastic_noise
            )

            agent.contagion_load = max(
                0.0,
                min(
                    1.0,
                    agent.contagion_load,
                ),
            )

        # =====================================================
        # AGGREGATE INDICATORS
        # =====================================================

        self.alive_count = len(
            [
                agent
                for agent in agents
                if agent.health_state > 0.0
            ]
        )

        self.average_health_state = (
            sum(
                agent.health_state
                for agent in agents
            )
            / len(agents)
        )

        self.average_immunity = (
            sum(
                agent.immunity
                for agent in agents
            )
            / len(agents)
        )

        self.average_contagion_load = (
            sum(
                agent.contagion_load
                for agent in agents
            )
            / len(agents)
        )

        self.average_mortality_risk = (
            sum(
                agent.mortality_risk
                for agent in agents
            )
            / len(agents)
        )

        self.health_fragmentation = (
            sum(
                agent.health_fragmentation
                for agent in agents
            )
            / len(agents)
        )

        # =====================================================
        # DEBUG OUTPUT
        # =====================================================

        print(
            "[HEALTH_ECOLOGY]",
            f"health={self.average_health_state:.2f}",
            f"immunity={self.average_immunity:.2f}",
            f"contagion={self.average_contagion_load:.2f}",
            f"mortality={self.average_mortality_risk:.2f}",
            f"fragmentation={self.health_fragmentation:.2f}",
        )

    def get_state(self):
        """
        Return aggregate sanitary indicators.
        """

        return {
            "health_alive_count": (
                self.alive_count
            ),
            "average_health_state": (
                self.average_health_state
            ),
            "average_immunity": (
                self.average_immunity
            ),
            "average_contagion_load": (
                self.average_contagion_load
            ),
            "average_mortality_risk": (
                self.average_mortality_risk
            ),
            "health_fragmentation": (
                self.health_fragmentation
            ),
        }
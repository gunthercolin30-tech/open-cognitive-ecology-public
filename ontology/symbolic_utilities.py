PRIMITIVE = "symbolic_utilities"
DESCRIPTION = "Symbolic utilities."
DEPENDENCIES = []

import math


class SymbolicUtilitiesMixin:

    # =========================================================
    # LOCAL NEIGHBORHOODS
    # =========================================================

    def _find_local_agents(
        self,
        source_agent,
        agents,
        radius=6.0,
    ):

        local_agents = []

        for agent in agents:

            dx = (
                agent.x
                - source_agent.x
            )

            dy = (
                agent.y
                - source_agent.y
            )

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance <= radius:
                local_agents.append(
                    agent
                )

        return local_agents
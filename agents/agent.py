# agents/agent.py

from agents.agent_components import (
    initialize_components,
)
from agents.agent_attribute_router import (
    agent_getattr,
    agent_setattr,
)
from agents.agent_behavior import (
    agent_perceive,
    agent_evolve,
)


class PersistentAgent:
    """
    Distributed cognitive agent.

    This class is intentionally minimal.
    All responsibilities are delegated to:
    - agent_components.py
    - agent_attribute_router.py
    - agent_behavior.py
    """

    def __init__(
        self,
        name,
    ):
        # Core state
        self.state = {
            "name": name,
            "status": "active",
            "cycle": 0,
        }

        # Initialize all components and ecologies
        initialize_components(
            self,
            name,
        )

    # =====================================================
    # ATTRIBUTE ROUTING
    # =====================================================

    def __getattr__(
        self,
        name,
    ):
        return agent_getattr(
            self,
            name,
        )

    def __setattr__(
        self,
        name,
        value,
    ):
        agent_setattr(
            self,
            name,
            value,
        )

    # =====================================================
    # PERCEPTION
    # =====================================================

    def perceive(
        self,
        environment_event,
        perception_fields=None,
    ):
        return agent_perceive(
            self,
            environment_event,
            perception_fields,
        )

    # =====================================================
    # EVOLUTION
    # =====================================================

    def evolve(
        self,
        perception_fields=None,
    ):
        agent_evolve(
            self,
            perception_fields,
        )
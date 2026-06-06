# core/type_safety/agent_resolver.py

from agents.agent import PersistentAgent


class AgentResolver:
    """
    Central safety layer ensuring that all ecological
    systems receive valid PersistentAgent objects.

    Prevents:
    - str leakage
    - graph node misuse
    - mixed representations

    Supports:
    - direct PersistentAgent instances
    - graph node wrappers exposing `.agent`
    - graph node wrappers exposing `.data.agent`
    - objects already carrying ecological components
    """

    @staticmethod
    def is_agent_like(obj):
        """
        Return True if the object already behaves like an agent.

        We use the presence of one or more known ecological
        components as a structural criterion. This keeps the
        resolver robust as new ecologies are added.
        """

        known_components = (
            "demographic_component",
            "health_component",
            "energy_component",
            "cognitive_component",
            "temporal_component",
            "spatial_component",
            "climatic_component",
            "constraint_component",
            "political_component",
            "legal_component",
            "cultural_component",
            "economic_component",
            "linguistic_component",
            "technological_component",
            "scientific_component",
            "educational_component",
            "media_component",
        )

        for component_name in known_components:
            if hasattr(obj, component_name):
                return True

        return False

    @staticmethod
    def resolve(agent_like):
        """
        Normalize any input into a valid PersistentAgent
        or raise a controlled error.
        """

        # -----------------------------------------------------
        # CASE 0: null
        # -----------------------------------------------------
        if agent_like is None:
            raise TypeError(
                "[TYPE_SAFETY] Invalid agent type: None."
            )

        # -----------------------------------------------------
        # CASE 1: already correct
        # -----------------------------------------------------
        if isinstance(agent_like, PersistentAgent):
            return agent_like

        # -----------------------------------------------------
        # CASE 2: graph node wrapper exposing `.agent`
        # -----------------------------------------------------
        if hasattr(agent_like, "agent"):
            candidate = getattr(agent_like, "agent")
            if candidate is not None:
                return AgentResolver.resolve(candidate)

        # -----------------------------------------------------
        # CASE 3: wrapper exposing `.data.agent`
        # -----------------------------------------------------
        if hasattr(agent_like, "data"):
            data = getattr(agent_like, "data")
            if data is not None and hasattr(data, "agent"):
                candidate = getattr(data, "agent")
                if candidate is not None:
                    return AgentResolver.resolve(candidate)

        # -----------------------------------------------------
        # CASE 4: object already behaving as an agent
        # -----------------------------------------------------
        if AgentResolver.is_agent_like(agent_like):
            return agent_like

        # -----------------------------------------------------
        # CASE 5: string (common graph key leakage bug)
        # -----------------------------------------------------
        if isinstance(agent_like, str):
            raise TypeError(
                f"[TYPE_SAFETY] Invalid agent type: str '{agent_like}'. "
                "Expected PersistentAgent but received a node identifier. "
                "Check graph -> agent mapping."
            )

        # -----------------------------------------------------
        # CASE 6: unknown object
        # -----------------------------------------------------
        raise TypeError(
            "[TYPE_SAFETY] Unknown agent type: "
            f"{type(agent_like)}"
        )

    @staticmethod
    def resolve_list(agents):
        """
        Normalize a list (or iterable) of agents safely.
        Raises explicit errors on invalid entries.
        """

        if agents is None:
            return []

        resolved = []

        for agent_like in agents:
            resolved.append(
                AgentResolver.resolve(agent_like)
            )

        return resolved
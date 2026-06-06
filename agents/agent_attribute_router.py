# agents/agent_attribute_router.py

# =========================================================
# DIRECT ATTRIBUTES
# =========================================================

DIRECT_ATTRIBUTES = (
    "state",
    "phenomenology",
    "civilization",
    "mobility",
    "politics",
    "technological_component",
    "scientific_component",
    "educational_component",
    "media_component",
    "health_component",
    "demographic_component",
    "energy_component",
    "legal_ecology",
    "cultural_ecology",
    "language_regime",
    "language_ecology",
    "node",
)

# =========================================================
# COMPONENT ATTRIBUTES
# =========================================================

COMPONENT_ATTRIBUTES = (
    "phenomenology",
    "civilization",
    "mobility",
    "politics",
    "technological_component",
    "scientific_component",
    "educational_component",
    "media_component",
    "health_component",
    "demographic_component",
    "energy_component",
)

# =========================================================
# HELPERS
# =========================================================


def _components(agent):
    """
    Return all local components that may own delegated
    attributes.
    """

    return tuple(
        getattr(agent, attr)
        for attr in COMPONENT_ATTRIBUTES
        if hasattr(agent, attr)
    )


# =========================================================
# ATTRIBUTE GETTER
# =========================================================


def agent_getattr(agent, name):
    """
    Delegate unknown attributes to components and
    distributed ecologies.
    """

    # -----------------------------------------------------
    # Local components
    # -----------------------------------------------------

    for component in _components(agent):
        if hasattr(component, name):
            return getattr(component, name)

    # -----------------------------------------------------
    # Legal ecology
    # -----------------------------------------------------

    if hasattr(agent, "legal_ecology"):
        legal_state = (
            agent.legal_ecology.get_state()
        )

        if name in legal_state:
            return legal_state[name]

    # -----------------------------------------------------
    # Cultural ecology
    # -----------------------------------------------------

    if hasattr(agent, "cultural_ecology"):
        cultural_state = {
            "cultural_alive_count": (
                agent.cultural_ecology.get_alive_count()
            ),
            "cultural_fragmentation": (
                agent.cultural_ecology.get_average_fragmentation()
            ),
            "cultural_memory": (
                agent.cultural_ecology.get_average_memory()
            ),
        }

        if name in cultural_state:
            return cultural_state[name]

    # -----------------------------------------------------
    # Local language regime
    # -----------------------------------------------------

    if hasattr(agent, "language_regime"):
        language_state = (
            agent.language_regime.get_summary()
        )

        if name in language_state:
            return language_state[name]

    # -----------------------------------------------------
    # Distributed language ecology
    # -----------------------------------------------------

    if hasattr(agent, "language_ecology"):
        distributed_language_state = (
            agent.language_ecology.get_state()
        )

        if name in distributed_language_state:
            return distributed_language_state[
                name
            ]

    # -----------------------------------------------------
    # Not found
    # -----------------------------------------------------

    raise AttributeError(
        (
            f"'{agent.__class__.__name__}' "
            f"object has no attribute '{name}'"
        )
    )


# =========================================================
# ATTRIBUTE SETTER
# =========================================================


def agent_setattr(agent, name, value):
    """
    Route assignments to the component that owns
    the attribute.
    """

    # -----------------------------------------------------
    # Direct attributes
    # -----------------------------------------------------

    if name in DIRECT_ATTRIBUTES:
        object.__setattr__(
            agent,
            name,
            value,
        )
        return

    # -----------------------------------------------------
    # Initialization phase
    # -----------------------------------------------------

    if not all(
        hasattr(agent, attr)
        for attr in COMPONENT_ATTRIBUTES
    ):
        object.__setattr__(
            agent,
            name,
            value,
        )
        return

    # -----------------------------------------------------
    # Delegated attributes
    # -----------------------------------------------------

    for component in _components(agent):
        if hasattr(component, name):
            setattr(
                component,
                name,
                value,
            )
            return

    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    object.__setattr__(
        agent,
        name,
        value,
    )
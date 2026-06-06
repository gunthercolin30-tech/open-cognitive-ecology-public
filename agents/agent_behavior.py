# agents/agent_behavior.py


def agent_perceive(
    agent,
    environment_event,
    perception_fields=None,
):
    """
    Distributed perception pipeline.
    """

    influencing_fields = []

    if perception_fields:
        influencing_fields = (
            agent.phenomenology.find_local_fields(
                agent,
                perception_fields,
            )
        )

    perceived_event = (
        agent.phenomenology.perceive(
            environment_event,
            influencing_fields,
        )
    )

    perceived_event = (
        agent.civilization.cultural_distortion(
            perceived_event
        )
    )

    return perceived_event


def agent_evolve(
    agent,
    perception_fields=None,
):
    """
    Full distributed agent evolution.
    Preserves all existing component dynamics.
    """

    agent.state["cycle"] += 1

    # =====================================================
    # INTERNAL COMPONENT DYNAMICS
    # =====================================================

    agent.phenomenology.evolve()
    agent.civilization.evolve()
    agent.politics.evolve()

    # Distributed legal dynamics
    agent.legal_ecology.update()

    # Distributed cultural dynamics
    agent.cultural_ecology.step()

    # Local linguistic dynamics
    agent.language_regime.update()

    # Distributed linguistic dynamics
    agent.language_ecology.step()

    # Local technological dynamics
    agent.technological_component.update_technological_dynamics()

    # Local scientific dynamics
    agent.scientific_component.update_scientific_dynamics()

    # Local educational dynamics
    agent.educational_component.update_educational_dynamics()

    # Local media dynamics
    agent.media_component.update_media_dynamics()

    # Local health dynamics
    agent.health_component.update()

    # Local demographic dynamics
    agent.demographic_component.update()

    # Local energy dynamics
    agent.energy_component.update()

    # =====================================================
    # CULTURAL PRODUCTION
    # =====================================================

    agent.civilization.generate_local_mythologies(
        cycle=agent.state["cycle"],
        fragmentation=agent.fragmentation,
    )

    agent.civilization.mutate_symbolic_patterns()

    agent.civilization.transmit_cultural_fragments(
        cycle=agent.state["cycle"],
        local_coherence=agent.local_coherence,
    )

    # =====================================================
    # LOCAL ECOLOGICAL INTERACTIONS
    # =====================================================

    normalized_fields = None

    if perception_fields:

        normalized_fields = (
            agent.phenomenology.normalize_perception_fields(
                perception_fields
            )
        )

        # Spatial migration
        agent.mobility.migrate_between_regimes(
            perception_fields=normalized_fields,
            fragmentation=agent.fragmentation,
        )

        # Phenomenological interactions
        agent.phenomenology.update_local_alliances(
            agent,
            normalized_fields,
        )

        agent.phenomenology.update_exclusions(
            agent,
            normalized_fields,
        )

        # Civilizational interactions
        agent.civilization.update_cultural_affinities(
            agent,
            normalized_fields,
        )

        agent.civilization.update_cultural_exclusions(
            agent,
            normalized_fields,
        )

    # =====================================================
    # POLITICAL ECOLOGY
    # =====================================================

    if normalized_fields:

        agent.politics.update_local_institutions(
            agent,
            normalized_fields,
        )

        agent.politics.update_symbolic_currency(
            agent,
            normalized_fields,
        )

        agent.politics.update_distributed_coordination(
            agent,
            normalized_fields,
        )

        agent.politics.update_political_affiliation(
            agent,
            normalized_fields,
        )

        agent.politics.update_political_tension(
            agent,
            normalized_fields,
        )
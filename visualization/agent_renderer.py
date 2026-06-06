# visualization/agent_renderer.py


def format_agent_summary(agent):
    """
    Create a compact textual representation of an agent,
    including linguistic, educational, media, health,
    and demographic indicators.

    Rendered indicators:
    - core identity
    - phenomenological fragmentation
    - political tension
    - legal fragmentation
    - cultural fragmentation
    - linguistic vitality
    - lexicon size
    - linguistic fragmentation
    - education level
    - educational prestige
    - pedagogical innovation
    - media virality
    - source credibility
    - misinformation
    - health state
    - immunity
    - contagion load
    - mortality risk
    - age
    - fertility
    - birth potential
    - generation index
    - alive status

    No global language.
    No universal education.
    No universal media.
    No universal health.
    No universal demography.
    Only local unstable regimes of transmission.
    """

    name = agent.state.get(
        "name",
        "unknown",
    )

    cycle = agent.state.get(
        "cycle",
        0,
    )

    # =====================================================
    # CORE DYNAMICS
    # =====================================================

    fragmentation = getattr(
        agent,
        "fragmentation",
        0.0,
    )

    political_tension = getattr(
        agent,
        "political_tension",
        0.0,
    )

    legal_fragmentation = getattr(
        agent,
        "legal_fragmentation",
        0.0,
    )

    cultural_fragmentation = getattr(
        agent,
        "cultural_fragmentation",
        0.0,
    )

    # =====================================================
    # LANGUAGE DYNAMICS
    # =====================================================

    language_vitality = getattr(
        agent,
        "vitality",
        0.0,
    )

    lexicon_size = getattr(
        agent,
        "terms",
        0,
    )

    language_fragmentation = getattr(
        agent,
        "fragmentation",
        0.0,
    )

    # =====================================================
    # EDUCATIONAL DYNAMICS
    # =====================================================

    education_level = getattr(
        agent,
        "education_level",
        0.0,
    )

    educational_prestige = getattr(
        agent,
        "educational_prestige",
        0.0,
    )

    pedagogical_innovation = getattr(
        agent,
        "pedagogical_innovation",
        0.0,
    )

    # =====================================================
    # MEDIA DYNAMICS
    # =====================================================

    virality = getattr(
        agent,
        "virality",
        0.0,
    )

    source_credibility = getattr(
        agent,
        "source_credibility",
        0.0,
    )

    misinformation = getattr(
        agent,
        "misinformation",
        0.0,
    )

    # =====================================================
    # HEALTH DYNAMICS
    # =====================================================

    health_state = getattr(
        agent,
        "health_state",
        0.0,
    )

    immunity = getattr(
        agent,
        "immunity",
        0.0,
    )

    contagion_load = getattr(
        agent,
        "contagion_load",
        0.0,
    )

    mortality_risk = getattr(
        agent,
        "mortality_risk",
        0.0,
    )

    # =====================================================
    # DEMOGRAPHIC DYNAMICS
    # =====================================================

    age = getattr(
        agent,
        "age",
        0.0,
    )

    fertility = getattr(
        agent,
        "fertility",
        0.0,
    )

    birth_potential = getattr(
        agent,
        "birth_potential",
        0.0,
    )

    generation_index = getattr(
        agent,
        "generation_index",
        0,
    )

    is_alive = getattr(
        agent,
        "is_alive",
        True,
    )

    # =====================================================
    # FORMAT
    # =====================================================

    return (
        f"{name} "
        f"| cycle={cycle} "
        f"| frag={fragmentation:.2f} "
        f"| pol={political_tension:.2f} "
        f"| law={legal_fragmentation:.2f} "
        f"| cult={cultural_fragmentation:.2f} "
        f"| lang_vit={language_vitality:.2f} "
        f"| lex={lexicon_size} "
        f"| lang_frag={language_fragmentation:.2f} "
        f"| edu={education_level:.2f} "
        f"| edu_prest={educational_prestige:.2f} "
        f"| pedag={pedagogical_innovation:.2f} "
        f"| vir={virality:.2f} "
        f"| cred={source_credibility:.2f} "
        f"| mis={misinformation:.2f} "
        f"| health={health_state:.2f} "
        f"| imm={immunity:.2f} "
        f"| cont={contagion_load:.2f} "
        f"| mort={mortality_risk:.2f} "
        f"| age={age:.1f} "
        f"| fert={fertility:.2f} "
        f"| birth={birth_potential:.4f} "
        f"| gen={generation_index} "
        f"| alive={is_alive}"
    )
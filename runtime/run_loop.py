# runtime/run_loop.py

import asyncio

from visualization.energy_renderer import EnergyRenderer
from core.type_safety.agent_resolver import AgentResolver


# =========================================================
# SAFE ECOLOGY CALL
# =========================================================

def safe_call_ecology(process, graph=None, agents=None):
    """
    Safe wrapper preserving all legacy interfaces.

    Execution priority:
    1. update(agents) for agent-based ecologies
    2. update(graph) for graph-based ecologies
    3. step(agents) for agent-based ecologies
    4. step(graph) for graph-based ecologies
    5. step() for parameterless processes

    No functionality is removed; this only stabilizes
    dispatch semantics.
    """

    # -----------------------------------------------------
    # UPDATE-BASED PROCESSES
    # -----------------------------------------------------
    if hasattr(process, "update"):

        # Prefer agent-based signature when agents are provided.
        if agents is not None:
            try:
                return process.update(agents)
            except TypeError:
                pass

        # Fall back to graph-based signature.
        if graph is not None:
            try:
                return process.update(graph)
            except TypeError:
                pass

        # Final fallback.
        try:
            return process.update()
        except TypeError:
            return None

    # -----------------------------------------------------
    # STEP-BASED PROCESSES
    # -----------------------------------------------------
    if hasattr(process, "step"):

        # Prefer agent-based signature when agents are provided.
        if agents is not None:
            try:
                return process.step(agents)
            except TypeError:
                pass

        # Fall back to graph-based signature.
        if graph is not None:
            try:
                return process.step(graph)
            except TypeError:
                pass

        # Final fallback.
        try:
            return process.step()
        except TypeError:
            return None

    # -----------------------------------------------------
    # UNSUPPORTED PROCESS TYPE
    # -----------------------------------------------------
    return None


async def run_loop(system):
    """
    Main execution loop for Open Cognitive Ecology.
    """

    graph = system["graph"]
    scheduler = system["scheduler"]
    visualizer = system["visualizer"]

    economic_ecology_process = system[
        "economic_ecology_process"
    ]

    cultural_ecology_process = system[
        "cultural_ecology_process"
    ]

    technological_ecology_process = system[
        "technological_ecology_process"
    ]

    scientific_ecology_process = system[
        "scientific_ecology_process"
    ]

    health_ecology_process = system[
        "health_ecology_process"
    ]

    demographic_ecology_process = system[
        "demographic_ecology_process"
    ]

    # =========================================================
    # ENERGY ECOLOGY
    # =========================================================

    energy_ecology_process = system[
        "energy_ecology_process"
    ]

    energy_renderer = EnergyRenderer()

    # =========================================================
    # TYPE SAFE AGENTS LAYER
    # =========================================================

    raw_agents = system.get("agents", [])
    agents = AgentResolver.resolve_list(raw_agents)

    while True:

        print("\n--- cognitive cycle ---")

        # =====================================================
        # REFRESH AGENT REFERENCES
        # =====================================================

        raw_agents = system.get("agents", [])
        agents = AgentResolver.resolve_list(raw_agents)

        # =====================================================
        # SCHEDULED PROCESSES
        # =====================================================

        await scheduler.run_cycle()

        # =====================================================
        # GRAPH-BASED ECOLOGIES
        # =====================================================

        safe_call_ecology(
            economic_ecology_process,
            graph=graph,
        )

        safe_call_ecology(
            cultural_ecology_process,
            graph=graph,
        )

        safe_call_ecology(
            technological_ecology_process,
            graph=graph,
            agents=agents,
        )

        safe_call_ecology(
            scientific_ecology_process,
            graph=graph,
        )

        # =====================================================
        # AGENT-BASED ECOLOGIES
        # =====================================================

        safe_call_ecology(
            health_ecology_process,
            agents=agents,
        )

        safe_call_ecology(
            demographic_ecology_process,
            agents=agents,
        )

        # =====================================================
        # ENERGY ECOLOGY
        # =====================================================

        energy_state = safe_call_ecology(
            energy_ecology_process,
            agents=agents,
        )

        energy_renderer.render(
            energy_state,
            agents,
        )

        # =====================================================
        # GLOBAL DECAY
        # =====================================================

        graph.decay()

        # =====================================================
        # ACTIVE NODES REPORT (UNCHANGED)
        # =====================================================

        active_nodes = graph.most_active_nodes()

        print("\n[TOP ACTIVE NODES]")

        for node in active_nodes:

            velocity = (
                (node.vx ** 2 + node.vy ** 2)
                ** 0.5
            )

            print(
                node.id,
                f"activation={node.activation:.2f}",
                f"salience={node.salience:.2f}",
                f"tension={node.tension:.2f}",
                f"velocity={velocity:.2f}",
                f"temp={node.temperature:.2f}",
                f"pressure={node.pressure:.2f}",
                f"storm={node.storm_potential:.2f}",
                f"vorticity={node.vorticity:.2f}",
                f"viability={node.local_viability:.2f}",
                f"coherence={node.coherence_field:.2f}",
                f"incompatibility={node.incompatibility_field:.2f}",
                f"plasticity={node.operational_plasticity:.2f}",
                f"institution={getattr(node, 'institutional_intensity', 0.0):.2f}",
                f"currency={getattr(node, 'symbolic_currency', 0.0):.2f}",
                f"coordination={getattr(node, 'coordination_intensity', 0.0):.2f}",
                f"political_tension={getattr(node, 'political_tension', 0.0):.2f}",
                f"legal_legitimacy={getattr(node, 'normative_legitimacy', 0.0):.2f}",
                f"jurisprudence={getattr(node, 'jurisprudence_density', 0.0):.2f}",
                f"legal_stability={getattr(node, 'legal_stability', 0.0):.2f}",
                f"legal_conflict={getattr(node, 'legal_conflict', 0.0):.2f}",
                f"compatibility={getattr(node, 'normative_compatibility', 0.0):.2f}",
                f"economic_intensity={getattr(node, 'economic_intensity', 0.0):.2f}",
                f"economic_stress={getattr(node, 'economic_stress', 0.0):.2f}",
                f"economic_risk={getattr(node, 'economic_collapse_risk', 0.0):.2f}",
                f"technological_stability={getattr(node, 'technological_stability', 0.0):.2f}",
                f"innovation={getattr(node, 'innovation_flow', 0.0):.2f}",
                f"obsolescence={getattr(node, 'obsolescence', 0.0):.2f}",
                f"lock_in={getattr(node, 'lock_in', 0.0):.2f}",
                f"tech_pressure={getattr(node, 'technological_pressure', 0.0):.2f}",
                f"hypotheses={getattr(node, 'hypothesis_generation_rate', 0.0):.2f}",
                f"rigor={getattr(node, 'experimental_rigor', 0.0):.2f}",
                f"knowledge={getattr(node, 'knowledge_stock', 0.0):.2f}",
                f"controversy={getattr(node, 'controversy_level', 0.0):.2f}",
                f"paradigm={getattr(node, 'paradigm_alignment', 0.0):.2f}",
                f"shift={getattr(node, 'conceptual_shift_pressure', 0.0):.2f}",
                f"anomalies={getattr(node, 'anomaly_load', 0.0):.2f}",
                f"science_legitimacy={getattr(node, 'scientific_legitimacy', 0.0):.2f}",
                f"health={getattr(node, 'health_state', 0.0):.2f}",
                f"immunity={getattr(node, 'immunity', 0.0):.2f}",
                f"fatigue_phys={getattr(node, 'physiological_fatigue', 0.0):.2f}",
                f"contagion={getattr(node, 'contagion_load', 0.0):.2f}",
                f"care={getattr(node, 'healthcare_access', 0.0):.2f}",
                f"mortality={getattr(node, 'mortality_risk', 0.0):.2f}",
                f"age={getattr(node, 'age', 0.0):.1f}",
                f"fertility={getattr(node, 'fertility', 0.0):.2f}",
                f"birth_potential={getattr(node, 'birth_potential', 0.0):.4f}",
                f"generation={getattr(node, 'generation_index', 0)}",
                f"alive={getattr(node, 'is_alive', True)}",
                f"legal_status={getattr(node, 'legal_status', 'none')}",
                f"affiliation={getattr(node, 'political_affiliation', 'none')}",
                f"position=({node.x:.2f},{node.y:.2f})",
            )

        # =====================================================
        # ECOLOGICAL REPORTS (UNCHANGED)
        # =====================================================

        economic_ecology_process.debug_print()

        cultural_state = cultural_ecology_process.get_state()

        print(
            "[CULTURAL_SUMMARY]",
            f"alive={cultural_state['cultural_alive_count']}",
            f"fragmentation={cultural_state['cultural_fragmentation']:.2f}",
            f"memory={cultural_state['cultural_memory']:.2f}",
        )

        health_state = health_ecology_process.get_state()

        print(
            "[HEALTH_SUMMARY]",
            f"alive={health_state['health_alive_count']}",
            f"health={health_state['average_health_state']:.2f}",
            f"immunity={health_state['average_immunity']:.2f}",
            f"contagion={health_state['average_contagion_load']:.2f}",
            f"mortality={health_state['average_mortality_risk']:.2f}",
            f"fragmentation={health_state['health_fragmentation']:.2f}",
        )

        demographic_state = demographic_ecology_process.__dict__

        print(
            "[DEMOGRAPHIC_SUMMARY]",
            f"population={demographic_state['population_size']}",
            f"age={demographic_state['average_age']:.2f}",
            f"fertility={demographic_state['average_fertility']:.2f}",
            f"births={demographic_state['birth_count']}",
            f"deaths={demographic_state['death_count']}",
            f"young={demographic_state['young_ratio']:.2f}",
            f"reproductive={demographic_state['reproductive_ratio']:.2f}",
            f"elder={demographic_state['elder_ratio']:.2f}",
            f"pressure={demographic_state['population_pressure']:.2f}",
            f"turnover={demographic_state['generation_turnover']:.2f}",
        )

        # =====================================================
        # VISUALIZATION
        # =====================================================

        visualizer.update(graph)

        # =====================================================
        # CLOCK
        # =====================================================

        await asyncio.sleep(1)
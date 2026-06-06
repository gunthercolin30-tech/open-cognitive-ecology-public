import math
import random


class PhenomenologicalConflictProcess:

    """
    Distributed phenomenological conflicts.

    No global war.
    No centralized factions.
    No stable empires.
    No universal ideology.

    Only:
    - local symbolic conflicts
    - mythological incompatibilities
    - semiotic destabilization
    - regional narrative fractures
    - distributed cultural turbulence
    - temporary conflict zones
    - cascading local collapses
    """

    def __init__(self):

        # =====================================================
        # CONFLICT ECOLOGY
        # =====================================================

        self.active_conflict_zones = []

        self.fracture_waves = []

        self.collapse_fronts = []

        self.symbolic_contaminations = []

        # =====================================================
        # ECOLOGICAL PARAMETERS
        # =====================================================

        self.conflict_radius = 7.0

        self.fracture_threshold = 0.6

        self.contamination_pressure = 0.01

        self.conflict_decay = 0.995

        self.collapse_decay = 0.998

    # =========================================================
    # MAIN EVOLUTION
    # =========================================================

    def evolve(
        self,
        agents,
    ):

        if not agents:
            return

        self._generate_local_conflicts(
            agents
        )

        self._propagate_symbolic_contamination(
            agents
        )

        self._destabilize_local_coherences(
            agents
        )

        self._trigger_regional_fractures(
            agents
        )

        self._propagate_collapse_fronts(
            agents
        )

        self._decay_conflict_structures()

    # =========================================================
    # LOCAL CONFLICT GENERATION
    # =========================================================

    def _generate_local_conflicts(
        self,
        agents,
    ):

        for agent in agents:

            nearby_agents = (
                self._find_local_agents(
                    agent,
                    agents,
                    radius=self.conflict_radius,
                )
            )

            for other in nearby_agents:

                if other is agent:
                    continue

                incompatibility = (
                    self._calculate_incompatibility(
                        agent,
                        other,
                    )
                )

                conflict_probability = (

                    incompatibility
                    * 0.03

                    + agent.compatibility_tension
                    * 0.01

                    + agent.cultural_fragmentation
                    * 0.01
                )

                if (
                    random.random()
                    > conflict_probability
                ):
                    continue

                conflict = {
                    "cycle": (
                        agent.state["cycle"]
                    ),
                    "agents": (
                        (
                            agent.state["name"],
                            other.state["name"],
                        )
                    ),
                    "position": (
                        (
                            (
                                agent.x
                                + other.x
                            ) * 0.5,
                            (
                                agent.y
                                + other.y
                            ) * 0.5,
                        )
                    ),
                    "intensity": incompatibility,
                }

                self.active_conflict_zones.append(
                    conflict
                )

                self._apply_local_conflict_effects(
                    agent,
                    other,
                    incompatibility,
                )

    # =========================================================
    # SYMBOLIC CONTAMINATION
    # =========================================================

    def _propagate_symbolic_contamination(
        self,
        agents,
    ):

        for agent in agents:

            nearby_agents = (
                self._find_local_agents(
                    agent,
                    agents,
                    radius=5.0,
                )
            )

            for other in nearby_agents:

                if other is agent:
                    continue

                incompatibility = (
                    self._calculate_incompatibility(
                        agent,
                        other,
                    )
                )

                contamination_probability = (

                    incompatibility
                    * 0.02

                    + self.contamination_pressure
                )

                if (
                    random.random()
                    > contamination_probability
                ):
                    continue

                contamination = {
                    "source": (
                        agent.state["name"]
                    ),
                    "target": (
                        other.state["name"]
                    ),
                    "drift": (
                        random.uniform(
                            0.01,
                            0.1,
                        )
                    ),
                }

                self.symbolic_contaminations.append(
                    contamination
                )

                other.symbolic_drift += (
                    contamination["drift"]
                )

                other.semiotic_instability += (
                    random.uniform(
                        0.01,
                        0.05,
                    )
                )

                other.compatibility_tension += (
                    random.uniform(
                        0.01,
                        0.04,
                    )
                )

    # =========================================================
    # LOCAL COHERENCE DESTABILIZATION
    # =========================================================

    def _destabilize_local_coherences(
        self,
        agents,
    ):

        for agent in agents:

            nearby_agents = (
                self._find_local_agents(
                    agent,
                    agents,
                    radius=6.0,
                )
            )

            local_pressure = 0.0

            for other in nearby_agents:

                if other is agent:
                    continue

                local_pressure += (
                    self._calculate_incompatibility(
                        agent,
                        other,
                    )
                )

            destabilization = (
                local_pressure
                * 0.002
            )

            agent.local_coherence -= (
                destabilization
            )

            agent.cultural_stability -= (
                destabilization
            )

            agent.fragmentation += (
                destabilization
                * 0.5
            )

            agent.cultural_fragmentation += (
                destabilization
                * 0.5
            )

            agent.local_coherence = max(
                0.0,
                agent.local_coherence,
            )

            agent.cultural_stability = max(
                0.0,
                agent.cultural_stability,
            )

    # =========================================================
    # REGIONAL FRACTURES
    # =========================================================

    def _trigger_regional_fractures(
        self,
        agents,
    ):

        for agent in agents:

            fracture_pressure = (

                agent.fragmentation

                + agent.cultural_fragmentation

                + agent.compatibility_tension

                + agent.semiotic_instability
            )

            if (
                fracture_pressure
                < self.fracture_threshold
            ):
                continue

            fracture_probability = (
                fracture_pressure
                * 0.01
            )

            if (
                random.random()
                > fracture_probability
            ):
                continue

            fracture = {
                "cycle": (
                    agent.state["cycle"]
                ),
                "position": (
                    (
                        agent.x,
                        agent.y,
                    )
                ),
                "pressure": (
                    fracture_pressure
                ),
            }

            self.fracture_waves.append(
                fracture
            )

            self._apply_fracture_effects(
                agent,
                agents,
            )

    # =========================================================
    # COLLAPSE PROPAGATION
    # =========================================================

    def _propagate_collapse_fronts(
        self,
        agents,
    ):

        for fracture in self.fracture_waves:

            fx, fy = fracture["position"]

            for agent in agents:

                dx = agent.x - fx
                dy = agent.y - fy

                distance = math.sqrt(
                    dx * dx + dy * dy
                )

                if distance > 6.0:
                    continue

                propagation_probability = (

                    fracture["pressure"]
                    * 0.005
                )

                if (
                    random.random()
                    > propagation_probability
                ):
                    continue

                collapse = {
                    "cycle": (
                        agent.state["cycle"]
                    ),
                    "agent": (
                        agent.state["name"]
                    ),
                    "position": (
                        (
                            agent.x,
                            agent.y,
                        )
                    ),
                }

                self.collapse_fronts.append(
                    collapse
                )

                agent.fragmentation += (
                    random.uniform(
                        0.05,
                        0.2,
                    )
                )

                agent.cultural_fragmentation += (
                    random.uniform(
                        0.05,
                        0.2,
                    )
                )

                agent.compatibility_tension += (
                    random.uniform(
                        0.02,
                        0.1,
                    )
                )

                agent.semiotic_instability += (
                    random.uniform(
                        0.02,
                        0.1,
                    )
                )

    # =========================================================
    # LOCAL CONFLICT EFFECTS
    # =========================================================

    def _apply_local_conflict_effects(
        self,
        agent_a,
        agent_b,
        incompatibility,
    ):

        turbulence = (
            incompatibility
            * random.uniform(
                0.05,
                0.2,
            )
        )

        agent_a.compatibility_tension += (
            turbulence
        )

        agent_b.compatibility_tension += (
            turbulence
        )

        agent_a.fragmentation += (
            turbulence
            * 0.5
        )

        agent_b.fragmentation += (
            turbulence
            * 0.5
        )

        agent_a.cultural_fragmentation += (
            turbulence
            * 0.5
        )

        agent_b.cultural_fragmentation += (
            turbulence
            * 0.5
        )

        agent_a.local_coherence -= (
            turbulence
            * 0.2
        )

        agent_b.local_coherence -= (
            turbulence
            * 0.2
        )

        if (
            random.random()
            < incompatibility * 0.1
        ):

            agent_a.local_alliances.clear()

        if (
            random.random()
            < incompatibility * 0.1
        ):

            agent_b.local_alliances.clear()

    # =========================================================
    # INCOMPATIBILITY
    # =========================================================

    def _calculate_incompatibility(
        self,
        agent_a,
        agent_b,
    ):

        civilizational_distance = abs(

            agent_a.civilizational_signature

            - agent_b.civilizational_signature
        )

        symbolic_distance = abs(

            agent_a.symbolic_drift

            - agent_b.symbolic_drift
        )

        perceptual_distance = abs(

            agent_a.reality_signature

            - agent_b.reality_signature
        )

        incompatibility = (

            civilizational_distance
            * 0.4

            + symbolic_distance
            * 0.3

            + perceptual_distance
            * 0.3
        )

        return max(
            0.0,
            min(
                1.5,
                incompatibility,
            )
        )

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

    # =========================================================
    # ECOLOGICAL DECAY
    # =========================================================

    def _decay_conflict_structures(
        self,
    ):

        self.active_conflict_zones = [

            zone

            for zone
            in self.active_conflict_zones

            if random.random()
            < self.conflict_decay
        ]

        if (
            len(self.active_conflict_zones)
            > 400
        ):

            self.active_conflict_zones = (
                self.active_conflict_zones[-400:]
            )

        self.fracture_waves = [

            fracture

            for fracture
            in self.fracture_waves

            if random.random()
            < self.collapse_decay
        ]

        if (
            len(self.fracture_waves)
            > 200
        ):

            self.fracture_waves = (
                self.fracture_waves[-200:]
            )

        self.collapse_fronts = [

            collapse

            for collapse
            in self.collapse_fronts

            if random.random()
            < self.collapse_decay
        ]

        if (
            len(self.collapse_fronts)
            > 200
        ):

            self.collapse_fronts = (
                self.collapse_fronts[-200:]
            )

        self.symbolic_contaminations = [

            contamination

            for contamination
            in self.symbolic_contaminations

            if random.random()
            < self.conflict_decay
        ]

        if (
            len(self.symbolic_contaminations)
            > 400
        ):

            self.symbolic_contaminations = (
                self.symbolic_contaminations[-400:]
            )
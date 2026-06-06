import math
import random


class CulturalMemoryEcology:

    """
    Distributed cultural ecology.

    No global civilization map.
    No universal language.
    No stable historical archive.
    No shared ontology.

    Only:
    - local narrative circulation
    - degraded transmission
    - symbolic mutation
    - mythological propagation
    - temporary civilizational stabilizations
    - cultural fragmentation
    - local extinction dynamics
    """

    def __init__(self):

        # =====================================================
        # LOCAL CULTURAL STRUCTURES
        # =====================================================

        self.cultural_regions = {}

        self.mythological_clusters = {}

        self.fragment_streams = []

        self.cultural_collapses = []

        # =====================================================
        # ECOLOGICAL PARAMETERS
        # =====================================================

        self.transmission_decay = 0.995

        self.symbolic_mutation_rate = 0.01

        self.fragmentation_pressure = 0.002

        self.extinction_pressure = 0.001

        self.coherence_decay = 0.998

    # =========================================================
    # MAIN EVOLUTION
    # =========================================================

    def evolve(
        self,
        agents,
    ):

        if not agents:
            return

        self._circulate_fragments(
            agents
        )

        self._propagate_mythologies(
            agents
        )

        self._mutate_symbolic_systems(
            agents
        )

        self._stabilize_local_cultures(
            agents
        )

        self._fragment_civilizations(
            agents
        )

        self._trigger_local_extinctions(
            agents
        )

        self._decay_global_streams()

    # =========================================================
    # CULTURAL FRAGMENT CIRCULATION
    # =========================================================

    def _circulate_fragments(
        self,
        agents,
    ):

        for source in agents:

            if not source.cultural_memory:
                continue

            nearby_agents = (
                self._find_local_agents(
                    source,
                    agents,
                    radius=8.0,
                )
            )

            for target in nearby_agents:

                if target is source:
                    continue

                transmission_probability = (

                    0.01

                    + source.transmission_drive
                    * 0.02

                    + source.local_coherence
                    * 0.01
                )

                if (
                    random.random()
                    > transmission_probability
                ):
                    continue

                fragment = random.choice(
                    source.cultural_memory
                )

                transmitted_fragment = (
                    self._degrade_fragment(
                        fragment
                    )
                )

                target.inherited_fragments.append(
                    transmitted_fragment
                )

                target.cultural_memory.append(
                    transmitted_fragment
                )

                self.fragment_streams.append(
                    {
                        "source": (
                            source.state["name"]
                        ),
                        "target": (
                            target.state["name"]
                        ),
                        "fragment": (
                            transmitted_fragment
                        ),
                    }
                )

                if (
                    len(target.cultural_memory)
                    > 120
                ):
                    target.cultural_memory.pop(
                        0
                    )

    # =========================================================
    # MYTHOLOGICAL PROPAGATION
    # =========================================================

    def _propagate_mythologies(
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

            for other in nearby_agents:

                if other is agent:
                    continue

                compatibility = (
                    self._cultural_compatibility(
                        agent,
                        other,
                    )
                )

                propagation_probability = (

                    compatibility
                    * 0.03

                    + agent.mythological_attachment
                    * 0.02
                )

                if (
                    random.random()
                    > propagation_probability
                ):
                    continue

                if not agent.local_mythologies:
                    continue

                mythology = random.choice(
                    list(
                        agent.local_mythologies
                    )
                )

                other.local_mythologies.add(
                    mythology
                )

                other.mythological_pressure += (
                    random.uniform(
                        0.01,
                        0.05,
                    )
                )

    # =========================================================
    # SYMBOLIC MUTATION
    # =========================================================

    def _mutate_symbolic_systems(
        self,
        agents,
    ):

        for agent in agents:

            mutation_pressure = (

                self.symbolic_mutation_rate

                + agent.symbolic_drift
                * 0.01
            )

            if (
                random.random()
                > mutation_pressure
            ):
                continue

            new_key = random.randint(
                -1000,
                1000,
            )

            new_value = random.uniform(
                -1.0,
                1.0,
            )

            agent.symbolic_patterns[
                new_key
            ] = new_value

            agent.semiotic_instability += (
                random.uniform(
                    0.01,
                    0.05,
                )
            )

    # =========================================================
    # LOCAL CULTURAL STABILIZATION
    # =========================================================

    def _stabilize_local_cultures(
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

            compatible_neighbors = 0

            for other in nearby_agents:

                if other is agent:
                    continue

                compatibility = (
                    self._cultural_compatibility(
                        agent,
                        other,
                    )
                )

                if compatibility > 0.6:
                    compatible_neighbors += 1

            if compatible_neighbors == 0:
                continue

            stabilization = (
                compatible_neighbors
                * 0.002
            )

            agent.cultural_stability += (
                stabilization
            )

            agent.local_coherence += (
                stabilization
            )

            region_key = int(
                (
                    agent.x
                    + agent.y
                )
                * 0.5
            )

            self.cultural_regions[
                region_key
            ] = (
                self.cultural_regions.get(
                    region_key,
                    0,
                )
                + 1
            )

    # =========================================================
    # CIVILIZATIONAL FRAGMENTATION
    # =========================================================

    def _fragment_civilizations(
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

            incompatibility = 0.0

            for other in nearby_agents:

                if other is agent:
                    continue

                compatibility = (
                    self._cultural_compatibility(
                        agent,
                        other,
                    )
                )

                incompatibility += (
                    1.0 - compatibility
                )

            fragmentation_risk = (

                incompatibility
                * 0.003

                + self.fragmentation_pressure
            )

            if (
                random.random()
                < fragmentation_risk
            ):

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

    # =========================================================
    # LOCAL EXTINCTIONS
    # =========================================================

    def _trigger_local_extinctions(
        self,
        agents,
    ):

        for agent in agents:

            extinction_risk = (

                agent.cultural_fragmentation
                * 0.01

                + agent.semiotic_instability
                * 0.005

                + self.extinction_pressure
            )

            if (
                random.random()
                > extinction_risk
            ):
                continue

            collapse = {
                "cycle": (
                    agent.state["cycle"]
                ),
                "signature": (
                    agent.civilizational_signature
                ),
                "position": (
                    (
                        agent.x,
                        agent.y,
                    )
                ),
            }

            self.cultural_collapses.append(
                collapse
            )

            agent.local_mythologies.clear()

            agent.cultural_affinities.clear()

            agent.cultural_exclusions.clear()

            agent.cultural_memory.clear()

            agent.symbolic_patterns.clear()

            agent.cultural_fragmentation += (
                random.uniform(
                    0.2,
                    0.5,
                )
            )

            agent.civilizational_fatigue += (
                random.uniform(
                    0.1,
                    0.3,
                )
            )

    # =========================================================
    # FRAGMENT DEGRADATION
    # =========================================================

    def _degrade_fragment(
        self,
        fragment,
    ):

        degraded = dict(fragment)

        degraded["mutation"] = (
            degraded.get(
                "mutation",
                0.0,
            )
            + random.uniform(
                -0.3,
                0.3,
            )
        )

        degraded["drift"] = (
            degraded.get(
                "drift",
                0.0,
            )
            + random.uniform(
                -0.2,
                0.2,
            )
        )

        degraded["degraded"] = True

        return degraded

    # =========================================================
    # CULTURAL COMPATIBILITY
    # =========================================================

    def _cultural_compatibility(
        self,
        agent_a,
        agent_b,
    ):

        signature_distance = abs(

            agent_a.civilizational_signature

            - agent_b.civilizational_signature
        )

        symbolic_distance = abs(

            agent_a.symbolic_drift

            - agent_b.symbolic_drift
        )

        compatibility = (

            1.0

            - signature_distance
            * 0.5

            - symbolic_distance
            * 0.3
        )

        return max(
            0.0,
            min(
                1.0,
                compatibility,
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

    def _decay_global_streams(
        self,
    ):

        self.fragment_streams = [

            stream

            for stream
            in self.fragment_streams

            if random.random()
            < self.transmission_decay
        ]

        if (
            len(self.fragment_streams)
            > 400
        ):

            self.fragment_streams = (
                self.fragment_streams[-400:]
            )

        self.cultural_collapses = [

            collapse

            for collapse
            in self.cultural_collapses

            if random.random()
            < self.coherence_decay
        ]

        if (
            len(self.cultural_collapses)
            > 120
        ):

            self.cultural_collapses = (
                self.cultural_collapses[-120:]
            )
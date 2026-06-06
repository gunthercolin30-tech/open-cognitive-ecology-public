import math
import random


class IntergenerationalTransmissionProcess:

    """
    Distributed intergenerational transmission ecology.

    No stable ancestry.
    No exact preservation.
    No universal history.
    No immutable civilization.

    Only:
    - degraded inheritance
    - partial memory transmission
    - symbolic reinterpretation
    - ancestral fragmentation
    - lineage divergence
    - narrative mutation
    - local civilizational persistence
    """

    def __init__(self):

        # =====================================================
        # TRANSMISSION ECOLOGY
        # =====================================================

        self.active_lineages = {}

        self.ancestral_fragments = []

        self.memory_resurgences = []

        self.lineage_collapses = []

        # =====================================================
        # ECOLOGICAL PARAMETERS
        # =====================================================

        self.transmission_radius = 6.0

        self.memory_decay = 0.996

        self.lineage_decay = 0.998

        self.fragment_mutation_rate = 0.02

        self.resurgence_probability = 0.002

    # =========================================================
    # MAIN EVOLUTION
    # =========================================================

    def evolve(
        self,
        agents,
    ):

        if not agents:
            return

        self._propagate_ancestral_fragments(
            agents
        )

        self._mutate_transmitted_memories(
            agents
        )

        self._stabilize_local_lineages(
            agents
        )

        self._trigger_memory_resurgences(
            agents
        )

        self._fragment_lineages(
            agents
        )

        self._collapse_lineages(
            agents
        )

        self._decay_ecology()

    # =========================================================
    # ANCESTRAL PROPAGATION
    # =========================================================

    def _propagate_ancestral_fragments(
        self,
        agents,
    ):

        for source in agents:

            if not source.inherited_fragments:
                continue

            nearby_agents = (
                self._find_local_agents(
                    source,
                    agents,
                    radius=self.transmission_radius,
                )
            )

            for target in nearby_agents:

                if target is source:
                    continue

                transmission_probability = (

                    0.01

                    + source.transmission_drive
                    * 0.02

                    + source.cultural_stability
                    * 0.01
                )

                if (
                    random.random()
                    > transmission_probability
                ):
                    continue

                fragment = random.choice(
                    source.inherited_fragments
                )

                inherited = (
                    self._mutate_fragment(
                        fragment
                    )
                )

                target.inherited_fragments.append(
                    inherited
                )

                self.ancestral_fragments.append(
                    {
                        "source": (
                            source.state["name"]
                        ),
                        "target": (
                            target.state["name"]
                        ),
                        "fragment": inherited,
                    }
                )

                if (
                    len(
                        target.inherited_fragments
                    )
                    > 120
                ):
                    target.inherited_fragments.pop(
                        0
                    )

    # =========================================================
    # MEMORY MUTATION
    # =========================================================

    def _mutate_transmitted_memories(
        self,
        agents,
    ):

        for agent in agents:

            if not agent.inherited_fragments:
                continue

            mutation_probability = (

                self.fragment_mutation_rate

                + agent.symbolic_drift
                * 0.01
            )

            if (
                random.random()
                > mutation_probability
            ):
                continue

            fragment = random.choice(
                agent.inherited_fragments
            )

            mutated = self._mutate_fragment(
                fragment
            )

            agent.cultural_memory.append(
                mutated
            )

            agent.symbolic_drift += (
                random.uniform(
                    0.01,
                    0.05,
                )
            )

            agent.semiotic_instability += (
                random.uniform(
                    0.01,
                    0.03,
                )
            )

    # =========================================================
    # LOCAL LINEAGES
    # =========================================================

    def _stabilize_local_lineages(
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

            lineage_strength = 0.0

            for other in nearby_agents:

                if other is agent:
                    continue

                compatibility = (
                    self._lineage_compatibility(
                        agent,
                        other,
                    )
                )

                lineage_strength += (
                    compatibility
                )

            if lineage_strength <= 0.0:
                continue

            lineage_key = int(
                (
                    agent.x
                    + agent.y
                )
                * 0.5
            )

            self.active_lineages[
                lineage_key
            ] = (
                self.active_lineages.get(
                    lineage_key,
                    0.0,
                )
                + lineage_strength
                * 0.001
            )

            agent.cultural_stability += (
                lineage_strength
                * 0.001
            )

    # =========================================================
    # MEMORY RESURGENCES
    # =========================================================

    def _trigger_memory_resurgences(
        self,
        agents,
    ):

        for agent in agents:

            if not agent.inherited_fragments:
                continue

            probability = (

                self.resurgence_probability

                + len(
                    agent.inherited_fragments
                )
                * 0.0001
            )

            if (
                random.random()
                > probability
            ):
                continue

            fragment = random.choice(
                agent.inherited_fragments
            )

            resurgence = {
                "cycle": (
                    agent.state["cycle"]
                ),
                "agent": (
                    agent.state["name"]
                ),
                "fragment": fragment,
            }

            self.memory_resurgences.append(
                resurgence
            )

            agent.mythological_pressure += (
                random.uniform(
                    0.05,
                    0.15,
                )
            )

            agent.local_mythologies.add(
                hash(
                    str(fragment)
                )
            )

    # =========================================================
    # LINEAGE FRAGMENTATION
    # =========================================================

    def _fragment_lineages(
        self,
        agents,
    ):

        for agent in agents:

            fragmentation_pressure = (

                agent.symbolic_drift

                + agent.cultural_fragmentation

                + agent.semiotic_instability
            )

            fragmentation_probability = (

                fragmentation_pressure
                * 0.005
            )

            if (
                random.random()
                > fragmentation_probability
            ):
                continue

            if agent.inherited_fragments:

                removable_count = max(
                    1,
                    int(
                        len(
                            agent.inherited_fragments
                        )
                        * 0.2
                    ),
                )

                for _ in range(
                    removable_count
                ):

                    if (
                        not agent.inherited_fragments
                    ):
                        break

                    index = random.randint(
                        0,
                        len(
                            agent.inherited_fragments
                        )
                        - 1,
                    )

                    agent.inherited_fragments.pop(
                        index
                    )

            agent.cultural_fragmentation += (
                random.uniform(
                    0.05,
                    0.2,
                )
            )

    # =========================================================
    # LINEAGE COLLAPSE
    # =========================================================

    def _collapse_lineages(
        self,
        agents,
    ):

        for agent in agents:

            collapse_pressure = (

                agent.civilizational_fatigue

                + agent.cultural_fragmentation

                + agent.semiotic_instability
            )

            collapse_probability = (
                collapse_pressure
                * 0.003
            )

            if (
                random.random()
                > collapse_probability
            ):
                continue

            collapse = {
                "cycle": (
                    agent.state["cycle"]
                ),
                "agent": (
                    agent.state["name"]
                ),
                "signature": (
                    agent.civilizational_signature
                ),
            }

            self.lineage_collapses.append(
                collapse
            )

            agent.inherited_fragments.clear()

            agent.local_mythologies.clear()

            agent.cultural_affinities.clear()

            agent.symbolic_drift += (
                random.uniform(
                    0.1,
                    0.3,
                )
            )

            agent.cultural_fragmentation += (
                random.uniform(
                    0.1,
                    0.3,
                )
            )

    # =========================================================
    # FRAGMENT MUTATION
    # =========================================================

    def _mutate_fragment(
        self,
        fragment,
    ):

        mutated = dict(fragment)

        mutated["mutation"] = (
            mutated.get(
                "mutation",
                0.0,
            )
            + random.uniform(
                -0.5,
                0.5,
            )
        )

        mutated["drift"] = (
            mutated.get(
                "drift",
                0.0,
            )
            + random.uniform(
                -0.3,
                0.3,
            )
        )

        mutated["ancestral_deformation"] = (
            True
        )

        return mutated

    # =========================================================
    # LINEAGE COMPATIBILITY
    # =========================================================

    def _lineage_compatibility(
        self,
        agent_a,
        agent_b,
    ):

        civilizational_distance = abs(

            agent_a.civilizational_signature

            - agent_b.civilizational_signature
        )

        drift_distance = abs(

            agent_a.symbolic_drift

            - agent_b.symbolic_drift
        )

        compatibility = (

            1.0

            - civilizational_distance
            * 0.5

            - drift_distance
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

    def _decay_ecology(
        self,
    ):

        self.ancestral_fragments = [

            fragment

            for fragment
            in self.ancestral_fragments

            if random.random()
            < self.memory_decay
        ]

        if (
            len(self.ancestral_fragments)
            > 400
        ):

            self.ancestral_fragments = (
                self.ancestral_fragments[-400:]
            )

        self.memory_resurgences = [

            resurgence

            for resurgence
            in self.memory_resurgences

            if random.random()
            < self.memory_decay
        ]

        if (
            len(self.memory_resurgences)
            > 200
        ):

            self.memory_resurgences = (
                self.memory_resurgences[-200:]
            )

        self.lineage_collapses = [

            collapse

            for collapse
            in self.lineage_collapses

            if random.random()
            < self.lineage_decay
        ]

        if (
            len(self.lineage_collapses)
            > 200
        ):

            self.lineage_collapses = (
                self.lineage_collapses[-200:]
            )
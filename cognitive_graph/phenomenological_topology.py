import math
import random


class PhenomenologicalTopology:

    def __init__(
        self,
        graph,
    ):

        self.graph = graph

        # =====================================================
        # TOPOLOGICAL INSTABILITY
        # =====================================================

        self.fracture_decay = 0.992

        self.minimum_fracture_strength = 0.02

        self.relational_instability = {}

        self.local_corridors = {}

        self.ontological_islands = {}

    # =========================================================
    # PHENOMENOLOGICAL NEIGHBORS
    # =========================================================

    def phenomenological_neighbors(
        self,
        node_id,
        agent=None,
    ):

        local_edges = self.graph.adjacency.get(
            node_id,
            []
        )

        if agent is None:
            return list(local_edges)

        visible_edges = []

        for edge in local_edges:

            if self._edge_is_excluded(
                edge,
                agent,
            ):
                continue

            if not self._edge_is_locally_viable(
                edge,
                agent,
            ):
                continue

            visible_edges.append(edge)

        return visible_edges

    # =========================================================
    # EDGE EXCLUSION
    # =========================================================

    def _edge_is_excluded(
        self,
        edge,
        agent,
    ):

        exclusion_pressure = (

            agent.fragmentation

            + agent.compatibility_tension

            + agent.collapse_exposure
        )

        source_signature = (
            math.sin(
                edge.source.activation
                + edge.source.salience
            )
        )

        target_signature = (
            math.cos(
                edge.target.activation
                + edge.target.salience
            )
        )

        incompatibility = abs(
            source_signature
            - target_signature
        )

        incompatibility += abs(

            agent.reality_signature
            - (
                source_signature
                + target_signature
            ) * 0.5
        )

        exclusion_probability = (

            incompatibility * 0.12

            + exclusion_pressure * 0.08
        )

        exclusion_probability = min(
            0.92,
            exclusion_probability,
        )

        return (
            random.random()
            < exclusion_probability
        )

    # =========================================================
    # LOCAL VIABILITY
    # =========================================================

    def _edge_is_locally_viable(
        self,
        edge,
        agent,
    ):

        local_flow = (
            self.graph.get_corridor_flow(
                edge.source.id,
                edge.target.id,
            )
        )

        habitat = (
            self.graph.cognitive_habitats.get(
                edge.target.id,
                {}
            )
        )

        habitat_strength = habitat.get(
            "strength",
            0.0,
        )

        viability = (

            edge.weight * 0.35

            + local_flow * 0.40

            + habitat_strength * 0.15

            + agent.local_coherence
            * 0.10
        )

        instability = (

            agent.fragmentation * 0.30

            + agent.ontological_fatigue
            * 0.25

            + edge.target.tension * 0.15
        )

        return viability > instability

    # =========================================================
    # TOPOLOGICAL FRACTURES
    # =========================================================

    def propagate_topological_fractures(
        self,
        agents,
    ):

        for agent in agents:

            local_edges = []

            for node_id in (
                self.graph.nodes.keys()
            ):

                edges = (
                    self.phenomenological_neighbors(
                        node_id,
                        agent,
                    )
                )

                local_edges.extend(edges)

            fracture_pressure = (

                agent.fragmentation

                + agent.compatibility_tension

                + agent.collapse_exposure
            )

            if fracture_pressure < 0.2:
                continue

            self._apply_local_fractures(
                local_edges,
                fracture_pressure,
            )

    # =========================================================
    # APPLY FRACTURES
    # =========================================================

    def _apply_local_fractures(
        self,
        edges,
        pressure,
    ):

        for edge in edges:

            fracture_probability = min(
                0.85,
                pressure * 0.08,
            )

            if (
                random.random()
                > fracture_probability
            ):
                continue

            edge.weight *= random.uniform(
                0.70,
                0.96,
            )

            edge.weight = max(
                self.graph.minimum_edge_weight,
                edge.weight,
            )

            if (
                random.random()
                < pressure * 0.03
            ):

                self.graph.register_bifurcation(
                    edge.source.id,
                    edge.target.id,
                    energy=random.uniform(
                        0.05,
                        0.30,
                    ),
                    metastability=pressure,
                )

    # =========================================================
    # LOCAL CORRIDORS
    # =========================================================

    def generate_local_corridors(
        self,
        agents,
    ):

        for agent in agents:

            if (
                agent.local_coherence
                < 0.15
            ):
                continue

            if (
                len(agent.local_alliances)
                == 0
            ):
                continue

            active_nodes = (
                self.graph.most_active_nodes(
                    limit=6
                )
            )

            if len(active_nodes) < 2:
                continue

            source = random.choice(
                active_nodes
            )

            target = random.choice(
                active_nodes
            )

            if source.id == target.id:
                continue

            corridor_energy = (

                agent.local_coherence

                * random.uniform(
                    0.05,
                    0.25,
                )
            )

            self.graph.register_bifurcation(
                source.id,
                target.id,
                energy=corridor_energy,
                metastability=(
                    agent.local_coherence
                ),
            )

    # =========================================================
    # RELATIONAL DIVERGENCE
    # =========================================================

    def relational_divergence(
        self,
        agents,
    ):

        divergence_map = {}

        for agent in agents:

            local_structure = {}

            for node_id in (
                self.graph.nodes.keys()
            ):

                neighbors = (
                    self.phenomenological_neighbors(
                        node_id,
                        agent,
                    )
                )

                local_structure[node_id] = len(
                    neighbors
                )

            divergence_map[
                id(agent)
            ] = local_structure

        return divergence_map

    # =========================================================
    # ONTOLOGICAL ISLANDS
    # =========================================================

    def detect_ontological_islands(
        self,
        agents,
    ):

        islands = []

        for agent in agents:

            accessible = set()

            for node_id in (
                self.graph.nodes.keys()
            ):

                neighbors = (
                    self.phenomenological_neighbors(
                        node_id,
                        agent,
                    )
                )

                if len(neighbors) > 0:

                    accessible.add(node_id)

            if len(accessible) == 0:
                continue

            islands.append(
                {
                    "agent": id(agent),
                    "accessible_nodes": (
                        accessible
                    ),
                    "fragmentation": (
                        agent.fragmentation
                    ),
                    "coherence": (
                        agent.local_coherence
                    ),
                }
            )

        return islands
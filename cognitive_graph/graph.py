# cognitive_graph/graph.py

from collections import defaultdict
import math
import random
import time

from cognitive_graph.node import CognitiveNode
from cognitive_graph.edge import CognitiveEdge


class CognitiveGraph:

    def __init__(self):

        self.nodes = {}

        self.edges = []

        self.adjacency = defaultdict(list)

        # =====================================================
        # BIFURCATION FIELD
        # =====================================================

        self.active_bifurcations = []

        self.bifurcation_decay = 0.96

        self.minimum_bifurcation_energy = 0.01

        # =====================================================
        # STRUCTURAL PLASTICITY
        # =====================================================

        self.edge_strengthening_rate = 0.015

        self.edge_weakening_rate = 0.003

        self.minimum_edge_weight = 0.05

        self.maximum_edge_weight = 3.0

        self.emergent_connection_threshold = 0.35

        # =====================================================
        # COGNITIVE HABITATS
        # =====================================================

        self.cognitive_habitats = {}

        self.habitat_decay = 0.985

        self.minimum_habitat_strength = 0.05

        # =====================================================
        # ECOLOGICAL FIELD
        # =====================================================

        self.ecological_field = {}

        self.ecological_decay = 0.985

        self.minimum_ecological_strength = 0.01

        self.long_range_corridors = {}

        self.corridor_decay = 0.992

        self.minimum_corridor_flow = 0.02

    # =========================================================
    # NODE MANAGEMENT
    # =========================================================

    def add_node(
        self,
        node_id,
        data=None
    ):

        if node_id not in self.nodes:

            self.nodes[node_id] = CognitiveNode(
                node_id,
                data
            )

        return self.nodes[node_id]

    # =========================================================
    # EDGE MANAGEMENT
    # =========================================================

    def add_edge(
        self,
        source_id,
        target_id,
        weight=1.0,
        relation="association"
    ):

        existing = self.find_edge(
            source_id,
            target_id,
        )

        if existing is not None:
            return existing

        source = self.add_node(source_id)

        target = self.add_node(target_id)

        edge = CognitiveEdge(
            source,
            target,
            weight,
            relation
        )

        self.edges.append(edge)

        self.adjacency[source_id].append(
            edge
        )

        return edge

    def find_edge(
        self,
        source_id,
        target_id,
    ):

        for edge in self.adjacency.get(
            source_id,
            []
        ):

            if edge.target.id == target_id:
                return edge

        return None

    # =========================================================
    # GRAPH ACCESS
    # =========================================================

    def get_node(self, node_id):

        return self.nodes.get(node_id)

    def neighbors(self, node_id):

        return self.adjacency.get(
            node_id,
            []
        )

    def get_neighbors(self, node_id):

        edges = self.adjacency.get(
            node_id,
            []
        )

        return [
            edge.target.id
            for edge in edges
        ]

    # =========================================================
    # BIFURCATION FIELD
    # =========================================================

    def register_bifurcation(
        self,
        source_id,
        target_id,
        energy,
        metastability=0.0,
    ):

        bifurcation = {

            "source": source_id,

            "target": target_id,

            "energy": energy,

            "metastability": metastability,

            "stability": energy,

            "created_at": time.time(),
        }

        self.active_bifurcations.append(
            bifurcation
        )

        self._register_corridor_flow(
            source_id,
            target_id,
            energy,
        )

    def tick_bifurcations(self):

        surviving = []

        for bifurcation in (
            self.active_bifurcations
        ):

            bifurcation["energy"] *= (
                self.bifurcation_decay
            )

            bifurcation["stability"] *= (
                self.bifurcation_decay
            )

            if (
                bifurcation["energy"]
                >= self.minimum_bifurcation_energy
            ):

                surviving.append(
                    bifurcation
                )

        self.active_bifurcations = surviving

    def get_active_bifurcations(self):

        return list(
            self.active_bifurcations
        )

    # =========================================================
    # STRUCTURAL PLASTICITY
    # =========================================================

    def tick_structural_plasticity(
        self,
    ):

        self._strengthen_corridors()

        self._weaken_unused_edges()

        self._create_emergent_connections()

    # =========================================================
    # CORRIDOR REINFORCEMENT
    # =========================================================

    def _strengthen_corridors(self):

        for bifurcation in (
            self.active_bifurcations
        ):

            source_id = bifurcation[
                "source"
            ]

            target_id = bifurcation[
                "target"
            ]

            stability = bifurcation[
                "stability"
            ]

            edge = self.find_edge(
                source_id,
                target_id,
            )

            if edge is None:
                continue

            reinforcement = (
                stability
                * self.edge_strengthening_rate
            )

            ecological_modifier = (
                1.0
                + self.get_corridor_flow(
                    source_id,
                    target_id,
                )
            )

            edge.weight = min(
                self.maximum_edge_weight,
                edge.weight
                + reinforcement
                * ecological_modifier,
            )

    # =========================================================
    # EDGE WEAKENING
    # =========================================================

    def _weaken_unused_edges(self):

        surviving_edges = []

        surviving_adjacency = defaultdict(
            list
        )

        for edge in self.edges:

            source_id = edge.source.id

            target_id = edge.target.id

            active = False

            for bifurcation in (
                self.active_bifurcations
            ):

                if (
                    bifurcation["source"]
                    == source_id
                    and
                    bifurcation["target"]
                    == target_id
                ):

                    active = True
                    break

            if not active:

                ecological_resistance = (
                    self.get_corridor_flow(
                        source_id,
                        target_id,
                    )
                )

                weakening = (
                    self.edge_weakening_rate
                    * (1.0 - ecological_resistance)
                )

                edge.weight *= (
                    1.0 - weakening
                )

            if (
                edge.weight
                >= self.minimum_edge_weight
            ):

                surviving_edges.append(
                    edge
                )

                surviving_adjacency[
                    source_id
                ].append(edge)

        self.edges = surviving_edges

        self.adjacency = surviving_adjacency

    # =========================================================
    # EMERGENT CONNECTIONS
    # =========================================================

    def _create_emergent_connections(
        self,
    ):

        for bifurcation in (
            self.active_bifurcations
        ):

            source_id = bifurcation[
                "source"
            ]

            target_id = bifurcation[
                "target"
            ]

            stability = bifurcation[
                "stability"
            ]

            existing = self.find_edge(
                source_id,
                target_id,
            )

            if existing is not None:
                continue

            if (
                stability
                < self.emergent_connection_threshold
            ):
                continue

            self.add_edge(
                source_id=source_id,
                target_id=target_id,
                weight=stability,
                relation="emergent_corridor",
            )

    # =========================================================
    # ECOLOGICAL FIELD
    # =========================================================

    def tick_ecological_field(
        self,
    ):

        self._update_ecological_field()

        self._decay_ecological_field()

        self._update_long_range_corridors()

    def _update_ecological_field(
        self,
    ):

        for node_id, node in (
            self.nodes.items()
        ):

            habitat = (
                self.cognitive_habitats.get(
                    node_id,
                    {}
                )
            )

            density = habitat.get(
                "density",
                0.0,
            )

            stability = habitat.get(
                "stability",
                0.0,
            )

            activation = getattr(
                node,
                "activation",
                0.0,
            )

            tension = getattr(
                node,
                "tension",
                0.0,
            )

            salience = getattr(
                node,
                "salience",
                0.0,
            )

            attractor_strength = getattr(
                node,
                "attractor_strength",
                0.0,
            )

            ecological_pressure = (

                activation * 0.35

                + tension * 0.30

                + density * 0.10

                + stability * 0.15
            )

            habitat_retention = (

                attractor_strength * 0.45

                + salience * 0.25

                + stability * 0.20
            )

            migration_potential = max(
                0.0,
                ecological_pressure
                - habitat_retention
            )

            permeability = (
                1.0
                / (
                    1.0
                    + density * 0.15
                )
            )

            ecological_state = {

                "pressure": (
                    ecological_pressure
                ),

                "retention": (
                    habitat_retention
                ),

                "migration_potential": (
                    migration_potential
                ),

                "permeability": (
                    permeability
                ),

                "stability": (
                    stability
                ),

                "updated_at": (
                    time.time()
                ),
            }

            self.ecological_field[
                node_id
            ] = ecological_state

    def _decay_ecological_field(
        self,
    ):

        surviving = {}

        for node_id, state in (
            self.ecological_field.items()
        ):

            state["pressure"] *= (
                self.ecological_decay
            )

            state["retention"] *= (
                self.ecological_decay
            )

            state["migration_potential"] *= (
                self.ecological_decay
            )

            if (
                state["migration_potential"]
                >= self.minimum_ecological_strength
            ):

                surviving[node_id] = (
                    state
                )

        self.ecological_field = surviving

    # =========================================================
    # LONG RANGE CORRIDORS
    # =========================================================

    def _register_corridor_flow(
        self,
        source_id,
        target_id,
        energy,
    ):

        key = (
            source_id,
            target_id,
        )

        if key not in self.long_range_corridors:

            self.long_range_corridors[
                key
            ] = {

                "flow": 0.0,

                "stability": 0.0,

                "last_update": (
                    time.time()
                ),
            }

        corridor = (
            self.long_range_corridors[key]
        )

        corridor["flow"] += (
            energy * 0.25
        )

        corridor["stability"] += (
            energy * 0.15
        )

        corridor["last_update"] = (
            time.time()
        )

    def _update_long_range_corridors(
        self,
    ):

        surviving = {}

        for key, corridor in (
            self.long_range_corridors.items()
        ):

            corridor["flow"] *= (
                self.corridor_decay
            )

            corridor["stability"] *= (
                self.corridor_decay
            )

            if (
                corridor["flow"]
                >= self.minimum_corridor_flow
            ):

                surviving[key] = corridor

        self.long_range_corridors = surviving

    def get_corridor_flow(
        self,
        source_id,
        target_id,
    ):

        corridor = (
            self.long_range_corridors.get(
                (
                    source_id,
                    target_id,
                )
            )
        )

        if corridor is None:
            return 0.0

        return corridor.get(
            "flow",
            0.0,
        )

    # =========================================================
    # HABITAT DYNAMICS
    # =========================================================

    def tick_cognitive_habitats(
        self,
    ):

        self._update_habitats()

        self._decay_habitats()

    def _update_habitats(
        self,
    ):

        for node_id, node in (
            self.nodes.items()
        ):

            local_edges = self.adjacency.get(
                node_id,
                []
            )

            local_density = len(
                local_edges
            )

            local_bifurcations = 0

            local_stability = 0.0

            for bifurcation in (
                self.active_bifurcations
            ):

                if (
                    bifurcation["source"]
                    == node_id
                ):

                    local_bifurcations += 1

                    local_stability += (
                        bifurcation["stability"]
                    )

            corridor_flow = 0.0

            for (
                source_id,
                target_id,
            ), corridor in (
                self.long_range_corridors.items()
            ):

                if source_id == node_id:

                    corridor_flow += (
                        corridor["flow"]
                    )

            habitat_strength = (

                node.activation * 0.30

                + node.salience * 0.20

                + node.tension * 0.15

                + local_density * 0.10

                + local_bifurcations * 0.10

                + corridor_flow * 0.15
            )

            habitat_type = (
                self._classify_habitat(
                    node,
                    local_bifurcations,
                    local_stability,
                    corridor_flow,
                )
            )

            self.cognitive_habitats[
                node_id
            ] = {

                "type": habitat_type,

                "strength": habitat_strength,

                "activation": (
                    node.activation
                ),

                "salience": (
                    node.salience
                ),

                "tension": (
                    node.tension
                ),

                "density": (
                    local_density
                ),

                "bifurcations": (
                    local_bifurcations
                ),

                "stability": (
                    local_stability
                ),

                "corridor_flow": (
                    corridor_flow
                ),

                "updated_at": (
                    time.time()
                ),
            }

    # =========================================================
    # HABITAT CLASSIFICATION
    # =========================================================

    def _classify_habitat(
        self,
        node,
        local_bifurcations,
        local_stability,
        corridor_flow,
    ):

        if (
            corridor_flow > 0.8
            and node.activation > 0.5
        ):
            return "migratory"

        if (
            node.tension > 0.7
            and local_bifurcations > 1
        ):
            return "unstable"

        if (
            local_bifurcations > 2
            and node.activation > 0.4
        ):
            return "exploratory"

        if (
            node.attractor_strength > 0.5
            and node.salience > 0.5
        ):
            return "attractive"

        if (
            node.activation < 0.15
            and node.salience < 0.15
        ):
            return "dormant"

        return "transitional"

    # =========================================================
    # HABITAT DECAY
    # =========================================================

    def _decay_habitats(
        self,
    ):

        surviving = {}

        for node_id, habitat in (
            self.cognitive_habitats.items()
        ):

            habitat["strength"] *= (
                self.habitat_decay
            )

            if (
                habitat["strength"]
                >= self.minimum_habitat_strength
            ):

                surviving[node_id] = (
                    habitat
                )

        self.cognitive_habitats = surviving

    def get_cognitive_habitats(
        self,
    ):

        return dict(
            self.cognitive_habitats
        )

    def get_ecological_state(
        self,
        node_id,
    ):

        return self.ecological_field.get(
            node_id,
            {}
        )

    # =========================================================
    # FIELD DECAY
    # =========================================================

    def decay(
        self,
        activation_decay=0.95,
        salience_decay=0.97,
        tension_decay=0.99,
        pressure_decay=0.96,
    ):

        for node in self.nodes.values():

            attractor_resistance = (
                1.0
                - min(
                    node.attractor_strength * 0.2,
                    0.5
                )
            )

            pressure_modifier = (
                1.0
                + node.competitive_pressure * 0.05
            )

            node.activation *= (
                activation_decay
                * attractor_resistance
                / pressure_modifier
            )

            node.salience *= (
                salience_decay
                * attractor_resistance
            )

            node.tension *= (
                tension_decay
            )

            node.competitive_pressure *= (
                pressure_decay
            )

            if node.activation < 0.001:
                node.activation = 0.0

            if node.salience < 0.001:
                node.salience = 0.0

            if node.tension < 0.001:
                node.tension = 0.0

            if (
                node.competitive_pressure
                < 0.001
            ):
                node.competitive_pressure = 0.0

        self.tick_bifurcations()

        self.tick_structural_plasticity()

        self.tick_cognitive_habitats()

        self.tick_ecological_field()

    # =========================================================
    # STIMULATION
    # =========================================================

    def stimulate_node(
        self,
        node_id,
        activation=1.0,
        salience=0.5,
        tension=0.0
    ):

        node = self.add_node(node_id)

        node.activation += activation

        node.salience += salience

        node.tension += tension

    # =========================================================
    # FIELD ANALYSIS
    # =========================================================

    def most_active_nodes(
        self,
        limit=10
    ):

        return sorted(
            self.nodes.values(),
            key=lambda n: n.activation,
            reverse=True
        )[:limit]

    def latent_nodes(
        self,
        activation_max=0.2
    ):

        return [

            node

            for node in self.nodes.values()

            if (
                node.activation
                <= activation_max
            )
        ]

    def local_density(
        self,
        node_id
    ):

        return len(
            self.adjacency.get(
                node_id,
                []
            )
        )
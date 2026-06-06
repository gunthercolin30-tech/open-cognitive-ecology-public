# cognitive_graph/bifurcation.py

import math
import random


class CognitiveBifurcationEngine:
    """
    Distributed ecological bifurcation dynamics.

    This module does NOT:
    - control propagation globally
    - create centralized cognition
    - optimize globally
    - impose symbolic routing

    It only computes:
    - local metastability
    - ecological migration potential
    - distributed divergence pressure
    - corridor emergence tendencies
    - dissipative topological plasticity
    """

    def __init__(
        self,
        metastability_threshold=0.6,
        tension_weight=0.35,
        activation_weight=0.25,
        competition_weight=0.20,
        migration_weight=0.20,
        max_branch_factor=3,
        minimum_branch_energy=0.05,

        # =====================================================
        # DISSIPATIVE TOPOLOGY
        # =====================================================

        branch_decay_factor=0.985,
        branch_cost_factor=0.020,

        fatigue_gain=0.015,
        fatigue_decay=0.995,

        saturation_gain=0.010,
        saturation_decay=0.997,

        collapse_probability_factor=0.015,

        topological_instability_factor=0.30,

        regenerative_bias=0.10,
    ):

        self.metastability_threshold = (
            metastability_threshold
        )

        self.tension_weight = (
            tension_weight
        )

        self.activation_weight = (
            activation_weight
        )

        self.competition_weight = (
            competition_weight
        )

        self.migration_weight = (
            migration_weight
        )

        self.max_branch_factor = (
            max_branch_factor
        )

        self.minimum_branch_energy = (
            minimum_branch_energy
        )

        # =====================================================
        # DISSIPATIVE PARAMETERS
        # =====================================================

        self.branch_decay_factor = (
            branch_decay_factor
        )

        self.branch_cost_factor = (
            branch_cost_factor
        )

        self.fatigue_gain = (
            fatigue_gain
        )

        self.fatigue_decay = (
            fatigue_decay
        )

        self.saturation_gain = (
            saturation_gain
        )

        self.saturation_decay = (
            saturation_decay
        )

        self.collapse_probability_factor = (
            collapse_probability_factor
        )

        self.topological_instability_factor = (
            topological_instability_factor
        )

        self.regenerative_bias = (
            regenerative_bias
        )

    # =========================================================
    # METASTABILITY
    # =========================================================

    def compute_metastability(
        self,
        activation,
        tension,
        competition,
        migration,
    ):

        activation = self._normalize(
            activation
        )

        tension = self._normalize(
            tension
        )

        competition = self._normalize(
            competition
        )

        migration = self._normalize(
            migration
        )

        metastability = (

            activation
            * self.activation_weight

            + tension
            * self.tension_weight

            + competition
            * self.competition_weight

            + migration
            * self.migration_weight
        )

        return min(
            1.0,
            metastability,
        )

    # =========================================================
    # CANDIDATE DETECTION
    # =========================================================

    def detect_bifurcation_candidates(
        self,
        graph,
    ):

        candidates = []

        for node_id, node in (
            graph.nodes.items()
        ):

            self._maintain_local_topology(
                node
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

            competition = (
                self._compute_local_competition(
                    graph,
                    node_id,
                )
            )

            ecology = (
                graph.get_ecological_state(
                    node_id
                )
            )

            migration = ecology.get(
                "migration_potential",
                0.0,
            )

            metastability = (
                self.compute_metastability(
                    activation=activation,
                    tension=tension,
                    competition=competition,
                    migration=migration,
                )
            )

            # =================================================
            # TOPOLOGICAL INSTABILITY
            # =================================================

            fatigue = getattr(
                node,
                "branch_fatigue",
                0.0,
            )

            saturation = getattr(
                node,
                "branch_saturation",
                0.0,
            )

            instability = (

                fatigue * 0.5

                + saturation * 0.5
            )

            metastability -= (
                instability
                * self.topological_instability_factor
            )

            if (
                metastability
                >= self.metastability_threshold
            ):

                candidates.append(
                    {
                        "node_id": node_id,

                        "metastability": (
                            metastability
                        ),

                        "activation": (
                            activation
                        ),

                        "tension": (
                            tension
                        ),

                        "competition": (
                            competition
                        ),

                        "migration": (
                            migration
                        ),
                    }
                )

        return sorted(
            candidates,
            key=lambda x: x[
                "metastability"
            ],
            reverse=True,
        )

    # =========================================================
    # LOCAL COMPETITION
    # =========================================================

    def _compute_local_competition(
        self,
        graph,
        node_id,
    ):

        neighbors = graph.get_neighbors(
            node_id
        )

        if not neighbors:
            return 0.0

        local_energies = []

        for neighbor_id in neighbors:

            neighbor = (
                graph.nodes.get(
                    neighbor_id
                )
            )

            if neighbor is None:
                continue

            local_energies.append(
                getattr(
                    neighbor,
                    "activation",
                    0.0,
                )
            )

        if not local_energies:
            return 0.0

        mean_energy = (
            sum(local_energies)
            / len(local_energies)
        )

        variance = sum(
            (
                e - mean_energy
            ) ** 2
            for e in local_energies
        ) / len(local_energies)

        return self._normalize(
            math.sqrt(
                variance
            )
        )

    # =========================================================
    # ECOLOGICAL BRANCH DISTRIBUTION
    # =========================================================

    def generate_branch_distribution(
        self,
        graph,
        node_id,
    ):

        neighbors = graph.get_neighbors(
            node_id
        )

        if not neighbors:
            return []

        node = graph.nodes[node_id]

        source_energy = getattr(
            node,
            "activation",
            0.0,
        )

        if (
            source_energy
            <= self.minimum_branch_energy
        ):
            return []

        source_ecology = (
            graph.get_ecological_state(
                node_id
            )
        )

        source_pressure = (
            source_ecology.get(
                "pressure",
                0.0,
            )
        )

        source_migration = (
            source_ecology.get(
                "migration_potential",
                0.0,
            )
        )

        fatigue = getattr(
            node,
            "branch_fatigue",
            0.0,
        )

        saturation = getattr(
            node,
            "branch_saturation",
            0.0,
        )

        scored_neighbors = []

        for neighbor_id in neighbors:

            neighbor = (
                graph.nodes.get(
                    neighbor_id
                )
            )

            if neighbor is None:
                continue

            neighbor_activation = getattr(
                neighbor,
                "activation",
                0.0,
            )

            neighbor_tension = getattr(
                neighbor,
                "tension",
                0.0,
            )

            neighbor_ecology = (
                graph.get_ecological_state(
                    neighbor_id
                )
            )

            target_retention = (
                neighbor_ecology.get(
                    "retention",
                    0.0,
                )
            )

            target_permeability = (
                neighbor_ecology.get(
                    "permeability",
                    1.0,
                )
            )

            target_migration = (
                neighbor_ecology.get(
                    "migration_potential",
                    0.0,
                )
            )

            exploratory_bias = (

                (
                    neighbor_tension
                    + 0.1
                )

                / (
                    neighbor_activation
                    + 0.1
                )
            )

            ecological_bias = (

                source_pressure * 0.25

                + source_migration * 0.25

                + target_permeability * 0.30

                + target_retention * 0.10

                - target_migration * 0.10
            )

            ecological_bias *= (
                random.uniform(
                    0.85,
                    1.15,
                )
            )

            # ================================================
            # TOPOLOGICAL DAMPING
            # ================================================

            topological_drag = (

                fatigue * 0.4

                + saturation * 0.4
            )

            ecological_bias *= max(
                0.05,
                1.0 - topological_drag,
            )

            # ================================================
            # REGENERATIVE EXPLORATION
            # ================================================

            if (
                target_migration > 0.4
            ):

                ecological_bias += (
                    self.regenerative_bias
                )

            total_bias = (
                exploratory_bias
                * ecological_bias
            )

            scored_neighbors.append(
                (
                    neighbor_id,
                    total_bias,
                )
            )

        if not scored_neighbors:
            return []

        scored_neighbors.sort(
            key=lambda x: x[1],
            reverse=True,
        )

        selected = scored_neighbors[
            : self.max_branch_factor
        ]

        total_score = sum(
            score
            for _, score in selected
        )

        if total_score <= 0:
            return []

        branches = []

        for neighbor_id, score in (
            selected
        ):

            branch_energy = (

                source_energy

                * (
                    score
                    / total_score
                )
            )

            # ================================================
            # BRANCH COST
            # ================================================

            branch_energy *= (
                self.branch_decay_factor
            )

            branch_energy -= (

                branch_energy
                * self.branch_cost_factor
            )

            if (
                branch_energy
                < self.minimum_branch_energy
            ):
                continue

            branches.append(
                {
                    "source": node_id,

                    "target": neighbor_id,

                    "energy": branch_energy,

                    "score": score,
                }
            )

        return branches

    # =========================================================
    # LOCAL DIVERGENCE
    # =========================================================

    def apply_local_divergence(
        self,
        graph,
        node_id,
    ):

        node = graph.nodes.get(
            node_id
        )

        if node is None:
            return None

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

        competition = (
            self._compute_local_competition(
                graph,
                node_id,
            )
        )

        ecology = (
            graph.get_ecological_state(
                node_id
            )
        )

        migration = ecology.get(
            "migration_potential",
            0.0,
        )

        metastability = (
            self.compute_metastability(

                activation,

                tension,

                competition,

                migration,
            )
        )

        fatigue = getattr(
            node,
            "branch_fatigue",
            0.0,
        )

        saturation = getattr(
            node,
            "branch_saturation",
            0.0,
        )

        instability = (

            fatigue * 0.5

            + saturation * 0.5
        )

        metastability -= (
            instability
            * self.topological_instability_factor
        )

        if (
            metastability
            < self.metastability_threshold
        ):

            return None

        # =====================================================
        # LOCAL TOPOLOGICAL COLLAPSE
        # =====================================================

        collapse_probability = (

            instability
            * self.collapse_probability_factor
        )

        if (
            random.random()
            < collapse_probability
        ):

            node.tension += 0.15

            print(
                "[BIFURCATION_COLLAPSE]",

                node_id,

                f"fatigue="
                f"{fatigue:.2f}",

                f"saturation="
                f"{saturation:.2f}",
            )

            return None

        branches = (
            self.generate_branch_distribution(
                graph,
                node_id,
            )
        )

        if not branches:
            return None

        return {

            "node_id": node_id,

            "metastability": (
                metastability
            ),

            "migration": (
                migration
            ),

            "branches": branches,
        }

    # =========================================================
    # LOCAL TOPOLOGICAL ECOLOGY
    # =========================================================

    def _maintain_local_topology(
        self,
        node,
    ):

        if not hasattr(
            node,
            "branch_fatigue",
        ):

            node.branch_fatigue = 0.0

        if not hasattr(
            node,
            "branch_saturation",
        ):

            node.branch_saturation = 0.0

        local_energy = (

            getattr(
                node,
                "activation",
                0.0,
            )

            + getattr(
                node,
                "tension",
                0.0,
            )
        )

        node.branch_fatigue *= (
            self.fatigue_decay
        )

        node.branch_fatigue += (
            local_energy
            * self.fatigue_gain
        )

        node.branch_saturation *= (
            self.saturation_decay
        )

        node.branch_saturation += (
            local_energy
            * self.saturation_gain
        )

    # =========================================================
    # UTILITIES
    # =========================================================

    def _normalize(
        self,
        value,
    ):

        if value <= 0:
            return 0.0

        return min(
            1.0,
            value,
        )
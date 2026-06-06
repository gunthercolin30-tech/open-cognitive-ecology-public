# processes/bifurcation_process.py

import asyncio
import random

from cognitive_graph.bifurcation import (
    CognitiveBifurcationEngine,
)


class BifurcationProcess:
    """
    Distributed ecological bifurcation process.

    Responsibilities:
    - scan metastable ecological regions
    - generate exploratory migrations
    - redistribute energetic pressure
    - preserve local ecological causality
    - stabilize migratory corridors
    - maintain distributed field circulation

    This process does NOT:
    - control cognition globally
    - impose symbolic trajectories
    - create centralized navigation
    - optimize globally
    """

    def __init__(
        self,
        graph,
        event_bus=None,
        interval=2.0,
        max_active_bifurcations=8,
        branch_energy_decay=0.92,
        divergence_injection_ratio=0.15,
    ):

        self.graph = graph

        self.event_bus = event_bus

        self.interval = interval

        self.max_active_bifurcations = (
            max_active_bifurcations
        )

        self.branch_energy_decay = (
            branch_energy_decay
        )

        self.divergence_injection_ratio = (
            divergence_injection_ratio
        )

        self.engine = (
            CognitiveBifurcationEngine()
        )

        self.running = False

    # =========================================================
    # LIFECYCLE
    # =========================================================

    async def run(self):

        self.running = True

        while self.running:

            try:

                await self.step()

            except Exception as e:

                print(
                    f"[BifurcationProcess] error: {e}"
                )

            await asyncio.sleep(
                self.interval
            )

    def stop(self):

        self.running = False

    # =========================================================
    # MAIN STEP
    # =========================================================

    async def step(self):

        candidates = (
            self.engine
            .detect_bifurcation_candidates(
                self.graph
            )
        )

        if not candidates:
            return

        selected_candidates = candidates[
            : self.max_active_bifurcations
        ]

        random.shuffle(
            selected_candidates
        )

        for candidate in selected_candidates:

            await self._process_candidate(
                candidate
            )

    # =========================================================
    # CANDIDATE PROCESSING
    # =========================================================

    async def _process_candidate(
        self,
        candidate,
    ):

        node_id = candidate["node_id"]

        divergence = (
            self.engine
            .apply_local_divergence(
                self.graph,
                node_id,
            )
        )

        if divergence is None:
            return

        branches = divergence["branches"]

        if not branches:
            return

        ecological_branches = (
            self._compute_ecological_branches(
                branches
            )
        )

        self._register_bifurcations(
            divergence,
            ecological_branches,
        )

        self._inject_branch_activation(
            ecological_branches
        )

        self._apply_ecological_feedback(
            node_id,
            ecological_branches,
        )

        await self._emit_bifurcation_event(
            divergence,
            ecological_branches,
        )

    # =========================================================
    # ECOLOGICAL BRANCH DYNAMICS
    # =========================================================

    def _compute_ecological_branches(
        self,
        branches,
    ):

        ecological_branches = []

        for branch in branches:

            source_id = branch["source"]

            target_id = branch["target"]

            branch_energy = branch[
                "energy"
            ]

            source_ecology = (
                self.graph
                .get_ecological_state(
                    source_id
                )
            )

            target_ecology = (
                self.graph
                .get_ecological_state(
                    target_id
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

            target_retention = (
                target_ecology.get(
                    "retention",
                    0.0,
                )
            )

            target_permeability = (
                target_ecology.get(
                    "permeability",
                    1.0,
                )
            )

            ecological_modifier = (

                source_pressure * 0.35

                + source_migration * 0.30

                + target_permeability * 0.25

                + target_retention * 0.10
            )

            ecological_modifier = max(
                0.1,
                ecological_modifier,
            )

            ecological_energy = (
                branch_energy
                * ecological_modifier
            )

            ecological_branch = dict(
                branch
            )

            ecological_branch[
                "ecological_energy"
            ] = ecological_energy

            ecological_branches.append(
                ecological_branch
            )

        return ecological_branches

    # =========================================================
    # BIFURCATION REGISTRATION
    # =========================================================

    def _register_bifurcations(
        self,
        divergence,
        ecological_branches,
    ):

        source_id = divergence["node_id"]

        metastability = divergence[
            "metastability"
        ]

        for branch in ecological_branches:

            target_id = branch["target"]

            energy = branch[
                "ecological_energy"
            ]

            self.graph.register_bifurcation(

                source_id=source_id,

                target_id=target_id,

                energy=energy,

                metastability=metastability,
            )

            print(
                "[ECOLOGICAL_BIFURCATION]",

                f"{source_id} -> {target_id}",

                f"energy={energy:.2f}",

                f"metastability="
                f"{metastability:.2f}",
            )

    # =========================================================
    # ECOLOGICAL ENERGY REDISTRIBUTION
    # =========================================================

    def _inject_branch_activation(
        self,
        ecological_branches,
    ):

        for branch in ecological_branches:

            target_id = branch["target"]

            target_node = (
                self.graph.nodes.get(
                    target_id
                )
            )

            if target_node is None:
                continue

            ecological_energy = branch[
                "ecological_energy"
            ]

            injected_energy = (

                ecological_energy

                * self.divergence_injection_ratio
            )

            injected_energy *= (
                self.branch_energy_decay
            )

            target_node.activation += (
                injected_energy
            )

            self._increase_local_tension(
                target_node,
                injected_energy,
            )

            self._increase_local_salience(
                target_node,
                injected_energy,
            )

            self._increase_migratory_pressure(
                target_node,
                injected_energy,
            )

    # =========================================================
    # ECOLOGICAL FEEDBACK
    # =========================================================

    def _apply_ecological_feedback(
        self,
        source_id,
        ecological_branches,
    ):

        source_node = (
            self.graph.get_node(
                source_id
            )
        )

        if source_node is None:
            return

        cumulative_flux = 0.0

        for branch in ecological_branches:

            cumulative_flux += (
                branch[
                    "ecological_energy"
                ]
            )

        source_node.tension += (
            cumulative_flux * 0.05
        )

        source_node.salience += (
            cumulative_flux * 0.03
        )

    # =========================================================
    # LOCAL TENSION DYNAMICS
    # =========================================================

    def _increase_local_tension(
        self,
        node,
        injected_energy,
    ):

        current_tension = getattr(
            node,
            "tension",
            0.0,
        )

        tension_delta = (
            injected_energy * 0.25
        )

        node.tension = min(
            1.0,
            current_tension + tension_delta,
        )

    # =========================================================
    # LOCAL SALIENCE DYNAMICS
    # =========================================================

    def _increase_local_salience(
        self,
        node,
        injected_energy,
    ):

        current_salience = getattr(
            node,
            "salience",
            0.0,
        )

        salience_delta = (
            injected_energy * 0.15
        )

        node.salience = min(
            1.0,
            current_salience + salience_delta,
        )

    # =========================================================
    # MIGRATORY PRESSURE
    # =========================================================

    def _increase_migratory_pressure(
        self,
        node,
        injected_energy,
    ):

        current_pressure = getattr(
            node,
            "competitive_pressure",
            0.0,
        )

        pressure_delta = (
            injected_energy * 0.10
        )

        node.competitive_pressure = min(
            1.0,
            current_pressure + pressure_delta,
        )

    # =========================================================
    # EVENT EMISSION
    # =========================================================

    async def _emit_bifurcation_event(
        self,
        divergence,
        ecological_branches,
    ):

        if self.event_bus is None:
            return

        event = {

            "type": (
                "ecological_bifurcation"
            ),

            "node_id": divergence[
                "node_id"
            ],

            "metastability": divergence[
                "metastability"
            ],

            "branches": ecological_branches,
        }

        try:

            await self.event_bus.publish(
                event
            )

        except Exception as e:

            print(
                "[BifurcationProcess] "
                f"event emission failed: {e}"
            )
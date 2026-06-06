# politics/distributed_coordination_system.py

import math
import random


class DistributedCoordinationSystem:

    """
    Distributed local coordination ecology.

    No central administration.
    No global governance.
    No universal synchronization.
    No stable hierarchy.

    Coordination emerges locally from:
    - temporary compatibility
    - symbolic legitimacy
    - institutional attraction
    - narrative resonance
    - ecological pressure

    Coordination systems remain:
    - unstable
    - fragmented
    - partially transmissible
    - historically mutable
    - regionally incompatible
    """

    def __init__(
        self,
        name,
        center=(0.0, 0.0),
    ):

        self.name = name

        self.center = center

        # =====================================================
        # COORDINATION CORE
        # =====================================================

        self.coordination_signature = (
            random.uniform(
                -1.0,
                1.0,
            )
        )

        self.coordination_strength = (
            random.uniform(
                0.2,
                1.0,
            )
        )

        self.legitimacy = random.uniform(
            0.2,
            1.0,
        )

        self.fragmentation = 0.0

        self.organizational_pressure = (
            0.0
        )

        self.bureaucratic_drift = (
            0.0
        )

        self.coordination_fatigue = (
            0.0
        )

        self.collapse_exposure = (
            0.0
        )

        # =====================================================
        # ECOLOGICAL DYNAMICS
        # =====================================================

        self.influence_radius = random.uniform(
            5.0,
            15.0,
        )

        self.coordination_density = (
            random.uniform(
                0.1,
                1.0,
            )
        )

        self.synchronization_instability = (
            random.uniform(
                0.0,
                0.5,
            )
        )

        self.normative_pressure = (
            random.uniform(
                0.0,
                1.0,
            )
        )

        self.coalition_capacity = (
            random.uniform(
                0.0,
                1.0,
            )
        )

        # =====================================================
        # NETWORK STRUCTURE
        # =====================================================

        self.coordinated_agents = set()

        self.coordinated_institutions = (
            set()
        )

        self.local_coalitions = set()

        self.excluded_entities = set()

        self.conflicting_systems = set()

        # =====================================================
        # TEMPORAL DYNAMICS
        # =====================================================

        self.temporal_drift = random.uniform(
            0.0,
            1.0,
        )

        self.organizational_mutation_rate = (
            random.uniform(
                0.001,
                0.02,
            )
        )

        self.local_synchronization = (
            random.uniform(
                0.0,
                1.0,
            )
        )

        # =====================================================
        # HISTORICAL MEMORY
        # =====================================================

        self.coordination_history = []

        self.coalition_history = []

        self.fragmentation_history = []

        self.collapse_history = []

        self.normative_history = []

    # =========================================================
    # EVOLUTION
    # =========================================================

    def evolve(
        self,
        nearby_agents=None,
        nearby_institutions=None,
        nearby_systems=None,
    ):

        self._update_internal_dynamics()

        self._coordinate_agents(
            nearby_agents
        )

        self._coordinate_institutions(
            nearby_institutions
        )

        self._update_coalitions(
            nearby_systems
        )

        self._update_conflicts(
            nearby_systems
        )

        self._generate_coordination_events()

    # =========================================================
    # INTERNAL DYNAMICS
    # =========================================================

    def _update_internal_dynamics(
        self,
    ):

        self.organizational_pressure *= (
            0.996
        )

        self.fragmentation *= (
            0.997
        )

        self.bureaucratic_drift *= (
            0.997
        )

        self.coordination_fatigue *= (
            0.997
        )

        self.collapse_exposure *= (
            0.996
        )

        self.synchronization_instability *= (
            0.997
        )

        self.coordination_strength += (
            random.uniform(
                -0.01,
                0.01,
            )
        )

        self.legitimacy += (
            random.uniform(
                -0.01,
                0.008,
            )
        )

        self.temporal_drift += (
            random.uniform(
                -0.005,
                0.01,
            )
        )

        self.local_synchronization += (
            random.uniform(
                -0.01,
                0.01,
            )
        )

        self.coordination_strength = max(
            0.0,
            min(
                2.0,
                self.coordination_strength,
            )
        )

        self.legitimacy = max(
            0.0,
            min(
                2.0,
                self.legitimacy,
            )
        )

        self.local_synchronization = max(
            0.0,
            min(
                2.0,
                self.local_synchronization,
            )
        )

        collapse_risk = (

            self.fragmentation
            * 0.01

            + self.coordination_fatigue
            * 0.01

            + self.synchronization_instability
            * 0.005
        )

        if (
            random.random()
            < collapse_risk
        ):

            self._trigger_coordination_collapse()

    # =========================================================
    # AGENT COORDINATION
    # =========================================================

    def _coordinate_agents(
        self,
        nearby_agents,
    ):

        if not nearby_agents:
            return

        for agent in nearby_agents:

            dx = self.center[0] - agent.x
            dy = self.center[1] - agent.y

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if (
                distance
                > self.influence_radius
            ):
                continue

            compatibility = 1.0 - abs(

                self.coordination_signature

                - agent.civilizational_signature
            )

            compatibility = max(
                0.0,
                compatibility,
            )

            coordination_probability = (

                compatibility
                * 0.02

                + self.legitimacy
                * 0.01
            )

            if (
                random.random()
                < coordination_probability
            ):

                self.coordinated_agents.add(
                    id(agent)
                )

                agent.local_coherence += (
                    self.coordination_strength
                    * 0.002
                )

                agent.cultural_stability += (
                    self.local_synchronization
                    * 0.002
                )

                agent.compatibility_tension *= (
                    0.995
                )

            else:

                agent.compatibility_tension += (
                    0.002
                )

    # =========================================================
    # INSTITUTIONAL COORDINATION
    # =========================================================

    def _coordinate_institutions(
        self,
        nearby_institutions,
    ):

        if not nearby_institutions:
            return

        for institution in nearby_institutions:

            dx = (
                institution.center[0]
                - self.center[0]
            )

            dy = (
                institution.center[1]
                - self.center[1]
            )

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance > 12.0:
                continue

            compatibility = 1.0 - abs(

                institution.institutional_signature

                - self.coordination_signature
            )

            compatibility = max(
                0.0,
                compatibility,
            )

            coordination_probability = (

                compatibility
                * 0.03
            )

            if (
                random.random()
                < coordination_probability
            ):

                self.coordinated_institutions.add(
                    id(institution)
                )

                institution.legitimacy += (
                    0.002
                )

                institution.stability += (
                    0.002
                )

                institution.fragmentation *= (
                    0.996
                )

            else:

                institution.fragmentation += (
                    0.001
                )

    # =========================================================
    # COALITIONS
    # =========================================================

    def _update_coalitions(
        self,
        nearby_systems,
    ):

        if not nearby_systems:
            return

        for system in nearby_systems:

            if system is self:
                continue

            dx = (
                system.center[0]
                - self.center[0]
            )

            dy = (
                system.center[1]
                - self.center[1]
            )

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance > 15.0:
                continue

            compatibility = 1.0 - abs(

                system.coordination_signature

                - self.coordination_signature
            )

            compatibility = max(
                0.0,
                compatibility,
            )

            coalition_probability = (

                compatibility
                * 0.02

                + self.coalition_capacity
                * 0.01
            )

            if (
                random.random()
                < coalition_probability
            ):

                self.local_coalitions.add(
                    id(system)
                )

    # =========================================================
    # CONFLICTS
    # =========================================================

    def _update_conflicts(
        self,
        nearby_systems,
    ):

        if not nearby_systems:
            return

        for system in nearby_systems:

            if system is self:
                continue

            incompatibility = abs(

                system.coordination_signature

                - self.coordination_signature
            )

            conflict_probability = (

                incompatibility
                * 0.02

                + self.fragmentation
                * 0.01
            )

            if (
                random.random()
                < conflict_probability
            ):

                self.conflicting_systems.add(
                    id(system)
                )

                self.organizational_pressure += (
                    0.01
                )

                self.synchronization_instability += (
                    0.005
                )

    # =========================================================
    # EVENTS
    # =========================================================

    def _generate_coordination_events(
        self,
    ):

        probability = (

            0.002

            + self.coordination_strength
            * 0.005

            + self.bureaucratic_drift
            * 0.01
        )

        if (
            random.random()
            < probability
        ):

            event = {
                "coordination_strength": (
                    self.coordination_strength
                ),
                "legitimacy": (
                    self.legitimacy
                ),
                "fragmentation": (
                    self.fragmentation
                ),
                "coalitions": len(
                    self.local_coalitions
                ),
                "cycle": len(
                    self.coordination_history
                ),
            }

            self.coordination_history.append(
                event
            )

            if (
                len(self.coordination_history)
                > 120
            ):
                self.coordination_history.pop(
                    0
                )

    # =========================================================
    # COLLAPSE
    # =========================================================

    def _trigger_coordination_collapse(
        self,
    ):

        self.fragmentation += (
            random.uniform(
                0.2,
                0.5,
            )
        )

        self.coordination_fatigue += (
            random.uniform(
                0.1,
                0.3,
            )
        )

        self.synchronization_instability += (
            random.uniform(
                0.1,
                0.4,
            )
        )

        self.collapse_exposure += (
            random.uniform(
                0.1,
                0.5,
            )
        )

        self.coordination_strength *= (
            random.uniform(
                0.4,
                0.8,
            )
        )

        self.legitimacy *= (
            random.uniform(
                0.4,
                0.8,
            )
        )

        self.local_coalitions.clear()

        self.coordinated_agents.clear()

        self.coordinated_institutions.clear()

        collapse_event = {
            "collapse": True,
            "fragmentation": (
                self.fragmentation
            ),
            "legitimacy": (
                self.legitimacy
            ),
            "coordination_strength": (
                self.coordination_strength
            ),
        }

        self.collapse_history.append(
            collapse_event
        )

        if (
            len(self.collapse_history)
            > 120
        ):
            self.collapse_history.pop(0)
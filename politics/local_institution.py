# politics/local_institution.py

import math
import random


class LocalInstitution:

    """
    Dissipative political structure.

    No sovereignty.
    No central authority.
    No universal legitimacy.
    No stable governance.

    Institutions emerge locally from:
    - symbolic compatibility
    - narrative coordination
    - mythological attraction
    - ecological pressure
    - temporary civilizational coherence

    Institutions remain:
    - unstable
    - fragmented
    - historically mutable
    - partially transmissible
    - ecologically constrained
    """

    def __init__(
        self,
        name,
        center=(0.0, 0.0),
    ):

        self.name = name

        # =====================================================
        # LOCAL POSITION
        # =====================================================

        self.center = center

        # =====================================================
        # INSTITUTIONAL CORE
        # =====================================================

        self.institutional_signature = (
            random.uniform(
                -1.0,
                1.0,
            )
        )

        self.legitimacy = random.uniform(
            0.3,
            1.0,
        )

        self.stability = random.uniform(
            0.3,
            1.0,
        )

        self.fragmentation = 0.0

        self.coordination_capacity = (
            random.uniform(
                0.2,
                1.0,
            )
        )

        self.symbolic_influence = (
            random.uniform(
                0.2,
                1.0,
            )
        )

        self.mythological_density = (
            random.uniform(
                0.0,
                1.0,
            )
        )

        self.political_pressure = 0.0

        self.collapse_exposure = 0.0

        # =====================================================
        # LOCAL POWER ECOLOGY
        # =====================================================

        self.influence_radius = random.uniform(
            4.0,
            12.0,
        )

        self.attraction_strength = (
            random.uniform(
                0.1,
                1.0,
            )
        )

        self.exclusion_tension = (
            random.uniform(
                0.0,
                0.5,
            )
        )

        self.hierarchical_instability = (
            random.uniform(
                0.0,
                1.0,
            )
        )

        self.symbolic_currency = (
            random.uniform(
                0.0,
                1.0,
            )
        )

        # =====================================================
        # CIVILIZATIONAL MEMORY
        # =====================================================

        self.institutional_memory = []

        self.legitimacy_history = []

        self.symbolic_history = []

        self.collapse_history = []

        self.norm_fragments = []

        self.local_doctrines = set()

        self.allied_institutions = set()

        self.excluded_institutions = set()

        # =====================================================
        # DISSIPATIVE DYNAMICS
        # =====================================================

        self.temporal_drift = random.uniform(
            0.0,
            1.0,
        )

        self.norm_mutation_rate = (
            random.uniform(
                0.001,
                0.02,
            )
        )

        self.institutional_fatigue = (
            0.0
        )

        self.semiotic_instability = (
            0.0
        )

    # =========================================================
    # EVOLUTION
    # =========================================================

    def evolve(
        self,
        nearby_institutions=None,
        nearby_agents=None,
    ):

        self._update_internal_dynamics()

        self._generate_local_doctrines()

        self._mutate_norms()

        self._propagate_symbolic_influence(
            nearby_agents
        )

        self._update_institutional_relations(
            nearby_institutions
        )

        self._update_exclusions(
            nearby_institutions
        )

    # =========================================================
    # INTERNAL DYNAMICS
    # =========================================================

    def _update_internal_dynamics(
        self,
    ):

        self.political_pressure *= (
            0.996
        )

        self.fragmentation *= (
            0.997
        )

        self.collapse_exposure *= (
            0.996
        )

        self.institutional_fatigue *= (
            0.997
        )

        self.semiotic_instability *= (
            0.996
        )

        self.legitimacy += (
            random.uniform(
                -0.01,
                0.008,
            )
        )

        self.stability += (
            random.uniform(
                -0.008,
                0.006,
            )
        )

        self.symbolic_currency += (
            random.uniform(
                -0.01,
                0.01,
            )
        )

        self.temporal_drift += (
            random.uniform(
                -0.005,
                0.01,
            )
        )

        self.legitimacy = max(
            0.0,
            min(
                1.5,
                self.legitimacy,
            )
        )

        self.stability = max(
            0.0,
            min(
                1.5,
                self.stability,
            )
        )

        collapse_risk = (

            self.fragmentation
            * 0.01

            + self.institutional_fatigue
            * 0.01

            + self.semiotic_instability
            * 0.005
        )

        if (
            random.random()
            < collapse_risk
        ):

            self._trigger_institutional_collapse()

    # =========================================================
    # DOCTRINE GENERATION
    # =========================================================

    def _generate_local_doctrines(
        self,
    ):

        probability = (

            0.002

            + self.symbolic_influence
            * 0.01

            + self.mythological_density
            * 0.005
        )

        if (
            random.random()
            < probability
        ):

            doctrine = {
                "cycle": len(
                    self.institutional_memory
                ),
                "signature": (
                    self.institutional_signature
                ),
                "currency": (
                    self.symbolic_currency
                ),
                "drift": (
                    self.temporal_drift
                ),
            }

            self.norm_fragments.append(
                doctrine
            )

            self.local_doctrines.add(
                hash(
                    str(doctrine)
                )
            )

            if (
                len(self.norm_fragments)
                > 100
            ):
                self.norm_fragments.pop(0)

    # =========================================================
    # SYMBOLIC MUTATION
    # =========================================================

    def _mutate_norms(
        self,
    ):

        self.institutional_signature += (
            random.uniform(
                -0.01,
                0.01,
            )
            * self.norm_mutation_rate
        )

        self.symbolic_influence += (
            random.uniform(
                -0.02,
                0.02,
            )
            * self.norm_mutation_rate
        )

        self.hierarchical_instability += (
            random.uniform(
                -0.01,
                0.015,
            )
        )

        self.hierarchical_instability = max(
            0.0,
            min(
                2.0,
                self.hierarchical_instability,
            )
        )

    # =========================================================
    # SYMBOLIC PROPAGATION
    # =========================================================

    def _propagate_symbolic_influence(
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

            influence_factor = (

                self.symbolic_influence

                * self.legitimacy

                / (
                    1.0
                    + distance
                )
            )

            agent.mythological_pressure += (
                influence_factor
                * 0.01
            )

            agent.compatibility_tension += (
                self.exclusion_tension
                * 0.002
            )

            agent.cultural_stability += (
                self.coordination_capacity
                * 0.001
            )

            if (
                random.random()
                < influence_factor * 0.01
            ):

                agent.local_mythologies.add(
                    id(self)
                )

    # =========================================================
    # INSTITUTIONAL RELATIONS
    # =========================================================

    def _update_institutional_relations(
        self,
        nearby_institutions,
    ):

        if not nearby_institutions:
            return

        for institution in nearby_institutions:

            if institution is self:
                continue

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

            if distance > 10.0:
                continue

            compatibility = abs(

                institution.institutional_signature

                - self.institutional_signature
            )

            alliance_probability = max(
                0.0,
                0.03 - compatibility * 0.02,
            )

            if (
                random.random()
                < alliance_probability
            ):

                self.allied_institutions.add(
                    id(institution)
                )

    # =========================================================
    # EXCLUSIONS
    # =========================================================

    def _update_exclusions(
        self,
        nearby_institutions,
    ):

        if not nearby_institutions:
            return

        for institution in nearby_institutions:

            if institution is self:
                continue

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

            if distance > 8.0:
                continue

            incompatibility = abs(

                institution.institutional_signature

                - self.institutional_signature
            )

            exclusion_probability = (

                incompatibility
                * 0.02

                + self.fragmentation
                * 0.01
            )

            if (
                random.random()
                < exclusion_probability
            ):

                self.excluded_institutions.add(
                    id(institution)
                )

    # =========================================================
    # COLLAPSE
    # =========================================================

    def _trigger_institutional_collapse(
        self,
    ):

        self.fragmentation += (
            random.uniform(
                0.2,
                0.6,
            )
        )

        self.institutional_fatigue += (
            random.uniform(
                0.1,
                0.4,
            )
        )

        self.semiotic_instability += (
            random.uniform(
                0.1,
                0.3,
            )
        )

        self.collapse_exposure += (
            random.uniform(
                0.2,
                0.5,
            )
        )

        self.legitimacy *= random.uniform(
            0.4,
            0.8,
        )

        self.stability *= random.uniform(
            0.4,
            0.8,
        )

        self.allied_institutions.clear()

        self.local_doctrines.clear()

        collapse_event = {
            "collapse": True,
            "signature": (
                self.institutional_signature
            ),
            "fragmentation": (
                self.fragmentation
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
        
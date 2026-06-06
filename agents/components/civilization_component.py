# agents/components/civilization_component.py

import random


class CivilizationComponent:
    """
    Local civilizational dynamics.

    This component encapsulates:
    - civilizational signatures
    - cultural memory
    - mythological generation
    - symbolic drift
    - intergenerational transmission
    - cultural exclusions
    - civilizational collapses

    No universal history.
    No common temporality.
    No stable symbolic order.
    """

    def __init__(self):

        # =====================================================
        # CIVILIZATIONAL ECOLOGY
        # =====================================================

        self.civilizational_signature = (
            random.uniform(
                -1.0,
                1.0,
            )
        )

        self.cultural_stability = 1.0

        self.mythological_pressure = 0.0

        self.symbolic_drift = 0.0

        self.cultural_fragmentation = 0.0

        self.civilizational_fatigue = 0.0

        self.semiotic_instability = 0.0

        # =====================================================
        # CULTURAL HISTORY
        # =====================================================

        self.cultural_memory = []

        self.mythology_fragments = []

        self.symbolic_patterns = {}

        self.inherited_fragments = []

        self.civilizational_history = []

        self.cultural_affinities = {}

        self.local_mythologies = set()

        self.cultural_exclusions = set()

        # =====================================================
        # CULTURAL DYNAMICS
        # =====================================================

        self.transmission_drive = random.uniform(
            0.0,
            1.0,
        )

        self.symbolic_mutation_rate = (
            random.uniform(
                0.001,
                0.02,
            )
        )

        self.mythological_attachment = (
            random.uniform(
                0.0,
                1.0,
            )
        )

        self.cultural_resilience = random.uniform(
            0.2,
            1.0,
        )

    # =========================================================
    # PERCEPTUAL POST-PROCESSING
    # =========================================================

    def cultural_distortion(
        self, event
    ):

        distortion = (
            self.symbolic_drift
            + self.mythological_pressure
            + self.semiotic_instability
        )

        if distortion < 0.05:
            return event

        return {
            "event": event,
            "cultural_distortion": distortion,
            "civilizational_signature": (
                self.civilizational_signature
            ),
            "symbolic_fragmentation": True,
        }

    # =========================================================
    # CULTURAL AFFINITIES
    # =========================================================

    def update_cultural_affinities(
        self,
        agent,
        perception_fields,
    ):

        import math

        for field in perception_fields:

            center = field.get(
                "center",
                (0.0, 0.0),
            )

            dx = center[0] - agent.x
            dy = center[1] - agent.y

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance > 7.0:
                continue

            affinity_probability = (
                self.cultural_stability
                * 0.01
                + self.transmission_drive
                * 0.02
            )

            if (
                random.random()
                < affinity_probability
            ):
                self.cultural_affinities[
                    id(field)
                ] = random.uniform(
                    0.0,
                    1.0,
                )

    # =========================================================
    # CULTURAL EXCLUSIONS
    # =========================================================

    def update_cultural_exclusions(
        self,
        agent,
        perception_fields,
    ):

        import math

        for field in perception_fields:

            center = field.get(
                "center",
                (0.0, 0.0),
            )

            dx = center[0] - agent.x
            dy = center[1] - agent.y

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance > 4.0:
                continue

            exclusion_probability = (
                self.symbolic_drift
                * 0.02
                + self.cultural_fragmentation
                * 0.03
            )

            if (
                random.random()
                < exclusion_probability
            ):
                self.cultural_exclusions.add(
                    id(field)
                )

    # =========================================================
    # MYTHOLOGY GENERATION
    # =========================================================

    def generate_local_mythologies(
        self,
        cycle,
        fragmentation,
    ):

        probability = (
            0.002
            + self.mythological_pressure
            * 0.01
        )

        if (
            random.random()
            < probability
        ):

            fragment = {
                "cycle": cycle,
                "signature": (
                    self.civilizational_signature
                ),
                "fragmentation": (
                    fragmentation
                ),
            }

            self.mythology_fragments.append(
                fragment
            )

            self.local_mythologies.add(
                hash(
                    str(fragment)
                )
            )

            if (
                len(self.mythology_fragments)
                > 80
            ):
                self.mythology_fragments.pop(
                    0
                )

    # =========================================================
    # SYMBOLIC DRIFT
    # =========================================================

    def mutate_symbolic_patterns(
        self,
    ):

        self.symbolic_drift += (
            random.uniform(
                -0.005,
                0.015,
            )
            * self.symbolic_mutation_rate
        )

        symbol_key = int(
            self.civilizational_signature
            * 100
        )

        self.symbolic_patterns[
            symbol_key
        ] = (
            self.symbolic_patterns.get(
                symbol_key,
                0.0,
            )
            + random.uniform(
                -0.1,
                0.1,
            )
        )

    # =========================================================
    # TRANSMISSION
    # =========================================================

    def transmit_cultural_fragments(
        self,
        cycle,
        local_coherence,
    ):

        transmission_probability = (
            self.transmission_drive
            * 0.01
            + local_coherence
            * 0.005
        )

        if (
            random.random()
            > transmission_probability
        ):
            return

        fragment = {
            "cycle": cycle,
            "signature": (
                self.civilizational_signature
            ),
            "drift": self.symbolic_drift,
            "mutation": random.uniform(
                -0.2,
                0.2,
            ),
        }

        self.cultural_memory.append(
            fragment
        )

        self.inherited_fragments.append(
            {
                "fragment": fragment,
                "degraded": True,
            }
        )

        if (
            len(self.cultural_memory)
            > 120
        ):
            self.cultural_memory.pop(0)

        if (
            len(self.inherited_fragments)
            > 80
        ):
            self.inherited_fragments.pop(
                0
            )

    # =========================================================
    # INTERNAL DYNAMICS
    # =========================================================

    def evolve(
        self,
    ):

        self.mythological_pressure *= 0.997
        self.symbolic_drift *= 0.998
        self.cultural_fragmentation *= 0.996
        self.civilizational_fatigue *= 0.997
        self.semiotic_instability *= 0.996

        self.civilizational_signature += (
            random.uniform(
                -0.01,
                0.01,
            )
        )

        self.cultural_stability += (
            random.uniform(
                -0.004,
                0.003,
            )
        )

        self.cultural_stability = max(
            0.0,
            min(
                1.5,
                self.cultural_stability,
            )
        )

        collapse_risk = (
            self.symbolic_drift
            * 0.01
            + self.cultural_fragmentation
            * 0.01
            + self.semiotic_instability
            * 0.005
        )

        if (
            random.random()
            < collapse_risk
        ):
            self.trigger_civilizational_collapse()

    # =========================================================
    # COLLAPSE
    # =========================================================

    def trigger_civilizational_collapse(
        self,
    ):

        self.cultural_fragmentation += (
            random.uniform(
                0.2,
                0.5,
            )
        )

        self.civilizational_fatigue += (
            random.uniform(
                0.1,
                0.3,
            )
        )

        self.semiotic_instability += (
            random.uniform(
                0.1,
                0.4,
            )
        )

        self.symbolic_drift += (
            random.uniform(
                0.1,
                0.3,
            )
        )

        self.local_mythologies.clear()

        self.civilizational_history.append(
            {
                "collapse": True,
                "signature": (
                    self.civilizational_signature
                ),
            }
        )

        if (
            len(self.civilizational_history)
            > 120
        ):
            self.civilizational_history.pop(0)
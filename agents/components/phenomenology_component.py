# agents/components/phenomenology_component.py

import math
import random


class PhenomenologyComponent:
    """
    Local phenomenological dynamics.

    This component encapsulates:
    - reality signatures
    - perceptual fragmentation
    - ontological fatigue
    - local collapses
    - perceptual alliances and exclusions

    No global ontology.
    No stable reconstruction.
    No universal observer.
    """

    def __init__(self):

        # =====================================================
        # PHENOMENOLOGICAL ECOLOGY
        # =====================================================

        self.perceptual_alignment = 0.0

        self.reality_signature = random.uniform(
            -1.0,
            1.0,
        )

        self.perceptual_stability = 1.0

        self.ontological_fatigue = 0.0

        self.fragmentation = 0.0

        self.compatibility_tension = 0.0

        self.perceptual_pressure = 0.0

        self.regime_capture = 0.0

        self.local_coherence = 1.0

        self.collapse_exposure = 0.0

        # =====================================================
        # PERCEPTUAL HISTORY
        # =====================================================

        self.perceptual_history = []

        self.regime_history = []

        self.compatibility_memory = {}

        # =====================================================
        # LOCAL ECOLOGICAL DYNAMICS
        # =====================================================

        self.current_regime = None

        self.regime_affinities = {}

        self.local_alliances = set()

        self.perceptual_exclusions = set()

    # =========================================================
    # FIELD DETECTION
    # =========================================================

    def normalize_perception_fields(
        self,
        perception_fields,
    ):

        if perception_fields is None:
            return []

        if isinstance(
            perception_fields,
            dict,
        ):
            return [perception_fields]

        try:
            return list(perception_fields)
        except TypeError:
            return [perception_fields]

    def find_local_fields(
        self,
        agent,
        perception_fields,
    ):

        perception_fields = (
            self.normalize_perception_fields(
                perception_fields
            )
        )

        local_fields = []

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

            if distance > 12.0:
                continue

            local_fields.append(
                (
                    distance,
                    field,
                )
            )

        local_fields.sort(
            key=lambda x: x[0]
        )

        return [
            field
            for _, field in local_fields
        ]

    # =========================================================
    # PERCEPTION
    # =========================================================

    def perceive(
        self,
        environment_event,
        influencing_fields,
    ):

        perceived_event = environment_event

        if influencing_fields:

            self.update_regime_exposure(
                influencing_fields
            )

            perceived_event = (
                self.distort_event(
                    environment_event,
                    influencing_fields,
                )
            )

        self.perceptual_history.append(
            perceived_event
        )

        if (
            len(self.perceptual_history)
            > 120
        ):
            self.perceptual_history.pop(0)

        return perceived_event

    # =========================================================
    # REGIME EXPOSURE
    # =========================================================

    def update_regime_exposure(
        self,
        influencing_fields,
    ):

        pressure = 0.0
        instability = 0.0

        for field in influencing_fields:

            nodes = field.get(
                "nodes",
                {}
            )

            local_density = (
                len(nodes) * 0.01
            )

            pressure += local_density

            instability += random.uniform(
                0.0,
                0.02,
            )

        self.perceptual_pressure += (
            pressure
        )

        self.fragmentation += (
            instability
        )

        self.ontological_fatigue += (
            instability * 0.5
        )

        self.local_coherence *= 0.999

    # =========================================================
    # DISTORTION
    # =========================================================

    def distort_event(
        self,
        event,
        influencing_fields,
    ):

        distortion_factor = (

            self.fragmentation
            + self.ontological_fatigue
            + self.compatibility_tension
        )

        if distortion_factor < 0.05:
            return event

        return {
            "event": event,
            "distortion": distortion_factor,
            "fragmented": True,
            "local_reality_count": len(
                influencing_fields
            ),
        }

    # =========================================================
    # LOCAL ALLIANCES
    # =========================================================

    def update_local_alliances(
        self,
        agent,
        perception_fields,
    ):

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

            if distance > 6.0:
                continue

            alliance_probability = (
                0.01
                + self.local_coherence * 0.02
            )

            if (
                random.random()
                < alliance_probability
            ):
                self.local_alliances.add(
                    id(field)
                )

    # =========================================================
    # EXCLUSIONS
    # =========================================================

    def update_exclusions(
        self,
        agent,
        perception_fields,
    ):

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

            if distance > 5.0:
                continue

            exclusion_probability = (

                self.fragmentation * 0.03
                + self.compatibility_tension
                * 0.02
            )

            if (
                random.random()
                < exclusion_probability
            ):
                self.perceptual_exclusions.add(
                    id(field)
                )

    # =========================================================
    # INTERNAL DYNAMICS
    # =========================================================

    def evolve(
        self,
    ):

        self.perceptual_pressure *= 0.995
        self.fragmentation *= 0.996
        self.ontological_fatigue *= 0.997
        self.compatibility_tension *= 0.996
        self.collapse_exposure *= 0.995

        self.reality_signature += (
            random.uniform(
                -0.01,
                0.01,
            )
        )

        self.perceptual_alignment += (
            random.uniform(
                -0.01,
                0.01,
            )
        )

        self.local_coherence += (
            random.uniform(
                -0.003,
                0.002,
            )
        )

        self.local_coherence = max(
            0.0,
            min(1.5, self.local_coherence)
        )

        collapse_risk = (
            self.fragmentation * 0.01
            + self.ontological_fatigue
            * 0.005
        )

        if (
            random.random()
            < collapse_risk
        ):
            self.trigger_local_collapse()

    # =========================================================
    # COLLAPSE
    # =========================================================

    def trigger_local_collapse(
        self,
    ):

        self.fragmentation += (
            random.uniform(
                0.2,
                0.5,
            )
        )

        self.ontological_fatigue += (
            random.uniform(
                0.1,
                0.3,
            )
        )

        self.compatibility_tension += (
            random.uniform(
                0.05,
                0.2,
            )
        )

        self.collapse_exposure += (
            random.uniform(
                0.1,
                0.4,
            )
        )

        self.local_alliances.clear()

        self.regime_history.append(
            {
                "collapse": True,
                "fragmentation": (
                    self.fragmentation
                ),
            }
        )

        if (
            len(self.regime_history)
            > 120
        ):
            self.regime_history.pop(0)
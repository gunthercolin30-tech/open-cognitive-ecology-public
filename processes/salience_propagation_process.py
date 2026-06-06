# processes/salience_propagation_process.py

class SaliencePropagationProcess:

    def __init__(
        self,
        graph,
        propagation_engine,
        activation_threshold=0.3,

        # =====================================================
        # DISSIPATIVE ECOLOGY
        # =====================================================

        fatigue_decay=0.992,
        fatigue_gain=0.020,

        saturation_gain=0.015,
        saturation_decay=0.996,

        recovery_rate=0.004,

        attractor_cost_factor=0.010,

        propagation_inhibition_factor=0.45,
    ):

        self.graph = graph

        self.propagation_engine = (
            propagation_engine
        )

        self.activation_threshold = (
            activation_threshold
        )

        # =====================================================
        # DISSIPATIVE PARAMETERS
        # =====================================================

        self.fatigue_decay = (
            fatigue_decay
        )

        self.fatigue_gain = (
            fatigue_gain
        )

        self.saturation_gain = (
            saturation_gain
        )

        self.saturation_decay = (
            saturation_decay
        )

        self.recovery_rate = (
            recovery_rate
        )

        self.attractor_cost_factor = (
            attractor_cost_factor
        )

        self.propagation_inhibition_factor = (
            propagation_inhibition_factor
        )

    # =========================================================
    # PROCESS EXECUTION
    # =========================================================

    async def run(self):

        active_nodes = [

            node

            for node in (
                self.graph.nodes.values()
            )

            if (
                self._should_propagate(
                    node
                )
            )
        ]

        for node in active_nodes:

            # =================================================
            # ECOLOGICAL MAINTENANCE
            # =================================================

            self._apply_local_ecology(
                node
            )

            intensity = (
                self._compute_ecological_intensity(
                    node
                )
            )

            # =================================================
            # ECOLOGICAL COLLAPSE PREVENTION
            # =================================================

            if intensity <= 0.01:
                continue

            self._update_local_circulation(
                node,
                intensity,
            )

            print(
                "[DISSIPATIVE_ECOLOGY]",

                node.id,

                f"intensity="
                f"{intensity:.2f}",

                f"fatigue="
                f"{getattr(node, 'fatigue', 0.0):.2f}",

                f"saturation="
                f"{getattr(node, 'saturation', 0.0):.2f}",

                f"recovery="
                f"{getattr(node, 'recovery', 1.0):.2f}",

                f"migration="
                f"{node.migration_pressure:.2f}",

                f"circulation="
                f"{node.circulation_potential:.2f}",
            )

            self.propagation_engine.propagate_from(

                node.id,

                intensity=intensity,
            )

    # =========================================================
    # PROPAGATION ELIGIBILITY
    # =========================================================

    def _should_propagate(
        self,
        node,
    ):

        activation_ready = (
            node.activation
            >= self.activation_threshold
        )

        migratory_ready = (
            node.migration_pressure
            >= 0.15
        )

        circulation_ready = (
            node.circulation_potential
            >= 0.12
        )

        resonance_ready = (
            node.path_resonance
            >= 0.10
        )

        fatigue = getattr(
            node,
            "fatigue",
            0.0,
        )

        saturation = getattr(
            node,
            "saturation",
            0.0,
        )

        ecological_viability = (

            fatigue < 1.5

            and saturation < 2.0
        )

        return (

            ecological_viability

            and
            (
                activation_ready

                or migratory_ready

                or circulation_ready

                or resonance_ready
            )
        )

    # =========================================================
    # ECOLOGICAL INTENSITY
    # =========================================================

    def _compute_ecological_intensity(
        self,
        node,
    ):

        intensity = (

            node.activation * 0.35

            + node.salience * 0.20

            + node.tension * 0.10

            + node.attractor_strength * 0.10

            + node.migration_pressure * 0.10

            + node.circulation_potential * 0.10

            + node.path_resonance * 0.05
        )

        ecological_modifier = (

            1.0

            + node.long_range_activation * 0.05
        )

        intensity *= ecological_modifier

        # =====================================================
        # FATIGUE INHIBITION
        # =====================================================

        fatigue = getattr(
            node,
            "fatigue",
            0.0,
        )

        fatigue_inhibition = (

            1.0

            - (
                fatigue
                * self.propagation_inhibition_factor
            )
        )

        intensity *= max(
            0.05,
            fatigue_inhibition,
        )

        # =====================================================
        # SATURATION DAMPING
        # =====================================================

        saturation = getattr(
            node,
            "saturation",
            0.0,
        )

        saturation_damping = (

            1.0

            - (
                saturation
                * 0.25
            )
        )

        intensity *= max(
            0.05,
            saturation_damping,
        )

        # =====================================================
        # RECOVERY MODULATION
        # =====================================================

        recovery = getattr(
            node,
            "recovery",
            1.0,
        )

        intensity *= recovery

        return intensity

    # =========================================================
    # LOCAL ECOLOGICAL MAINTENANCE
    # =========================================================

    def _apply_local_ecology(
        self,
        node,
    ):

        # =====================================================
        # FATIGUE
        # =====================================================

        if not hasattr(node, "fatigue"):
            node.fatigue = 0.0

        local_activity = (

            node.activation
            + node.salience
            + node.tension
        )

        node.fatigue *= (
            self.fatigue_decay
        )

        node.fatigue += (
            local_activity
            * self.fatigue_gain
        )

        # =====================================================
        # SATURATION
        # =====================================================

        if not hasattr(node, "saturation"):
            node.saturation = 0.0

        node.saturation *= (
            self.saturation_decay
        )

        node.saturation += (

            node.attractor_strength
            * self.saturation_gain
        )

        # =====================================================
        # ATTRACTOR MAINTENANCE COST
        # =====================================================

        maintenance_cost = (

            node.attractor_strength
            * self.attractor_cost_factor
        )

        node.activation -= (
            maintenance_cost
        )

        node.salience -= (
            maintenance_cost * 0.5
        )

        # =====================================================
        # RECOVERY
        # =====================================================

        if not hasattr(node, "recovery"):
            node.recovery = 1.0

        recovery_pressure = (

            node.fatigue * 0.4

            + node.saturation * 0.3
        )

        node.recovery += (
            self.recovery_rate
        )

        node.recovery -= (
            recovery_pressure
            * 0.01
        )

        node.recovery = max(
            0.05,
            min(
                1.0,
                node.recovery,
            ),
        )

        # =====================================================
        # SOFT ECOLOGICAL DISSIPATION
        # =====================================================

        node.activation *= 0.995
        node.salience *= 0.996
        node.tension *= 0.997

        # =====================================================
        # FLOOR STABILITY
        # =====================================================

        node.activation = max(
            0.0,
            node.activation,
        )

        node.salience = max(
            0.0,
            node.salience,
        )

        node.tension = max(
            0.0,
            node.tension,
        )

    # =========================================================
    # ECOLOGICAL CIRCULATION
    # =========================================================

    def _update_local_circulation(
        self,
        node,
        intensity,
    ):

        fatigue = getattr(
            node,
            "fatigue",
            0.0,
        )

        saturation = getattr(
            node,
            "saturation",
            0.0,
        )

        ecological_drag = (

            fatigue * 0.15

            + saturation * 0.10
        )

        ecological_modifier = max(
            0.05,
            1.0 - ecological_drag,
        )

        # =====================================================
        # MIGRATORY PRESSURE
        # =====================================================

        node.migration_pressure *= (
            0.985
        )

        node.migration_pressure += (
            intensity
            * 0.015
            * ecological_modifier
        )

        # =====================================================
        # CIRCULATION POTENTIAL
        # =====================================================

        node.circulation_potential *= (
            0.992
        )

        node.circulation_potential += (
            node.salience
            * 0.010
            * ecological_modifier
        )

        # =====================================================
        # PATH RESONANCE
        # =====================================================

        node.path_resonance *= (
            0.994
        )

        node.path_resonance += (
            node.corridor_affinity
            * 0.008
            * ecological_modifier
        )

        # =====================================================
        # LONG RANGE ACTIVATION
        # =====================================================

        node.long_range_activation *= (
            0.990
        )

        node.long_range_activation += (
            node.circulation_potential
            * 0.006
            * ecological_modifier
        )

        # =====================================================
        # REACTIVATION POTENTIAL
        # =====================================================

        node.reactivation_potential *= (
            0.996
        )

        node.reactivation_potential += (
            intensity
            * 0.004
            * ecological_modifier
        )

        # =====================================================
        # ECOLOGICAL STABILITY
        # =====================================================

        node.ecological_stability *= (
            0.995
        )

        node.ecological_stability += (

            node.attractor_strength
            * 0.005
            * ecological_modifier
        )
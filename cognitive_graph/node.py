# cognitive_graph/node.py

from constraints.regional_constraint_field import (
    RegionalConstraintField
)


class CognitiveNode:

    def __init__(
        self,
        node_id,
        data=None,
    ):

        self.id = node_id
        self.data = data or {}

        # =====================================================
        # PRIMARY COGNITIVE FIELD
        # =====================================================

        self.activation = 0.0
        self.salience = 0.0
        self.tension = 0.0
        self.energy = 1.0

        # =====================================================
        # DISTRIBUTED ATTRACTORS
        # =====================================================

        self.attractor_strength = 0.0
        self.competitive_pressure = 0.0

        # =====================================================
        # ECOLOGICAL MIGRATION FIELD
        # =====================================================

        self.migration_pressure = 0.0
        self.migration_flux = 0.0
        self.retention_force = 0.0
        self.ecological_stability = 0.0

        # =====================================================
        # LONG RANGE CIRCULATION
        # =====================================================

        self.corridor_affinity = 0.0
        self.long_range_activation = 0.0
        self.circulation_potential = 0.0

        # =====================================================
        # ECOLOGICAL MEMORY
        # =====================================================

        self.migration_trace = 0.0
        self.path_resonance = 0.0
        self.reactivation_potential = 0.0

        # =====================================================
        # METASTABLE ECOLOGY
        # =====================================================

        self.habitat_affinity = {}
        self.local_ecological_state = "transitional"
        self.last_ecological_update = 0.0

        # =====================================================
        # TEMPORAL ECOLOGY
        # =====================================================

        self.temporal_phase = 0.0
        self.temporal_inertia = 1.0
        self.temporal_variability = 0.0
        self.sleep_pressure = 0.0
        self.wake_potential = 1.0
        self.temporal_acceleration = 1.0
        self.temporal_memory = 0.0
        self.temporal_resonance = 0.0
        self.activity_cycle = 0.0
        self.temporal_drag = 0.0
        self.ecological_age = 0.0
        self.temporal_adaptation = 0.0
        self.dormant = False

        # =====================================================
        # CONTINUOUS COGNITIVE FIELD PHYSICS
        # =====================================================

        self.x = 0.0
        self.y = 0.0

        self.vx = 0.0
        self.vy = 0.0

        self.ax = 0.0
        self.ay = 0.0

        self.spatial_inertia = 1.0
        self.spatial_drag = 0.02

        self.turbulence = 0.0
        self.directional_memory = 0.0
        self.mobility = 1.0
        self.flow_coupling = 0.0
        self.pressure_response = 0.0
        self.vortex_affinity = 0.0

        self.trajectory_memory = []

        self.motion_energy = 0.0
        self.climatic_drift = 0.0

        # =====================================================
        # DISTRIBUTED CLIMATIC ECOLOGY
        # =====================================================

        self.temperature = 0.0
        self.pressure = 0.0
        self.humidity = 0.0
        self.turbulence_field = 0.0
        self.vorticity = 0.0
        self.climatic_memory = 0.0
        self.storm_potential = 0.0
        self.atmospheric_stability = 1.0
        self.flow_memory = 0.0
        self.environmental_resonance = 0.0
        self.climatic_inertia = 1.0
        self.heat_accumulation = 0.0
        self.pressure_accumulation = 0.0
        self.climatic_dissipation = 0.01
        self.environmental_saturation = 0.0
        self.regional_drift = 0.0
        self.weather_signature = 0.0

        # =====================================================
        # REGIONAL CONSTRAINT ECOLOGY
        # =====================================================

        # Local domain of viability
        self.constraint_field = (
            RegionalConstraintField()
        )

        # Regional compatibility persistence
        self.local_viability = 1.0

        # Constraint tension accumulation
        self.constraint_pressure = 0.0

        # Local ontological coherence
        self.coherence_field = 1.0

        # Regime persistence
        self.regional_persistence = 0.0

        # Ecological incompatibility
        self.incompatibility_field = 0.0

        # Distributed regime drift
        self.constraint_drift = 0.0

        # Local operational plasticity
        self.operational_plasticity = 1.0

        # Constraint saturation
        self.constraint_saturation = 0.0

        # Local viability turbulence
        self.viability_turbulence = 0.0

        # =====================================================
        # POLITICAL ECOLOGY
        # =====================================================

        # Institutional presence
        self.institutional_intensity = 0.0

        # Symbolic wealth and exchange capacity
        self.symbolic_currency = 0.0

        # Local coordination dependence
        self.coordination_intensity = 0.0

        # Political fragmentation and stress
        self.political_tension = 0.0

        # Local affiliation
        self.political_affiliation = "none"

        # Distributed symbolic drift
        self.symbolic_drift = 0.0

        # =====================================================
        # LEGAL ECOLOGY
        # =====================================================

        # Normative legitimacy
        self.normative_legitimacy = 0.0

        # Jurisprudential density
        self.jurisprudence_density = 0.0

        # Local legal stability
        self.legal_stability = 0.0

        # Normative conflict
        self.legal_conflict = 0.0

        # Compatibility between normative orders
        self.normative_compatibility = 0.0

        # Local legal status
        self.legal_status = "none"

        # =====================================================
        # ECONOMIC ECOLOGY
        # =====================================================

        # Local economic abundance
        self.economic_intensity = 0.0

        # Economic stress
        self.economic_stress = 0.0

        # Economic collapse risk
        self.economic_collapse_risk = 0.0
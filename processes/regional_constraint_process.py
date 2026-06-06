# processes/regional_constraint_process.py

import random


class RegionalConstraintProcess:

    """
    Distributed regional constraint ecology.

    No global viability system.
    No universal rules.
    No central ontology.

    Only:
    - local constraint evolution
    - ecological compatibility
    - regional viability drift
    - metastable regime formation
    - distributed incompatibilities
    """

    def __init__(
        self,
        graph,
    ):

        self.graph = graph

        # =====================================================
        # CONSTRAINT ECOLOGY
        # =====================================================

        self.local_drift = 0.002

        self.compatibility_decay = 0.995

        self.persistence_decay = 0.998

        self.saturation_decay = 0.992

        # =====================================================
        # ECOLOGICAL COUPLING
        # =====================================================

        self.temperature_pressure = 0.010

        self.turbulence_pressure = 0.015

        self.motion_pressure = 0.008

        self.storm_pressure = 0.020

        # =====================================================
        # REGIONAL INCOMPATIBILITY
        # =====================================================

        self.incompatibility_growth = 0.010

        self.coherence_repair = 0.003

        self.plasticity_adaptation = 0.004

    # =========================================================
    # PROCESS EXECUTION
    # =========================================================

    async def run(self):

        for node in (
            self.graph.nodes.values()
        ):

            self._update_constraints(
                node
            )

    # =========================================================
    # LOCAL CONSTRAINT ECOLOGY
    # =========================================================

    def _update_constraints(
        self,
        node,
    ):

        field = node.constraint_field

        # =====================================================
        # FIELD EVOLUTION
        # =====================================================

        field.evolve(node)

        # =====================================================
        # ECOLOGICAL PRESSURE
        # =====================================================

        ecological_pressure = (

            node.temperature
            * self.temperature_pressure

            + node.turbulence_field
            * self.turbulence_pressure

            + node.motion_energy
            * self.motion_pressure

            + node.storm_potential
            * self.storm_pressure
        )

        # =====================================================
        # LOCAL VIABILITY
        # =====================================================

        viability_shift = (

            field.memory_retention

            + field.temporal_coherence

            + field.attractor_stability

            - ecological_pressure
        )

        node.local_viability *= (
            self.compatibility_decay
        )

        node.local_viability += (
            viability_shift
            * 0.002
        )

        # =====================================================
        # CONSTRAINT PRESSURE
        # =====================================================

        node.constraint_pressure *= (
            self.persistence_decay
        )

        node.constraint_pressure += (
            ecological_pressure
            * 0.010
        )

        # =====================================================
        # COHERENCE FIELD
        # =====================================================

        coherence_shift = (

            field.identity_viscosity

            + field.temporal_coherence

            - field.turbulence_sensitivity
        )

        node.coherence_field *= (
            0.996
        )

        node.coherence_field += (
            coherence_shift
            * self.coherence_repair
        )

        # =====================================================
        # REGIONAL PERSISTENCE
        # =====================================================

        persistence_shift = (

            field.memory_retention

            + field.attractor_stability

            + field.thermal_dissipation
        )

        node.regional_persistence *= (
            self.persistence_decay
        )

        node.regional_persistence += (
            persistence_shift
            * 0.002
        )

        # =====================================================
        # INCOMPATIBILITY FIELD
        # =====================================================

        incompatibility = (

            abs(
                field.memory_retention
                - field.propagation_permeability
            )

            +

            abs(
                field.identity_viscosity
                - field.turbulence_sensitivity
            )
        )

        node.incompatibility_field *= (
            0.997
        )

        node.incompatibility_field += (
            incompatibility
            * self.incompatibility_growth
        )

        # =====================================================
        # OPERATIONAL PLASTICITY
        # =====================================================

        plasticity_shift = (

            field.propagation_permeability

            + field.temporal_coherence

            - field.identity_viscosity
        )

        node.operational_plasticity *= (
            0.995
        )

        node.operational_plasticity += (
            plasticity_shift
            * self.plasticity_adaptation
        )

        # =====================================================
        # CONSTRAINT SATURATION
        # =====================================================

        node.constraint_saturation *= (
            self.saturation_decay
        )

        node.constraint_saturation += (
            (
                node.constraint_pressure
                + node.incompatibility_field
            )
            * 0.003
        )

        # =====================================================
        # VIABILITY TURBULENCE
        # =====================================================

        viability_instability = (

            node.constraint_pressure

            + node.incompatibility_field

            + node.storm_potential
        )

        node.viability_turbulence *= (
            0.992
        )

        node.viability_turbulence += (
            viability_instability
            * 0.004
        )

        # =====================================================
        # REGIONAL DRIFT
        # =====================================================

        node.constraint_drift *= (
            0.998
        )

        node.constraint_drift += (
            (
                field.memory_retention
                + field.temporal_coherence
                + field.propagation_permeability
            )
            * 0.0005
        )

        # =====================================================
        # LOCAL SATURATION
        # =====================================================

        node.local_viability = min(
            max(node.local_viability, 0.0),
            5.0,
        )

        node.coherence_field = min(
            max(node.coherence_field, 0.0),
            5.0,
        )

        node.operational_plasticity = min(
            max(
                node.operational_plasticity,
                0.0,
            ),
            5.0,
        )

        # =====================================================
        # DEBUG
        # =====================================================

        print(
            "[CONSTRAINT]",

            node.id,

            f"viability={node.local_viability:.2f}",

            f"coherence={node.coherence_field:.2f}",

            f"incompatibility={node.incompatibility_field:.2f}",

            f"plasticity={node.operational_plasticity:.2f}",
        )
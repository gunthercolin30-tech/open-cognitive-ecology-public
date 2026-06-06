# processes/climatic_ecology_process.py

import math
import random


class ClimaticEcologyProcess:

    """
    Distributed climatic ecology.

    No global weather map.
    No planetary controller.
    No central atmosphere.

    Only:
    - local climatic production
    - distributed pressure fields
    - ecological heat accumulation
    - turbulence propagation
    - regional climatic memory
    - emergent weather dynamics
    - directional climatic circulation
    - mesoscale atmospheric fragmentation
    """

    def __init__(
        self,
        graph,
    ):

        self.graph = graph

        # =====================================================
        # CLIMATIC DYNAMICS
        # =====================================================

        self.temperature_decay = 0.988

        self.pressure_decay = 0.992

        self.humidity_decay = 0.996

        self.turbulence_decay = 0.982

        self.vorticity_decay = 0.986

        # =====================================================
        # ECOLOGICAL COUPLING
        # =====================================================

        self.activation_heat = 0.016

        self.tension_heat = 0.028

        self.motion_heat = 0.010

        self.salience_humidity = 0.010

        self.migration_pressure = 0.020

        # =====================================================
        # CLIMATIC TRANSPORT
        # =====================================================

        self.temperature_diffusion = 0.003

        self.pressure_diffusion = 0.006

        self.humidity_diffusion = 0.003

        self.turbulence_diffusion = 0.006

        self.advection_strength = 0.010

        self.vortex_transport = 0.008

        self.jet_stream_factor = 0.012

        self.shear_factor = 0.015

        # =====================================================
        # DISSIPATIVE CONSTRAINTS
        # =====================================================

        self.thermal_cap = 3.5

        self.saturation_cooling = 0.040

        self.cold_zone_amplification = 0.004

        self.diffusion_resistance = 0.8

        self.turbulence_viscosity = 0.6

        self.quiet_cooling = 0.012

        self.front_sharpening = 0.004

        # =====================================================
        # WEATHER INSTABILITY
        # =====================================================

        self.storm_threshold = 1.8

        self.vortex_threshold = 1.0

    # =========================================================
    # PROCESS EXECUTION
    # =========================================================

    async def run(self):

        for node in (
            self.graph.nodes.values()
        ):

            self._update_local_climate(
                node
            )

        for node in (
            self.graph.nodes.values()
        ):

            self._diffuse_climate(
                node
            )

    # =========================================================
    # LOCAL CLIMATE PRODUCTION
    # =========================================================

    def _update_local_climate(
        self,
        node,
    ):

        # =====================================================
        # ECOLOGICAL HEAT
        # =====================================================

        local_heat = (

            node.activation
            * self.activation_heat

            + node.tension
            * self.tension_heat

            + node.motion_energy
            * self.motion_heat
        )

        node.temperature *= (
            self.temperature_decay
        )

        node.temperature += (
            local_heat
        )

        # =====================================================
        # SATURATION COOLING
        # =====================================================

        thermal_pressure = (
            max(
                0.0,
                node.temperature
                - self.thermal_cap
            )
        )

        node.temperature -= (
            thermal_pressure
            * self.saturation_cooling
        )

        # =====================================================
        # QUIET ZONE COOLING
        # =====================================================

        calmness = (
            1.0
            /
            (
                1.0
                + node.turbulence_field
                + abs(node.vx)
                + abs(node.vy)
            )
        )

        node.temperature -= (
            calmness
            * self.quiet_cooling
        )

        # =====================================================
        # COLD POCKET AMPLIFICATION
        # =====================================================

        if node.temperature < 0.5:

            node.temperature -= (
                self.cold_zone_amplification
            )

        # =====================================================
        # ECOLOGICAL PRESSURE
        # =====================================================

        pressure_input = (

            node.migration_pressure
            * self.migration_pressure

            + node.competitive_pressure
            * 0.012

            + node.attractor_strength
            * 0.006
        )

        node.pressure *= (
            self.pressure_decay
        )

        node.pressure += (
            pressure_input
        )

        # =====================================================
        # INFORMATIONAL HUMIDITY
        # =====================================================

        humidity_input = (

            node.salience
            * self.salience_humidity

            + node.path_resonance
            * 0.006
        )

        node.humidity *= (
            self.humidity_decay
        )

        node.humidity += (
            humidity_input
        )

        # =====================================================
        # TURBULENCE FIELD
        # =====================================================

        turbulence_input = (

            abs(node.vx)
            + abs(node.vy)

            + node.temporal_variability

            + node.tension
        )

        node.turbulence_field *= (
            self.turbulence_decay
        )

        node.turbulence_field += (
            turbulence_input
            * 0.008
        )

        # =====================================================
        # VORTICITY
        # =====================================================

        rotational_energy = (

            abs(node.vx - node.vy)
        )

        node.vorticity *= (
            self.vorticity_decay
        )

        node.vorticity += (
            rotational_energy
            * 0.012
        )

        # =====================================================
        # STORM POTENTIAL
        # =====================================================

        instability = (

            node.temperature

            + node.pressure

            + node.turbulence_field
        )

        node.storm_potential *= 0.988

        if instability > self.storm_threshold:

            node.storm_potential += (
                instability
                * 0.008
            )

        # =====================================================
        # ENVIRONMENTAL SATURATION
        # =====================================================

        node.environmental_saturation *= (
            0.992
        )

        node.environmental_saturation += (
            (
                node.temperature
                + node.humidity
            )
            * 0.001
        )

        # =====================================================
        # CLIMATIC MEMORY
        # =====================================================

        node.climatic_memory *= (
            0.997
        )

        node.climatic_memory += (
            (
                node.temperature
                + node.pressure
                + node.humidity
            )
            * 0.0005
        )

        # =====================================================
        # WEATHER SIGNATURE
        # =====================================================

        node.weather_signature *= (
            0.993
        )

        node.weather_signature += (
            (
                node.vorticity
                + node.storm_potential
            )
            * 0.0015
        )

    # =========================================================
    # DIRECTIONAL CLIMATE DIFFUSION
    # =========================================================

    def _diffuse_climate(
        self,
        node,
    ):

        edges = self.graph.neighbors(
            node.id
        )

        for edge in edges:

            neighbor = edge.target

            dx = (
                neighbor.x
                - node.x
            )

            dy = (
                neighbor.y
                - node.y
            )

            distance = math.sqrt(
                dx * dx
                + dy * dy
            ) + 0.001

            # =================================================
            # FLOW DIRECTION
            # =================================================

            flow_dx = (
                node.vx
                - neighbor.vx
            )

            flow_dy = (
                node.vy
                - neighbor.vy
            )

            directional_alignment = (
                (
                    dx * flow_dx
                    + dy * flow_dy
                )
                /
                distance
            )

            # =================================================
            # TURBULENCE BARRIER
            # =================================================

            turbulence_barrier = (
                1.0
                +
                (
                    node.turbulence_field
                    + neighbor.turbulence_field
                )
                * self.turbulence_viscosity
            )

            climatic_resistance = (
                self.diffusion_resistance
                * turbulence_barrier
            )

            coupling = (
                (
                    edge.weight
                    * 0.05
                )
                /
                climatic_resistance
            )

            # =================================================
            # DIRECTIONAL ADVECTION
            # =================================================

            advection = (
                directional_alignment
                * self.advection_strength
            )

            # =================================================
            # VORTEX TRANSPORT
            # =================================================

            vortex_flow = (
                (
                    node.vorticity
                    + neighbor.vorticity
                )
                * self.vortex_transport
            )

            # =================================================
            # JET STREAM EFFECT
            # =================================================

            jet_stream = (
                (
                    abs(node.vx)
                    + abs(node.vy)
                )
                * self.jet_stream_factor
            )

            # =================================================
            # SHEAR INSTABILITY
            # =================================================

            shear = (
                abs(
                    node.vx
                    - neighbor.vx
                )
                +
                abs(
                    node.vy
                    - neighbor.vy
                )
            )

            shear_factor = (
                1.0
                +
                shear
                * self.shear_factor
            )

            transport_factor = (
                (
                    coupling
                    + advection
                    + vortex_flow
                    + jet_stream
                )
                /
                shear_factor
            )

            # =================================================
            # TEMPERATURE FLOW
            # =================================================

            temperature_delta = (
                node.temperature
                - neighbor.temperature
            )

            transfer = (
                temperature_delta
                * self.temperature_diffusion
                * transport_factor
            )

            # =================================================
            # FRONT SHARPENING
            # =================================================

            if abs(temperature_delta) > 1.0:

                transfer *= (
                    1.0
                    - self.front_sharpening
                )

            node.temperature -= transfer

            neighbor.temperature += transfer

            # =================================================
            # PRESSURE FLOW
            # =================================================

            pressure_delta = (
                node.pressure
                - neighbor.pressure
            )

            pressure_transfer = (
                pressure_delta
                * self.pressure_diffusion
                * transport_factor
            )

            node.pressure -= (
                pressure_transfer
            )

            neighbor.pressure += (
                pressure_transfer
            )

            # =================================================
            # HUMIDITY FLOW
            # =================================================

            humidity_delta = (
                node.humidity
                - neighbor.humidity
            )

            humidity_transfer = (
                humidity_delta
                * self.humidity_diffusion
                * transport_factor
            )

            node.humidity -= (
                humidity_transfer
            )

            neighbor.humidity += (
                humidity_transfer
            )

            # =================================================
            # TURBULENCE PROPAGATION
            # =================================================

            turbulence_delta = (
                node.turbulence_field
                - neighbor.turbulence_field
            )

            turbulence_transfer = (
                turbulence_delta
                * self.turbulence_diffusion
                * transport_factor
            )

            node.turbulence_field -= (
                turbulence_transfer
            )

            neighbor.turbulence_field += (
                turbulence_transfer
            )

            # =================================================
            # REGIONAL FLOW MEMORY
            # =================================================

            node.flow_memory *= 0.997

            node.flow_memory += (
                neighbor.motion_energy
                * 0.001
            )

            # =================================================
            # ENVIRONMENTAL RESONANCE
            # =================================================

            node.environmental_resonance *= (
                0.993
            )

            node.environmental_resonance += (
                (
                    neighbor.temperature
                    + neighbor.pressure
                )
                * 0.0005
            )

            # =================================================
            # REGIONAL DRIFT
            # =================================================

            node.regional_drift *= (
                0.997
            )

            node.regional_drift += (
                neighbor.weather_signature
                * 0.0002
            )

        print(
            "[CLIMATE]",

            node.id,

            f"temp={node.temperature:.2f}",

            f"pressure={node.pressure:.2f}",

            f"humidity={node.humidity:.2f}",

            f"turbulence={node.turbulence_field:.2f}",

            f"storm={node.storm_potential:.2f}",
        )
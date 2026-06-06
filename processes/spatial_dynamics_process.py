# processes/spatial_dynamics_process.py

import math
import random


class SpatialDynamicsProcess:

    """
    Distributed spatial ecology.

    No global coordinates.
    No central solver.
    No navigation engine.

    Only:
    - local inertial dynamics
    - ecological pressure
    - climatic coupling
    - vortex interaction
    - distributed turbulence
    - emergent regional flow
    - mesoscale fragmentation
    - dissipative corridor ecology
    """

    def __init__(
        self,
        graph,
    ):

        self.graph = graph

        # =====================================================
        # FIELD PHYSICS
        # =====================================================

        self.base_noise = 0.006

        self.max_velocity = 0.32

        self.velocity_decay = 0.955

        self.acceleration_decay = 0.68

        # =====================================================
        # ECOLOGICAL COUPLING
        # =====================================================

        self.activation_coupling = 0.014

        self.migration_coupling = 0.022

        self.tension_coupling = 0.028

        self.attractor_coupling = 0.024

        self.temporal_coupling = 0.010

        # =====================================================
        # CLIMATIC COUPLING
        # =====================================================

        self.temperature_mobility = 0.010

        self.pressure_drift = 0.018

        self.turbulence_exploration = 0.018

        self.vortex_rotation = 0.020

        self.storm_disruption = 0.035

        self.humidity_cohesion = 0.028

        # =====================================================
        # MESOSCALE VISCOSITY
        # =====================================================

        self.thermal_viscosity = 0.020

        self.turbulence_friction = 0.040

        self.corridor_fatigue = 0.003

        self.regional_inertia = 0.015

        self.long_range_decay = 0.002

        self.cold_zone_retention = 0.020

        # =====================================================
        # LOCAL FIELD ECOLOGY
        # =====================================================

        self.neighbor_repulsion = 0.018

        self.neighbor_attraction = 0.002

        self.flow_alignment = 0.010

        self.pressure_coupling = 0.012

        # =====================================================
        # FLOW MEMORY
        # =====================================================

        self.flow_memory_decay = 0.990

        self.max_trajectory_memory = 300

    # =========================================================
    # PROCESS EXECUTION
    # =========================================================

    async def run(self):

        self._update_spatial_field()

    # =========================================================
    # DISTRIBUTED SPATIAL FIELD
    # =========================================================

    def _update_spatial_field(self):

        for node in self.graph.nodes.values():

            # =================================================
            # ECOLOGICAL PRESSURE
            # =================================================

            ecological_pressure = (

                node.activation * 0.24

                + node.salience * 0.18

                + node.tension * 0.28

                + node.migration_pressure * 0.18
            )

            # =================================================
            # STOCHASTIC BACKGROUND
            # =================================================

            node.ax += random.uniform(
                -self.base_noise,
                self.base_noise,
            )

            node.ay += random.uniform(
                -self.base_noise,
                self.base_noise,
            )

            # =================================================
            # ACTIVATION FLOW
            # =================================================

            node.ax += (
                random.uniform(-1, 1)
                * node.activation
                * self.activation_coupling
            )

            node.ay += (
                random.uniform(-1, 1)
                * node.migration_pressure
                * self.migration_coupling
            )

            # =================================================
            # TEMPORAL FLOW
            # =================================================

            node.ax += (
                math.sin(
                    node.temporal_phase
                )
                * self.temporal_coupling
            )

            node.ay += (
                math.cos(
                    node.temporal_phase
                )
                * self.temporal_coupling
            )

            # =================================================
            # CLIMATIC MOBILITY
            # =================================================

            thermal_mobility = (

                node.temperature
                * self.temperature_mobility
            )

            node.ax += random.uniform(
                -thermal_mobility,
                thermal_mobility,
            )

            node.ay += random.uniform(
                -thermal_mobility,
                thermal_mobility,
            )

            # =================================================
            # PRESSURE DRIFT
            # =================================================

            node.ax += (
                node.pressure
                * self.pressure_drift
                * random.uniform(-1, 1)
            )

            node.ay += (
                node.pressure
                * self.pressure_drift
                * random.uniform(-1, 1)
            )

            # =================================================
            # TURBULENT EXPLORATION
            # =================================================

            climatic_turbulence = (

                node.turbulence_field
                * self.turbulence_exploration
            )

            node.ax += random.uniform(
                -climatic_turbulence,
                climatic_turbulence,
            )

            node.ay += random.uniform(
                -climatic_turbulence,
                climatic_turbulence,
            )

            # =================================================
            # STORM DISRUPTION
            # =================================================

            if (
                node.storm_potential > 0.30
            ):

                disruption = (

                    node.storm_potential
                    * self.storm_disruption
                )

                node.ax += random.uniform(
                    -disruption,
                    disruption,
                )

                node.ay += random.uniform(
                    -disruption,
                    disruption,
                )

            # =================================================
            # THERMAL VISCOSITY
            # =================================================

            thermal_drag = (

                node.temperature
                * self.thermal_viscosity
            )

            node.ax -= (
                node.vx
                * thermal_drag
            )

            node.ay -= (
                node.vy
                * thermal_drag
            )

            # =================================================
            # TURBULENCE FRICTION
            # =================================================

            turbulence_drag = (

                node.turbulence_field
                * self.turbulence_friction
            )

            node.ax -= (
                node.vx
                * turbulence_drag
            )

            node.ay -= (
                node.vy
                * turbulence_drag
            )

            # =================================================
            # COLD ZONE RETENTION
            # =================================================

            if node.temperature < 0.5:

                node.ax -= (
                    node.vx
                    * self.cold_zone_retention
                )

                node.ay -= (
                    node.vy
                    * self.cold_zone_retention
                )

            # =================================================
            # HUMIDITY COHESION
            # =================================================

            humidity_drag = (

                node.humidity
                * self.humidity_cohesion
            )

            node.ax -= (
                node.vx
                * humidity_drag
            )

            node.ay -= (
                node.vy
                * humidity_drag
            )

            # =================================================
            # ATTRACTOR RETENTION
            # =================================================

            attractor_drag = (

                node.attractor_strength
                * self.attractor_coupling
            )

            node.ax -= (
                node.vx
                * attractor_drag
            )

            node.ay -= (
                node.vy
                * attractor_drag
            )

            # =================================================
            # REGIONAL FIELD
            # =================================================

            self._apply_neighbor_field(
                node,
                ecological_pressure,
            )

            # =================================================
            # VORTEX ROTATION
            # =================================================

            rotational_force = (

                node.vorticity
                * self.vortex_rotation
            )

            vortex_x = -node.vy
            vortex_y = node.vx

            node.ax += (
                vortex_x
                * rotational_force
            )

            node.ay += (
                vortex_y
                * rotational_force
            )

            # =================================================
            # REGIONAL INERTIA
            # =================================================

            node.ax -= (
                node.vx
                * self.regional_inertia
            )

            node.ay -= (
                node.vy
                * self.regional_inertia
            )

            # =================================================
            # INERTIAL INTEGRATION
            # =================================================

            node.vx += (
                node.ax
                / max(
                    node.spatial_inertia,
                    0.001
                )
            )

            node.vy += (
                node.ay
                / max(
                    node.spatial_inertia,
                    0.001
                )
            )

            # =================================================
            # ECOLOGICAL DRAG
            # =================================================

            drag = (

                self.velocity_decay

                * (
                    1.0
                    - node.spatial_drag
                )
            )

            node.vx *= drag
            node.vy *= drag

            # =================================================
            # LONG RANGE DECOHERENCE
            # =================================================

            trajectory_size = len(
                node.trajectory_memory
            )

            decoherence = (
                trajectory_size
                * self.long_range_decay
            )

            node.vx *= (
                max(
                    0.6,
                    1.0 - decoherence
                )
            )

            node.vy *= (
                max(
                    0.6,
                    1.0 - decoherence
                )
            )

            # =================================================
            # VELOCITY LIMIT
            # =================================================

            velocity = math.sqrt(
                node.vx ** 2
                + node.vy ** 2
            )

            if velocity > self.max_velocity:

                scale = (
                    self.max_velocity
                    / velocity
                )

                node.vx *= scale
                node.vy *= scale

            # =================================================
            # POSITION UPDATE
            # =================================================

            node.x += node.vx
            node.y += node.vy

            # =================================================
            # MOTION ECOLOGY
            # =================================================

            node.motion_energy *= 0.980

            node.motion_energy += (
                velocity * 0.05
            )

            node.directional_memory *= (
                self.flow_memory_decay
            )

            node.directional_memory += (
                velocity * 0.03
            )

            # =================================================
            # FLOW COUPLING
            # =================================================

            node.flow_coupling *= 0.990

            node.flow_coupling += (
                ecological_pressure
                * 0.006
            )

            # =================================================
            # CLIMATIC DRIFT
            # =================================================

            node.climatic_drift *= 0.996

            node.climatic_drift += (
                (
                    node.motion_energy
                    + node.temperature
                    + node.pressure
                )
                * 0.0006
            )

            # =================================================
            # TRAJECTORY MEMORY
            # =================================================

            node.trajectory_memory.append(
                (
                    node.x,
                    node.y,
                )
            )

            if (
                len(node.trajectory_memory)
                > self.max_trajectory_memory
            ):

                node.trajectory_memory.pop(0)

            # =================================================
            # CORRIDOR FATIGUE
            # =================================================

            node.spatial_drag *= 0.995

            node.spatial_drag += (
                velocity
                * self.corridor_fatigue
            )

            node.spatial_drag = min(
                node.spatial_drag,
                0.35
            )

            # =================================================
            # ACCELERATION DECAY
            # =================================================

            node.ax *= (
                self.acceleration_decay
            )

            node.ay *= (
                self.acceleration_decay
            )

            print(
                "[SPATIAL]",

                node.id,

                f"pos=({node.x:.2f},{node.y:.2f})",

                f"vel=({node.vx:.2f},{node.vy:.2f})",

                f"temp={node.temperature:.2f}",

                f"storm={node.storm_potential:.2f}",

                f"vorticity={node.vorticity:.2f}",
            )

    # =========================================================
    # REGIONAL FLOW FIELD
    # =========================================================

    def _apply_neighbor_field(
        self,
        node,
        ecological_pressure,
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

            # =============================================
            # LOCAL REPULSION
            # =============================================

            if distance < 1.5:

                repulsion = (
                    self.neighbor_repulsion
                    / distance
                )

                node.ax -= (
                    dx * repulsion
                )

                node.ay -= (
                    dy * repulsion
                )

            # =============================================
            # CORRIDOR ATTRACTION
            # =============================================

            attraction = (
                edge.weight
                * self.neighbor_attraction
            )

            node.ax += (
                dx * attraction
            )

            node.ay += (
                dy * attraction
            )

            # =============================================
            # FLOW ALIGNMENT
            # =============================================

            node.ax += (
                (
                    neighbor.vx
                    - node.vx
                )
                * self.flow_alignment
            )

            node.ay += (
                (
                    neighbor.vy
                    - node.vy
                )
                * self.flow_alignment
            )

            # =============================================
            # PRESSURE FIELD
            # =============================================

            pressure_delta = (
                ecological_pressure
                - (
                    neighbor.activation
                    + neighbor.tension
                    + neighbor.pressure
                )
            )

            node.ax += (
                dx
                * pressure_delta
                * self.pressure_coupling
                * 0.008
            )

            node.ay += (
                dy
                * pressure_delta
                * self.pressure_coupling
                * 0.008
            )
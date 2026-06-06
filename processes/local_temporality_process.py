import math
import random


class LocalTemporalityProcess:

    """
    Distributed local temporality ecology.

    No universal clock.
    No shared chronology.
    No synchronized civilization.
    No stable historical rate.

    Only:
    - local historical velocities
    - narrative acceleration
    - cultural inertia
    - temporal fragmentation
    - asynchronous civilizations
    - regional temporal turbulence
    - incompatible historical flows
    """

    def __init__(self):

        # =====================================================
        # TEMPORAL ECOLOGY
        # =====================================================

        self.temporal_regions = {}

        self.temporal_fractures = []

        self.temporal_vortices = []

        self.asynchronous_zones = []

        # =====================================================
        # ECOLOGICAL PARAMETERS
        # =====================================================

        self.temporal_decay = 0.997

        self.fracture_threshold = 1.2

        self.temporal_mutation_rate = 0.01

        self.vortex_probability = 0.002

    # =========================================================
    # MAIN EVOLUTION
    # =========================================================

    def evolve(
        self,
        agents,
    ):

        if not agents:
            return

        self._update_local_temporalities(
            agents
        )

        self._generate_temporal_drift(
            agents
        )

        self._stabilize_temporal_regions(
            agents
        )

        self._generate_temporal_vortices(
            agents
        )

        self._fragment_historical_flows(
            agents
        )

        self._trigger_temporal_fractures(
            agents
        )

        self._decay_temporal_ecology()

    # =========================================================
    # LOCAL TEMPORALITIES
    # =========================================================

    def _update_local_temporalities(
        self,
        agents,
    ):

        for agent in agents:

            if not hasattr(
                agent,
                "historical_velocity",
            ):

                agent.historical_velocity = (
                    random.uniform(
                        0.5,
                        1.5,
                    )
                )

            if not hasattr(
                agent,
                "temporal_inertia",
            ):

                agent.temporal_inertia = (
                    random.uniform(
                        0.0,
                        1.0,
                    )
                )

            acceleration = (

                random.uniform(
                    -0.02,
                    0.03,
                )

                + agent.symbolic_drift
                * 0.005

                + agent.mythological_pressure
                * 0.003
            )

            agent.historical_velocity += (
                acceleration
            )

            agent.historical_velocity = max(
                0.1,
                min(
                    5.0,
                    agent.historical_velocity,
                )
            )

            agent.temporal_inertia += (
                random.uniform(
                    -0.01,
                    0.01,
                )
            )

            agent.temporal_inertia = max(
                0.0,
                min(
                    2.0,
                    agent.temporal_inertia,
                )
            )

    # =========================================================
    # TEMPORAL DRIFT
    # =========================================================

    def _generate_temporal_drift(
        self,
        agents,
    ):

        for agent in agents:

            drift_probability = (

                self.temporal_mutation_rate

                + agent.semiotic_instability
                * 0.01
            )

            if (
                random.random()
                > drift_probability
            ):
                continue

            drift = random.uniform(
                -0.2,
                0.5,
            )

            agent.historical_velocity += (
                drift
            )

            agent.symbolic_drift += (
                abs(drift)
                * 0.1
            )

            agent.cultural_fragmentation += (
                abs(drift)
                * 0.05
            )

    # =========================================================
    # TEMPORAL REGIONS
    # =========================================================

    def _stabilize_temporal_regions(
        self,
        agents,
    ):

        for agent in agents:

            nearby_agents = (
                self._find_local_agents(
                    agent,
                    agents,
                    radius=6.0,
                )
            )

            compatible_temporalities = 0

            for other in nearby_agents:

                if other is agent:
                    continue

                compatibility = (
                    self._temporal_compatibility(
                        agent,
                        other,
                    )
                )

                if compatibility > 0.6:
                    compatible_temporalities += 1

            if compatible_temporalities == 0:
                continue

            region_key = int(
                (
                    agent.x
                    + agent.y
                )
                * 0.5
            )

            self.temporal_regions[
                region_key
            ] = (
                self.temporal_regions.get(
                    region_key,
                    0.0,
                )
                + compatible_temporalities
                * 0.002
            )

            agent.local_coherence += (
                compatible_temporalities
                * 0.001
            )

    # =========================================================
    # TEMPORAL VORTICES
    # =========================================================

    def _generate_temporal_vortices(
        self,
        agents,
    ):

        for agent in agents:

            probability = (

                self.vortex_probability

                + agent.historical_velocity
                * 0.001
            )

            if (
                random.random()
                > probability
            ):
                continue

            vortex = {
                "cycle": (
                    agent.state["cycle"]
                ),
                "position": (
                    (
                        agent.x,
                        agent.y,
                    )
                ),
                "velocity": (
                    agent.historical_velocity
                ),
            }

            self.temporal_vortices.append(
                vortex
            )

            self._apply_temporal_vortex(
                vortex,
                agents,
            )

    # =========================================================
    # HISTORICAL FRAGMENTATION
    # =========================================================

    def _fragment_historical_flows(
        self,
        agents,
    ):

        for agent in agents:

            nearby_agents = (
                self._find_local_agents(
                    agent,
                    agents,
                    radius=7.0,
                )
            )

            divergence = 0.0

            for other in nearby_agents:

                if other is agent:
                    continue

                divergence += abs(

                    agent.historical_velocity

                    - other.historical_velocity
                )

            fragmentation_probability = (
                divergence
                * 0.003
            )

            if (
                random.random()
                > fragmentation_probability
            ):
                continue

            agent.fragmentation += (
                random.uniform(
                    0.02,
                    0.1,
                )
            )

            agent.cultural_fragmentation += (
                random.uniform(
                    0.02,
                    0.1,
                )
            )

            asynchronous_zone = {
                "cycle": (
                    agent.state["cycle"]
                ),
                "position": (
                    (
                        agent.x,
                        agent.y,
                    )
                ),
                "divergence": divergence,
            }

            self.asynchronous_zones.append(
                asynchronous_zone
            )

    # =========================================================
    # TEMPORAL FRACTURES
    # =========================================================

    def _trigger_temporal_fractures(
        self,
        agents,
    ):

        for agent in agents:

            fracture_pressure = (

                abs(
                    agent.historical_velocity
                    - 1.0
                )

                + agent.temporal_inertia

                + agent.fragmentation

                + agent.cultural_fragmentation
            )

            if (
                fracture_pressure
                < self.fracture_threshold
            ):
                continue

            fracture_probability = (
                fracture_pressure
                * 0.005
            )

            if (
                random.random()
                > fracture_probability
            ):
                continue

            fracture = {
                "cycle": (
                    agent.state["cycle"]
                ),
                "position": (
                    (
                        agent.x,
                        agent.y,
                    )
                ),
                "pressure": (
                    fracture_pressure
                ),
            }

            self.temporal_fractures.append(
                fracture
            )

            self._apply_temporal_fracture(
                agent,
                agents,
            )

    # =========================================================
    # TEMPORAL VORTEX EFFECTS
    # =========================================================

    def _apply_temporal_vortex(
        self,
        vortex,
        agents,
    ):

        vx, vy = vortex["position"]

        for agent in agents:

            dx = agent.x - vx
            dy = agent.y - vy

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance > 5.0:
                continue

            distortion = (

                vortex["velocity"]
                * 0.01
            )

            agent.historical_velocity += (
                random.uniform(
                    -distortion,
                    distortion,
                )
            )

            agent.temporal_inertia += (
                random.uniform(
                    0.0,
                    distortion,
                )
            )

            agent.symbolic_drift += (
                distortion
                * 0.2
            )

    # =========================================================
    # TEMPORAL FRACTURE EFFECTS
    # =========================================================

    def _apply_temporal_fracture(
        self,
        source_agent,
        agents,
    ):

        nearby_agents = (
            self._find_local_agents(
                source_agent,
                agents,
                radius=6.0,
            )
        )

        for other in nearby_agents:

            if other is source_agent:
                continue

            distortion = random.uniform(
                0.05,
                0.2,
            )

            other.historical_velocity += (
                random.uniform(
                    -distortion,
                    distortion,
                )
            )

            other.temporal_inertia += (
                distortion
            )

            other.fragmentation += (
                distortion
                * 0.3
            )

            other.cultural_fragmentation += (
                distortion
                * 0.3
            )

            other.semiotic_instability += (
                distortion
                * 0.2
            )

    # =========================================================
    # TEMPORAL COMPATIBILITY
    # =========================================================

    def _temporal_compatibility(
        self,
        agent_a,
        agent_b,
    ):

        velocity_distance = abs(

            agent_a.historical_velocity

            - agent_b.historical_velocity
        )

        inertia_distance = abs(

            agent_a.temporal_inertia

            - agent_b.temporal_inertia
        )

        compatibility = (

            1.0

            - velocity_distance
            * 0.3

            - inertia_distance
            * 0.2
        )

        return max(
            0.0,
            min(
                1.0,
                compatibility,
            )
        )

    # =========================================================
    # LOCAL NEIGHBORHOODS
    # =========================================================

    def _find_local_agents(
        self,
        source_agent,
        agents,
        radius=6.0,
    ):

        local_agents = []

        for agent in agents:

            dx = (
                agent.x
                - source_agent.x
            )

            dy = (
                agent.y
                - source_agent.y
            )

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance <= radius:
                local_agents.append(
                    agent
                )

        return local_agents

    # =========================================================
    # ECOLOGICAL DECAY
    # =========================================================

    def _decay_temporal_ecology(
        self,
    ):

        self.temporal_fractures = [

            fracture

            for fracture
            in self.temporal_fractures

            if random.random()
            < self.temporal_decay
        ]

        if (
            len(self.temporal_fractures)
            > 200
        ):

            self.temporal_fractures = (
                self.temporal_fractures[-200:]
            )

        self.temporal_vortices = [

            vortex

            for vortex
            in self.temporal_vortices

            if random.random()
            < self.temporal_decay
        ]

        if (
            len(self.temporal_vortices)
            > 200
        ):

            self.temporal_vortices = (
                self.temporal_vortices[-200:]
            )

        self.asynchronous_zones = [

            zone

            for zone
            in self.asynchronous_zones

            if random.random()
            < self.temporal_decay
        ]

        if (
            len(self.asynchronous_zones)
            > 300
        ):

            self.asynchronous_zones = (
                self.asynchronous_zones[-300:]
            )
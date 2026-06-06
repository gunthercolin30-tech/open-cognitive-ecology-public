# technology/distributed_technological_ecology.py

import random


class DistributedTechnologicalEcology:
    """
    Distributed technological dynamics.

    This ecology models:
    - diffusion of innovation
    - technological convergence
    - infrastructure fragmentation
    - local lock-in
    - technical collapse
    - resilience propagation

    No central platform.
    No universal standard.
    No guaranteed compatibility.
    """

    def __init__(self):
        self.global_innovation = 0.0
        self.global_obsolescence = 0.0
        self.global_lock_in = 0.0
        self.global_fragility = 0.0
        self.global_resilience = 0.0

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        agents,
    ):
        """
        Update distributed technological ecology.
        """

        if not agents:
            return

        innovation_values = []
        obsolescence_values = []
        lock_in_values = []
        fragility_values = []
        resilience_values = []

        for agent in agents:
            if not hasattr(
                agent,
                "technological_component",
            ):
                continue

            component = (
                agent.technological_component
            )

            component.update_technological_dynamics()

            innovation_values.append(
                component.innovation_flow
            )

            obsolescence_values.append(
                component.obsolescence
            )

            lock_in_values.append(
                component.lock_in
            )

            fragility_values.append(
                component.technical_fragility
            )

            resilience_values.append(
                component.infrastructure_resilience
            )

            # Local diffusion effects
            component.technological_capital += (
                component.innovation_flow
                * random.uniform(
                    0.0,
                    0.02,
                )
            )

            component.technological_capital = max(
                0.0,
                min(
                    2.0,
                    component.technological_capital,
                ),
            )

        if innovation_values:
            n = len(
                innovation_values
            )

            self.global_innovation = (
                sum(innovation_values) / n
            )

            self.global_obsolescence = (
                sum(obsolescence_values) / n
            )

            self.global_lock_in = (
                sum(lock_in_values) / n
            )

            self.global_fragility = (
                sum(fragility_values) / n
            )

            self.global_resilience = (
                sum(resilience_values) / n
            )
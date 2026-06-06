# science/distributed_scientific_ecology.py

class DistributedScientificEcology:
    """
    Distributed scientific ecology.

    Aggregates local scientific dynamics across all agents:
    - hypothesis production
    - experimental rigor
    - knowledge accumulation
    - controversies
    - paradigm competition
    - conceptual shifts

    No global truth.
    No final scientific equilibrium.
    Only evolving distributed epistemic structures.
    """

    def __init__(self):
        self.total_hypothesis_generation = 0.0
        self.total_experimental_rigor = 0.0
        self.total_knowledge_stock = 0.0
        self.total_controversy = 0.0
        self.total_paradigm_alignment = 0.0
        self.total_conceptual_shift_pressure = 0.0
        self.total_scientific_legitimacy = 0.0
        self.total_anomaly_load = 0.0
        self.total_paradigm_inertia = 0.0
        self.total_scientific_fragmentation = 0.0

        self.agent_count = 0

    def update(self, agents):
        """
        Aggregate scientific variables across all active agents.

        The runtime may provide:
        - a list of agent objects, or
        - a dictionary of nodes.

        Only objects exposing a scientific component are
        included in the aggregation.
        """

        self.total_hypothesis_generation = 0.0
        self.total_experimental_rigor = 0.0
        self.total_knowledge_stock = 0.0
        self.total_controversy = 0.0
        self.total_paradigm_alignment = 0.0
        self.total_conceptual_shift_pressure = 0.0
        self.total_scientific_legitimacy = 0.0
        self.total_anomaly_load = 0.0
        self.total_paradigm_inertia = 0.0
        self.total_scientific_fragmentation = 0.0

        # If a dictionary is provided, use its values.
        if isinstance(agents, dict):
            iterable = agents.values()
        else:
            iterable = agents

        active_agents = []

        for agent in iterable:

            # Keep only objects exposing scientific dynamics.
            if not hasattr(
                agent,
                "hypothesis_generation_rate",
            ):
                continue

            # If the object has a state, ensure it is active.
            if hasattr(agent, "state"):
                if (
                    agent.state.get("status")
                    != "active"
                ):
                    continue

            active_agents.append(agent)

        self.agent_count = len(active_agents)

        if self.agent_count == 0:
            return

        for agent in active_agents:
            self.total_hypothesis_generation += (
                agent.hypothesis_generation_rate
            )
            self.total_experimental_rigor += (
                agent.experimental_rigor
            )
            self.total_knowledge_stock += (
                agent.knowledge_stock
            )
            self.total_controversy += (
                agent.controversy_level
            )
            self.total_paradigm_alignment += (
                agent.paradigm_alignment
            )
            self.total_conceptual_shift_pressure += (
                agent.conceptual_shift_pressure
            )
            self.total_scientific_legitimacy += (
                agent.scientific_legitimacy
            )
            self.total_anomaly_load += (
                agent.anomaly_load
            )
            self.total_paradigm_inertia += (
                agent.paradigm_inertia
            )
            self.total_scientific_fragmentation += (
                agent.scientific_fragmentation
            )

        n = self.agent_count

        self.total_hypothesis_generation /= n
        self.total_experimental_rigor /= n
        self.total_knowledge_stock /= n
        self.total_controversy /= n
        self.total_paradigm_alignment /= n
        self.total_conceptual_shift_pressure /= n
        self.total_scientific_legitimacy /= n
        self.total_anomaly_load /= n
        self.total_paradigm_inertia /= n
        self.total_scientific_fragmentation /= n
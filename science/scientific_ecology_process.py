# science/scientific_ecology_process.py

from science.distributed_scientific_ecology import (
    DistributedScientificEcology,
)


class ScientificEcologyProcess:
    """
    Process integrating distributed scientific ecology
    into the main cognitive cycle.
    """

    def __init__(self):
        self.scientific_ecology = (
            DistributedScientificEcology()
        )

    def update(self, graph):
        """
        Update distributed scientific ecology.
        """

        # The runtime stores active agents in graph.nodes.
        self.scientific_ecology.update(
            graph.nodes
        )

        print(
            "[SCIENTIFIC_ECOLOGY] "
            f"hypotheses="
            f"{self.scientific_ecology.total_hypothesis_generation:.2f} "
            f"rigor="
            f"{self.scientific_ecology.total_experimental_rigor:.2f} "
            f"knowledge="
            f"{self.scientific_ecology.total_knowledge_stock:.2f} "
            f"controversy="
            f"{self.scientific_ecology.total_controversy:.2f} "
            f"paradigm="
            f"{self.scientific_ecology.total_paradigm_alignment:.2f} "
            f"shift="
            f"{self.scientific_ecology.total_conceptual_shift_pressure:.2f} "
            f"legitimacy="
            f"{self.scientific_ecology.total_scientific_legitimacy:.2f} "
            f"anomalies="
            f"{self.scientific_ecology.total_anomaly_load:.2f} "
            f"inertia="
            f"{self.scientific_ecology.total_paradigm_inertia:.2f} "
            f"fragmentation="
            f"{self.scientific_ecology.total_scientific_fragmentation:.2f}"
        )
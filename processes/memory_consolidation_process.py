# processes/memory_consolidation_process.py

class MemoryConsolidationProcess:
    def __init__(
        self,
        graph,
        activation_threshold=0.4,
        salience_gain=0.05,
    ):
        self.graph = graph
        self.activation_threshold = activation_threshold
        self.salience_gain = salience_gain

    async def run(self):

        for node in self.graph.nodes.values():

            if node.activation >= self.activation_threshold:

                node.salience += self.salience_gain

                print(
                    "[CONSOLIDATION]",
                    node.id,
                    f"salience={node.salience:.2f}"
                )
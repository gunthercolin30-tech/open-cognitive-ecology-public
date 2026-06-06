# processes/competitive_tension_process.py

class CompetitiveTensionProcess:
    def __init__(
        self,
        graph,
        activation_threshold=0.8,
        pressure_gain=0.04,
        tension_gain=0.02,
    ):

        self.graph = graph

        self.activation_threshold = (
            activation_threshold
        )

        self.pressure_gain = pressure_gain

        self.tension_gain = tension_gain

    async def run(self):

        highly_active_nodes = [

            node

            for node in self.graph.nodes.values()

            if node.activation >= (
                self.activation_threshold
            )
        ]

        if len(highly_active_nodes) < 2:
            return

        total_activation = sum(
            node.activation
            for node in highly_active_nodes
        )

        for node in highly_active_nodes:

            relative_dominance = (
                node.activation
                / total_activation
            )

            competitive_load = (
                (1.0 - relative_dominance)
                * self.pressure_gain
            )

            node.competitive_pressure += (
                competitive_load
            )

            node.tension += (
                competitive_load
                * self.tension_gain
            )

            print(
                "[COMPETITION]",
                node.id,
                f"pressure={node.competitive_pressure:.2f}",
                f"tension={node.tension:.2f}"
            )
from processes.base import (
    CognitiveProcess
)


class SaliencePropagationProcess(
    CognitiveProcess
):

    def __init__(self):

        super().__init__(
            "salience_propagation"
        )

    async def step(self):

        graph = (
            self.context
            .cognitive_graph
        )

        active_nodes = (
            graph.get_active_nodes(
                threshold=0.05
            )
        )

        for node in active_nodes:

            node.salience += (
                node.activation * 0.02
            )

            if node.tension > 0:

                node.activation += (
                    node.tension * 0.01
                )

            if node.salience > 5.0:

                node.salience = 5.0

            if node.activation > 5.0:

                node.activation = 5.0

        self.energy -= 0.2

        print(
            "[process] salience propagation"
        )

        for node in active_nodes:

            print(

                "[salience-node]",

                node.content,

                "| activation =",

                round(
                    node.activation,
                    3
                ),

                "| salience =",

                round(
                    node.salience,
                    3
                ),

                "| tension =",

                round(
                    node.tension,
                    3
                ),
            )
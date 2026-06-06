from processes.base import (
    CognitiveProcess
)


class MemoryConsolidationProcess(
    CognitiveProcess
):

    def __init__(self):

        super().__init__(
            "memory_consolidation"
        )

    async def step(self):

        memories = (

            self.context
            .memory_manager
            .memories
            .values()
        )

        for memory in memories:

            memory.salience *= 0.99

            memory.energy *= 0.995

        self.energy -= 0.5

        print(
            "[process] consolidation"
        )

        for memory in memories:

            print(

                "[memory]",

                memory.content,

                "| salience =",

                round(
                    memory.salience,
                    3
                ),

                "| energy =",

                round(
                    memory.energy,
                    3
                ),
            )
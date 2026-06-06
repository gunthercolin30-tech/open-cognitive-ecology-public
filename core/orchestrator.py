import asyncio

from core.event_bus import EventBus

from core.scheduler import (
    CognitiveScheduler
)

from core.context import (
    CognitiveContext
)

from memory.memory_manager import (
    MemoryManager
)

from salience.salience_engine import (
    SalienceEngine
)

from environment.environment_manager import (
    EnvironmentManager
)

from processes.memory_consolidation import (
    MemoryConsolidationProcess
)

from processes.salience_propagation import (
    SaliencePropagationProcess
)

from processes.bifurcation_process import (
    BifurcationProcess
)

from cognitive_graph import (
    CognitiveGraph,
    CognitiveNode,
)


class CognitiveOrchestrator:

    def __init__(self):

        self.running = True

        self.event_bus = EventBus()

        self.memory_manager = (
            MemoryManager(
                self.event_bus
            )
        )

        self.salience_engine = (
            SalienceEngine(
                self.event_bus
            )
        )

        self.environment_manager = (
            EnvironmentManager(
                self.event_bus
            )
        )

        self.scheduler = (
            CognitiveScheduler()
        )

        self.cognitive_graph = (
            CognitiveGraph()
        )

        self.context = CognitiveContext(

            memory_manager=(
                self.memory_manager
            ),

            salience_engine=(
                self.salience_engine
            ),

            environment_manager=(
                self.environment_manager
            ),

            cognitive_graph=(
                self.cognitive_graph
            ),

            event_bus=self.event_bus,
        )

    async def initialize(self):

        consolidation_process = (
            MemoryConsolidationProcess()
        )

        consolidation_process.bind_context(
            self.context
        )

        self.scheduler.register(
            consolidation_process
        )

        salience_process = (
            SaliencePropagationProcess()
        )

        salience_process.bind_context(
            self.context
        )

        self.scheduler.register(
            salience_process
        )

        bifurcation_process = (
            BifurcationProcess(
                graph=self.cognitive_graph,
                event_bus=self.event_bus,
            )
        )

        self.scheduler.register(
            bifurcation_process
        )

        initial_memories = [

            (
                "System initialization",
                ["system"],
            ),

            (
                "Persistent identity emerging",
                ["identity"],
            ),

            (
                "Environment monitoring active",
                ["environment"],
            ),

            (
                "Unresolved contradiction detected",
                ["tension"],
            ),
        ]

        previous_node = None

        for content, tags in initial_memories:

            await self.memory_manager.add_memory(
                content,
                tags=tags,
            )

            node = CognitiveNode(
                content=content,
                activation=1.0,
                salience=1.0,
            )

            if "tension" in tags:

                node.tension = 1.0

            self.cognitive_graph.add_node(
                node
            )

            if previous_node:

                self.cognitive_graph.connect(
                    previous_node.id,
                    node.id,
                    weight=0.5,
                )

            previous_node = node

    async def run(self):

        while self.running:

            await (
                self.environment_manager
                .tick()
            )

            await (
                self.salience_engine
                .tick()
            )

            selected = (
                self.scheduler
                .select_processes()
            )

            for process in selected:

                await process.step()

            await (
                self.memory_manager
                .tick()
            )

            self.cognitive_graph.tick()

            active_nodes = (
                self.cognitive_graph
                .get_active_nodes()
            )

            print(
                "[runtime] tick"
            )

            print(
                "[environment]",
                self.environment_manager.state,
            )

            print(
                "[memory-count]",
                len(
                    self.memory_manager
                    .memories
                ),
            )

            print(
                "[active-cognitive-nodes]",
                len(active_nodes),
            )

            for node in active_nodes:

                print(
                    "[node]",
                    node.content,
                    "| activation:",
                    round(
                        node.activation,
                        3
                    ),
                    "| salience:",
                    round(
                        node.salience,
                        3
                    ),
                    "| tension:",
                    round(
                        node.tension,
                        3
                    ),
                )

            print(
                "------------------"
            )

            await asyncio.sleep(1)
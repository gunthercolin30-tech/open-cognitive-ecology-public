# runtime/build_core.py

from cognitive_graph.graph import CognitiveGraph
from cognitive_graph.propagation import (
    PropagationEngine,
)

from visualization import (
    CognitiveFieldVisualizer,
)

from core.scheduler import (
    CognitiveScheduler,
)


def build_core():
    """
    Build the core runtime infrastructure.

    Returns:
        dict containing:
        - graph
        - propagation_engine
        - visualizer
        - scheduler
        - agents
    """

    graph = CognitiveGraph()

    propagation_engine = (
        PropagationEngine(graph)
    )

    visualizer = (
        CognitiveFieldVisualizer()
    )

    scheduler = (
        CognitiveScheduler()
    )

    # Shared mutable collection of agents
    agents = []

    return {
        "graph": graph,
        "propagation_engine": (
            propagation_engine
        ),
        "visualizer": visualizer,
        "scheduler": scheduler,
        "agents": agents,
    }
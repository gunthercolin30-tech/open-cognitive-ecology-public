# runtime/initialize_graph.py

from agents.agent import PersistentAgent

from runtime.graph_builders import (
    apply_positions,
    build_core_topology,
    build_ecology_topology,
    build_theoretical_topology,
    stimulate_initial_nodes,
)


def _collect_node_objects(graph):
    """
    Normalize graph.nodes into a list of node objects.
    Supports:
    - dict-like containers
    - iterables of node objects
    - iterables of node identifiers
    """

    raw_nodes = graph.nodes

    if isinstance(raw_nodes, dict):
        return list(raw_nodes.values())

    node_objects = []

    for item in raw_nodes:

        # Already a node object
        if hasattr(item, "__dict__") and not isinstance(
            item,
            str,
        ):
            node_objects.append(item)
            continue

        # Node identifier
        if isinstance(item, str):
            node = graph.get_node(item)
            if node is not None:
                node_objects.append(node)

    return node_objects


def _couple_agents(graph, agents):
    """
    Create one PersistentAgent per node and register
    it in the shared population.
    """

    if agents is None:
        return

    # Preserve shared list identity.
    agents.clear()

    for node in _collect_node_objects(graph):

        agent = PersistentAgent(
            name=getattr(
                node,
                "id",
                "agent",
            )
        )

        # Mirror spatial coordinates.
        if hasattr(node, "x"):
            agent.x = node.x

        if hasattr(node, "y"):
            agent.y = node.y

        # Bidirectional links.
        node.agent = agent
        agent.node = node

        # Register in shared population.
        agents.append(agent)


def initialize_graph(graph, agents=None):
    """
    Initialize the cognitive graph with:

    - original cognitive topology
    - 17 ecological domains
    - theoretical corpus concepts
    - spatial coordinates
    - initial stimulation
    - PersistentAgent coupling
    """

    # Original core topology.
    build_core_topology(graph)

    # Explicit ecological domains.
    build_ecology_topology(graph)

    # Theoretical corpus concepts.
    build_theoretical_topology(graph)

    # Spatial embedding.
    apply_positions(graph)

    # Initial activation.
    stimulate_initial_nodes(graph)

    # Persistent agent coupling.
    _couple_agents(graph, agents)
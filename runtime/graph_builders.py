# runtime/graph_builders.py

from runtime.graph_constants import ECOLOGY_NODES
from runtime.graph_layout import (
    BASE_POSITIONS,
    ECOLOGY_POSITIONS,
    THEORETICAL_POSITIONS,
)


def build_core_topology(graph):
    """
    Create the original cognitive topology.
    """

    graph.add_edge(
        "origin",
        "memory_cluster",
        weight=0.9,
    )

    graph.add_edge(
        "memory_cluster",
        "concept_field",
        weight=0.7,
    )

    graph.add_edge(
        "concept_field",
        "tension_loop",
        weight=0.8,
    )

    graph.add_edge(
        "tension_loop",
        "origin",
        weight=0.6,
    )

    graph.add_edge(
        "concept_field",
        "exploration_branch",
        weight=0.5,
    )

    graph.add_edge(
        "exploration_branch",
        "novelty_zone",
        weight=0.6,
    )

    graph.add_edge(
        "novelty_zone",
        "origin",
        weight=0.4,
    )


def build_ecology_topology(graph):
    """
    Attach the 17 ecological domains to the conceptual core.
    """

    for ecology_node in ECOLOGY_NODES:

        graph.add_edge(
            "concept_field",
            ecology_node,
            weight=0.45,
        )

        graph.add_edge(
            ecology_node,
            "origin",
            weight=0.25,
        )

    # Structural coupling between the constraints ecology
    # and the theoretical concept of constraint fields.
    graph.add_edge(
        "constraints_ecology",
        "constraint_fields",
        weight=0.8,
    )


def build_theoretical_topology(graph):
    """
    Create the conceptual chain derived from the theoretical corpus.
    """

    graph.add_edge(
        "concept_field",
        "non_closure",
        weight=0.9,
    )

    graph.add_edge(
        "non_closure",
        "constraint_fields",
        weight=0.85,
    )

    graph.add_edge(
        "constraint_fields",
        "non_representability",
        weight=0.8,
    )

    graph.add_edge(
        "constraint_fields",
        "constraint_induced_domain",
        weight=0.85,
    )

    graph.add_edge(
        "constraint_induced_domain",
        "trajectories_without_globality",
        weight=0.8,
    )

    graph.add_edge(
        "trajectories_without_globality",
        "unstable_configuration_principle",
        weight=0.75,
    )

    graph.add_edge(
        "unstable_configuration_principle",
        "formal_constraint_foundations",
        weight=0.8,
    )

    graph.add_edge(
        "formal_constraint_foundations",
        "impossibility_of_global_closure",
        weight=0.9,
    )

    graph.add_edge(
        "impossibility_of_global_closure",
        "origin",
        weight=0.5,
    )


def apply_positions(graph):
    """
    Assign spatial coordinates to all predefined nodes.
    """

    positions = {}

    positions.update(BASE_POSITIONS)
    positions.update(ECOLOGY_POSITIONS)
    positions.update(THEORETICAL_POSITIONS)

    for node_id, (x, y) in positions.items():

        node = graph.get_node(node_id)

        if node is None:
            continue

        node.x = x
        node.y = y


def stimulate_initial_nodes(graph):
    """
    Stimulate the origin and key conceptual nodes.
    """

    graph.stimulate_node(
        "origin",
        activation=1.0,
        salience=1.0,
        tension=0.3,
    )

    for node_id in (
        "concept_field",
        "constraints_ecology",
        "non_closure",
        "constraint_fields",
    ):

        graph.stimulate_node(
            node_id,
            activation=0.4,
            salience=0.6,
            tension=0.1,
        )
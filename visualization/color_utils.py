# visualization/color_utils.py


def get_node_color(
    node,
    political_renderer=None,
):
    """
    Determine the display color of a node.

    Priority order:
    - strong political structures
    - storms
    - vortices
    - special conceptual nodes
    - exploratory nodes
    - dormant nodes
    - default cognitive nodes
    """

    if political_renderer is not None:
        if (
            political_renderer.get_strength(
                node
            ) > 0.7
        ):
            return political_renderer.get_color(
                node
            )

    if getattr(
        node,
        "storm_potential",
        0.0,
    ) > 0.8:
        return "#ff2222"

    if getattr(
        node,
        "vorticity",
        0.0,
    ) > 0.5:
        return "#8844ff"

    if getattr(
        node,
        "id",
        "",
    ) == "concept_field":
        return "#ff3333"

    node_id = getattr(
        node,
        "id",
        "",
    )

    if (
        "exploration" in node_id
        or "novelty" in node_id
    ):
        return "#22aa22"

    if getattr(
        node,
        "dormant",
        False,
    ):
        return "#888888"

    return "#3333ff"


def get_color_from_id(
    node_id,
):
    """
    Stable trajectory color derived from node id.
    """

    if node_id == "concept_field":
        return "#ff6666"

    if (
        "exploration" in node_id
        or "novelty" in node_id
    ):
        return "#44cc44"

    return "#6666ff"
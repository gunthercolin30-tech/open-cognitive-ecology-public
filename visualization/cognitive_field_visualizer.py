# visualization/cognitive_field_visualizer.py

import matplotlib.pyplot as plt

from visualization.distributed_perception_ecology import (
    DistributedPerceptionEcology,
)
from visualization.trajectory_renderer import (
    TrajectoryRenderer,
)
from visualization.climatic_renderer import (
    ClimaticRenderer,
)
from visualization.political_renderer import (
    PoliticalRenderer,
)
from visualization.node_renderer import (
    NodeRenderer,
)
from visualization.health_renderer import (
    HealthRenderer,
)
from visualization.demographic_renderer import (
    DemographicRenderer,
)
from visualization.energy_renderer import (
    EnergyRenderer,
)
from visualization.color_utils import (
    get_color_from_id,
)


class CognitiveFieldVisualizer:
    """
    Distributed cognitive field visualizer.

    The visualizer orchestrates:
    - distributed perception
    - climatic rendering
    - trajectory rendering
    - political overlays
    - node rendering
    - health overlays
    - demographic overlays
    - energy overlays

    The fourth panel is reserved for a global energy view.
    """

    def __init__(self):

        plt.ion()

        # =====================================================
        # DISTRIBUTED PERCEPTION ECOLOGY
        # =====================================================

        self.perception_ecology = (
            DistributedPerceptionEcology(
                perception_count=4,
            )
        )

        # =====================================================
        # SPECIALIZED RENDERERS
        # =====================================================

        self.trajectory_renderer = (
            TrajectoryRenderer(
                max_trajectory_length=60,
            )
        )

        self.climatic_renderer = (
            ClimaticRenderer()
        )

        self.political_renderer = (
            PoliticalRenderer()
        )

        self.node_renderer = (
            NodeRenderer(
                political_renderer=(
                    self.political_renderer
                )
            )
        )

        self.health_renderer = (
            HealthRenderer()
        )

        self.demographic_renderer = (
            DemographicRenderer()
        )

        self.energy_renderer = (
            EnergyRenderer()
        )

        # =====================================================
        # VISUAL STATE
        # =====================================================

        self.frame = 0

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        graph,
    ):

        self.frame += 1

        plt.clf()

        distributed_fields = (
            self.perception_ecology.perceive(
                graph
            )
        )

        axes = []

        for i in range(4):

            ax = plt.subplot(
                2,
                2,
                i + 1,
            )

            ax.set_facecolor(
                "#ececec"
            )

            axes.append(ax)

        # =====================================================
        # FIRST 3 PANELS: DISTRIBUTED PERCEPTION
        # =====================================================

        for field_index, perceived_field in enumerate(
            distributed_fields[:3]
        ):

            if field_index >= len(axes):
                break

            ax = axes[field_index]

            perceived_nodes = (
                perceived_field["nodes"]
            )

            perceived_edges = (
                perceived_field["edges"]
            )

            center_x, center_y = (
                perceived_field["center"]
            )

            xs = []
            ys = []

            # =================================================
            # LOCAL TRAJECTORIES
            # =================================================

            self.trajectory_renderer.update(
                field_index,
                perceived_nodes,
            )

            self.climatic_renderer.draw(
                perceived_nodes,
                ax,
            )

            self.trajectory_renderer.draw(
                field_index,
                ax,
                get_color_from_id,
            )

            # =================================================
            # EDGES
            # =================================================

            self._draw_edges(
                perceived_edges,
                perceived_nodes,
                ax,
                xs,
                ys,
            )

            # =================================================
            # NODES
            # =================================================

            for perception in perceived_nodes.values():

                node = perception["node"]

                x = perception["x"]
                y = perception["y"]

                self.node_renderer.draw(
                    node=node,
                    x=x,
                    y=y,
                    memory_strength=perception["memory"],
                    frame=self.frame,
                    ax=ax,
                    xs=xs,
                    ys=ys,
                )

                # Health overlay
                self.health_renderer.draw(
                    node=node,
                    x=x,
                    y=y,
                    ax=ax,
                )

                # Demographic overlay
                self.demographic_renderer.draw(
                    node=node,
                    x=x,
                    y=y,
                    ax=ax,
                )

                # Energy overlay
                self.energy_renderer.draw(
                    node=node,
                    x=x,
                    y=y,
                    ax=ax,
                )

            # =================================================
            # PANEL STYLE
            # =================================================

            self._configure_panel(
                ax=ax,
                xs=xs,
                ys=ys,
                center_x=center_x,
                center_y=center_y,
                field_index=field_index,
            )

        # =====================================================
        # PANEL 4 (BOTTOM RIGHT): GLOBAL ENERGY VIEW
        # =====================================================

        self._render_energy_panel(
            axes[3],
            graph,
        )

        # =====================================================
        # FINAL DISPLAY
        # =====================================================

        plt.suptitle(
            "Distributed Cognitive Perception Ecology"
        )

        plt.tight_layout()

        plt.pause(0.01)

    # =========================================================
    # ENERGY PANEL
    # =========================================================

    def _render_energy_panel(
        self,
        ax,
        graph,
    ):
        """
        Render a dedicated global energy panel in the
        bottom-right quadrant.

        This panel displays:
        - all agents with their current energy state
        - environmental energy resources, if available
        """

        # IMPORTANT:
        # graph.nodes is a dictionary:
        # {node_id: node_object}
        nodes = list(
            getattr(graph, "nodes", {}).values()
        )

        ax.clear()
        ax.set_facecolor("#ececec")
        ax.set_title("Energy Ecology")

        if not nodes:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect("equal")
            return

        xs = []
        ys = []

        # =====================================================
        # DRAW ENVIRONMENTAL ENERGY RESOURCES
        # =====================================================

        resources = getattr(
            graph,
            "energy_resources",
            [],
        )

        for resource in resources:

            x = getattr(resource, "x", None)
            y = getattr(resource, "y", None)

            if x is None or y is None:
                continue

            quantity = getattr(
                resource,
                "quantity",
                getattr(
                    resource,
                    "energy",
                    1.0,
                ),
            )

            size = 80 + max(0.0, quantity) * 40.0

            ax.scatter(
                x,
                y,
                s=size,
                c="#f1c40f",
                alpha=0.35,
                edgecolors="#b7950b",
                linewidths=1.0,
                zorder=1,
            )

            xs.append(x)
            ys.append(y)

        # =====================================================
        # DRAW AGENTS
        # =====================================================

        for node in nodes:

            x = getattr(node, "x", 0.0)
            y = getattr(node, "y", 0.0)

            xs.append(x)
            ys.append(y)

            # Draw core node marker
            try:
                self.node_renderer.draw(
                    node=node,
                    x=x,
                    y=y,
                    memory_strength=1.0,
                    frame=self.frame,
                    ax=ax,
                    xs=[],
                    ys=[],
                )
            except Exception:
                # If node rendering fails,
                # fallback to a simple marker.
                ax.scatter(
                    x,
                    y,
                    s=80,
                    color="#808080",
                    alpha=0.8,
                    zorder=3,
                )

            # Draw energy-specific overlay
            self.energy_renderer.draw(
                node=node,
                x=x,
                y=y,
                ax=ax,
            )

        # =====================================================
        # PANEL BOUNDS
        # =====================================================

        if xs and ys:

            padding = 2.8

            ax.set_xlim(
                min(xs) - padding,
                max(xs) + padding,
            )

            ax.set_ylim(
                min(ys) - padding,
                max(ys) + padding,
            )

        else:

            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)

        ax.set_aspect("equal")
        ax.grid(alpha=0.01)

    # =========================================================
    # EDGE RENDERING
    # =========================================================

    def _draw_edges(
        self,
        perceived_edges,
        perceived_nodes,
        ax,
        xs,
        ys,
    ):

        for (
            source_id,
            target_id,
            edge,
        ) in perceived_edges:

            source = perceived_nodes[source_id]
            target = perceived_nodes[target_id]

            x1 = source["x"]
            y1 = source["y"]

            x2 = target["x"]
            y2 = target["y"]

            xs.extend([x1, x2])
            ys.extend([y1, y2])

            node = source["node"]

            corridor_intensity = min(
                1.0,
                (
                    getattr(node, "path_resonance", 0.0)
                    + getattr(
                        node,
                        "circulation_potential",
                        0.0,
                    )
                    + getattr(
                        node,
                        "long_range_activation",
                        0.0,
                    )
                    + getattr(
                        node,
                        "motion_energy",
                        0.0,
                    )
                    + getattr(
                        node,
                        "temperature",
                        0.0,
                    )
                ),
            )

            alpha = 0.01 + corridor_intensity * 0.18
            linewidth = (
                0.2 + corridor_intensity * 1.6
            )

            ax.plot(
                [x1, x2],
                [y1, y2],
                color="#444444",
                alpha=alpha,
                linewidth=linewidth,
            )

    # =========================================================
    # PANEL CONFIGURATION
    # =========================================================

    def _configure_panel(
        self,
        ax,
        xs,
        ys,
        center_x,
        center_y,
        field_index,
    ):

        if xs and ys:

            padding = 2.8

            ax.set_xlim(
                min(xs) - padding,
                max(xs) + padding,
            )

            ax.set_ylim(
                min(ys) - padding,
                max(ys) + padding,
            )

        else:

            ax.set_xlim(
                center_x - 4,
                center_x + 4,
            )
            ax.set_ylim(
                center_y - 4,
                center_y + 4,
            )

        ax.set_aspect("equal")
        ax.grid(alpha=0.01)

        ax.set_title(
            f"Perception Field {field_index}"
        )
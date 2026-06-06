# visualization/node_renderer.py

import math

import matplotlib.pyplot as plt

from visualization.agent_renderer import (
    format_agent_summary,
)
from visualization.color_utils import (
    get_node_color,
)


class NodeRenderer:
    """
    Render cognitive nodes with local overlays.

    Includes:
    - activity body
    - climatic halo
    - vortex rings
    - political halos
    - simplified labels
    - essential linguistic indicators

    No global viewpoint.
    """

    def __init__(
        self,
        political_renderer=None,
    ):
        self.political_renderer = (
            political_renderer
        )

    # =========================================================
    # DRAW
    # =========================================================

    def draw(
        self,
        node,
        x,
        y,
        memory_strength,
        frame,
        ax,
        xs,
        ys,
    ):
        """
        Draw a single node and append coordinates.
        """

        xs.append(x)
        ys.append(y)

        normalized_activation = min(
            getattr(
                node,
                "activation",
                0.0,
            ),
            3.0,
        )

        normalized_attractor = min(
            getattr(
                node,
                "attractor_strength",
                0.0,
            ),
            2.0,
        )

        motion_factor = min(
            getattr(
                node,
                "motion_energy",
                0.0,
            ),
            1.0,
        )

        temperature_factor = min(
            getattr(
                node,
                "temperature",
                0.0,
            ),
            2.0,
        )

        storm_factor = min(
            getattr(
                node,
                "storm_potential",
                0.0,
            ),
            2.0,
        )

        instability = (
            getattr(
                node,
                "turbulence_field",
                0.0,
            )
            + getattr(
                node,
                "viability_turbulence",
                0.0,
            )
            + getattr(
                node,
                "pressure",
                0.0,
            ) * 0.03
        )

        temporal_factor = (
            1.0
            + (
                math.sin(
                    frame * 0.05
                    + getattr(
                        node,
                        "temporal_phase",
                        0.0,
                    )
                )
                * 0.08
            )
        )

        activity_size = (
            70
            + normalized_activation
            * 320
            + motion_factor
            * 100
            + storm_factor
            * 100
        )

        activity_size *= temporal_factor
        activity_size *= (
            1.0
            - instability * 0.08
        )

        attractor_radius = (
            0.05
            + normalized_attractor
            * 0.55
            + temperature_factor
            * 0.15
        )

        attractor_radius *= temporal_factor

        color = get_node_color(
            node,
            political_renderer=(
                self.political_renderer
            ),
        )

        alpha = (
            0.18
            + memory_strength
            * 0.5
        )

        if getattr(
            node,
            "dormant",
            False,
        ):
            alpha *= 0.4

        # =====================================================
        # CLIMATIC HALO
        # =====================================================

        climatic_radius = (
            attractor_radius
            * (
                1.2
                + getattr(
                    node,
                    "temperature",
                    0.0,
                )
                + getattr(
                    node,
                    "humidity",
                    0.0,
                )
            )
        )

        climatic_alpha = min(
            0.08,
            (
                0.01
                + getattr(
                    node,
                    "temperature",
                    0.0,
                )
                * 0.015
            )
            * memory_strength,
        )

        climatic_halo = plt.Circle(
            (x, y),
            climatic_radius,
            color="#ff8844",
            alpha=climatic_alpha,
        )

        ax.add_patch(
            climatic_halo
        )

        # =====================================================
        # VORTEX HALO
        # =====================================================

        if getattr(
            node,
            "vorticity",
            0.0,
        ) > 0.35:

            vortex_radius = (
                climatic_radius
                * (
                    1.0
                    + getattr(
                        node,
                        "vorticity",
                        0.0,
                    )
                )
            )

            vortex_halo = plt.Circle(
                (x, y),
                vortex_radius,
                fill=False,
                color="#8844ff",
                alpha=min(
                    0.14,
                    getattr(
                        node,
                        "vorticity",
                        0.0,
                    )
                    * 0.04,
                ),
                linewidth=1.0,
            )

            ax.add_patch(
                vortex_halo
            )

        # =====================================================
        # POLITICAL HALO
        # =====================================================

        if self.political_renderer is not None:
            self.political_renderer.draw(
                node=node,
                x=x,
                y=y,
                climatic_radius=(
                    climatic_radius
                ),
                ax=ax,
            )

        # =====================================================
        # PRIMARY HALO
        # =====================================================

        halo = plt.Circle(
            (x, y),
            attractor_radius,
            color=color,
            alpha=0.03
            * memory_strength,
        )

        ax.add_patch(
            halo
        )

        # =====================================================
        # NODE BODY
        # =====================================================

        ax.scatter(
            x,
            y,
            s=activity_size,
            c=color,
            alpha=alpha,
        )

        # =====================================================
        # FLOW VECTOR
        # =====================================================

        if memory_strength > 0.25:
            ax.arrow(
                x,
                y,
                getattr(
                    node,
                    "vx",
                    0.0,
                ),
                getattr(
                    node,
                    "vy",
                    0.0,
                ),
                alpha=0.10,
                width=0.006,
                head_width=0.06,
                color=color,
                length_includes_head=True,
            )

        # =====================================================
        # SIMPLIFIED LABELS
        # =====================================================

        activation = getattr(
            node,
            "activation",
            0.0,
        )

        if (
            memory_strength > 0.75
            and activation > 1.4
        ):

            node_id = str(
                getattr(
                    node,
                    "id",
                    "?",
                )
            )

            if len(node_id) > 10:
                node_id = node_id[:10]

            label = (
                f"{node_id}\n"
                f"A:{activation:.1f}"
            )

            # Linguistic indicator:
            # keep only one compact token if available.
            try:
                summary = (
                    format_agent_summary(
                        node
                    )
                )

                summary_parts = (
                    summary.split("|")
                )

                if len(summary_parts) >= 1:
                    linguistic_part = (
                        summary_parts[-1]
                        .strip()
                    )

                    if (
                        linguistic_part
                        and len(
                            linguistic_part
                        )
                        <= 12
                    ):
                        label += (
                            "\n"
                            + linguistic_part
                        )

            except Exception:
                pass

            ax.text(
                x,
                y + 0.28,
                label,
                ha="center",
                va="bottom",
                fontsize=5,
                color="white",
                alpha=0.80,
                bbox={
                    "boxstyle": "round,pad=0.15",
                    "facecolor": "black",
                    "edgecolor": "none",
                    "alpha": 0.35,
                },
                zorder=20,
            )
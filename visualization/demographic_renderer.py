# visualization/demographic_renderer.py

from matplotlib.patches import Circle


class DemographicRenderer:
    """
    Render demographic indicators around agents.

    Visual encoding:
    - blue halo for young agents
    - purple halo for reproductive agents
    - dark gray halo for elderly agents
    - radius increases with age
    - black cross for dead agents

    No stable demographic equilibrium.
    Only local transient population structures.
    """

    def draw(
        self,
        node,
        x,
        y,
        ax,
    ):
        """
        Draw demographic overlays around a node.
        """

        age = getattr(
            node,
            "age",
            None,
        )

        if age is None:
            return

        is_alive = getattr(
            node,
            "is_alive",
            True,
        )

        is_reproductive = getattr(
            node,
            "is_reproductive",
            False,
        )

        # =====================================================
        # COLOR BY DEMOGRAPHIC STATUS
        # =====================================================

        if age < 15.0:
            color = "#3399ff"      # young
            alpha = 0.10

        elif is_reproductive:
            color = "#aa44ff"      # reproductive
            alpha = 0.12

        else:
            color = "#555555"      # elderly
            alpha = 0.10

        # =====================================================
        # AGE-DEPENDENT SIZE
        # =====================================================

        normalized_age = min(
            1.0,
            max(0.0, age / 100.0),
        )

        radius = (
            0.34
            + normalized_age * 0.18
        )

        linewidth = (
            0.6
            + normalized_age * 1.6
        )

        demographic_ring = Circle(
            (x, y),
            radius=radius,
            facecolor="none",
            edgecolor=color,
            linewidth=linewidth,
            alpha=alpha,
            zorder=8,
        )

        ax.add_patch(
            demographic_ring
        )

        # =====================================================
        # DEATH MARKER
        # =====================================================

        if not is_alive:

            size = 0.15

            ax.plot(
                [x - size, x + size],
                [y - size, y + size],
                color="black",
                linewidth=1.5,
                alpha=0.8,
                zorder=20,
            )

            ax.plot(
                [x - size, x + size],
                [y + size, y - size],
                color="black",
                linewidth=1.5,
                alpha=0.8,
                zorder=20,
            )
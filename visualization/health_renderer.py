# visualization/health_renderer.py

from matplotlib.patches import Circle


class HealthRenderer:
    """
    Render sanitary indicators around agents.

    Visual encoding:
    - green halo for health state
    - orange ring for contagion load
    - red ring for high mortality risk

    No universal health equilibrium.
    Only local unstable sanitary regimes.
    """

    def draw(
        self,
        node,
        x,
        y,
        ax,
    ):
        """
        Draw health overlays around a node.
        """

        health_state = getattr(
            node,
            "health_state",
            None,
        )

        if health_state is None:
            return

        contagion_load = getattr(
            node,
            "contagion_load",
            0.0,
        )

        mortality_risk = getattr(
            node,
            "mortality_risk",
            0.0,
        )

        # =====================================================
        # HEALTH HALO
        # =====================================================

        health_state = max(
            0.0,
            min(1.0, health_state),
        )

        health_alpha = (
            0.05
            + health_state * 0.20
        )

        health_radius = (
            0.18
            + (1.0 - health_state) * 0.08
        )

        health_circle = Circle(
            (x, y),
            radius=health_radius,
            facecolor="#00aa00",
            edgecolor="none",
            alpha=health_alpha,
            zorder=1,
        )

        ax.add_patch(
            health_circle
        )

        # =====================================================
        # CONTAGION RING
        # =====================================================

        if contagion_load > 0.05:

            contagion_ring = Circle(
                (x, y),
                radius=(
                    0.24
                    + contagion_load * 0.12
                ),
                facecolor="none",
                edgecolor="#ff8800",
                linewidth=(
                    0.5
                    + contagion_load * 2.0
                ),
                alpha=(
                    0.10
                    + contagion_load * 0.50
                ),
                zorder=6,
            )

            ax.add_patch(
                contagion_ring
            )

        # =====================================================
        # MORTALITY ALERT
        # =====================================================

        if mortality_risk > 0.60:

            mortality_ring = Circle(
                (x, y),
                radius=(
                    0.30
                    + mortality_risk * 0.15
                ),
                facecolor="none",
                edgecolor="#cc0000",
                linewidth=(
                    0.8
                    + mortality_risk * 2.5
                ),
                alpha=(
                    0.15
                    + mortality_risk * 0.55
                ),
                zorder=7,
            )

            ax.add_patch(
                mortality_ring
            )
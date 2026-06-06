# visualization/political_renderer.py

import matplotlib.pyplot as plt


class PoliticalRenderer:
    """
    Render local political halos.

    Political organization is distributed, unstable,
    and locally contingent. No universal sovereignty.
    """

    # =========================================================
    # POLITICAL STRENGTH
    # =========================================================

    def get_strength(
        self,
        node,
    ):
        """
        Aggregate local political intensity.
        """

        strength = 0.0

        strength += getattr(
            node,
            "institutional_intensity",
            0.0,
        )

        strength += (
            getattr(
                node,
                "symbolic_currency",
                0.0,
            )
            * 0.5
        )

        strength += getattr(
            node,
            "coordination_intensity",
            0.0,
        )

        strength += (
            getattr(
                node,
                "political_tension",
                0.0,
            )
            * 0.5
        )

        return min(
            1.0,
            strength,
        )

    # =========================================================
    # POLITICAL COLOR
    # =========================================================

    def get_color(
        self,
        node,
    ):
        """
        Color associated with local affiliation.
        """

        affiliation = getattr(
            node,
            "political_affiliation",
            "",
        )

        if affiliation == "institutional":
            return "#0055ff"

        if affiliation == "dissident":
            return "#ff5500"

        if affiliation == "mercantile":
            return "#22aa22"

        if affiliation == "coalitional":
            return "#aa22aa"

        return "#777777"

    # =========================================================
    # RENDER
    # =========================================================

    def draw(
        self,
        node,
        x,
        y,
        climatic_radius,
        ax,
    ):
        """
        Draw political influence halo.
        """

        political_strength = (
            self.get_strength(node)
        )

        if political_strength <= 0.05:
            return

        political_radius = (
            climatic_radius
            * (
                1.4
                + political_strength
                * 1.8
            )
        )

        political_halo = plt.Circle(
            (x, y),
            political_radius,
            fill=False,
            color=self.get_color(node),
            alpha=min(
                0.20,
                0.02
                + political_strength
                * 0.08,
            ),
            linewidth=(
                0.6
                + political_strength
                * 1.6
            ),
        )

        ax.add_patch(
            political_halo
        )
# visualization/climatic_renderer.py

import matplotlib.pyplot as plt


class ClimaticRenderer:
    """
    Render local climatic halos.

    Climatic conditions are spatially distributed,
    historically contingent and perceptually local.
    No global equilibrium is assumed.
    """

    def draw(
        self,
        perceived_nodes,
        ax,
    ):
        """
        Draw climatic influence fields around nodes.
        """

        for perception in (
            perceived_nodes.values()
        ):
            node = perception["node"]

            if (
                getattr(
                    node,
                    "temperature",
                    0.0,
                ) <= 0.01
            ):
                continue

            x = perception["x"]
            y = perception["y"]

            memory_strength = (
                perception["memory"]
            )

            climatic_radius = (
                0.8
                + getattr(
                    node,
                    "temperature",
                    0.0,
                ) * 1.8
                + getattr(
                    node,
                    "humidity",
                    0.0,
                )
            )

            alpha = min(
                0.025,
                (
                    getattr(
                        node,
                        "temperature",
                        0.0,
                    )
                    * 0.008
                )
                * memory_strength
            )

            climate = plt.Circle(
                (x, y),
                climatic_radius,
                color="#ffaa66",
                alpha=alpha,
            )

            ax.add_patch(
                climate
            )
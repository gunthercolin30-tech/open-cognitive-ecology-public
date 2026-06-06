# economy/economic_ecology_process.py

from economy.distributed_economic_ecology import (
    DistributedEconomicEcology,
)


class EconomicEcologyProcess:
    """
    Process integrating distributed economic ecology into
    the main cognitive cycle.
    """

    def __init__(
        self,
        regime_count=4,
    ):
        # =====================================================
        # DISTRIBUTED ECONOMY
        # =====================================================

        self.economic_ecology = (
            DistributedEconomicEcology(
                regime_count=regime_count,
            )
        )

        # =====================================================
        # AGGREGATE STATE
        # =====================================================

        self.economic_intensity = 0.0
        self.economic_stress = 0.0
        self.crisis_count = 0
        self.last_crisis = False

    # =========================================================
    # STATE AGGREGATION
    # =========================================================

    def update_aggregate_state(self):
        """
        Aggregate distributed economic variables.
        """

        state = self.economic_ecology.get_state()
        regimes = state["regimes"]

        if not regimes:
            self.economic_intensity = 0.0
            self.economic_stress = 0.0
            self.crisis_count = state["crisis_count"]
            self.last_crisis = state["last_crisis"]
            return

        self.economic_intensity = (
            sum(
                regime["abundance"]
                for regime in regimes
            )
            / len(regimes)
        )

        self.economic_stress = (
            sum(
                regime["economic_stress"]
                for regime in regimes
            )
            / len(regimes)
        )

        self.crisis_count = state["crisis_count"]
        self.last_crisis = state["last_crisis"]

    # =========================================================
    # GRAPH PROJECTION
    # =========================================================

    def project_on_graph(
        self,
        graph,
    ):
        """
        Project local economic variables onto graph nodes.
        """

        if graph is None:
            return

        if not hasattr(
            graph,
            "nodes",
        ):
            return

        regimes = (
            self.economic_ecology.resource_regimes
        )

        if not regimes:
            return

        regime_count = len(regimes)

        if isinstance(
            graph.nodes,
            dict,
        ):
            node_iterable = (
                graph.nodes.values()
            )
        else:
            node_iterable = graph.nodes

        for i, node in enumerate(
            node_iterable
        ):

            if isinstance(
                node,
                str,
            ):
                continue

            regime = regimes[
                i % regime_count
            ]

            regime_state = (
                regime.get_state()
            )

            node.economic_intensity = (
                regime_state["abundance"]
            )

            node.economic_stress = (
                regime_state[
                    "economic_stress"
                ]
            )

            node.economic_collapse_risk = (
                regime_state[
                    "collapse_risk"
                ]
            )

    # =========================================================
    # MAIN UPDATE
    # =========================================================

    def update(
        self,
        graph=None,
    ):
        """
        Execute one economic ecology cycle.
        """

        self.economic_ecology.update()
        self.update_aggregate_state()
        self.project_on_graph(graph)

        self.debug_print()

    # =========================================================
    # DEBUG OUTPUT
    # =========================================================

    def debug_print(self):
        """
        Backward-compatible textual summary.

        This method is explicitly called by the runtime.
        """

        print(
            "[ECONOMIC_ECOLOGY]",
            f"intensity="
            f"{self.economic_intensity:.2f}",
            f"stress="
            f"{self.economic_stress:.2f}",
            f"crises="
            f"{self.crisis_count}",
        )

    # =========================================================
    # STATE EXPORT
    # =========================================================

    def get_state(self):
        """
        Export aggregate economic state.
        """

        return {
            "economic_intensity":
                self.economic_intensity,
            "economic_stress":
                self.economic_stress,
            "crisis_count":
                self.crisis_count,
            "last_crisis":
                self.last_crisis,
            "distributed_state":
                self.economic_ecology.get_state(),
        }
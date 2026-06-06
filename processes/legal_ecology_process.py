# processes/legal_ecology_process.py

from agents.agent import PersistentAgent


class LegalEcologyProcess:
    """
    Distributed legal ecology process.

    This process projects the dynamics of a distributed
    legal ecology onto the cognitive graph nodes.

    No central legal authority.
    No universal law.
    Only local normative regimes interacting through
    partial compatibilities and conflicts.
    """

    def __init__(
        self,
        graph,
    ):
        self.graph = graph

        # A single distributed agent orchestrates
        # the legal ecology.
        self.agent = PersistentAgent(
            name="legal_ecology_agent"
        )

    async def run(self):
        """
        Execute one legal ecology cycle and project
        local legal indicators onto graph nodes.
        """

        # Update the agent and its distributed
        # legal ecology.
        self.agent.evolve()

        # Aggregate legal state
        legal_state = (
            self.agent.legal_ecology.get_state()
        )

        # Detailed regime states
        regime_states = (
            self.agent.legal_ecology.get_regime_states()
        )

        if not regime_states:
            return

        regime_count = len(regime_states)

        # Project onto graph nodes
        for index, node in enumerate(
            self.graph.nodes.values()
        ):
            regime_state = regime_states[
                index % regime_count
            ]

            # =================================================
            # LOCAL LEGAL PROJECTION
            # =================================================

            node.normative_legitimacy = (
                regime_state[
                    "normative_legitimacy"
                ]
            )

            node.jurisprudence_density = (
                regime_state[
                    "jurisprudence_density"
                ]
            )

            node.legal_stability = (
                regime_state[
                    "stability"
                ]
            )

            node.legal_conflict = (
                regime_state[
                    "internal_conflict"
                ]
            )

            node.normative_compatibility = (
                regime_state[
                    "compatibility_index"
                ]
            )

            node.legal_status = (
                regime_state[
                    "status"
                ]
            )

            node.local_norm_count = (
                regime_state[
                    "norm_count"
                ]
            )

            node.legal_collapse_risk = (
                regime_state[
                    "collapse_risk"
                ]
            )

            # =================================================
            # GLOBAL AGGREGATE INDICATORS
            # =================================================

            node.active_regimes = (
                legal_state[
                    "active_regimes"
                ]
            )

            node.collapsed_regimes = (
                legal_state[
                    "collapsed_regimes"
                ]
            )

            node.average_legal_legitimacy = (
                legal_state[
                    "average_legitimacy"
                ]
            )

            node.average_legal_stability = (
                legal_state[
                    "average_stability"
                ]
            )

            node.average_jurisprudence = (
                legal_state[
                    "average_jurisprudence"
                ]
            )

            node.total_legal_collapses = (
                legal_state[
                    "total_collapses"
                ]
            )

            node.total_legal_reformations = (
                legal_state[
                    "total_reformations"
                ]
            )
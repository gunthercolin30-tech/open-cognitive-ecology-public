PRIMITIVE = "semantic_collapse"
DESCRIPTION = "Semantic collapse."
DEPENDENCIES = []

import random


class SemanticCollapseMixin:

    # =========================================================
    # SEMANTIC COLLAPSES
    # =========================================================

    def _trigger_semantic_collapses(
        self,
        agents,
    ):

        for agent in agents:

            collapse_pressure = (
                agent.symbolic_drift
                + agent.semiotic_instability
                + agent.cultural_fragmentation
            )

            if (
                collapse_pressure
                < self.collapse_threshold
            ):
                continue

            collapse_probability = (
                collapse_pressure
                * 0.005
            )

            if (
                random.random()
                > collapse_probability
            ):
                continue

            collapse = {
                "cycle": (
                    agent.state["cycle"]
                ),
                "agent": (
                    agent.state["name"]
                ),
                "signature": (
                    agent.civilizational_signature
                ),
                "pressure": (
                    collapse_pressure
                ),
            }

            self.semantic_collapses.append(
                collapse
            )

            self._apply_semantic_collapse(
                agent
            )

    # =========================================================
    # COLLAPSE EFFECTS
    # =========================================================

    def _apply_semantic_collapse(
        self,
        agent,
    ):

        lexicon = self.local_lexicons.get(
            agent.state["name"],
            {},
        )

        retained_symbols = {}

        for symbol, value in lexicon.items():

            if self._is_structural_primitive(
                symbol
            ):
                retain_probability = 0.95
            else:
                retain_probability = 0.2

            if (
                random.random()
                < retain_probability
            ):
                retained_symbols[symbol] = (
                    value
                )

        if (
            not retained_symbols
            and any(
                self._is_structural_primitive(
                    symbol
                )
                for symbol in lexicon
            )
        ):
            primitive_symbols = [
                symbol
                for symbol in lexicon
                if self._is_structural_primitive(
                    symbol
                )
            ]

            if primitive_symbols:
                symbol = random.choice(
                    primitive_symbols
                )
                retained_symbols[symbol] = (
                    lexicon[symbol]
                )

        self.local_lexicons[
            agent.state["name"]
        ] = retained_symbols

        agent.symbolic_patterns.clear()

        for symbol in retained_symbols:

            agent.symbolic_patterns[
                symbol
            ] = retained_symbols[
                symbol
            ]["weight"]

        agent.local_mythologies.clear()

        agent.symbolic_drift += (
            random.uniform(
                0.1,
                0.3,
            )
        )

        agent.semiotic_instability += (
            random.uniform(
                0.1,
                0.4,
            )
        )

        agent.cultural_fragmentation += (
            random.uniform(
                0.05,
                0.2,
            )
        )
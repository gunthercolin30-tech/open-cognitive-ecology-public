PRIMITIVE = "ecological_decay"
DESCRIPTION = "Ecological decay."
DEPENDENCIES = []

import random


class EcologicalDecayMixin:

    # =========================================================
    # ECOLOGICAL DECAY
    # =========================================================

    def _decay_symbolic_ecology(
        self,
    ):

        self.semantic_collapses = [
            collapse
            for collapse
            in self.semantic_collapses
            if random.random()
            < self.semantic_decay
        ]

        if (
            len(self.semantic_collapses)
            > 200
        ):
            self.semantic_collapses = (
                self.semantic_collapses[-200:]
            )

        for lexicon in self.local_lexicons.values():

            removable = []

            for symbol in lexicon:

                if self._is_structural_primitive(
                    symbol
                ):
                    decay_probability = (
                        1.0
                        - self.non_closure_floor
                    )
                else:
                    decay_probability = (
                        self.semantic_decay
                    )

                if (
                    random.random()
                    > decay_probability
                ):
                    removable.append(
                        symbol
                    )

            for symbol in removable:
                del lexicon[symbol]
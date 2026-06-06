# language/distributed_language_ecology.py

import random

from language.local_language_regime import (
    LocalLanguageRegime,
)


class DistributedLanguageEcology:
    """
    Distributed ecology of local language regimes.

    Models:
    - coexistence of multiple local languages
    - imperfect translation
    - semantic divergence
    - fragmentation
    - language extinction
    - emergence of new regimes

    Fundamental principles:
    - no universal language
    - no perfect translation
    - only local historically unstable regimes
    """

    def __init__(
        self,
        language_count=4,
    ):
        # =====================================================
        # LOCAL LANGUAGE REGIMES
        # =====================================================

        self.language_regimes = []

        for i in range(language_count):
            regime = LocalLanguageRegime(
                name=f"language_{i}",
                initial_terms=random.randint(
                    20,
                    80,
                ),
            )

            self.language_regimes.append(
                regime
            )

        self.cycle = 0

    # =========================================================
    # DYNAMICS
    # =========================================================

    def step(self):
        """
        Update all local language regimes.
        """

        self.cycle += 1

        for regime in self.language_regimes:
            regime.update()

    # =========================================================
    # STATE AGGREGATION
    # =========================================================

    def get_alive_count(self):
        """
        Number of linguistically viable regimes.
        """

        return sum(
            1
            for regime in self.language_regimes
            if regime.vitality > 0.0
        )

    def get_average_vitality(self):
        """
        Mean vitality across regimes.
        """

        if not self.language_regimes:
            return 0.0

        return sum(
            regime.vitality
            for regime in self.language_regimes
        ) / len(self.language_regimes)

    def get_average_fragmentation(self):
        """
        Mean linguistic fragmentation.
        """

        if not self.language_regimes:
            return 0.0

        return sum(
            regime.fragmentation
            for regime in self.language_regimes
        ) / len(self.language_regimes)

    def get_average_translation_noise(self):
        """
        Mean translation imperfection.
        """

        if not self.language_regimes:
            return 0.0

        return sum(
            regime.translation_noise
            for regime in self.language_regimes
        ) / len(self.language_regimes)

    def get_average_lexicon_size(self):
        """
        Mean number of terms.
        """

        if not self.language_regimes:
            return 0.0

        return sum(
            len(regime.lexicon)
            for regime in self.language_regimes
        ) / len(self.language_regimes)

    # =========================================================
    # IMPERFECT TRANSLATION
    # =========================================================

    def sample_translation_similarity(self):
        """
        Sample similarity between two random regimes.

        Returns a value in [0, 1].
        """

        if len(self.language_regimes) < 2:
            return 0.0

        source, target = random.sample(
            self.language_regimes,
            2,
        )

        if not source.lexicon:
            return 0.0

        term = random.choice(
            list(source.lexicon.keys())
        )

        return source.translate_term(
            term,
            target,
        )

    # =========================================================
    # SUMMARY
    # =========================================================

    def get_state(self):
        """
        Aggregate distributed linguistic state.
        """

        return {
            "language_alive_count": (
                self.get_alive_count()
            ),
            "language_vitality": (
                self.get_average_vitality()
            ),
            "language_fragmentation": (
                self.get_average_fragmentation()
            ),
            "language_translation_noise": (
                self.get_average_translation_noise()
            ),
            "language_lexicon_size": (
                self.get_average_lexicon_size()
            ),
            "language_translation_similarity": (
                self.sample_translation_similarity()
            ),
        }
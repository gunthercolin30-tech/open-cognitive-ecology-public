# language/local_language_regime.py

import random
import math


class LocalLanguageRegime:
    """
    Local linguistic regime.

    Models:
    - local lexicons
    - semantic drift
    - ambiguity
    - imperfect translation
    - linguistic fragmentation
    - language disappearance

    Fundamental principles:
    - no universal language
    - no perfect translation
    - only local historically contingent linguistic regimes
    - unstable and dissipative symbolic structures
    """

    def __init__(
        self,
        name,
        initial_terms=50,
    ):
        self.name = name

        # =====================================================
        # LOCAL LEXICON
        # =====================================================

        self.lexicon = {}

        for i in range(initial_terms):
            term = f"term_{i}"

            self.lexicon[term] = {
                "meaning": random.uniform(0.0, 1.0),
                "ambiguity": random.uniform(0.0, 0.3),
                "stability": random.uniform(0.5, 1.0),
                "usage": random.uniform(0.3, 1.0),
                "age": 0.0,
            }

        # =====================================================
        # REGIME VARIABLES
        # =====================================================

        self.semantic_drift = random.uniform(0.0, 0.05)
        self.fragmentation = random.uniform(0.0, 0.2)
        self.translation_noise = random.uniform(0.05, 0.25)
        self.extinction_risk = random.uniform(0.0, 0.1)

        self.vitality = 1.0
        self.coherence = 1.0
        self.speaker_population = random.uniform(0.5, 1.5)

        self.cycle = 0

    # =========================================================
    # TERM DYNAMICS
    # =========================================================

    def update_terms(self):
        """
        Local semantic evolution.
        """

        for data in self.lexicon.values():
            drift = random.uniform(
                -self.semantic_drift,
                self.semantic_drift,
            )

            data["meaning"] += drift
            data["meaning"] = max(
                0.0,
                min(1.0, data["meaning"])
            )

            data["ambiguity"] += random.uniform(
                -0.01,
                0.02 + self.fragmentation * 0.02
            )
            data["ambiguity"] = max(
                0.0,
                min(1.0, data["ambiguity"])
            )

            data["usage"] += random.uniform(
                -0.03,
                0.02
            )
            data["usage"] = max(
                0.0,
                min(1.0, data["usage"])
            )

            data["stability"] -= abs(drift) * 0.5
            data["stability"] += random.uniform(
                -0.01,
                0.01
            )
            data["stability"] = max(
                0.0,
                min(1.0, data["stability"])
            )

            data["age"] += 1.0

    # =========================================================
    # LEXICAL TURNOVER
    # =========================================================

    def lexical_turnover(self):
        """
        Terms can disappear and new terms can emerge.
        """

        to_remove = []

        for term, data in self.lexicon.items():
            fragility = (
                (1.0 - data["usage"]) * 0.4
                + (1.0 - data["stability"]) * 0.4
                + self.fragmentation * 0.2
            )

            if random.random() < fragility * 0.05:
                to_remove.append(term)

        for term in to_remove:
            del self.lexicon[term]

        births = random.randint(0, 2)

        for _ in range(births):
            index = self.cycle * 1000 + random.randint(0, 999)
            term = f"term_{index}"

            self.lexicon[term] = {
                "meaning": random.uniform(0.0, 1.0),
                "ambiguity": random.uniform(0.1, 0.5),
                "stability": random.uniform(0.2, 0.7),
                "usage": random.uniform(0.1, 0.5),
                "age": 0.0,
            }

    # =========================================================
    # GLOBAL REGIME DYNAMICS
    # =========================================================

    def update_regime(self):
        """
        Linguistic coherence is always partial and unstable.
        """

        if self.lexicon:
            avg_ambiguity = sum(
                data["ambiguity"]
                for data in self.lexicon.values()
            ) / len(self.lexicon)

            avg_stability = sum(
                data["stability"]
                for data in self.lexicon.values()
            ) / len(self.lexicon)

            avg_usage = sum(
                data["usage"]
                for data in self.lexicon.values()
            ) / len(self.lexicon)
        else:
            avg_ambiguity = 1.0
            avg_stability = 0.0
            avg_usage = 0.0

        self.coherence = max(
            0.0,
            min(
                1.0,
                avg_stability
                * (1.0 - avg_ambiguity)
            )
        )

        self.semantic_drift += random.uniform(
            -0.005,
            0.005
        )
        self.semantic_drift = max(
            0.0,
            min(0.2, self.semantic_drift)
        )

        self.fragmentation += random.uniform(
            -0.01,
            0.02
        )
        self.fragmentation = max(
            0.0,
            min(1.0, self.fragmentation)
        )

        self.translation_noise += random.uniform(
            -0.01,
            0.01
        )
        self.translation_noise = max(
            0.0,
            min(1.0, self.translation_noise)
        )

        self.extinction_risk = max(
            0.0,
            min(
                1.0,
                0.5 * self.fragmentation
                + 0.3 * (1.0 - self.coherence)
                + 0.2 * (1.0 - avg_usage)
            )
        )

        self.vitality = max(
            0.0,
            min(
                1.0,
                0.6 * avg_usage
                + 0.4 * self.speaker_population / 1.5
            )
        )

    # =========================================================
    # SPEAKER POPULATION
    # =========================================================

    def update_population(self):
        """
        Speaker population fluctuates and may collapse.
        """

        growth = random.uniform(
            -0.05,
            0.03
        )

        decline = self.extinction_risk * 0.08

        self.speaker_population += growth - decline
        self.speaker_population = max(
            0.0,
            self.speaker_population
        )

    # =========================================================
    # LANGUAGE EXTINCTION
    # =========================================================

    def apply_extinction(self):
        """
        Local language may disappear entirely.
        """

        if (
            self.speaker_population < 0.05
            or self.vitality < 0.05
            or len(self.lexicon) == 0
        ):
            self.lexicon = {}
            self.vitality = 0.0
            self.coherence = 0.0
            self.fragmentation = 1.0

    # =========================================================
    # IMPERFECT TRANSLATION
    # =========================================================

    def translate_term(
        self,
        term,
        target_regime,
    ):
        """
        Imperfect translation between incompatible local regimes.

        Returns:
            similarity in [0, 1]
        """

        if term not in self.lexicon:
            return 0.0

        if not target_regime.lexicon:
            return 0.0

        source_meaning = self.lexicon[term]["meaning"]

        best_similarity = 0.0

        for data in target_regime.lexicon.values():
            distance = abs(
                source_meaning - data["meaning"]
            )

            similarity = max(
                0.0,
                1.0 - distance
            )

            noise = random.uniform(
                0.0,
                self.translation_noise
                + target_regime.translation_noise
            )

            similarity = max(
                0.0,
                similarity - noise
            )

            if similarity > best_similarity:
                best_similarity = similarity

        return best_similarity

    # =========================================================
    # MAIN UPDATE
    # =========================================================

    def update(self):
        """
        Full linguistic evolution cycle.
        """

        self.cycle += 1

        if self.vitality <= 0.0:
            return

        self.update_terms()
        self.lexical_turnover()
        self.update_regime()
        self.update_population()
        self.apply_extinction()

    # =========================================================
    # SUMMARY
    # =========================================================

    def get_summary(self):
        """
        Compact state summary.
        """

        return {
            "name": self.name,
            "terms": len(self.lexicon),
            "vitality": self.vitality,
            "coherence": self.coherence,
            "semantic_drift": self.semantic_drift,
            "fragmentation": self.fragmentation,
            "translation_noise": self.translation_noise,
            "extinction_risk": self.extinction_risk,
            "speaker_population": self.speaker_population,
        }
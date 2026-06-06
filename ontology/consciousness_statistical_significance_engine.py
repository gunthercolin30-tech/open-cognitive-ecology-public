
"""
Consciousness Statistical Significance Engine

Provides basic statistical inference utilities using only the Python standard library.
"""

from statistics import mean, stdev
from math import sqrt


class ConsciousnessStatisticalSignificanceEngine:
    PRIMITIVE = "CONSCIOUSNESS_STATISTICAL_SIGNIFICANCE_ENGINE"

    def __init__(self):
        self.samples = []

    def record(self, value):
        try:
            self.samples.append(float(value))
        except Exception:
            pass

    def _confidence_interval_95(self):
        n = len(self.samples)
        if n < 2:
            return (None, None)
        m = mean(self.samples)
        s = stdev(self.samples)
        margin = 1.96 * s / sqrt(n)
        return (round(m - margin, 6), round(m + margin, 6))

    def _effect_size_vs_reference(self, reference=0.5):
        n = len(self.samples)
        if n < 2:
            return None
        s = stdev(self.samples)
        if s == 0:
            return None
        return round((mean(self.samples) - reference) / s, 6)

    def step(self):
        n = len(self.samples)
        if n == 0:
            return {
                "primitive": self.PRIMITIVE,
                "sample_count": 0,
                "mean_score": None,
                "confidence_interval_95": (None, None),
                "effect_size": None,
                "statistically_supported": False,
                "publication_ready": False,
            }

        ci = self._confidence_interval_95()
        effect = self._effect_size_vs_reference()

        statistically_supported = (
            n >= 5 and
            ci[0] is not None and
            ci[0] > 0.5
        )

        return {
            "primitive": self.PRIMITIVE,
            "sample_count": n,
            "mean_score": round(mean(self.samples), 6),
            "confidence_interval_95": ci,
            "effect_size": effect,
            "statistically_supported": statistically_supported,
            "publication_ready": statistically_supported,
        }

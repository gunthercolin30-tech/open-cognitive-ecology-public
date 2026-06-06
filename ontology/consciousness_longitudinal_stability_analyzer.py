
"""
Consciousness Longitudinal Stability Analyzer

Provides longitudinal statistical analysis of functional consciousness metrics.
"""

from statistics import mean, pvariance


class ConsciousnessLongitudinalStabilityAnalyzer:
    PRIMITIVE = "CONSCIOUSNESS_LONGITUDINAL_STABILITY_ANALYZER"

    def __init__(self):
        self.samples = []

    def record(self, value):
        try:
            self.samples.append(float(value))
        except Exception:
            pass

    def _trend(self, values):
        if len(values) < 5:
            return "insufficient_data"
        midpoint = len(values) // 2
        first = mean(values[:midpoint])
        second = mean(values[midpoint:])
        delta = second - first
        if abs(delta) < 0.002:
            return "stable"
        if delta > 0:
            return "improving"
        return "degrading"

    def step(self):
        n = len(self.samples)
        if n == 0:
            return {
                "primitive": self.PRIMITIVE,
                "sample_count": 0,
                "mean_score": 0.0,
                "variance": 0.0,
                "stability_index": 1.0,
                "trend": "insufficient_data",
                "publication_ready": False,
            }

        avg = mean(self.samples)
        var = pvariance(self.samples) if n > 1 else 0.0
        stability_index = max(0.0, min(1.0, 1.0 - min(var * 100.0, 1.0)))

        return {
            "primitive": self.PRIMITIVE,
            "sample_count": n,
            "mean_score": round(avg, 6),
            "variance": round(var, 10),
            "stability_index": round(stability_index, 6),
            "trend": self._trend(self.samples),
            "publication_ready": n >= 5 and stability_index >= 0.95,
        }

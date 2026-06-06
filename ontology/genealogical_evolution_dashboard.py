"""Genealogical Evolution Dashboard"""

PRIMITIVE = "genealogical_evolution_dashboard"

DEPENDENCIES = [
    "evolution_sandbox",
    "persistent_multi_scale_memory",
    "self_parameter_optimization",
    "monitoring",
    "report_generation",
]


class GenealogicalEvolutionDashboard:
    def __init__(self):
        self.lineages = []

    def register_lineage(self, lineage_record):
        self.lineages.append(dict(lineage_record))

    def lineage_count(self):
        return len(self.lineages)

    def best_lineage(self, score_key="score"):
        if not self.lineages:
            return None
        return max(
            self.lineages,
            key=lambda item: item.get(score_key, float("-inf"))
        )

    def diagnostics(self):
        best = self.best_lineage()
        return {
            "primitive": PRIMITIVE,
            "lineage_count": self.lineage_count(),
            "has_best_lineage": best is not None,
        }

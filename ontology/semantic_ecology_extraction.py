
from collections import Counter

class SemanticEcologyExtraction:

    def step(self, symbolic_ecology=None):

        if symbolic_ecology is None:
            return {
                "semantic_drift": 0.0,
                "semantic_diversity": 0.0,
                "fragmentation_pressure": 0.0,
                "convergence_pressure": 1.0,
                "inter_lineage_exchange_rate": 0.0,
            }

        fluxes = getattr(symbolic_ecology, "semantic_fluxes", [])

        flux_count = len(fluxes)

        regions = {
            f.get("region")
            for f in fluxes
            if isinstance(f, dict)
        }

        agents = [
            f.get("agent")
            for f in fluxes
            if isinstance(f, dict)
        ]

        semantic_diversity = min(
            1.0,
            len(regions) / 20.0,
        )

        semantic_drift = min(
            1.0,
            flux_count / 500.0,
        )

        fragmentation_pressure = min(
            1.0,
            semantic_diversity * semantic_drift,
        )

        convergence_pressure = max(
            0.0,
            1.0 - semantic_diversity,
        )

        exchange_rate = min(
            1.0,
            len(set(agents)) / max(1, flux_count),
        )

        return {
            "semantic_drift": round(semantic_drift, 4),
            "semantic_diversity": round(semantic_diversity, 4),
            "fragmentation_pressure": round(fragmentation_pressure, 4),
            "convergence_pressure": round(convergence_pressure, 4),
            "inter_lineage_exchange_rate": round(exchange_rate, 4),
        }


from pathlib import Path
import json

ROOT = Path.home() / "open-cognitive-ecology"
POPULATION_ROOT = ROOT / "runtime_population"

class PopulationEcologicalExtraction:

    def step(self):
        lineages = set()
        individuals = 0
        divergences = []

        if POPULATION_ROOT.exists():
            for lineage_dir in POPULATION_ROOT.iterdir():
                if not lineage_dir.is_dir():
                    continue
                lineages.add(lineage_dir.name)

                for individual_dir in lineage_dir.iterdir():
                    if not individual_dir.is_dir():
                        continue

                    individuals += 1

                    memory_file = individual_dir / "local_memory.json"
                    if memory_file.exists():
                        try:
                            data = json.loads(memory_file.read_text(encoding="utf-8"))
                            divergences.append(
                                float(data.get("historical_divergence", 0.0))
                            )
                        except Exception:
                            pass

        lineage_count = len(lineages)
        historical_divergence_mean = (
            sum(divergences) / len(divergences)
            if divergences else 0.0
        )

        return {
            "population_size": individuals,
            "lineage_count": lineage_count,
            "lineage_diversity": min(1.0, lineage_count / 10.0),
            "historical_divergence_mean": round(
                historical_divergence_mean, 4
            ),
        }

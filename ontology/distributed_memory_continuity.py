from statistics import mean
from pathlib import Path
import json
import math
import hashlib


class DistributedMemoryContinuity:

    def __init__(self):
        self.history = []

    def step(self):

        root = Path.home() / "open-cognitive-ecology"
        archive_root = root / "civilizational_memory_archive"

        json_files = []
        if archive_root.exists():
            json_files = list(archive_root.rglob("*.json"))

        total_files = len(json_files)

        readable_files = 0
        cma_files = 0
        hashes = []

        for path in json_files:

            try:
                content = path.read_text(encoding="utf-8")
                json.loads(content)

                readable_files += 1

                digest = hashlib.sha256(
                    content.encode("utf-8")
                ).hexdigest()

                hashes.append(digest)

            except Exception:
                pass

            if "CMA-" in path.name:
                cma_files += 1

        distributed_memory_index = (
            readable_files / total_files
            if total_files > 0 else 0.0
        )

        genealogical_continuity = (
            1.0 - math.exp(-cma_files / 40.0)
            if total_files > 0 else 0.0
        )

        historical_depth = (
            min(
                1.0,
                math.log(total_files + 1) / math.log(1000.0)
            )
            if total_files > 0 else 0.0
        )

        unique_hashes = len(set(hashes))

        archive_diversity = (
            unique_hashes / len(hashes)
            if len(hashes) > 0 else 0.0
        )

        duplicate_ratio = max(
            0.0,
            1.0 - archive_diversity
        )

        redundancy_penalty = (
            1.0 - math.exp(-250.0 * duplicate_ratio)
        )

        archive_diversity_adjusted = max(
            0.0,
            1.0 - redundancy_penalty
        )

        survivability = archive_diversity_adjusted

        continuity_index = round(
            mean(
                [
                    distributed_memory_index,
                    genealogical_continuity,
                    historical_depth,
                    archive_diversity_adjusted,
                    survivability,
                ]
            ),
            4,
        )

        result = {
            "success": True,
            "total_files": total_files,
            "unique_hashes": unique_hashes,
            "duplicate_ratio": round(duplicate_ratio, 6),
            "distributed_memory_index":
                round(distributed_memory_index, 4),
            "genealogical_continuity":
                round(genealogical_continuity, 4),
            "historical_depth":
                round(historical_depth, 4),
            "archive_diversity":
                round(archive_diversity, 4),
            "archive_diversity_adjusted":
                round(archive_diversity_adjusted, 4),
            "survivability":
                round(survivability, 4),
            "distributed_memory_continuity_index":
                continuity_index,
            "continuity_established":
                continuity_index >= 0.75,
        }

        self.history.append(result)

        return result


ENGINE = DistributedMemoryContinuity()
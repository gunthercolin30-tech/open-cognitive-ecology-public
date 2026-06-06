
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class ScientificSelfRevisionController:
    primitive = "SCIENTIFIC_SELF_REVISION_CONTROLLER"

    def __init__(self, archive_dir=None):
        if archive_dir is None:
            archive_dir = (
                Path.home()
                / "open-cognitive-ecology"
                / "runtime_experiments"
                / "scientific_self_revision"
            )
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def step(self, paradigm_result):
        if (
            not isinstance(paradigm_result, dict)
            or not paradigm_result.get("publication_ready")
        ):
            return {
                "primitive": self.primitive,
                "publication_ready": False,
                "reason": "invalid_paradigm_result",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        shift_probability = float(
            paradigm_result.get("paradigm_shift_probability", 0.0)
        )
        instability = float(
            paradigm_result.get("conceptual_instability_index", 0.0)
        )

        revision_priority = min(
            1.0,
            0.6 * shift_probability + 0.4 * instability,
        )

        if revision_priority < 0.05:
            action = "maintain_current_theory"
            revision_required = False
        elif revision_priority < 0.20:
            action = "monitor_and_collect_more_evidence"
            revision_required = False
        elif revision_priority < 0.50:
            action = "prepare_targeted_theory_revision"
            revision_required = True
        else:
            action = "initiate_major_theory_reconstruction"
            revision_required = True

        result = {
            "primitive": self.primitive,
            "revision_priority_index": round(revision_priority, 6),
            "revision_required": revision_required,
            "recommended_action": action,
            "self_revision_ready": True,
            "publication_ready": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self._archive(result)
        return result

    def _archive(self, result):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = (
            self.archive_dir
            / f"scientific_self_revision_{timestamp}.json"
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    from pprint import pprint

    sample = {
        "paradigm_shift_probability": 0.003701,
        "conceptual_instability_index": 0.003326,
        "publication_ready": True,
    }

    pprint(ScientificSelfRevisionController().step(sample))

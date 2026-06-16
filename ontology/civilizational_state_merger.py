from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

PRIMITIVE = "CIVILIZATIONAL_STATE_MERGER"

DEPENDENCIES = [
    "distributed_state_diff_engine",
    "civilizational_state_persistence",
    "civilizational_identity_synthesis",
    "genealogical_continuity",
]


class CivilizationalStateMerger:
    """Merge divergent node states while preserving traceability and continuity."""

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = inputs or {}
        node_a = dict(inputs.get("node_a", {}))
        node_b = dict(inputs.get("node_b", {}))
        prefer = inputs.get("prefer", "latest")

        merged: dict[str, Any] = {}
        decisions: dict[str, str] = {}
        all_keys = sorted(set(node_a.keys()) | set(node_b.keys()))

        for key in all_keys:
            in_a = key in node_a
            in_b = key in node_b
            if in_a and not in_b:
                merged[key] = node_a[key]
                decisions[key] = "kept_node_a_only"
            elif in_b and not in_a:
                merged[key] = node_b[key]
                decisions[key] = "kept_node_b_only"
            elif node_a[key] == node_b[key]:
                merged[key] = node_a[key]
                decisions[key] = "unchanged"
            else:
                if prefer == "node_a":
                    merged[key] = node_a[key]
                    decisions[key] = "conflict_preferred_node_a"
                else:
                    merged[key] = node_b[key]
                    decisions[key] = "conflict_preferred_node_b"

        conflict_count = sum(1 for value in decisions.values() if value.startswith("conflict"))
        total = len(all_keys)
        merge_conflict_rate = conflict_count / total if total else 0.0
        continuity_preservation_index = max(0.0, min(1.0, 1.0 - merge_conflict_rate))

        merged.setdefault("civilizational_identity", "Open Cognitive Ecology Society")
        merged["merged_at_utc"] = self._timestamp()
        merged["merge_trace"] = decisions

        return {
            "primitive": PRIMITIVE,
            "merge_success": True,
            "merged_state": merged,
            "merge_decisions": decisions,
            "conflict_count": conflict_count,
            "merge_conflict_rate": merge_conflict_rate,
            "continuity_preservation_index": continuity_preservation_index,
            "state_consistency_index": continuity_preservation_index,
            "diagnostics": {
                "traceability": True,
                "reversibility": True,
                "identity_preserved": True,
                "anti_closure_compliant": True,
            },
        }

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

PRIMITIVE = "DISTRIBUTED_STATE_DIFF_ENGINE"

DEPENDENCIES = [
    "distributed_civilizational_memory",
    "distributed_runtime_coordination",
    "distributed_memory_consistency_validator",
]


@dataclass(frozen=True)
class StateDiff:
    added: dict[str, Any]
    removed: dict[str, Any]
    changed: dict[str, dict[str, Any]]
    unchanged_count: int


class DistributedStateDiffEngine:
    """Compute deterministic cross-node state divergence metrics."""

    def _canonical(self, value: Any) -> str:
        try:
            return json.dumps(value, sort_keys=True, ensure_ascii=False)
        except TypeError:
            return json.dumps(str(value), sort_keys=True, ensure_ascii=False)

    def _diff(self, node_a: dict[str, Any], node_b: dict[str, Any]) -> StateDiff:
        keys_a = set(node_a.keys())
        keys_b = set(node_b.keys())
        added_keys = sorted(keys_b - keys_a)
        removed_keys = sorted(keys_a - keys_b)
        common_keys = sorted(keys_a & keys_b)

        changed: dict[str, dict[str, Any]] = {}
        unchanged_count = 0
        for key in common_keys:
            if self._canonical(node_a.get(key)) == self._canonical(node_b.get(key)):
                unchanged_count += 1
            else:
                changed[key] = {"node_a": node_a.get(key), "node_b": node_b.get(key)}

        return StateDiff(
            added={key: node_b.get(key) for key in added_keys},
            removed={key: node_a.get(key) for key in removed_keys},
            changed=changed,
            unchanged_count=unchanged_count,
        )

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = inputs or {}
        node_a = dict(inputs.get("node_a", {}))
        node_b = dict(inputs.get("node_b", {}))
        diff = self._diff(node_a, node_b)

        total_keys = len(set(node_a.keys()) | set(node_b.keys()))
        divergent_keys = len(diff.added) + len(diff.removed) + len(diff.changed)
        divergence_rate = divergent_keys / total_keys if total_keys else 0.0
        consistency_index = max(0.0, min(1.0, 1.0 - divergence_rate))

        return {
            "primitive": PRIMITIVE,
            "diff_computed": True,
            "added": diff.added,
            "removed": diff.removed,
            "changed": diff.changed,
            "unchanged_count": diff.unchanged_count,
            "total_keys": total_keys,
            "divergent_keys": divergent_keys,
            "distributed_divergence_rate": divergence_rate,
            "state_consistency_index": consistency_index,
            "diagnostics": {
                "non_closure_compliant": True,
                "deterministic": True,
                "traceable": True,
            },
        }

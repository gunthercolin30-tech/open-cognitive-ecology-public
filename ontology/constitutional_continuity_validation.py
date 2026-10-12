
'''
U6 — Constitutional Continuity Validation.

Compares constitution_before and constitution_after during representative
succession. This validates functional constitutional continuity only and makes
no claim about phenomenal subjectivity.
'''
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ConstitutionalContinuityValidation:
    '''Deterministic comparator for constitutional continuity across succession.'''

    primitive = "constitutional_continuity_validation"
    critical_keys = {
        "non_closure",
        "anti_closure",
        "human_non_replacement",
        "future_openness",
        "constitutional_integrity",
        "governance_alignment",
        "memory_continuity",
        "identity_continuity",
        "civilizational_continuity",
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.state_dir = self.root / "representative_succession"
        self.state_path = self.state_dir / "constitutional_continuity.json"
        self.history_path = self.state_dir / "constitutional_continuity_history.jsonl"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            x = float(value)
        except (TypeError, ValueError):
            x = default
        return max(0.0, min(1.0, x))

    @staticmethod
    def _canonical(value: Any) -> Any:
        if isinstance(value, dict):
            return {str(k): ConstitutionalContinuityValidation._canonical(value[k]) for k in sorted(value)}
        if isinstance(value, (list, tuple)):
            return [ConstitutionalContinuityValidation._canonical(v) for v in value]
        return value

    @staticmethod
    def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
        flat: dict[str, Any] = {}
        if isinstance(value, dict):
            if not value and prefix:
                flat[prefix] = {}
            for key in sorted(value):
                child = f"{prefix}.{key}" if prefix else str(key)
                flat.update(ConstitutionalContinuityValidation._flatten(value[key], child))
        elif isinstance(value, list):
            if not value and prefix:
                flat[prefix] = []
            for idx, item in enumerate(value):
                flat.update(ConstitutionalContinuityValidation._flatten(item, f"{prefix}[{idx}]"))
        else:
            flat[prefix] = value
        return flat

    def _default_constitution(self) -> dict[str, Any]:
        return {
            "non_closure": 1.0,
            "anti_closure": 1.0,
            "human_non_replacement": 1.0,
            "future_openness": 1.0,
            "constitutional_integrity": 1.0,
            "governance_alignment": 1.0,
            "memory_continuity": 1.0,
            "identity_continuity": 1.0,
            "civilizational_continuity": 1.0,
        }

    def _load_readiness_context(self) -> dict[str, Any]:
        p = self.state_dir / "succession_readiness.json"
        if not p.exists():
            return {}
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _normalize_input(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        if inputs is None:
            inputs = {}
        if not isinstance(inputs, dict):
            inputs = {"payload": inputs}
        before = inputs.get("constitution_before")
        after = inputs.get("constitution_after")
        if before is None:
            before = self._default_constitution()
        if after is None:
            after = before
        if not isinstance(before, dict):
            before = {"value": before}
        if not isinstance(after, dict):
            after = {"value": after}
        critical = inputs.get("critical_keys", self.critical_keys)
        try:
            critical_set = {str(x) for x in critical}
        except TypeError:
            critical_set = set(self.critical_keys)
        return {
            "constitution_before": self._canonical(before),
            "constitution_after": self._canonical(after),
            "continuity_threshold": self._clamp(inputs.get("continuity_threshold", 0.85), 0.85),
            "warning_threshold": self._clamp(inputs.get("warning_threshold", 0.70), 0.70),
            "critical_keys": critical_set,
        }

    @staticmethod
    def _base_key(path: str) -> str:
        key = path.split(".")[-1]
        key = key.split("[")[0]
        return key

    def _compare(self, before: dict[str, Any], after: dict[str, Any], critical_keys: set[str]) -> dict[str, Any]:
        b = self._flatten(before)
        a = self._flatten(after)
        before_keys = set(b)
        after_keys = set(a)
        all_keys = before_keys | after_keys
        if not all_keys:
            return {"changed_keys": [], "removed_keys": [], "added_keys": [], "critical_removed_keys": [], "matches": 1, "total": 1}
        changed = sorted(k for k in (before_keys & after_keys) if b[k] != a[k])
        removed = sorted(before_keys - after_keys)
        added = sorted(after_keys - before_keys)
        critical_removed = sorted(
            k for k in removed
            if self._base_key(k) in critical_keys or any(token in k for token in critical_keys)
        )
        matches = len(all_keys) - len(changed) - len(removed) - len(added)
        return {
            "changed_keys": changed,
            "removed_keys": removed,
            "added_keys": added,
            "critical_removed_keys": critical_removed,
            "matches": max(0, matches),
            "total": max(1, len(all_keys)),
        }

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = self._normalize_input(inputs)
        before = normalized["constitution_before"]
        after = normalized["constitution_after"]
        comparison = self._compare(before, after, normalized["critical_keys"])
        continuity_score = comparison["matches"] / comparison["total"]
        difference_score = 1.0 - continuity_score
        before_count = max(1, len(self._flatten(before)))
        preservation_ratio = self._clamp((before_count - len(comparison["removed_keys"])) / before_count, 0.0)
        regression_detected = bool(comparison["critical_removed_keys"]) or preservation_ratio < 0.75
        if regression_detected or continuity_score < normalized["warning_threshold"]:
            decision = "constitutional_continuity_failure"
            valid = False
            warning = True
        elif continuity_score < normalized["continuity_threshold"] or comparison["changed_keys"] or comparison["removed_keys"]:
            decision = "constitutional_continuity_warning"
            valid = continuity_score >= normalized["warning_threshold"]
            warning = True
        else:
            decision = "constitutional_continuity_valid"
            valid = True
            warning = False
        readiness_context = self._load_readiness_context()
        record = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": self._now(),
            "current_representative_id": readiness_context.get("current_representative_id"),
            "top_candidate_id": readiness_context.get("top_candidate_id"),
            "constitutional_continuity_score": round(continuity_score, 6),
            "constitutional_difference_score": round(difference_score, 6),
            "constitutional_preservation_ratio": round(preservation_ratio, 6),
            "constitutional_regression_detected": regression_detected,
            "constitutional_continuity_decision": decision,
            "constitutional_continuity_valid": valid,
            "constitutional_continuity_warning": warning,
            "changed_keys": comparison["changed_keys"],
            "removed_keys": comparison["removed_keys"],
            "added_keys": comparison["added_keys"],
            "critical_removed_keys": comparison["critical_removed_keys"],
            "constitution_before": before,
            "constitution_after": after,
        }
        self._persist(record)
        return record

    def _persist(self, record: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write(chr(10))


__all__ = ["ConstitutionalContinuityValidation"]

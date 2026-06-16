from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


ROOT = Path.home() / "open-cognitive-ecology"
DEFAULT_SSD_ROOT = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class CivilizationalStorageRouter:
    """
    F17.2-R2 — Civilizational Storage Router.

    Routes future persistence artifacts to /Volumes/OCE_SSD when available,
    with local fallback when the SSD is absent.
    """

    primitive = "civilizational_storage_router"
    refinement = "F17.2-R2"

    def __init__(self, root: Optional[Path] = None, ssd_root: Optional[Path] = None, fallback_root: Optional[Path] = None):
        self.root = Path(root) if root is not None else ROOT
        self.ssd_root = Path(ssd_root) if ssd_root is not None else DEFAULT_SSD_ROOT
        self.fallback_root = Path(fallback_root) if fallback_root is not None else (self.root / "local_storage_fallback")

    def ssd_available(self) -> bool:
        return self.ssd_root.exists() and self.ssd_root.is_dir()

    def _category_for(self, relative_path: str, category: Optional[str] = None) -> str:
        if category:
            return category
        s = str(relative_path).lower()
        name = Path(relative_path).name.lower()
        if name.endswith(".prom") or "prometheus" in s:
            return "metrics/prometheus"
        if "metric" in s or s.startswith("metrics/"):
            return "metrics"
        if "dashboard" in s or name.endswith(".html") or "grafana" in s:
            return "dashboards"
        if "memory" in s or "knowledge" in s or "semantic" in s or name.endswith(".db") or name.endswith(".sqlite"):
            return "memory"
        if "experiment" in s or "runtime_experiment" in s or "stability" in s:
            return "experiments"
        if "continuity" in s or "recovery" in s or "replication" in s or "migration" in s or "distributed" in s or "node" in s:
            return "continuity"
        if "archive" in s or "history" in s or "queue" in s or "collaboration" in s or "governance" in s or "identity" in s or "external" in s:
            return "archive"
        return "archive"

    def _ssd_category_root(self, category: str) -> Path:
        if category.startswith("metrics/prometheus"):
            return self.ssd_root / "OCE_METRICS" / "prometheus"
        mapping = {
            "memory": self.ssd_root / "OCE_MEMORY",
            "metrics": self.ssd_root / "OCE_METRICS",
            "dashboards": self.ssd_root / "OCE_DASHBOARDS",
            "experiments": self.ssd_root / "OCE_EXPERIMENTS",
            "continuity": self.ssd_root / "OCE_CIVILIZATIONAL_CONTINUITY",
            "archive": self.ssd_root / "OCE_ARCHIVE",
        }
        return mapping.get(category, self.ssd_root / "OCE_ARCHIVE")

    def route_path(self, relative_path: str | Path, category: Optional[str] = None, create_parent: bool = True) -> Path:
        rel = Path(relative_path)
        if rel.is_absolute():
            try:
                rel = rel.relative_to(self.root)
            except Exception:
                rel = Path(rel.name)
        category_key = self._category_for(str(rel), category)
        if self.ssd_available():
            base = self._ssd_category_root(category_key)
            dest = (base / rel.name) if category_key == "metrics/prometheus" else (base / "routed" / rel)
        else:
            dest = self.fallback_root / category_key.replace("/", "_") / rel
        if create_parent:
            dest.parent.mkdir(parents=True, exist_ok=True)
        return dest

    def route_directory(self, relative_path: str | Path, category: Optional[str] = None) -> Path:
        return self.route_path(Path(relative_path) / ".router_directory_anchor", category=category, create_parent=True).parent

    def write_text(self, relative_path: str | Path, text: str, category: Optional[str] = None, encoding: str = "utf-8") -> Path:
        path = self.route_path(relative_path, category=category)
        path.write_text(text, encoding=encoding)
        return path

    def write_json(self, relative_path: str | Path, payload, category: Optional[str] = None) -> Path:
        return self.write_text(relative_path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), category=category)

    def append_jsonl(self, relative_path: str | Path, payload, category: Optional[str] = None) -> Path:
        path = self.route_path(relative_path, category=category)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        return path

    def step(self, inputs: Optional[dict] = None) -> dict:
        inputs = inputs or {}
        probes = [
            "external_memory/memory.db",
            "metrics/metrics_history.jsonl",
            "civilizational_dashboard.html",
            "distributed_nodes/distributed_memory_history.jsonl",
            "autonomous_external_collaboration_history.jsonl",
        ]
        routed = []
        for p in probes:
            dest = self.route_path(p, create_parent=False)
            routed.append({
                "source_relative_path": p,
                "destination": str(dest),
                "category": self._category_for(p),
                "storage_mode": "ssd" if self.ssd_available() else "local_fallback",
            })
        state_path = None
        history_path = None
        if bool(inputs.get("persist", True)):
            state = {
                "primitive": self.primitive,
                "refinement": self.refinement,
                "timestamp_utc": _utc_now(),
                "ssd_available": self.ssd_available(),
                "routed_probe_count": len(routed),
                "routed": routed,
                "epistemic_boundary": "functional_storage_routing_only_no_phenomenal_subjectivity_claim",
            }
            state_path = self.write_json("storage_router/civilizational_storage_router_state.json", state, category="archive")
            history_path = self.append_jsonl("storage_router/civilizational_storage_router_history.jsonl", state, category="archive")
        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc_now(),
            "classification": "Civilizational Storage Router SSD Ready" if self.ssd_available() else "Civilizational Storage Router Local Fallback",
            "ssd_available": self.ssd_available(),
            "ssd_root": str(self.ssd_root),
            "fallback_root": str(self.fallback_root),
            "routed_probe_count": len(routed),
            "routed": routed,
            "state_path": str(state_path) if state_path else None,
            "history_path": str(history_path) if history_path else None,
            "storage_router_ready": True,
            "fallback_available": True,
            "non_closure_compliant": True,
            "reversible": True,
            "epistemic_boundary": "functional_storage_routing_only_no_phenomenal_subjectivity_claim",
        }

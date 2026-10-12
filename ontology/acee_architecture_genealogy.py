from __future__ import annotations

import fcntl
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_ARCHITECTURE_GENEALOGY"
STATUS_READY = "ACEE_ARCHITECTURE_GENEALOGY_READY"
STATUS_DEGRADED = "ACEE_ARCHITECTURE_GENEALOGY_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _finite(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _score(value: Any) -> Optional[float]:
    number = _finite(value)
    if number is None or not 0.0 <= number <= 1.0:
        return None
    return number


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _clean_id(value: Any) -> str:
    raw = str(value or "").strip()
    return "".join(ch if ch.isalnum() or ch in "_-.:" else "_" for ch in raw)


class AceeArchitectureGenealogy:
    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"

    def _paths(self) -> Tuple[Path, Path, Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE12_acee_architecture_genealogy"
        return (
            directory / "latest_genealogy_record.json",
            directory / "genealogy_history.jsonl",
            directory / "architecture_genealogy_graph.json",
            directory / ".genealogy.lock",
        )

    def _history(self, path: Path) -> Tuple[List[Dict[str, Any]], bool]:
        if not path.exists():
            return [], False
        records: List[Dict[str, Any]] = []
        corrupted = False
        previous_hash = None
        try:
            for raw in path.read_text(encoding="utf-8").splitlines():
                if not raw.strip():
                    continue
                item = json.loads(raw)
                if not isinstance(item, dict):
                    corrupted = True
                    continue
                expected = _sha({k: v for k, v in item.items() if k not in {"genealogy_hash", "persisted", "latest_path", "history_path", "graph_path"}})
                if item.get("genealogy_hash") != expected:
                    corrupted = True
                if item.get("previous_genealogy_hash") != previous_hash:
                    corrupted = True
                previous_hash = item.get("genealogy_hash")
                records.append(item)
        except (OSError, json.JSONDecodeError):
            return records, True
        return records, corrupted

    def _graph(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        nodes: Dict[str, Dict[str, Any]] = {}
        children: Dict[str, List[str]] = {}
        for record in records:
            aid = str(record.get("architecture_id") or "")
            if not aid:
                continue
            nodes[aid] = {
                "architecture_id": aid,
                "parent_architecture_id": record.get("parent_architecture_id"),
                "generation_id": record.get("generation_id"),
                "architecture_fingerprint": record.get("architecture_fingerprint"),
                "rollback_status": record.get("rollback_status"),
                "active": record.get("active"),
            }
            parent = record.get("parent_architecture_id")
            if parent:
                children.setdefault(str(parent), []).append(aid)
        return {
            "primitive": PRIMITIVE,
            "node_count": len(nodes),
            "edge_count": sum(len(v) for v in children.values()),
            "nodes": nodes,
            "children": {k: sorted(set(v)) for k, v in sorted(children.items())},
        }

    def _ancestry(self, parent: Optional[str], by_id: Dict[str, Dict[str, Any]]) -> List[str]:
        path: List[str] = []
        seen = set()
        current = parent
        while current:
            if current in seen:
                path.append(current)
                break
            seen.add(current)
            path.append(current)
            current = by_id.get(current, {}).get("parent_architecture_id")
        path.reverse()
        return path

    def _build(self, inputs: Mapping[str, Any], records: List[Dict[str, Any]], corrupted: bool) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        architecture = _mapping(supplied.get("architecture"))
        selection = _mapping(supplied.get("selection_decision"))
        causal = _mapping(supplied.get("causal_analysis"))
        impact = _mapping(supplied.get("impact_evaluation"))
        continuity = _mapping(supplied.get("continuity_evidence"))
        diversity = _mapping(supplied.get("diversity_evidence"))
        inheritance = _mapping(supplied.get("inheritance_evidence"))

        fingerprint_payload = architecture if architecture else _mapping(supplied.get("architecture_state"))
        fingerprint = _sha(fingerprint_payload) if fingerprint_payload else ""
        architecture_id = _clean_id(supplied.get("architecture_id") or architecture.get("architecture_id"))
        if not architecture_id and fingerprint:
            architecture_id = "ARCH-" + fingerprint[:16]
        parent = _clean_id(supplied.get("parent_architecture_id") or architecture.get("parent_architecture_id")) or None
        mutation_id = _clean_id(supplied.get("mutation_id") or architecture.get("mutation_id")) or None

        by_id = {str(r.get("architecture_id")): r for r in records if r.get("architecture_id")}
        blocking: List[str] = []
        if not fingerprint_payload:
            blocking.append("architecture_payload_required")
        if not architecture_id:
            blocking.append("architecture_id_required")
        if corrupted:
            blocking.append("history_corrupted")
        duplicate = architecture_id in by_id
        if duplicate:
            blocking.append("duplicate_architecture_id")
        if parent == architecture_id and architecture_id:
            blocking.append("genealogical_cycle_detected")
        orphan = bool(parent and parent not in by_id)
        if orphan:
            blocking.append("parent_architecture_not_found")

        parent_generation = by_id.get(parent or "", {}).get("generation_id")
        generation_supplied = "generation_id" in supplied or "generation_id" in architecture
        requested_generation = supplied.get("generation_id", architecture.get("generation_id"))
        generation_number = _finite(requested_generation)
        if generation_number is None and generation_supplied:
            generation_id = None
            blocking.append("generation_id_invalid")
        elif generation_number is None:
            generation_id = 0 if parent is None else int(parent_generation or 0) + 1
        elif generation_number < 0 or not float(generation_number).is_integer():
            generation_id = None
            blocking.append("generation_id_invalid")
        else:
            generation_id = int(generation_number)
        if parent and parent_generation is not None and generation_id is not None and generation_id <= int(parent_generation):
            blocking.append("generation_not_monotonic")

        selection_id = str(selection.get("selection_id") or supplied.get("selection_decision_id") or "")
        decision = str(selection.get("decision") or supplied.get("selection_decision_status") or "").lower()
        if decision and decision not in {"accept", "rollback", "reject", "repeat", "sandbox_longer"}:
            blocking.append("selection_decision_invalid")
        if decision and decision != "accept" and not bool(supplied.get("record_non_accepted", False)):
            blocking.append("accepted_selection_required")

        rollback_status = str(supplied.get("rollback_status") or architecture.get("rollback_status") or "not_rolled_back")
        if rollback_status not in {"not_rolled_back", "rollback_requested", "rolled_back", "rollback_failed"}:
            blocking.append("rollback_status_invalid")
        active = rollback_status != "rolled_back"

        lineage_integrity = _score(continuity.get("lineage_integrity"))
        if lineage_integrity is None:
            lineage_integrity = _score(continuity.get("continuity_strength"))
        lineage_diversity = _score(diversity.get("lineage_diversity_score"))
        if lineage_diversity is None:
            lineage_diversity = _score(diversity.get("diversity_score"))
        inheritance_fidelity = _score(inheritance.get("inheritance_fidelity"))

        ancestry_path = self._ancestry(parent, by_id)
        lineage_depth = len(ancestry_path)
        descendants = sorted(
            str(r.get("architecture_id"))
            for r in records
            if r.get("parent_architecture_id") == architecture_id
        )
        previous_hash = records[-1].get("genealogy_hash") if records else None

        ready = not blocking
        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "timestamp_utc": str(supplied.get("timestamp_utc") or _now()),
            "genealogy_status": STATUS_READY if ready else STATUS_DEGRADED,
            "genealogy_ready": ready,
            "architecture_id": architecture_id or None,
            "architecture_fingerprint": fingerprint or None,
            "parent_architecture_id": parent,
            "generation_id": generation_id,
            "mutation_id": mutation_id,
            "selection_decision_id": selection_id or None,
            "causal_analysis_id": causal.get("analysis_id"),
            "impact_evaluation_id": impact.get("evaluation_id"),
            "rollback_status": rollback_status,
            "active": active,
            "lineage_depth": lineage_depth,
            "ancestry_path": ancestry_path,
            "descendant_ids": descendants,
            "lineage_integrity_score": lineage_integrity,
            "lineage_diversity_score": lineage_diversity,
            "inheritance_fidelity": inheritance_fidelity,
            "orphan_detected": orphan,
            "duplicate_architecture_detected": duplicate,
            "cycle_detected": "genealogical_cycle_detected" in blocking,
            "generation_monotonic": "generation_not_monotonic" not in blocking,
            "blocking_reasons": sorted(set(blocking)),
            "previous_genealogy_hash": previous_hash,
            "selection_executed_by_genealogy": False,
            "mutation_executed_by_genealogy": False,
            "rollback_executed_by_genealogy": False,
            "lineage_management_executed": False,
            "best_architecture_selection_executed": False,
            "dashboard_generated": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
        }
        result["genealogy_hash"] = _sha({k: v for k, v in result.items() if k != "genealogy_hash"})
        return result

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        latest, history, graph_path, lock = self._paths()
        records, corrupted = self._history(history)
        result = self._build(supplied, records, corrupted)
        result.update({
            "persisted": False,
            "latest_path": str(latest),
            "history_path": str(history),
            "graph_path": str(graph_path),
        })
        if not persist or not result["genealogy_ready"]:
            return result
        latest.parent.mkdir(parents=True, exist_ok=True)
        with lock.open("a+", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            records, corrupted = self._history(history)
            record = self._build(supplied, records, corrupted)
            record.update({
                "persisted": True,
                "latest_path": str(latest),
                "history_path": str(history),
                "graph_path": str(graph_path),
            })
            if not record["genealogy_ready"]:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
                return record
            with history.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
                handle.flush()
            tmp = latest.with_suffix(".tmp")
            tmp.write_text(json.dumps(record, sort_keys=True, indent=2), encoding="utf-8")
            tmp.replace(latest)
            graph = self._graph(records + [record])
            graph_tmp = graph_path.with_suffix(".tmp")
            graph_tmp.write_text(json.dumps(graph, sort_keys=True, indent=2), encoding="utf-8")
            graph_tmp.replace(graph_path)
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            return record

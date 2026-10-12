from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Mapping, Tuple

from ontology import occ_normative_ir as nir

PRIMITIVE = "occ_normative_ir_real_builder"
VERSION = "P159-OCC1B-real-package-to-nir-v1"
SCHEMA = "oce.p159.occ1b.real_package_to_nir.v1"
PASS, FAIL = "PASS", "FAIL"

PARTITIONS = (
    ("GENESIS", "genesis/genesis.yaml"),
    ("DNA_H", "dna/dna_h.yaml"),
    ("DNA_L0", "dna/dna_l0.yaml"),
    ("DNA_L1", "dna/dna_l1.yaml"),
    ("CCAD", "ccad/ccad_principles.yaml"),
    ("CCAD", "ccad/ccad_arbitration_rules.yaml"),
)

def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def _result(status: str, reason: str, **extra: Any) -> Dict[str, Any]:
    out = {
        "primitive": PRIMITIVE, "version": VERSION, "status": status, "reason": reason,
        "authorization_created": False, "authority_activated": False,
        "execution_performed": False, "occ1c_opened": False, "p160_opened": False,
        "functional_conclusion_only": True, "phenomenology_undetermined": True,
    }
    out.update(deepcopy(extra))
    return out

def _manifest_scalar(text: str, key: str) -> str:
    # Canonical OCC-1A YAML scalars may be nested under mappings.
    # Keys queried here must be unique; ambiguity fails closed.
    pattern = r"(?m)^[ \t]*%s:\s*([^\n#]+?)\s*$" % re.escape(key)
    matches = [m.strip() for m in re.findall(pattern, text)]
    return matches[0] if len(matches) == 1 else ""

def _manifest_ids(text: str) -> Tuple[str, ...]:
    return tuple(re.findall(r"(?m)^\s*-\s*((?:GENESIS|DNA|CCAD)\.[A-Za-z0-9.]+)\s*$", text))

def inspect_source_package(package_root: Path) -> Dict[str, Any]:
    root = Path(package_root)
    manifest = root / "manifest.yaml"
    if not manifest.is_file():
        return _result(FAIL, "SOURCE_MANIFEST_MISSING")
    text = manifest.read_text(encoding="utf-8")
    state = _manifest_scalar(text, "package_state")
    population = _manifest_scalar(text, "kernel_population_status")
    count_s = _manifest_scalar(text, "principal_object_count")
    ids = _manifest_ids(text)
    try:
        declared_count = int(count_s)
    except Exception:
        declared_count = -1
    if state != "VALIDATED":
        return _result(FAIL, "SOURCE_PACKAGE_NOT_VALIDATED", package_state=state)
    if population != "POPULATED_48_VERIFIED":
        return _result(FAIL, "SOURCE_KERNEL_NOT_VERIFIED", kernel_population_status=population)
    if declared_count != 48 or len(ids) != 48 or len(set(ids)) != 48:
        return _result(FAIL, "SOURCE_MANIFEST_KERNEL_IDENTITY_INVALID",
                       declared_count=declared_count, manifest_id_count=len(ids))
    return _result(PASS, "SOURCE_PACKAGE_READY", package_state=state,
                   kernel_population_status=population, manifest_ids=ids,
                   manifest_sha256=_sha(manifest))

def _reject_duplicate_json_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATE_JSON_KEY:%s" % key)
        out[key] = value
    return out

def _load_partition(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except Exception as exc:
        raise ValueError("PARTITION_NOT_CANONICAL_JSON:%s:%s" % (path.name, exc))
    if not isinstance(data, Mapping) or not isinstance(data.get("norms"), list):
        raise ValueError("PARTITION_STRUCTURE_INVALID:%s" % path.name)
    return dict(data)

def _formalization(value: Any) -> str:
    raw = str(value or "").strip().upper()
    m = re.match(r"^(F[0-3])(?:_|$)", raw)
    if not m:
        raise ValueError("FORMALIZATION_UNSUPPORTED:%s" % raw)
    return m.group(1)

def _source_map(rel: str, idx: int, digest: str, cid: str) -> Dict[str, Any]:
    return {
        "source_id": cid,
        "source_path": "normative/occ1a/" + rel,
        "source_field": "norms[%d]" % idx,
        "source_sha256": digest,
    }

def _norm_to_node(norm: Mapping[str, Any], rel: str, idx: int, digest: str, level: str) -> Dict[str, Any]:
    cid = str(norm.get("canonical_id", "")).strip()
    if not cid:
        raise ValueError("CANONICAL_ID_MISSING:%s:%d" % (rel, idx))
    if bool(norm.get("execution_enabled", False)):
        raise ValueError("SOURCE_EXECUTION_ENABLED:%s" % cid)
    if bool(norm.get("runtime_authority_granted", False)):
        raise ValueError("SOURCE_RUNTIME_AUTHORITY_GRANTED:%s" % cid)
    formal = _formalization(norm.get("formalization"))
    status = str(norm.get("semantic_status", "")).strip()
    if not status:
        raise ValueError("SEMANTIC_STATUS_MISSING:%s" % cid)
    allowed_status_by_level = {
        "GENESIS": {"HUMAN_JUDGMENT_REQUIRED"},
        "DNA_H": {"GOVERNED_ADOPTED_SEMANTIC_BINDING"},
        "DNA_L0": {"PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION"},
        "DNA_L1": {"GOVERNED_ADOPTED_SEMANTIC_BINDING"},
        "CCAD": {"DIRECT_EXPLICIT_SOURCE_BINDING"},
    }
    if status not in allowed_status_by_level.get(level, set()):
        raise ValueError("SEMANTIC_STATUS_NOT_ALLOWED:%s:%s:%s" % (level, cid, status))
    text = norm.get("text")
    if cid == "GENESIS.G0":
        if formal != "F0" or status != "HUMAN_JUDGMENT_REQUIRED":
            raise ValueError("GENESIS_BOUNDARY_WEAKENED")
        if text is not None:
            raise ValueError("GENESIS_INVENTED_MACHINE_TEXT")
        if bool(norm.get("machine_formalization_claimed", False)):
            raise ValueError("GENESIS_MACHINE_FORMALIZATION_CLAIMED")
    node = {
        "node_id": cid,
        "node_type": "NormNode",
        "formalization_level": formal,
        "source_map": _source_map(rel, idx, digest, cid),
        "normative_level": level,
        "semantic_status": status,
        "source_object_id": norm.get("source_object_id"),
        "text": text,
        "evidence_ids": deepcopy(norm.get("evidence_ids", [])),
        "lineage_kind": norm.get("lineage_kind"),
        "lineage_artifacts": deepcopy(norm.get("lineage_artifacts", [])),
        "execution_enabled": False,
        "runtime_authority_granted": False,
        "partial_formalization_explicit": formal in ("F0", "F1", "F2"),
    }
    if cid == "GENESIS.G0":
        node["human_judgment_required"] = True
        node["machine_formalization_claimed"] = False
    return node

def build_real_nir(package_root: Path) -> Dict[str, Any]:
    root = Path(package_root)
    ready = inspect_source_package(root)
    if ready["status"] != PASS:
        return ready
    before = {}
    for _, rel in PARTITIONS:
        path = root / rel
        if not path.is_file():
            return _result(FAIL, "SOURCE_PARTITION_MISSING", missing_partition=rel)
        before[rel] = _sha(path)
    before["manifest.yaml"] = _sha(root / "manifest.yaml")

    nodes: List[Dict[str, Any]] = []
    partition_hashes = {}
    try:
        for level, rel in PARTITIONS:
            path = root / rel
            digest = _sha(path)
            partition_hashes[rel] = digest
            data = _load_partition(path)
            for idx, norm in enumerate(data["norms"]):
                if not isinstance(norm, Mapping):
                    raise ValueError("NORM_NOT_MAPPING:%s:%d" % (rel, idx))
                nodes.append(_norm_to_node(norm, rel, idx, digest, level))
    except ValueError as exc:
        return _result(FAIL, str(exc))

    ids = tuple(n["node_id"] for n in nodes)
    expected = tuple(ready["manifest_ids"])
    if len(ids) != 48:
        return _result(FAIL, "REAL_KERNEL_COUNT_MISMATCH", actual_count=len(ids))
    if len(set(ids)) != len(ids):
        return _result(FAIL, "DUPLICATE_CANONICAL_ID")
    if set(ids) != set(expected):
        return _result(FAIL, "REAL_KERNEL_IDENTITY_MISMATCH",
                       missing=tuple(sorted(set(expected)-set(ids))),
                       invented=tuple(sorted(set(ids)-set(expected))))

    # Canonical ordering is by stable ID; file order is non-normative.
    nodes = sorted(nodes, key=lambda n: n["node_id"])
    graph = {
        "nodes": nodes,
        "edges": [],
        "metadata": {
            "schema": SCHEMA,
            "source_package_state": "VALIDATED",
            "kernel_population_status": "POPULATED_48_VERIFIED",
            "principal_object_count": 48,
            "representation_stage": "REAL_SOURCE_PROJECTION",
            "semantic_relations_compiled": False,
            "v3_normative_coherence_claimed": False,
            "v4_semantic_preservation_claimed": False,
        },
        "source_map": {
            "package_manifest_path": "normative/occ1a/manifest.yaml",
            "package_manifest_sha256": ready["manifest_sha256"],
            "partition_sha256": dict(sorted(partition_hashes.items())),
        },
    }
    validation = nir.validate_graph(graph)
    if validation["status"] != nir.PASS:
        return _result(FAIL, "NIR_FOUNDATION_VALIDATION_FAILED", validation=validation)

    after = {rel: _sha(root / rel) for _, rel in PARTITIONS}
    after["manifest.yaml"] = _sha(root / "manifest.yaml")
    if before != after:
        return _result(FAIL, "SOURCE_PACKAGE_MUTATED_DURING_BUILD")

    source_map_complete = all(
        n.get("source_map", {}).get("source_sha256") == partition_hashes[
            n["source_map"]["source_path"].split("normative/occ1a/",1)[1]
        ] for n in nodes
    )
    if not source_map_complete:
        return _result(FAIL, "SOURCE_MAPPING_INCOMPLETE")

    package = {
        "schema": SCHEMA,
        "version": VERSION,
        "source_package_state": "VALIDATED",
        "source_kernel_objects": 48,
        "nir_principal_objects": 48,
        "stable_ids": tuple(n["node_id"] for n in nodes),
        "graph": graph,
        "boundaries": {
            "source_package_mutated": False,
            "semantic_relations_compiled": False,
            "authorization_created": False,
            "authority_activated": False,
            "execution_performed": False,
            "occ1c_opened": False,
            "p160_opened": False,
            "final_lock_performed": False,
        },
    }
    return _result(
        PASS, "P159_OCC1B_REAL_PACKAGE_TO_NIR_V1_OK",
        package=package, nir_sha256=nir.canonical_sha256(package),
        source_kernel_objects=48, nir_principal_objects=48,
        stable_ids_preserved="48/48", source_mapping_complete="48/48",
        silent_loss=0, invented_norms=0, source_package_mutated=False,
        genesis_human_judgment_preserved=True,
        genesis_f0_preserved=True, genesis_invented_text=False,
        v3_normative_coherence_claimed=False,
        v4_semantic_preservation_claimed=False,
    )

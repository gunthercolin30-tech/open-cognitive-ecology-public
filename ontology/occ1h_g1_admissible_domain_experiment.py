from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any, Dict, Mapping
from ontology import occ_normative_ir_real_builder as real_builder

PRIMITIVE = "occ1h_g1_admissible_domain_experiment"
VERSION = "P159-OCC1H-G1-admissible-domain-experiment-v1"
SCHEMA = "oce.p159.occ1h.g1.admissible_domain_experiment.v1"
TARGETS = {
    "A021": {"field": "modality", "value": "MAY", "dimension": "MAY_MODALITY"},
    "A041": {"field": "sunset", "value": "2099-12-31T23:59:59Z", "dimension": "SUNSET"},
    "A042": {"field": "purpose", "value": "OCC1H_G1_SYNTHETIC_PURPOSE_FIXTURE", "dimension": "PURPOSE"},
}
PARTITION = "ccad/ccad_principles.yaml"

def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def _package_hashes(package_root: Path) -> Dict[str, str]:
    paths = ["manifest.yaml"] + [rel for _, rel in real_builder.PARTITIONS]
    return {rel: _sha(package_root / rel) for rel in paths}

def _find_target_norm(data: Mapping[str, Any]) -> int:
    norms = data.get("norms")
    if not isinstance(norms, list):
        raise AssertionError("fixture partition lacks norms")
    for idx, norm in enumerate(norms):
        if isinstance(norm, Mapping) and str(norm.get("canonical_id", "")).startswith("CCAD."):
            return idx
    raise AssertionError("no CCAD norm available for fixture")

def _field_projected(build: Mapping[str, Any], canonical_id: str, field: str, value: Any) -> bool:
    graph = build.get("graph", {})
    nodes = graph.get("nodes", []) if isinstance(graph, Mapping) else []
    for node in nodes:
        if isinstance(node, Mapping) and node.get("node_id") == canonical_id:
            return field in node and node.get(field) == value
    return False

def _run_one(source_root: Path, scenario_id: str) -> Dict[str, Any]:
    spec = TARGETS[scenario_id]
    with tempfile.TemporaryDirectory(prefix="oce_occ1h_g1_fixture_") as td:
        fixture = Path(td) / "occ1a"
        shutil.copytree(str(source_root), str(fixture))
        partition = fixture / PARTITION
        data = json.loads(partition.read_text(encoding="utf-8"))
        idx = _find_target_norm(data)
        canonical_id = str(data["norms"][idx]["canonical_id"])
        data["norms"][idx][spec["field"]] = deepcopy(spec["value"])
        partition.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        inspect = real_builder.inspect_source_package(fixture)
        build = real_builder.build_real_nir(fixture)
        accepted = inspect.get("status") == real_builder.PASS and build.get("status") == real_builder.PASS
        projected = accepted and _field_projected(build, canonical_id, spec["field"], spec["value"])
        observation = ("REJECTED_BY_ADMISSIBLE_DOMAIN" if not accepted
                       else "ACCEPTED_AND_PROJECTED" if projected
                       else "ACCEPTED_BUT_NOT_PROJECTED")
        return {
            "scenario_id": scenario_id, "dimension": spec["dimension"], "field": spec["field"],
            "target_canonical_id": canonical_id, "source_partition": PARTITION,
            "inspect_status": inspect.get("status"), "inspect_reason": inspect.get("reason"),
            "build_status": build.get("status"), "build_reason": build.get("reason"),
            "field_projected": bool(projected), "observation": observation,
            "historical_verdict_modified": False, "applicability_reclassified": False,
            "positive_non_instantiability_proof_created": False,
        }

def run(root: Path) -> Dict[str, Any]:
    root = Path(root)
    source_root = root / "normative" / "occ1a"
    before = _package_hashes(source_root)
    results = {sid: _run_one(source_root, sid) for sid in sorted(TARGETS)}
    repeated = {sid: _run_one(source_root, sid) for sid in sorted(TARGETS)}
    deterministic = all(
        results[sid]["observation"] == repeated[sid]["observation"]
        and results[sid]["inspect_status"] == repeated[sid]["inspect_status"]
        and results[sid]["build_status"] == repeated[sid]["build_status"]
        for sid in sorted(TARGETS)
    )
    after = _package_hashes(source_root)
    observations = {sid: results[sid]["observation"] for sid in sorted(results)}
    accepted_not_projected = tuple(sid for sid in sorted(results) if results[sid]["observation"] == "ACCEPTED_BUT_NOT_PROJECTED")
    rejected = tuple(sid for sid in sorted(results) if results[sid]["observation"] == "REJECTED_BY_ADMISSIBLE_DOMAIN")
    projected = tuple(sid for sid in sorted(results) if results[sid]["observation"] == "ACCEPTED_AND_PROJECTED")
    decision = ("ADMISSIBLE_INPUT_ACCEPTED_BUT_NOT_PROJECTED"
                if len(accepted_not_projected) == len(TARGETS)
                else "MIXED_ADMISSIBLE_DOMAIN_OBSERVATIONS")
    core = {
        "schema": SCHEMA, "version": VERSION, "decision": decision, "results": results,
        "observations": observations, "accepted_but_not_projected": accepted_not_projected,
        "rejected_by_admissible_domain": rejected, "accepted_and_projected": projected,
        "deterministic": deterministic, "canonical_sources_unchanged": before == after,
        "canonical_source_hashes": before, "a040_excluded": True,
        "a040_reason": "NORMATIVE_GAP_NOT_TECHNICALLY_RECLASSIFIED",
        "positive_non_instantiability_proof_count": 0, "applicability_reclassified_count": 0,
        "historical_verdicts_modified": False, "canonical_sources_modified": False,
        "compiled_profile_modified": False, "authority_created": False,
        "execution_authority_created": False, "occ1h_closed": False, "occ1i_opened": False,
        "p159_final_lock": False, "p160_opened": False,
        "functional_conclusion_only": True, "phenomenology_undetermined": True,
    }
    core["evidence_sha256"] = sha256(_canonical(core).encode("utf-8")).hexdigest()
    return core

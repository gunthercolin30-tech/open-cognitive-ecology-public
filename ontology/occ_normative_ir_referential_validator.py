from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re
from typing import Any, Dict, Mapping, Sequence, Tuple

from ontology import occ_normative_ir as nir
from ontology import occ_normative_ir_real_builder as real_builder

PRIMITIVE = "occ_normative_ir_referential_validator"
VERSION = "P159-OCC1B-V2-referential-validation-v1"
PASS, FAIL = "PASS", "FAIL"

DNA_SOURCE_RE = re.compile(r"^F(?:[1-9]|1[0-8])$")
CCAD_P_RE = re.compile(r"^P(?:[0-9]|1[0-3])$")
CCAD_AR_RE = re.compile(r"^AR-(?:[1-9]|10)$")
GENESIS_SOURCE_RE = re.compile(r"^P155_GENESIS_CONCEPTUAL_SOURCE$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

def _result(status: str, reason: str, **extra: Any) -> Dict[str, Any]:
    out = {
        "primitive": PRIMITIVE, "version": VERSION, "status": status, "reason": reason,
        "authorization_created": False, "authority_activated": False,
        "execution_performed": False, "occ1c_opened": False, "p160_opened": False,
        "v3_normative_coherence_claimed": False,
        "v4_semantic_preservation_claimed": False,
        "functional_conclusion_only": True, "phenomenology_undetermined": True,
    }
    out.update(deepcopy(extra))
    return out

def _source_tokens(node: Mapping[str, Any]) -> Tuple[str, ...]:
    raw = str(node.get("source_object_id") or "").strip()
    if not raw:
        return ()
    return tuple(x.strip() for x in raw.split("+") if x.strip())

def _expected_source_kind(node: Mapping[str, Any], token: str) -> str:
    cid = str(node.get("node_id", ""))
    if cid == "GENESIS.G0" and GENESIS_SOURCE_RE.match(token):
        return "GENESIS_EXTERNAL_SOURCE"
    if cid.startswith("DNA.") and DNA_SOURCE_RE.match(token):
        return "HUMAN_VALUE_EXTERNAL_SOURCE"
    if cid.startswith("CCAD.P") and CCAD_P_RE.match(token):
        return "CCAD_PRINCIPLE_EXTERNAL_SOURCE"
    if cid.startswith("CCAD.AR") and CCAD_AR_RE.match(token):
        return "CCAD_ARBITRATION_EXTERNAL_SOURCE"
    return ""

def _lineage_ref(artifact: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "reference_type": "EXTERNAL_LINEAGE_ARTIFACT",
        "target": str(artifact.get("path", "")).strip(),
        "sha256": str(artifact.get("sha256", "")).strip().lower(),
        "resolution_domain": "EXTERNAL_ARTIFACT",
        "authority_granted": False,
    }

def validate_real_nir_references(package_root: Path) -> Dict[str, Any]:
    built = real_builder.build_real_nir(Path(package_root))
    if built.get("status") != PASS:
        return _result(FAIL, "REAL_NIR_BUILD_REQUIRED", build_result=built)

    package = built["package"]
    graph = package["graph"]
    nodes = graph["nodes"]
    canonical_ids = tuple(n["node_id"] for n in nodes)
    canonical_set = set(canonical_ids)

    if len(canonical_ids) != 48 or len(canonical_set) != 48:
        return _result(FAIL, "BROKEN_NORM_REFERENCE", detail="canonical_identity_set_invalid")

    references = []
    broken = []

    for node in nodes:
        cid = node["node_id"]
        sm = node.get("source_map")
        if not isinstance(sm, Mapping):
            broken.append((cid, "SOURCE_MAP_MISSING"))
            continue
        if sm.get("source_id") != cid:
            broken.append((cid, "SOURCE_MAP_SOURCE_ID_MISMATCH"))
        digest = str(sm.get("source_sha256", "")).lower()
        if not SHA256_RE.match(digest):
            broken.append((cid, "SOURCE_MAP_SHA256_INVALID"))

        tokens = _source_tokens(node)
        if not tokens:
            broken.append((cid, "SOURCE_OBJECT_ID_MISSING"))
        for token in tokens:
            kind = _expected_source_kind(node, token)
            if not kind:
                broken.append((cid, "UNRESOLVED_EXTERNAL_SOURCE:" + token))
            references.append({
                "owner": cid, "reference_type": kind or "BROKEN_EXTERNAL_SOURCE",
                "target": token, "resolution_domain": "EXTERNAL_NORMATIVE_SOURCE",
                "internal_canonical_target": False, "authority_granted": False,
            })

        evidence = tuple(str(x).strip() for x in node.get("evidence_ids", ()) if str(x).strip())
        for ev in evidence:
            if not DNA_SOURCE_RE.match(ev):
                broken.append((cid, "INVALID_EVIDENCE_REFERENCE:" + ev))
            references.append({
                "owner": cid, "reference_type": "EVIDENCE_REFERENCE",
                "target": ev, "resolution_domain": "EXTERNAL_EVIDENCE",
                "internal_canonical_target": False, "authority_granted": False,
            })

        # DNA bindings must expose their F-source as evidence. H9 deliberately has
        # two distinct source clauses F12 + F17; this must not be collapsed.
        if cid.startswith("DNA."):
            if set(tokens) != set(evidence):
                broken.append((cid, "DNA_SOURCE_EVIDENCE_MISMATCH"))

        lineage = node.get("lineage_artifacts", ())
        if not isinstance(lineage, (list, tuple)) or not lineage:
            broken.append((cid, "LINEAGE_ARTIFACT_MISSING"))
        else:
            for artifact in lineage:
                if not isinstance(artifact, Mapping):
                    broken.append((cid, "LINEAGE_ARTIFACT_INVALID"))
                    continue
                ref = _lineage_ref(artifact)
                if not ref["target"] or not SHA256_RE.match(ref["sha256"]):
                    broken.append((cid, "LINEAGE_ARTIFACT_REFERENCE_INVALID"))
                ref["owner"] = cid
                references.append(ref)

    # Any future graph edge is an internal reference and must resolve to one of
    # the 48 canonical IDs. V2 validates references; it does not invent edges.
    for edge in graph.get("edges", ()):
        source, target = edge.get("source"), edge.get("target")
        if source not in canonical_set or target not in canonical_set:
            broken.append((str(source), "BROKEN_INTERNAL_EDGE:" + str(target)))

    if broken:
        return _result(
            FAIL, "BROKEN_NORM_REFERENCE",
            broken_references=tuple(sorted(broken)),
            reference_count=len(references),
            canonical_object_count=len(canonical_ids),
        )

    # Referential validation is intentionally distinct from artifact existence:
    # external lineage paths are typed/hash-bound references and may live outside
    # the OCC-1A package. V2 does not silently convert them to internal nodes.
    report = {
        "schema": "oce.p159.occ1b.v2.referential_validation.v1",
        "canonical_object_count": 48,
        "canonical_ids_unique": True,
        "source_map_resolved": "48/48",
        "external_source_references_typed": True,
        "evidence_references_typed": True,
        "lineage_references_hash_bound": True,
        "external_references_promoted_to_internal_nodes": False,
        "broken_reference_count": 0,
        "reference_count": len(references),
        "references": sorted(references, key=lambda r: (
            str(r.get("owner")), str(r.get("reference_type")), str(r.get("target"))
        )),
        "v3_normative_coherence_claimed": False,
        "v4_semantic_preservation_claimed": False,
    }
    return _result(
        PASS, "P159_OCC1B_V2_REFERENTIAL_VALIDATION_OK",
        report=report, report_sha256=nir.canonical_sha256(report),
        canonical_object_count=48, source_map_resolved="48/48",
        broken_reference_count=0,
    )

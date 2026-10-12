from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Mapping, List, Tuple

from ontology import occ_normative_ir as nir
from ontology import occ_normative_ir_real_builder as builder

PRIMITIVE="occ_constitutional_compiled_profile_independent_verifier"
VERSION="P159-OCC1C-independent-semantic-verifier-v1"
SCHEMA="oce.p159.occ1c.independent_semantic_verification.v1"
PASS,FAIL="PASS","FAIL"

# Intentionally duplicated projection contract: this verifier MUST NOT import
# occ_constitutional_compiler or the compilation transaction as an oracle.
RULE_FIELDS=(
 "norm_id","node_type","formalization_level","normative_level","semantic_status",
 "source_object_id","text","evidence_ids","lineage_kind","lineage_artifacts",
 "source_map","partial_formalization_explicit","human_judgment_required",
 "machine_formalization_claimed","authorization","execution",
)

def _sha(p:Path)->str: return sha256(p.read_bytes()).hexdigest()

def _expected_rule(node:Mapping[str,Any])->Dict[str,Any]:
    return {
      "norm_id":node["node_id"],
      "node_type":node["node_type"],
      "formalization_level":node["formalization_level"],
      "normative_level":node.get("normative_level"),
      "semantic_status":node.get("semantic_status"),
      "source_object_id":node.get("source_object_id"),
      "text":deepcopy(node.get("text")),
      "evidence_ids":deepcopy(node.get("evidence_ids",[])),
      "lineage_kind":node.get("lineage_kind"),
      "lineage_artifacts":deepcopy(node.get("lineage_artifacts",[])),
      "source_map":deepcopy(node["source_map"]),
      "partial_formalization_explicit":bool(node.get("partial_formalization_explicit",False)),
      "human_judgment_required":bool(node.get("human_judgment_required",False)),
      "machine_formalization_claimed":bool(node.get("machine_formalization_claimed",False)),
      "authorization":False,
      "execution":False,
    }

def _expected_edges(graph:Mapping[str,Any])->List[Dict[str,Any]]:
    return deepcopy(sorted(graph.get("edges",[]),key=lambda e:(
        str(e.get("source","")),str(e.get("edge_type","")),str(e.get("target","")))))

def verify(source_root:Path, profile_path:Path, tx_path:Path)->Dict[str,Any]:
    source_root=Path(source_root); profile_path=Path(profile_path); tx_path=Path(tx_path)
    try:
        profile=json.loads(profile_path.read_text(encoding="utf-8"))
        tx=json.loads(tx_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"status":FAIL,"reason":"INPUT_UNREADABLE","detail":type(e).__name__}

    built=builder.build_real_nir(source_root)
    if built.get("status")!=PASS:
        return {"status":FAIL,"reason":"INDEPENDENT_NIR_RECONSTRUCTION_FAILED"}

    graph=built["package"]["graph"]
    nodes=graph.get("nodes",[])
    expected={n["node_id"]:_expected_rule(n) for n in nodes}
    actual_rules=profile.get("rules")
    if not isinstance(actual_rules,list):
        return {"status":FAIL,"reason":"PROFILE_RULES_MISSING"}
    actual={r.get("norm_id"):r for r in actual_rules if isinstance(r,dict)}

    findings=[]
    if len(expected)!=48 or len(actual_rules)!=48 or len(actual)!=48:
        findings.append("RULE_CARDINALITY_OR_IDENTITY_MISMATCH")
    missing=sorted(set(expected)-set(actual))
    invented=sorted(set(actual)-set(expected))
    if missing: findings.append("MISSING_NORMS:"+",".join(missing))
    if invented: findings.append("INVENTED_NORMS:"+",".join(invented))

    field_diffs=[]
    for nid in sorted(set(expected)&set(actual)):
        e,a=expected[nid],actual[nid]
        for f in RULE_FIELDS:
            if a.get(f)!=e.get(f):
                field_diffs.append({"norm_id":nid,"field":f,"expected":e.get(f),"actual":a.get(f)})
        # Extra executable/authority semantics are not permitted even if rehashed.
        for forbidden in ("authority_created","authority_activated","authorized","executable_payload","generated_python"):
            if a.get(forbidden) not in (None,False):
                field_diffs.append({"norm_id":nid,"field":forbidden,"expected":False,"actual":a.get(forbidden)})
    if field_diffs: findings.append("RULE_SEMANTIC_MISMATCH")

    expected_edges=_expected_edges(graph)
    if profile.get("relations")!=expected_edges:
        findings.append("RELATION_SEMANTIC_MISMATCH")
    if profile.get("source_map")!=graph.get("source_map",{}):
        findings.append("SOURCE_MAP_MISMATCH")
    if profile.get("source_nir_sha256")!=built.get("nir_sha256"):
        findings.append("SOURCE_NIR_BINDING_MISMATCH")
    if profile.get("principal_rule_count")!=48:
        findings.append("PRINCIPAL_RULE_COUNT_MISMATCH")

    contract=profile.get("compiler_contract")
    if not isinstance(contract,dict):
        findings.append("COMPILER_CONTRACT_MISSING")
    else:
        false_keys=("compiler_creates_norms","compiler_creates_authority","compiler_authorizes",
          "compiler_executes","compiler_self_certifies","compiler_modifies_sources",
          "compiler_invents_normative_defaults","conflict_arbitration_performed",
          "generated_python","executable_payload","network_semantic_dependency",
          "clock_semantic_dependency","random_semantic_dependency","cwd_semantic_dependency")
        if any(contract.get(k) is not False for k in false_keys):
            findings.append("COMPILER_BOUNDARY_VIOLATION")

    # Independently bind persisted transaction to persisted profile and source NIR.
    payload=tx.get("payload") if isinstance(tx,dict) else None
    if not isinstance(payload,dict):
        findings.append("TRANSACTION_PAYLOAD_MISSING")
    else:
        ph=nir.canonical_sha256(payload)
        if tx.get("payload_sha256")!=ph or tx.get("transaction_id")!=ph:
            findings.append("TRANSACTION_HASH_MISMATCH")
        if payload.get("profile_artifact_sha256")!=_sha(profile_path):
            findings.append("TRANSACTION_PROFILE_ARTIFACT_BINDING_MISMATCH")
        if payload.get("profile_sha256")!=profile.get("profile_sha256"):
            findings.append("TRANSACTION_PROFILE_SEMANTIC_HASH_BINDING_MISMATCH")
        if payload.get("source_nir_sha256")!=built.get("nir_sha256"):
            findings.append("TRANSACTION_NIR_BINDING_MISMATCH")
        for k in ("authorization_created","authority_activated","execution_performed",
                  "generated_python","executable_payload","conflict_arbitrated",
                  "source_modified","occ1d_opened","p160_opened","p159_final_lock_performed"):
            if payload.get(k) is not False:
                findings.append("TRANSACTION_BOUNDARY_VIOLATION:"+k)

    if findings:
        return {"status":FAIL,"reason":"INDEPENDENT_SEMANTIC_VERIFICATION_FAILED",
                "findings":findings,"field_diffs":field_diffs[:50],
                "missing_norms":missing,"invented_norms":invented,
                "compiler_imported":False,"transaction_writer_imported":False}

    proof_payload={
      "schema":SCHEMA,"milestone":"P159/OCC-1C",
      "verification":"INDEPENDENT_SEMANTIC_PRESERVATION",
      "decision":"VERIFIED",
      "verified_rules":48,"missing_norms":0,"invented_norms":0,"semantic_differences":0,
      "relations_preserved":True,"source_map_preserved":True,
      "source_nir_sha256":built["nir_sha256"],
      "profile_artifact_sha256":_sha(profile_path),
      "profile_sha256":profile.get("profile_sha256"),
      "transaction_artifact_sha256":_sha(tx_path),
      "transaction_id":tx.get("transaction_id"),
      "compiler_imported":False,"transaction_writer_imported":False,
      "authorization_created":False,"authority_activated":False,"execution_performed":False,
      "occ1d_opened":False,"p160_opened":False,"p159_final_lock_performed":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True,
    }
    proof_sha=nir.canonical_sha256(proof_payload)
    return {"status":PASS,"reason":"P159_OCC1C_INDEPENDENT_SEMANTIC_VERIFICATION_OK",
            "proof":{"payload":proof_payload,"proof_sha256":proof_sha},
            "proof_sha256":proof_sha,"verified_rules":48,
            "compiler_imported":False,"transaction_writer_imported":False}

def verify_proof(proof:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(proof,Mapping) or not isinstance(proof.get("payload"),dict):
        return {"status":FAIL,"reason":"PROOF_STRUCTURE_INVALID"}
    if proof.get("proof_sha256")!=nir.canonical_sha256(proof["payload"]):
        return {"status":FAIL,"reason":"PROOF_HASH_MISMATCH"}
    p=proof["payload"]
    req={"schema":SCHEMA,"verification":"INDEPENDENT_SEMANTIC_PRESERVATION",
         "decision":"VERIFIED","verified_rules":48,"missing_norms":0,
         "invented_norms":0,"semantic_differences":0,"relations_preserved":True,
         "source_map_preserved":True,"compiler_imported":False,
         "transaction_writer_imported":False,"authorization_created":False,
         "authority_activated":False,"execution_performed":False,"occ1d_opened":False,
         "p160_opened":False,"p159_final_lock_performed":False,
         "functional_conclusion_only":True,"phenomenology_undetermined":True}
    bad=[k for k,v in req.items() if p.get(k)!=v]
    return {"status":FAIL,"reason":"PROOF_SEMANTICS_INVALID","failed_checks":bad} if bad else \
           {"status":PASS,"reason":"INDEPENDENT_SEMANTIC_PROOF_INTEGRITY_OK"}

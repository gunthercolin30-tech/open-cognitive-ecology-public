from pathlib import Path
import json, hashlib, os, tempfile

ROOT = Path.home() / "open-cognitive-ecology"
AA = ROOT / "validation_artifacts/p159/occ1k_r9aa/genesis_g0_resolution_assessment_v1.json"
W = ROOT / "validation_artifacts/p159/occ1k_r9w/governed_direct_rule_consumer_binding_layer_v1.json"
Z = ROOT / "validation_artifacts/p159/occ1k_r9z/governed_contextual_rule_consumer_binding_layer_v1.json"
OUT = ROOT / "validation_artifacts/p159/occ1k_r9ab"
LAYER = OUT / "governed_genesis_g0_ccad_binding_layer_v1.json"
RECEIPT = OUT / "atomic_governed_genesis_g0_ccad_binding_commit_receipt_v1.json"
TOKEN = "I_CONFIRM_R9AA_ADOPT_CCAD_AS_GOVERNED_GENESIS_SEMANTIC_CONTRACT"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def canonical_bytes(o):
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def build():
    aa, w, z = load(AA), load(W), load(Z)
    if aa.get("status") != "GENESIS_G0_HUMAN_JUDGMENT_REQUIRED_NO_AUTOMATIC_CONSUMER_BINDING":
        raise RuntimeError("R9AA_NOT_DECISION_READY")
    if aa.get("canonical_id") != "GENESIS.G0":
        raise RuntimeError("R9AA_CANONICAL_ID_MISMATCH")
    if aa["assessment"].get("ccad_binding_proven_by_source") is not False:
        raise RuntimeError("R9AA_SOURCE_PROOF_BOUNDARY_VIOLATION")
    if aa["assessment"].get("machine_formalization_claimed") is not False:
        raise RuntimeError("R9AA_MACHINE_FORMALIZATION_BOUNDARY_VIOLATION")

    prior = {b["rule_id"] for b in w["bindings"]} | {b["rule_id"] for b in z["bindings"]}
    if "GENESIS.G0" in prior:
        raise RuntimeError("GENESIS_G0_ALREADY_BOUND_IN_PRIOR_LAYER")

    binding = {
        "rule_id": "GENESIS.G0",
        "consumers": ["CCAD"],
        "binding_basis": "NEW_GOVERNED_GENESIS_SEMANTIC_CONTRACT_DECISION",
        "source_proven_binding": False,
        "machine_formalization_claimed": False,
        "retroactive_source_proof_claimed": False,
        "human_governed_decision": True,
        "effect": "PROSPECTIVE"
    }
    return {
        "schema": "oce.p159.occ1k.r9ab.governed.genesis.g0.ccad.binding.layer.v1",
        "milestone": "P159/OCC-1K-R9AB",
        "status": "COMMITTED",
        "decision": "ADOPT_CCAD_AS_GOVERNED_GENESIS_SEMANTIC_CONTRACT",
        "inputs": {
            "r9aa_sha256": sha(AA),
            "r9w_sha256": sha(W),
            "r9z_sha256": sha(Z)
        },
        "binding": binding,
        "coverage": {
            "prior_bound_rules": len(prior),
            "new_bound_rules": 1,
            "expected_total_rules": 48,
            "candidate_complete_48_of_48": len(prior) + 1 == 48
        },
        "preservation": {
            "r9w_preserved": True,
            "r9z_preserved": True,
            "historical_unresolved_state_preserved": True,
            "retroactive_repair": False
        },
        "boundaries": {
            "canonical_source_modified": False,
            "cnp_modified": False,
            "runtime_binding_created": False,
            "runtime_enforcement_proven": False,
            "authorization_created": False,
            "execution_performed": False,
            "s10": "REPLAY_REQUIRED",
            "fl_b3": "BLOCKED_PENDING_CONSOLIDATION_AND_INDEPENDENT_S10_REPLAY",
            "lock_ready": False,
            "lock_granted": False,
            "p160b_opened": False
        },
        "next_required_step": "R9AC_CONSOLIDATED_48_RULE_BINDING_MAP_AND_S10_REPLAY_PRECHECK",
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True
    }

def commit(confirm):
    if confirm != TOKEN:
        raise RuntimeError("EXPLICIT_CONFIRMATION_REQUIRED")
    d = build()
    lb = canonical_bytes(d)
    receipt = {
        "schema": "oce.p159.occ1k.r9ab.atomic.governed.genesis.g0.ccad.binding.commit.receipt.v1",
        "milestone": "P159/OCC-1K-R9AB",
        "status": "COMMITTED",
        "confirmation_token_verified": True,
        "decision": d["decision"],
        "r9aa_sha256": sha(AA),
        "binding_layer_sha256": hashlib.sha256(lb).hexdigest(),
        "r9w_preserved": True,
        "r9z_preserved": True,
        "source_proven_binding": False,
        "retroactive_source_proof_claimed": False,
        "runtime_binding_created": False,
        "authorization_created": False,
        "execution_performed": False,
        "p160b_opened": False
    }
    rb = canonical_bytes(receipt)
    for path, data in ((LAYER, lb), (RECEIPT, rb)):
        if path.exists() and path.read_bytes() != data:
            raise RuntimeError("DIVERGENT_EXISTING_ARTIFACT:" + str(path))
        atomic_write(path, data)
    return d, hashlib.sha256(lb).hexdigest(), hashlib.sha256(rb).hexdigest()

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", required=True)
    args = ap.parse_args()
    d, lh, rh = commit(args.confirm)
    c = d["coverage"]
    print("P159_OCC1K_R9AB_ATOMIC_GOVERNED_GENESIS_G0_CCAD_BINDING_COMMIT_COMPLETE")
    print("STATUS=COMMITTED")
    print("CANONICAL_ID=GENESIS.G0")
    print("CONSUMER=CCAD")
    print("SOURCE_PROVEN_BINDING=false")
    print("MACHINE_FORMALIZATION_CLAIMED=false")
    print("RETROACTIVE_SOURCE_PROOF_CLAIMED=false")
    print("HUMAN_GOVERNED_DECISION=true")
    print("PRIOR_BOUND_RULES=%d" % c["prior_bound_rules"])
    print("NEW_BOUND_RULES=1")
    print("CANDIDATE_COMPLETE_48_OF_48=%s" % str(c["candidate_complete_48_of_48"]).lower())
    print("R9W_PRESERVED=true")
    print("R9Z_PRESERVED=true")
    print("RUNTIME_BINDING_CREATED=false")
    print("RUNTIME_ENFORCEMENT_PROVEN=false")
    print("AUTHORIZATION_CREATED=false")
    print("EXECUTION_PERFORMED=false")
    print("S10=REPLAY_REQUIRED")
    print("FL_B3=BLOCKED_PENDING_CONSOLIDATION_AND_INDEPENDENT_S10_REPLAY")
    print("P160B_OPENED=false")
    print("NEXT=" + d["next_required_step"])
    print("LAYER_SHA256=" + lh)
    print("RECEIPT_SHA256=" + rh)

if __name__ == "__main__":
    main()

from pathlib import Path
import json, hashlib, os, tempfile

ROOT = Path.home() / "open-cognitive-ecology"
DOSSIER = ROOT / "validation_artifacts/p159/occ1k_r9v/governed_direct_binding_adoption_dossier_v1.json"
OUTDIR = ROOT / "validation_artifacts/p159/occ1k_r9w"
LAYER = OUTDIR / "governed_direct_rule_consumer_binding_layer_v1.json"
RECEIPT = OUTDIR / "atomic_governed_direct_binding_commit_receipt_v1.json"
TOKEN = "I_CONFIRM_R9V_ADOPT_DIRECT_BINDINGS_ONLY"

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

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

def build_layer():
    d = load(DOSSIER)
    if d.get("status") != "HUMAN_GOVERNED_DIRECT_BINDING_ADOPTION_DECISION_REQUIRED":
        raise RuntimeError("R9V_DOSSIER_NOT_DECISION_READY")
    direct = d.get("direct_candidates", [])
    deferred = d.get("deferred", [])
    if len(direct) != 6 or len(deferred) != 15:
        raise RuntimeError("R9V_PARTITION_MISMATCH")
    bindings = []
    seen = set()
    for item in direct:
        consumers = list(item.get("proposed_consumers", []))
        if not consumers:
            raise RuntimeError("DIRECT_BINDING_WITHOUT_CONSUMER")
        for rid in item.get("rule_ids", []):
            if rid in seen:
                raise RuntimeError("DUPLICATE_DIRECT_RULE:" + rid)
            seen.add(rid)
            bindings.append({
                "rule_id": rid,
                "subgroup_id": item["subgroup_id"],
                "source_object_id": item.get("source_object_id"),
                "consumers": consumers,
                "evidence_ids": list(item.get("evidence_ids", [])),
                "binding_basis": "R9U_DIRECT_SEMANTIC_ROLE_MATCH",
                "governance_basis": "R9V_HUMAN_CONFIRMED_ADOPT_DIRECT_BINDINGS_ONLY"
            })
    if len(bindings) != 9:
        raise RuntimeError("DIRECT_RULE_COUNT_MISMATCH")
    return {
        "schema": "oce.p159.occ1k.r9w.governed.direct.rule.consumer.binding.layer.v1",
        "milestone": "P159/OCC-1K-R9W",
        "status": "COMMITTED",
        "decision": "ADOPT_DIRECT_BINDINGS_ONLY",
        "input_r9v_sha256": sha(DOSSIER),
        "bindings": sorted(bindings, key=lambda x: x["rule_id"]),
        "counts": {
            "direct_subgroups_adopted": 6,
            "direct_rules_adopted": 9,
            "deferred_subgroups_preserved": 15
        },
        "preservation": {
            "history_preserved": True,
            "retroactive_repair": False,
            "contextual_cases_not_promoted": True,
            "unresolved_cases_not_promoted": True
        },
        "boundaries": {
            "cnp_modified": False,
            "runtime_binding_created": False,
            "runtime_enforcement_proven": False,
            "authorization_created": False,
            "execution_performed": False,
            "fl_b3": "BLOCKED_PENDING_RESIDUAL_RESOLUTION_AND_CHECKER_REPLAY",
            "lock_ready": False,
            "lock_granted": False,
            "p160b_opened": False
        },
        "next_required_step": "R9X_CONTEXTUAL_BINDING_SEMANTIC_REVIEW",
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True
    }

def commit(confirm):
    if confirm != TOKEN:
        raise RuntimeError("EXPLICIT_CONFIRMATION_REQUIRED")
    layer = build_layer()
    lb = canonical_bytes(layer)
    receipt = {
        "schema": "oce.p159.occ1k.r9w.atomic.governed.direct.binding.commit.receipt.v1",
        "milestone": "P159/OCC-1K-R9W",
        "status": "COMMITTED",
        "decision": "ADOPT_DIRECT_BINDINGS_ONLY",
        "confirmation_token_verified": True,
        "r9v_dossier_sha256": sha(DOSSIER),
        "binding_layer_sha256": hashlib.sha256(lb).hexdigest(),
        "history_preserved": True,
        "retroactive_repair": False,
        "runtime_binding_created": False,
        "runtime_enforcement_proven": False,
        "authorization_created": False,
        "execution_performed": False,
        "p160b_opened": False
    }
    rb = canonical_bytes(receipt)
    for path, data in ((LAYER, lb), (RECEIPT, rb)):
        if path.exists() and path.read_bytes() != data:
            raise RuntimeError("DIVERGENT_EXISTING_ARTIFACT:" + str(path))
    atomic_write(LAYER, lb)
    atomic_write(RECEIPT, rb)
    return layer, receipt, hashlib.sha256(lb).hexdigest(), hashlib.sha256(rb).hexdigest()

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", required=True)
    args = ap.parse_args()
    layer, receipt, lh, rh = commit(args.confirm)
    c = layer["counts"]
    print("P159_OCC1K_R9W_ATOMIC_GOVERNED_DIRECT_BINDING_COMMIT_COMPLETE")
    print("STATUS=COMMITTED")
    print("DECISION=ADOPT_DIRECT_BINDINGS_ONLY")
    print("DIRECT_SUBGROUPS_ADOPTED=%d/6" % c["direct_subgroups_adopted"])
    print("DIRECT_RULES_ADOPTED=%d/9" % c["direct_rules_adopted"])
    print("DEFERRED_SUBGROUPS_PRESERVED=%d/15" % c["deferred_subgroups_preserved"])
    print("HISTORY_PRESERVED=true")
    print("RETROACTIVE_REPAIR=false")
    print("CONTEXTUAL_CASES_PROMOTED=false")
    print("RUNTIME_BINDING_CREATED=false")
    print("RUNTIME_ENFORCEMENT_PROVEN=false")
    print("AUTHORIZATION_CREATED=false")
    print("EXECUTION_PERFORMED=false")
    print("FL_B3=BLOCKED_PENDING_RESIDUAL_RESOLUTION_AND_CHECKER_REPLAY")
    print("P160B_OPENED=false")
    print("NEXT=" + layer["next_required_step"])
    print("LAYER_SHA256=" + lh)
    print("RECEIPT_SHA256=" + rh)

if __name__ == "__main__":
    main()

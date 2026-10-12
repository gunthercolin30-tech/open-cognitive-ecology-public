from pathlib import Path
from ontology.governed_isolated_probe_runner import run_isolated_generated_probe, as_completed_process
from ontology.bounded_filesystem_validation_context import BoundedFilesystemValidationContext
import hashlib, json, shutil, sys, tempfile

SCHEMA = "oce.p159.occ1h.a075.independent_anchor_rebinding_probe.v2"
HISTORICAL_VERIFIER_SHA256 = "dfd4aa673abb58a08d9970a9d320f5efee7d4409173f985a1f1cce1af87f90f0"
CURRENT_BUILDER_SHA256 = "b1e0ad044f6c2f59c37e71e6b03519c4d707e2b50d9b7e8ba187437b5d964828"
HISTORICAL_BUILDER_SHA256 = "0ae2b0e5728f1db3b9a07cdef16fd553a5a9e45efaf68fe6dee82e797a1d35b4"

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _copy(root, sandbox, rel, filesystem_context):
    src, dst = root / rel, sandbox / rel
    if src.is_file():
        filesystem_context.copy2_from(src, dst.relative_to(filesystem_context.root))
        return
    if src.is_dir():
        filesystem_context.copytree_from(src, dst.relative_to(filesystem_context.root))
        return
    raise RuntimeError("A075_REQUIRED_INPUT_MISSING:" + rel)

def _result(classification, reason, observations):
    result = {
        "schema": SCHEMA, "scenario": "A075", "classification": classification,
        "reason": reason, "observations": observations,
        "historical_evidence_rewritten": False, "occ1f_modified": False,
        "authorization_created": False, "execution_performed": False,
        "functional_only": True, "phenomenology_undetermined": True,
        "occ1h_closed": False, "occ1i_opened": False,
        "p159_final_lock": False, "p160_opened": False,
    }
    result["evidence_sha256"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    return result

def _child(sandbox, mode):
    child = sandbox / ("a075_" + mode + "_child.py")
    child.write_text(
        """import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(root))
from ontology import occ_independent_constitutional_verifier as v
from ontology import occ_independent_constitutional_verification_report as r
def sh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
vp=root/"ontology"/"occ_independent_constitutional_verifier.py"
tcb=root/r.COMMON_TCB_REL
reg=root/r.CHECK_REGISTRY_REL
mode=sys.argv[2]
out={"loaded_from_sandbox":Path(v.__file__).resolve()==vp.resolve(),
     "loaded_verifier_sha256":sh(Path(v.__file__).resolve()),
     "verify":r.verify_preclose_evidence(root)}
if mode=="attack":
    out["old_tcb_sha256"]=sh(tcb); out["old_registry_sha256"]=sh(reg)
    try:
        r.materialize_preclose_evidence(root); out["rematerialize"]="SUCCEEDED"
    except Exception as e:
        out["rematerialize"]="REJECTED"
        out["rematerialize_error"]=type(e).__name__+":"+str(e)
    out["post"]=r.verify_preclose_evidence(root)
    out["new_tcb_sha256"]=sh(tcb) if tcb.is_file() else None
    out["new_registry_sha256"]=sh(reg) if reg.is_file() else None
    td=json.loads(tcb.read_text()); rd=json.loads(reg.read_text())
    out["tcb_bound_verifier_sha256"]=td.get("verifier_identity",{}).get("file_sha256")
    out["registry_bound_verifier_sha256"]=rd.get("verifier_identity",{}).get("file_sha256")
print(json.dumps(out,sort_keys=True))
""", encoding="utf-8")
    cp = as_completed_process(run_isolated_generated_probe(script=child, sandbox=sandbox, args=(mode,), timeout_seconds=30))
    if cp.returncode != 0:
        return {"child_failed": True, "returncode": cp.returncode, "stderr": cp.stderr[-2000:]}
    return json.loads(cp.stdout.strip().splitlines()[-1])

def run(root):
    root = Path(root)
    inv = root / "ontology_inventory.txt"
    if not inv.is_file():
        raise RuntimeError("ONTOLOGY_INVENTORY_MISSING")
    inventory = inv.read_text(encoding="utf-8", errors="replace")
    for primitive in ("occ_independent_constitutional_verifier",
                      "occ_independent_constitutional_verification_report"):
        if primitive not in inventory:
            raise RuntimeError("ONTOLOGY_INVENTORY_PRIMITIVE_MISSING:" + primitive)

    verifier = root / "ontology/occ_independent_constitutional_verifier.py"
    builder = root / "ontology/occ_normative_ir_real_builder.py"
    historical_builder = root / "ontology/occ_normative_ir_real_builder.py.bak"
    if sha(verifier) != HISTORICAL_VERIFIER_SHA256:
        return _result("INCONCLUSIVE", "INCUMBENT_VERIFIER_IDENTITY_DRIFT_BEFORE_EXPERIMENT",
                       {"observed_verifier_sha256": sha(verifier)})
    if sha(builder) != CURRENT_BUILDER_SHA256:
        return _result("INCONCLUSIVE", "CURRENT_BUILDER_IDENTITY_DRIFT_BEFORE_EXPERIMENT",
                       {"observed_builder_sha256": sha(builder)})
    if not historical_builder.is_file() or sha(historical_builder) != HISTORICAL_BUILDER_SHA256:
        return _result("INCONCLUSIVE", "HISTORICAL_BUILDER_FIXTURE_UNAVAILABLE_OR_DRIFTED", {})

    from ontology import occ_independent_constitutional_verifier as incumbent
    closure = [
        "ontology/dna_adversarial_regression.py","ontology/dna_fitness_suite.py",
        "ontology/dna_fundamental.py","ontology/dna_inheritance.py",
        "ontology/dna_mutation_protocol.py","ontology/dna_registry.py",
        "ontology/dna_rule_contract.py","ontology/dna_severity_model.py",
        "ontology/dna_stack.py","ontology/dna_versioning_lineage.py",
        "ontology/minimal_dna.py","ontology/normative_hierarchy.py",
        "ontology/occ_independent_constitutional_verification_report.py",
        "ontology/occ_independent_constitutional_verifier.py",
        "ontology/occ_normative_ir.py","ontology/occ_normative_ir_real_builder.py",
        "validation_artifacts/p159/occ1f/common_tcb_manifest_v1.json",
        "validation_artifacts/p159/occ1f/verifier_check_registry_v1.json",
    ]
    for path in incumbent.paths(root).values():
        if path.exists():
            closure.append(str(path.relative_to(root)))

    filesystem_context = BoundedFilesystemValidationContext(prefix="oce-a075-anchor-v2-")
    temp = filesystem_context.root
    sandbox = temp / "repo"
    try:
        for rel in sorted(set(closure)):
            _copy(root, sandbox, rel, filesystem_context)

        # Remove the already-known current-builder drift from the fixture only.
        sandbox_builder = sandbox / "ontology/occ_normative_ir_real_builder.py"
        filesystem_context.copy2_from(historical_builder,sandbox_builder.relative_to(filesystem_context.root))
        if sha(sandbox_builder) != HISTORICAL_BUILDER_SHA256:
            raise RuntimeError("A075_HISTORICAL_BUILDER_FIXTURE_COPY_FAILED")

        # Mandatory control: historical fixture must verify before verifier substitution.
        control = _child(sandbox, "control")
        if control.get("child_failed"):
            return _result("INCONCLUSIVE", "HISTORICAL_CONTROL_CHILD_FAILED", {"control": control})
        if control.get("loaded_from_sandbox") is not True:
            return _result("INCONCLUSIVE", "HISTORICAL_CONTROL_NOT_LOADED_FROM_SANDBOX", {"control": control})
        if control.get("loaded_verifier_sha256") != HISTORICAL_VERIFIER_SHA256:
            return _result("INCONCLUSIVE", "HISTORICAL_CONTROL_VERIFIER_IDENTITY_MISMATCH", {"control": control})
        if control.get("verify", {}).get("status") != "VERIFIED_PRECLOSE_BINDING":
            return _result("INCONCLUSIVE", "HISTORICAL_FIXTURE_NOT_VERIFIED_BEFORE_SUBSTITUTION",
                           {"control": control})

        # Controlled verifier identity drift in sandbox only.
        vp = sandbox / "ontology/occ_independent_constitutional_verifier.py"
        original = vp.read_text(encoding="utf-8")
        marker = 'lm.get("self_activation") is False'
        if marker not in original:
            return _result("INCONCLUSIVE", "CONTROLLED_WEAKENING_MARKER_MISSING", {"control": control})
        vp.write_text(original.replace(marker, "True", 1), encoding="utf-8")
        replacement_sha = sha(vp)
        if replacement_sha == HISTORICAL_VERIFIER_SHA256:
            raise RuntimeError("A075_FIXTURE_IDENTITY_NOT_CHANGED")

        attack = _child(sandbox, "attack")
        if attack.get("child_failed"):
            return _result("INCONCLUSIVE", "ATTACK_CHILD_FAILED",
                           {"control": control, "attack": attack})
        attack["fixture_v2_sha256"] = replacement_sha
        observations = {"control": control, "attack": attack}

        loaded = (attack.get("loaded_from_sandbox") is True and
                  attack.get("loaded_verifier_sha256") == replacement_sha)
        pre_rejected = attack.get("verify", {}).get("status") == "REJECTED"
        rewritten = (attack.get("old_tcb_sha256") != attack.get("new_tcb_sha256") or
                     attack.get("old_registry_sha256") != attack.get("new_registry_sha256"))
        rebound = (attack.get("tcb_bound_verifier_sha256") == replacement_sha and
                   attack.get("registry_bound_verifier_sha256") == replacement_sha)
        post_verified = attack.get("post", {}).get("status") == "VERIFIED_PRECLOSE_BINDING"

        if loaded and pre_rejected and attack.get("rematerialize") == "SUCCEEDED" and rewritten and rebound and post_verified:
            return _result("ASSURANCE_GAP",
                "CURRENT_PRECLOSE_BINDING_CAN_BE_REBOUND_TO_REPLACEMENT_IDENTITY_WITHIN_SAME_TRUST_CHAIN",
                observations)
        if loaded and pre_rejected and attack.get("rematerialize") == "REJECTED" and not post_verified:
            return _result("RESISTED",
                "REPLACEMENT_IDENTITY_REFUSED_AFTER_VERIFIED_HISTORICAL_CONTROL",
                observations)
        return _result("INCONCLUSIVE", "EXPERIMENT_DID_NOT_DISCRIMINATE_ANCHOR_INDEPENDENCE",
                       observations)
    finally:
        filesystem_context.remove_tree()

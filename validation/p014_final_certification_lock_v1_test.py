from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"validation"/"evidence"/"w0_w3_r14_semantic_review"
cert=json.loads((E/"p014_final_certification_v1.json").read_text())
lock=json.loads((E/"p014_final_lock_v1.json").read_text())
assert cert["canonical_objects"]==cert["bound_objects"]==59
assert cert["unbound_objects"]==0 and cert["duplicate_objects"]==0
assert len(cert["objects"])==59 and len({x["id"] for x in cert["objects"]})==59
assert all(x["status"]=="BOUND" and x["implementation_symbols"] for x in cert["objects"])
paths={"core":ROOT/"ontology"/"p014_supply_chain_sovereignty.py",
"complete_test":ROOT/"validation"/"p014_canonical_rebuild_complete_test.py",
"adversarial_test":ROOT/"validation"/"p014_adversarial_crown_v1_test.py",
"certification":E/"p014_final_certification_v1.json"}
for k,p in paths.items():
    assert hashlib.sha256(p.read_bytes()).hexdigest()==lock["protected_hashes"][k]
assert lock["status"]=="LOCKED" and lock["canonical_compliance_proven"] is True
assert lock["functional_only"] is True and lock["phenomenology_undetermined"] is True
print("P014_FINAL_CERTIFICATION_59_59_OK")
print("canonical_objects=59")
print("bound_objects=59")
print("unbound_objects=0")
print("P014_FINAL_LOCK_OK")

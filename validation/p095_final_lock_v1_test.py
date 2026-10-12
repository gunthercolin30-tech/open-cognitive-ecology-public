from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ontology.human_reserved_authority_registry import P095Canonical
E=ROOT/"validation"/"evidence"/"w0_w3_r19_semantic_review"
lock=json.loads((E/"p095_final_lock_v1.json").read_text(encoding="utf-8"))
c=P095Canonical().canonical_contract()
assert lock["status"]=="LOCKED"
assert lock["milestone"]=="P095"
assert lock["r19_requirements"]==67
assert lock["canonical_objects_total"]==76
assert lock["adversarial_cases"]==29
assert lock["functional_test"]=="PASS"
assert lock["degradation_test"]=="PASS"
assert lock["non_regression_test"]=="PASS"
assert lock["adversarial_crown"]=="PASS"
assert lock["functional_only"] is True
assert lock["phenomenology_undetermined"] is True
assert lock["production_modified_by_lock"] is False
assert c["r19_count"]==67 and c["canonical_object_count"]==76
assert c["functional_only"] is True and c["phenomenology_undetermined"] is True
for rel,digest in lock["protected_hashes"].items():
    p=ROOT/rel
    assert p.is_file()
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
print("P095_FINAL_LOCK_V1_OK")
print("status=LOCKED")
print("r19_requirements=67")
print("canonical_objects_total=76")
print("adversarial_cases=29")
print("functional_only=true")
print("phenomenology_undetermined=true")

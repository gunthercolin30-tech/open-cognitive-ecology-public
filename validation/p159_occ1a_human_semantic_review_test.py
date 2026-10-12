from pathlib import Path
import json,tempfile,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_human_semantic_review as r
w=r.build_workbook(ROOT)
assert len(w["entries"])==23 and len({e["canonical_id"] for e in w["entries"]})==23;print("P159_OCC1A_HUMAN_REVIEW_23_TARGETS_OK")
assert all(e["candidate"]["historical_id"] is None and e["candidate"]["candidate_definition"] is None for e in w["entries"]);print("P159_OCC1A_HUMAN_REVIEW_ZERO_PREASSIGNMENT_OK")
r.validate_integrity(ROOT,w);print("P159_OCC1A_HUMAN_REVIEW_SOURCE_HASH_BINDING_OK")
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/"w.json";p.write_text(json.dumps(w),encoding="utf-8");cid=w["entries"][0]["candidate_id"]
 try:r.save_decision(ROOT,p,cid,"ACCEPT_CANDIDATE","human","principal_investigator","Justification humaine suffisamment longue.")
 except ValueError:print("P159_OCC1A_HUMAN_REVIEW_EMPTY_ACCEPT_FAIL_CLOSED_OK")
 else:raise AssertionError
 x=r.save_decision(ROOT,p,cid,"UNRESOLVED","human","principal_investigator","Les sources ne permettent pas encore une affectation exacte.");assert not x["adoption_performed"];print("P159_OCC1A_HUMAN_REVIEW_UNRESOLVED_OK")
 t=json.loads(p.read_text());t["entries"][0]["candidate"]["historical_id"]="F1"
 try:r.validate_integrity(ROOT,t)
 except ValueError:print("P159_OCC1A_HUMAN_REVIEW_IMMUTABLE_CANDIDATE_OK")
 else:raise AssertionError
assert w["genesis_review"]["pdf_extraction_must_not_define_machine_semantics"];print("P159_OCC1A_HUMAN_REVIEW_GENESIS_SEPARATE_OK")
m=r.manifest();assert not m["occ1a_closed"] and not m["occ1b_opened"] and not m["p160_opened"];assert m["functional_conclusion_only"] and m["phenomenology_undetermined"];print("P159_OCC1A_HUMAN_REVIEW_SCOPE_EPISTEMIC_OK")
print("P159_OCC1A_HUMAN_SEMANTIC_REVIEW_OK")

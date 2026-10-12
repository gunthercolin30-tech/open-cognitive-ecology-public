from pathlib import Path
import hashlib,json,shutil,tempfile
from ontology import occ_semantic_binding as q
ROOT=Path(__file__).resolve().parents[1]

def main():
 watched=[ROOT/q.PROPOSALS,ROOT/q.LEDGER,ROOT/"normative/occ1a/manifest.yaml",ROOT/"normative/occ1a/dna/dna_h.yaml",ROOT/"normative/occ1a/dna/dna_l0.yaml",ROOT/"normative/occ1a/dna/dna_l1.yaml"]
 before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
 m=q.manifest(ROOT)
 after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
 assert before==after
 assert m["target_count"]==48 and m["explicit_disposition_count"]==48 and not m["unresolved_ids"],m
 assert m["direct_ccad_bindings"]==24
 assert m["governed_adopted_dna_bindings"]==17
 assert m["protected_constitutive_l0_bindings"]==6
 assert m["human_judgment_required_bindings"]==1
 assert m["invented_bindings"]==0
 print("P159_OCC1A_CANONICAL_SEMANTIC_BINDING_48_DISPOSITION_OK")
 rows={x["canonical_id"]:x for x in m["bindings"]}
 assert rows["GENESIS.G0"]["binding_status"]==q.HUMAN_REQUIRED and rows["GENESIS.G0"]["text"] is None
 print("P159_OCC1A_CANONICAL_SEMANTIC_BINDING_GENESIS_NO_INVENTION_OK")
 assert all(rows[f"DNA.L0.{i}"]["binding_status"]==q.PROTECTED_CONSTITUTIVE for i in range(1,7))
 assert all(rows[f"DNA.L0.{i}"]["ordinary_adoption_applicable"] is False for i in range(1,7))
 print("P159_OCC1A_CANONICAL_SEMANTIC_BINDING_L0_PROTECTED_NOT_ADOPTED_OK")
 assert m["h9_f12_f17_distinct"] is True and m["f18_bound_to_h9"] is False
 print("P159_OCC1A_CANONICAL_SEMANTIC_BINDING_H9_F12_F17_F18_EXCLUDED_OK")
 assert not m["package_population_performed"] and not m["source_lineage_resolved"] and not m["package_state_changed"]
 assert not m["authority_activated"] and not m["execution_performed"] and not m["occ1a_closed"] and not m["occ1b_opened"] and not m["p160_opened"]
 print("P159_OCC1A_CANONICAL_SEMANTIC_BINDING_STAGE_BOUNDARY_OK")
 with tempfile.TemporaryDirectory() as td:
  t=Path(td); rels=[q.PROPOSALS,q.LEDGER]
  for rel in rels:
   d=t/rel; d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/rel,d)
  x=json.loads((t/q.LEDGER).read_text()); x["transaction"]["events"]=x["transaction"]["events"][:-1]
  (t/q.LEDGER).write_text(json.dumps(x),encoding="utf-8")
  mm=q.manifest(t)
  assert mm["governed_adopted_dna_bindings"]<17 and mm["semantic_disposition_complete"] is False
 print("P159_OCC1A_CANONICAL_SEMANTIC_BINDING_LEDGER_DEGRADATION_OK")
 with tempfile.TemporaryDirectory() as td:
  t=Path(td); d=t/q.PROPOSALS; d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/q.PROPOSALS,d)
  d2=t/q.LEDGER; d2.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/q.LEDGER,d2)
  x=json.loads(d.read_text()); del x["proposals"]["DNA.L0.1"]; d.write_text(json.dumps(x),encoding="utf-8")
  mm=q.manifest(t); assert "DNA.L0.1" in mm["unresolved_ids"]
 print("P159_OCC1A_CANONICAL_SEMANTIC_BINDING_MISSING_L0_PROVENANCE_FAIL_CLOSED_OK")
 assert q.manifest(ROOT)==q.manifest(ROOT)
 print("P159_OCC1A_CANONICAL_SEMANTIC_BINDING_DETERMINISM_OK")
 print("explicit_disposition_count=48")
 print("governed_adopted_dna_bindings=17")
 print("protected_constitutive_l0_bindings=6")
 print("human_judgment_required_bindings=1")
 print("direct_ccad_bindings=24")
 print("package_population_performed=false")
 print("occ1a_closed=false")
if __name__=="__main__":main()

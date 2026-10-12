from pathlib import Path
import hashlib,json,shutil,tempfile
from ontology import occ_source_lineage_binding as q
from ontology import occ_semantic_binding as semantic
ROOT=Path(__file__).resolve().parents[1]

def copy_rel(srcroot,dstroot,rel):
 p=srcroot/rel
 d=dstroot/rel; d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,d)

def main():
 sm=semantic.manifest(ROOT)
 rels=set()
 for b in sm["bindings"]:
  for k in ("source_path","historical_source_path","adoption_evidence_path"):
   if b.get(k): rels.add(b[k])
 watched=[ROOT/x for x in rels]+[ROOT/"normative/occ1a/manifest.yaml"]
 before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
 m=q.manifest(ROOT)
 after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
 assert before==after
 assert m["target_count"]==48 and m["lineage_verified_count"]==48 and m["source_lineage_resolved"] is True,m
 print("P159_OCC1A_SOURCE_LINEAGE_BINDING_48_VERIFIED_OK")
 assert m["genesis_lineage_verified"] is True and m["genesis_machine_formalization_claimed"] is False
 print("P159_OCC1A_SOURCE_LINEAGE_BINDING_GENESIS_NO_FORMALIZATION_INVENTION_OK")
 assert not m["package_population_performed"] and not m["package_state_changed"]
 assert not m["authority_activated"] and not m["execution_performed"] and not m["occ1a_closed"] and not m["occ1b_opened"] and not m["p160_opened"]
 print("P159_OCC1A_SOURCE_LINEAGE_BINDING_STAGE_BOUNDARY_OK")
 # Missing source artifact must fail closed.
 with tempfile.TemporaryDirectory() as td:
  t=Path(td)
  for rel in rels: copy_rel(ROOT,t,rel)
  victim=next(x for x in rels if x.endswith("ccad_specification.py"))
  (t/victim).unlink()
  mm=q.manifest(t)
  assert mm["source_lineage_resolved"] is False and any(x.startswith("CCAD.") for x in mm["unresolved_lineage_ids"])
 print("P159_OCC1A_SOURCE_LINEAGE_BINDING_MISSING_SOURCE_FAIL_CLOSED_OK")
 # Tampered source remains a different lineage hash, not silently equivalent.
 base={x["canonical_id"]:x for x in m["lineages"]}
 with tempfile.TemporaryDirectory() as td:
  t=Path(td)
  for rel in rels: copy_rel(ROOT,t,rel)
  p=t/"ontology/ccad_specification.py"; p.write_bytes(p.read_bytes()+b"\n# tamper\n")
  mm=q.manifest(t); alt={x["canonical_id"]:x for x in mm["lineages"]}
  a=next(z["sha256"] for z in base["CCAD.P0"]["artifacts"] if z["path"]=="ontology/ccad_specification.py")
  b=next(z["sha256"] for z in alt["CCAD.P0"]["artifacts"] if z["path"]=="ontology/ccad_specification.py")
  assert a!=b
 print("P159_OCC1A_SOURCE_LINEAGE_BINDING_TAMPER_HASH_VISIBLE_OK")
 assert q.manifest(ROOT)==q.manifest(ROOT)
 print("P159_OCC1A_SOURCE_LINEAGE_BINDING_DETERMINISM_OK")
 print("lineage_verified_count=48")
 print("source_lineage_resolved=true")
 print("package_population_performed=false")
 print("occ1a_closed=false")
if __name__=="__main__":main()

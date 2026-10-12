import json
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology import dna_versioning_lineage as d

with TemporaryDirectory() as td:
 p=Path(td)/"lineage.json"
 x=d.create_lineage("INST",d.INSTITUTION,"DNA-A",provenance="corrupt")
 x=d.migrate_lineage(x,migration_id="M1",to_DNA="DNA-B",mutation_ref="P021:M1",evidence_refs=("EV",),authority_ref="AUTH",provenance="corrupt")
 d.save_lineage(p,x)
 good=json.loads(p.read_text())

 variants=[]
 q=dict(good); q["created_under_DNA"]="DNA-X"; variants.append(q)
 q=dict(good); q["current_DNA"]="DNA-X"; variants.append(q)
 q=dict(good); q["migration_history"]=[]; variants.append(q)
 q=dict(good); q["entity_type"]="institution"; variants.append(q)
 q=dict(good); q["unexpected"]="x"; variants.append(q)

 for i,payload in enumerate(variants):
  p.write_text(json.dumps(payload),encoding="utf-8")
  try: d.load_lineage(p)
  except (ValueError,KeyError,TypeError): pass
  else: raise AssertionError("corrupt_persistence_accepted:"+str(i))

 p.write_text("{broken",encoding="utf-8")
 try: d.load_lineage(p)
 except json.JSONDecodeError: pass
 else: raise AssertionError("invalid_json_accepted")

print("P022_PERSISTENCE_CORRUPTION_TEST_OK")

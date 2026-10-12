from copy import deepcopy
from ontology import dna_versioning_lineage as d

base=d.create_lineage("E1",d.CRITICAL_COMPONENT,"DNA-A",provenance="adv")
m1=d.migrate_lineage(base,migration_id="M1",to_DNA="DNA-B",mutation_ref="P021:M1",evidence_refs=("EV1",),authority_ref="AUTH1",provenance="adv")
m2=d.migrate_lineage(m1,migration_id="M2",to_DNA="DNA-C",mutation_ref="P021:M2",evidence_refs=("EV2",),authority_ref="AUTH2",provenance="adv")

cases=[]
x=deepcopy(m2); x["created_under_DNA"]="DNA-X"; cases.append(x)
x=deepcopy(m2); x["current_DNA"]="DNA-B"; cases.append(x)
x=deepcopy(m2); x["migration_history"]=(x["migration_history"][1],x["migration_history"][0]); cases.append(x)
x=deepcopy(m2); x["migration_history"]=(x["migration_history"][1],); cases.append(x)
x=deepcopy(m2); x["migration_history"]=x["migration_history"][:1]; cases.append(x)
x=deepcopy(m2); h=list(x["migration_history"]); h[1]=deepcopy(h[1]); h[1]["from_DNA"]="DNA-X"; x["migration_history"]=tuple(h); cases.append(x)

for i,bad in enumerate(cases):
 try: d.validate_lineage(bad)
 except ValueError: pass
 else: raise AssertionError("adversarial_lineage_accepted:"+str(i))

for bad_type in ("Individual","institution","critical_component","UNKNOWN",""):
 try: d.create_lineage("E",bad_type,"DNA-A",provenance="adv")
 except ValueError: pass
 else: raise AssertionError("lexical_near_miss_entity_type_accepted")

print("P022_ADVERSARIAL_TEST_OK")

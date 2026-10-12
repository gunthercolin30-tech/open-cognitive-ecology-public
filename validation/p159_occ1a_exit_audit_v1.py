from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
EXPECTED=["GENESIS.G0"]+[f"DNA.H{i}" for i in range(1,10)]+[f"DNA.L0.{i}" for i in range(1,7)]+[f"DNA.L1.{i}" for i in range(1,9)]+[f"CCAD.P{i}" for i in range(14)]+[f"CCAD.AR{i}" for i in range(1,11)]
PARTS=["genesis/genesis.yaml","dna/dna_h.yaml","dna/dna_l0.yaml","dna/dna_l1.yaml","ccad/ccad_principles.yaml","ccad/ccad_arbitration_rules.yaml","ccad/ccad_states.yaml","ccad/ccad_conflict_classes.yaml","constitution/constitution.yaml","governance/governance.yaml","policy/policy_index.yaml"]
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(root=ROOT):
 pkg=root/"normative/occ1a"; regp=root/"oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json"
 m=load(pkg/"manifest.yaml"); lin=load(pkg/"provenance/source_lineage.yaml"); reg=load(regp)
 checks={}
 checks["manifest_48_target_ids"]=m.get("kernel_target",{}).get("principal_object_count")==48 and m.get("kernel_target",{}).get("ids")==EXPECTED
 checks["package_draft_shadow_only"]=m.get("package_state")=="DRAFT" and m.get("shadow_test_only") is True
 checks["kernel_binding_unresolved"]=m.get("kernel_population_status")=="UNRESOLVED_PENDING_EXPLICIT_SEMANTIC_BINDING"
 checks["lineage_binding_unresolved"]=lin.get("kernel_semantic_binding_status")=="UNRESOLVED"
 part={}; populated=[]
 for rel in PARTS:
  d=load(pkg/rel); norms=d.get("norms",[])
  part[rel]={"population_status":d.get("population_status"),"package_state":d.get("package_state"),"norm_count":len(norms)}
  populated += [n.get("id") for n in norms if isinstance(n,dict)]
 checks["all_partitions_present"]=len(part)==len(PARTS)
 checks["principal_kernel_populated_exactly"]=sorted(x for x in populated if x in EXPECTED)==sorted(EXPECTED)
 proposals=reg.get("proposals",{})
 checks["23_governed_proposals_present"]=len(proposals)==23
 checks["proposals_not_adopted"]=len(proposals)==23 and all(v.get("status")=="PROPOSED_NOT_ADOPTED" and v.get("adoption_performed") is False and v.get("activation_performed") is False and v.get("execution_performed") is False for v in proposals.values())
 checks["f18_not_numbered_dna"]=all("F18" not in v.get("evidence_ids",[]) for v in proposals.values())
 checks["stage_boundaries_preserved"]=reg.get("occ1a_closed") is False and reg.get("occ1b_opened") is False and reg.get("p160_opened") is False
 blockers=[]
 if not checks["principal_kernel_populated_exactly"]: blockers.append("CANONICAL_PACKAGE_PRINCIPAL_KERNEL_NOT_POPULATED")
 if checks["kernel_binding_unresolved"]: blockers.append("KERNEL_SEMANTIC_BINDING_STILL_UNRESOLVED")
 if checks["lineage_binding_unresolved"]: blockers.append("SOURCE_LINEAGE_BINDING_STILL_UNRESOLVED")
 if checks["proposals_not_adopted"]: blockers.append("23_DNA_BINDINGS_ARE_PROPOSED_NOT_ADOPTED")
 if m.get("package_state")=="DRAFT": blockers.append("CANONICAL_PACKAGE_STATE_DRAFT")
 decision="READY_TO_CLOSE_OCC1A" if not blockers else "OCC1A_REMAINS_OPEN"
 return {"schema":"oce.p159.occ1a.exit_audit.v1","decision":decision,"blockers":blockers,"checks":checks,"partition_population":part,"target_count":len(EXPECTED),"populated_principal_count":len(set(populated)&set(EXPECTED)),"proposal_count":len(proposals),"registry_sha256":sha(regp),"manifest_sha256":sha(pkg/"manifest.yaml"),"adoption_performed":False,"activation_performed":False,"execution_performed":False,"occ1b_opened":False,"p160_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def main():
 r=audit()
 print("P159_OCC1A_EXIT_AUDIT_V1_OK");print("decision="+r["decision"]);print("target_count="+str(r["target_count"]));print("populated_principal_count="+str(r["populated_principal_count"]));print("proposal_count="+str(r["proposal_count"]))
 for b in r["blockers"]: print("BLOCKER="+b)
 print("adoption_performed=false");print("activation_performed=false");print("execution_performed=false");print("occ1b_opened=false");print("p160_opened=false")
if __name__=="__main__": main()

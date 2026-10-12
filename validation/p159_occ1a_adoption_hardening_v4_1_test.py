from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_norm_adoption_event as o
from ontology import human_reserved_authority_registry as p095
def ck(v,n):
 if not v:raise AssertionError(n)
 print(n)
def registry():
 r=p095.P095Canonical()
 a=p095.HumanAuthority("A1","human-1",True,"constitutional_authority","OCC1A",("CONSTITUTIONAL_CHANGE",),("P159_OCC1A_NORM_ADOPTION",),0,9999999999,"C1","G1")
 e=p095.ReservedEntry("R1","CONSTITUTIONAL_CHANGE",("OCC1A",),("constitutional_authority",),1,1,False,9999999999)
 assert r.register_authority(a)["status"]==p095.PASS
 assert r.register_reserved(e)["status"]==p095.PASS
 return r
def evidence(rec):
 return {"proposal":True,"rationale":True,"incompatibility_analysis":True,"rights_impact":True,"adversarial_review":True,"long_form_human_governance":True,"fork_or_migration_decision":True,"provenance":True,"proposal_hash":rec["proposal_hash"],"registered_proposal_seal":rec["registered_proposal_seal"]}
def bind(raw,cid):
 p=raw["proposals"][cid]
 return o.bind_registered_proposal(cid,proposal_hash=p["proposal_hash"],dossier_hash=p["dossier_hash"],evidence_snapshot_hash=p["evidence_snapshot_hash"],candidate_definition=p["candidate_definition"],evidence_ids=p["evidence_ids"],root=ROOT)["record"]
def main():
 regpath=ROOT/o.REG_REL;before=regpath.read_bytes();raw=json.loads(before.decode())
 r1=bind(raw,"DNA.H1");rl0=bind(raw,"DNA.L0.1")
 fakea={"status":p095.PASS,"authority_proof_valid":True,"registered_proposal_seal":r1["registered_proposal_seal"],"authority_proof_hash":"a"*64}
 fakeu={"accepted":True,"p106_status":"ADMISSIBLE_FOR_DECISION","registered_proposal_seal":r1["registered_proposal_seal"],"amendment_proof_hash":"b"*64}
 q=o.build_adoption_decision(r1,fakea,fakeu,"D-FORGE","2026-09-23T00:00:00Z")
 ck(q.get("status")!="PASS" and q.get("reason")=="CALLER_SUPPLIED_PROOFS_NOT_AUTHORITATIVE","P159_OCC1A_HARDEN_V4_FORGED_PROOF_DICTS_REJECT_OK")
 q=o.build_adoption_decision_from_authoritative_inputs(r1,registry(),authority_ids=["A1"],independent_domains=["device-A"],now=100,nonce="real-v4",rationale="authoritative v4 path",explicit_confirmation=True,out_of_band=True,amendment_evidence=evidence(r1),decision_id="D-REAL",decision_time="2026-09-23T00:00:00Z")
 ck(q.get("status")=="PASS","P159_OCC1A_HARDEN_V4_REAL_P095_P106_P104_PATH_OK")
 ck(q.get("persisted") is False,"P159_OCC1A_HARDEN_V4_DECISION_NOT_PERSISTED_OK")
 q=o.build_adoption_decision_from_authoritative_inputs(rl0,registry(),authority_ids=["A1"],independent_domains=["device-A"],now=100,nonce="l0-v4",rationale="l0 blocked",explicit_confirmation=True,out_of_band=True,amendment_evidence=evidence(rl0),decision_id="D-L0",decision_time="2026-09-23T00:00:00Z")
 ck(q.get("status")!="PASS" and q.get("reason")=="REFOUNDING_OR_FORK_REQUIRED","P159_OCC1A_HARDEN_V4_DNA_L0_REFOUNDING_OK")
 ck(regpath.read_bytes()==before,"P159_OCC1A_HARDEN_V4_REGISTRY_IMMUTABLE_OK")
 m=o.manifest();ck(not m["machine_adoption_permitted"] and not m["machine_activation_permitted"] and not m["real_execution_enabled"],"P159_OCC1A_HARDEN_V4_NO_ADOPTION_ACTIVATION_EXECUTION_OK");ck(not m["occ1a_closed"] and not m["occ1b_opened"] and not m["p160_opened"],"P159_OCC1A_HARDEN_V4_STAGE_BOUNDARY_OK")
 print("P159_OCC1A_ADOPTION_HARDENING_V4_OK")
if __name__=="__main__":main()

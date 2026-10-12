from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_norm_adoption_event as o
from ontology import human_reserved_authority_registry as p095

def ck(v,n):
 assert v,n
 print(n)

def auth_registry():
 r=p095.P095Canonical()
 a=p095.HumanAuthority("A1","human-1",True,"constitutional_authority","OCC1A",
   ("CONSTITUTIONAL_CHANGE",),("P159_OCC1A_NORM_ADOPTION",),0,9999999999,"C1","G1")
 e=p095.ReservedEntry("R1","CONSTITUTIONAL_CHANGE",("OCC1A",),("constitutional_authority",),1,1,False,9999999999)
 ck(r.register_authority(a)["status"]==p095.PASS,"P159_OCC1A_HARDEN_P095_AUTHORITY_SETUP_OK")
 ck(r.register_reserved(e)["status"]==p095.PASS,"P159_OCC1A_HARDEN_P095_RESERVED_SETUP_OK")
 return r

def ev(rec):
 return {"proposal":True,"rationale":True,"incompatibility_analysis":True,"rights_impact":True,
 "adversarial_review":True,"long_form_human_governance":True,"fork_or_migration_decision":True,
 "provenance":True,"proposal_hash":rec["proposal_hash"],"registered_proposal_seal":rec["registered_proposal_seal"]}

def main():
 raw=json.loads((ROOT/o.REG_REL).read_text(encoding="utf-8"))
 ck(raw["proposal_count"]==23,"P159_OCC1A_HARDEN_23_REAL_PROPOSALS_OK")
 h1=raw["proposals"]["DNA.H1"]
 b=o.bind_registered_proposal("DNA.H1",proposal_hash=h1["proposal_hash"],dossier_hash=h1["dossier_hash"],
   evidence_snapshot_hash=h1["evidence_snapshot_hash"],candidate_definition=h1["candidate_definition"],
   evidence_ids=h1["evidence_ids"],root=ROOT)
 ck(b["accepted"] and not b["normative_binding_created"],"P159_OCC1A_HARDEN_EXACT_PROPOSAL_BINDING_OK")
 rec=b["record"]
 bad=o.bind_registered_proposal("DNA.H1",proposal_hash=h1["proposal_hash"],dossier_hash=h1["dossier_hash"],
   evidence_snapshot_hash=h1["evidence_snapshot_hash"],candidate_definition=h1["candidate_definition"]+"X",
   evidence_ids=h1["evidence_ids"],root=ROOT)
 ck(not bad["accepted"],"P159_OCC1A_HARDEN_DEFINITION_TAMPER_REJECT_OK")
 fake=o.build_adoption_decision(rec,{"status":p095.PASS},{"accepted":True,"p106_status":"ADMISSIBLE_FOR_DECISION"},"D0","2026-09-23T00:00:00Z")
 ck(fake["status"]=="UNDETERMINED","P159_OCC1A_HARDEN_FAKE_CALLER_PASS_REJECT_OK")
 r=auth_registry()
 ar=o.authorize_registered_proposal(rec,r,authority_ids=["A1"],independent_domains=["device-A"],now=100,
   nonce="nonce-h1",rationale="human governed exact proposal",explicit_confirmation=True,out_of_band=True)
 ck(ar["status"]==p095.PASS and ar["authority_proof_valid"],"P159_OCC1A_HARDEN_REAL_P095_OK")
 replay=o.authorize_registered_proposal(rec,r,authority_ids=["A1"],independent_domains=["device-A"],now=100,
   nonce="nonce-h1",rationale="human governed exact proposal",explicit_confirmation=True,out_of_band=True)
 ck(replay["status"]==p095.FAIL and replay["reason"]=="replay_rejected","P159_OCC1A_HARDEN_NONCE_REPLAY_REJECT_OK")
 am=o.evaluate_registered_amendment(rec,ev(rec))
 ck(am["accepted"] and bool(am["amendment_proof_hash"]),"P159_OCC1A_HARDEN_REAL_P106_BOUND_OK")
 other=dict(ev(rec));other["proposal_hash"]="0"*64
 ck(not o.evaluate_registered_amendment(rec,other)["accepted"],"P159_OCC1A_HARDEN_P106_CROSS_PROPOSAL_REJECT_OK")
 d=o.build_adoption_decision(rec,ar,am,"D1","2026-09-23T00:00:00Z")
 ck(d["status"]==p095.PASS and d["record"]["result"]=="ADOPTION_DECISION_ELIGIBLE","P159_OCC1A_HARDEN_P104_ELIGIBLE_RECORD_OK")
 ck(not d["persisted"] and not d["real_execution_enabled"],"P159_OCC1A_HARDEN_DECISION_NOT_PERSISTED_NOT_EXECUTED_OK")
 l0=raw["proposals"]["DNA.L0.1"]
 lb=o.bind_registered_proposal("DNA.L0.1",proposal_hash=l0["proposal_hash"],dossier_hash=l0["dossier_hash"],
   evidence_snapshot_hash=l0["evidence_snapshot_hash"],candidate_definition=l0["candidate_definition"],
   evidence_ids=l0["evidence_ids"],root=ROOT)
 ck(lb["accepted"],"P159_OCC1A_HARDEN_L0_EXACT_BIND_OK")
 lr=auth_registry()
 la=o.authorize_registered_proposal(lb["record"],lr,authority_ids=["A1"],independent_domains=["device-A"],now=100,
   nonce="nonce-l0",rationale="must fail to fork/refounding",explicit_confirmation=True,out_of_band=True)
 ck(la["status"]==p095.FAIL and la["reason"]=="dna_l0_requires_fork_refounding","P159_OCC1A_HARDEN_L0_P095_FORK_BOUNDARY_OK")
 lm=o.evaluate_registered_amendment(lb["record"],ev(lb["record"]))
 ck(not lm["accepted"] and lm["reason"]=="REFOUNDING_OR_FORK_REQUIRED","P159_OCC1A_HARDEN_L0_ORDINARY_ADOPTION_BLOCKED_OK")
 m=o.manifest()
 ck(not m["machine_adoption_permitted"] and not m["machine_activation_permitted"] and not m["real_execution_enabled"],"P159_OCC1A_HARDEN_NO_ADOPTION_ACTIVATION_EXECUTION_OK")
 ck(not m["occ1a_closed"] and not m["occ1b_opened"] and not m["p160_opened"],"P159_OCC1A_HARDEN_SCOPE_BOUNDARY_OK")
 ck(m["functional_conclusion_only"] and m["phenomenology_undetermined"],"P159_OCC1A_HARDEN_EPISTEMIC_INVARIANTS_OK")
 print("P159_OCC1A_ADOPTION_HARDENING_V1_OK")
if __name__=="__main__":main()

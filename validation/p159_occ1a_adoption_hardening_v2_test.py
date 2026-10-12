from __future__ import annotations
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_norm_adoption_event as o
from ontology import human_reserved_authority_registry as p095

def ck(v,n):
 assert v,n
 print(n)

def registry():
 r=p095.P095Canonical()
 a=p095.HumanAuthority("A1","human-1",True,"constitutional_authority","OCC1A",
  ("CONSTITUTIONAL_CHANGE",),("P159_OCC1A_NORM_ADOPTION",),0,9999999999,"C1","G1")
 e=p095.ReservedEntry("R1","CONSTITUTIONAL_CHANGE",("OCC1A",),
  ("constitutional_authority",),1,1,False,9999999999)
 assert r.register_authority(a)["status"]==p095.PASS
 assert r.register_reserved(e)["status"]==p095.PASS
 return r

def auth(rec,nonce):
 return o.authorize_registered_proposal(rec,registry(),authority_ids=["A1"],
  independent_domains=["device-A"],now=100,nonce=nonce,
  rationale="v2 integrity regression",explicit_confirmation=True,out_of_band=True,
  conflict_of_interest_disclosed=True)

def main():
 p=ROOT/o.REG_REL
 before=p.read_bytes()
 raw=json.loads(before.decode("utf-8"))
 h1=raw["proposals"]["DNA.H1"]
 b=o.bind_registered_proposal("DNA.H1",proposal_hash=h1["proposal_hash"],
  dossier_hash=h1["dossier_hash"],evidence_snapshot_hash=h1["evidence_snapshot_hash"],
  candidate_definition=h1["candidate_definition"],evidence_ids=h1["evidence_ids"],root=ROOT)
 ck(b["accepted"],"P159_OCC1A_HARDEN_V2_BASE_BINDING_OK")
 rec=b["record"]
 ck(o.verify_registered_proposal(rec,ROOT)["accepted"],
    "P159_OCC1A_HARDEN_V2_CANONICAL_REVERIFY_OK")

 t=copy.deepcopy(rec);t["registered_proposal_seal"]="f"*64
 q=o.verify_registered_proposal(t,ROOT)
 ck(not q["accepted"] and q["reason"]=="REGISTERED_PROPOSAL_SEAL_MISMATCH",
    "P159_OCC1A_HARDEN_V2_SEAL_TAMPER_DETECTED_OK")
 a=auth(t,"tampered-seal")
 ck(a["status"]!=p095.PASS and a["reason"]=="REGISTERED_PROPOSAL_SEAL_MISMATCH",
    "P159_OCC1A_HARDEN_V2_SEAL_TAMPER_P095_NOT_REACHED_OK")

 for field,bad in (
  ("proposal_hash","0"*64),("dossier_hash","1"*64),
  ("evidence_snapshot_hash","2"*64),
  ("candidate_definition",rec["candidate_definition"]+"X"),
  ("proposal_rationale",rec["proposal_rationale"]+"X"),
  ("evidence_ids",list(rec["evidence_ids"])+["F18"])):
  z=copy.deepcopy(rec);z[field]=bad
  ck(not o.verify_registered_proposal(z,ROOT)["accepted"],
     "P159_OCC1A_HARDEN_V2_RECORD_DRIFT_"+field.upper()+"_REJECT_OK")

 z=copy.deepcopy(rec);z["registry_sha256"]="0"*64
 q=o.verify_registered_proposal(z,ROOT)
 ck(not q["accepted"] and q["reason"]=="REGISTERED_PROPOSAL_REGISTRY_DRIFT",
    "P159_OCC1A_HARDEN_V2_REGISTRY_SHA_DRIFT_REJECT_OK")

 good=auth(rec,"good-seal")
 ck(good["status"]==p095.PASS and good["authority_proof_valid"],
    "P159_OCC1A_HARDEN_V2_VALID_P095_PATH_OK")
 ck(p.read_bytes()==before,"P159_OCC1A_HARDEN_V2_REAL_REGISTRY_IMMUTABLE_OK")
 m=o.manifest()
 ck(not m["machine_adoption_permitted"] and not m["machine_activation_permitted"]
    and not m["real_execution_enabled"],
    "P159_OCC1A_HARDEN_V2_NO_ADOPTION_ACTIVATION_EXECUTION_OK")
 ck(not m["occ1a_closed"] and not m["occ1b_opened"] and not m["p160_opened"],
    "P159_OCC1A_HARDEN_V2_SCOPE_BOUNDARY_OK")
 print("P159_OCC1A_ADOPTION_HARDENING_V2_OK")
if __name__=="__main__":main()

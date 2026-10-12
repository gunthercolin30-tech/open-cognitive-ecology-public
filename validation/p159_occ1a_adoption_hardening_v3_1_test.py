from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_norm_adoption_event as o
from ontology import human_reserved_authority_registry as p095
def ck(v,n):
 if not v: raise AssertionError(n)
 print(n)
def reg(scope=("CONSTITUTIONAL_CHANGE",),contexts=("P159_OCC1A_NORM_ADOPTION",),vf=0,vu=9999999999):
 r=p095.P095Canonical()
 a=p095.HumanAuthority("A1","human-1",True,"constitutional_authority","OCC1A",tuple(scope),tuple(contexts),vf,vu,"C1","G1")
 e=p095.ReservedEntry("R1","CONSTITUTIONAL_CHANGE",("OCC1A",),("constitutional_authority",),1,1,False,9999999999)
 ck(r.register_authority(a)["status"]==p095.PASS,"P159_OCC1A_HARDEN_V3_1_AUTHORITY_SETUP_OK")
 ck(r.register_reserved(e)["status"]==p095.PASS,"P159_OCC1A_HARDEN_V3_1_RESERVED_SETUP_OK")
 return r
def main():
 p=ROOT/o.REG_REL; before=p.read_bytes(); x=json.loads(before.decode())["proposals"]["DNA.H1"]
 b=o.bind_registered_proposal("DNA.H1",proposal_hash=x["proposal_hash"],dossier_hash=x["dossier_hash"],evidence_snapshot_hash=x["evidence_snapshot_hash"],candidate_definition=x["candidate_definition"],evidence_ids=x["evidence_ids"],root=ROOT)
 ck(b["accepted"],"P159_OCC1A_HARDEN_V3_1_BINDING_OK"); rec=b["record"]
 def auth(r,n): return o.authorize_registered_proposal(rec,r,authority_ids=["A1"],independent_domains=["device-A"],now=100,nonce=n,rationale="v3.1",explicit_confirmation=True,out_of_band=True)
 q=auth(reg(),"valid"); print("VALID_SCOPE_STATUS="+str(q.get("status"))); print("VALID_SCOPE_REASON="+str(q.get("reason"))); ck(q.get("status")==p095.PASS,"P159_OCC1A_HARDEN_V3_1_VALID_SCOPE_PASS_OK")
 q=auth(reg(contexts=("OTHER_CONTEXT",)),"context"); print("WRONG_CONTEXT_STATUS="+str(q.get("status"))); print("WRONG_CONTEXT_REASON="+str(q.get("reason"))); ck(q.get("status")!=p095.PASS and q.get("reason")=="P095_CONTEXT_SCOPE_MISMATCH","P159_OCC1A_HARDEN_V3_1_CONTEXT_SCOPE_REJECT_OK")
 q=auth(reg(scope=("OTHER_ACTION",)),"scope"); ck(q.get("status")!=p095.PASS and q.get("reason")=="P095_ACTION_CLASS_SCOPE_MISMATCH","P159_OCC1A_HARDEN_V3_1_ACTION_SCOPE_REJECT_OK")
 q=auth(reg(vf=101),"future"); ck(q.get("status")!=p095.PASS and q.get("reason")=="P095_AUTHORITY_NOT_YET_VALID","P159_OCC1A_HARDEN_V3_1_NOT_YET_VALID_REJECT_OK")
 q=auth(reg(vu=99),"expired"); ck(q.get("status")!=p095.PASS and q.get("reason")=="P095_AUTHORITY_EXPIRED","P159_OCC1A_HARDEN_V3_1_EXPIRED_REJECT_OK")
 ck(p.read_bytes()==before,"P159_OCC1A_HARDEN_V3_1_REGISTRY_IMMUTABLE_OK")
 m=o.manifest(); ck(not m["machine_adoption_permitted"] and not m["machine_activation_permitted"] and not m["real_execution_enabled"],"P159_OCC1A_HARDEN_V3_1_NO_ADOPTION_ACTIVATION_EXECUTION_OK"); ck(not m["occ1a_closed"] and not m["occ1b_opened"] and not m["p160_opened"],"P159_OCC1A_HARDEN_V3_1_STAGE_BOUNDARY_OK")
 print("P159_OCC1A_ADOPTION_HARDENING_V3_1_OK")
if __name__=="__main__": main()

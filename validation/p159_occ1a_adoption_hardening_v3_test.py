from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT)) if str(ROOT) not in sys.path else None
from ontology import occ_norm_adoption_event as o
from ontology import human_reserved_authority_registry as p095
def mk(ctx):
 r=p095.P095Canonical(); a=p095.HumanAuthority("A1","human-1",True,"constitutional_authority","OCC1A",("CONSTITUTIONAL_CHANGE",),(ctx,),0,9999999999,"C1","G1"); e=p095.ReservedEntry("R1","CONSTITUTIONAL_CHANGE",("OCC1A",),("constitutional_authority",),1,1,False,9999999999); assert r.register_authority(a)["status"]==p095.PASS; assert r.register_reserved(e)["status"]==p095.PASS; return r
def main():
 p=ROOT/o.REG_REL; before=p.read_bytes(); x=json.loads(before.decode())["proposals"]["DNA.H1"]; b=o.bind_registered_proposal("DNA.H1",proposal_hash=x["proposal_hash"],dossier_hash=x["dossier_hash"],evidence_snapshot_hash=x["evidence_snapshot_hash"],candidate_definition=x["candidate_definition"],evidence_ids=x["evidence_ids"],root=ROOT); assert b["accepted"]; rec=b["record"]; f=lambda r,n:o.authorize_registered_proposal(rec,r,authority_ids=["A1"],independent_domains=["device-A"],now=100,nonce=n,rationale="v3 scope",explicit_confirmation=True,out_of_band=True); assert f(mk("P159_OCC1A_NORM_ADOPTION"),"g")["status"]==p095.PASS; q=f(mk("OTHER_CONTEXT"),"b"); assert q["status"]!=p095.PASS and q["reason"]=="P095_CONTEXT_SCOPE_MISMATCH"; assert p.read_bytes()==before; m=o.manifest(); assert not m["machine_adoption_permitted"] and not m["machine_activation_permitted"] and not m["real_execution_enabled"]; print("P159_OCC1A_HARDEN_V3_CONTEXT_SCOPE_REJECT_OK"); print("P159_OCC1A_ADOPTION_HARDENING_V3_OK")
if __name__=="__main__": main()

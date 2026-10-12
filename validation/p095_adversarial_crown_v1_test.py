from pathlib import Path
import sys, time
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology.human_reserved_authority_registry import *

now=int(time.time())
def auth(i,human,role,scope,start=None,end=None,authenticated=True,depth=0,parent=None):
    return HumanAuthority(i,human,authenticated,role,"bounded mandate",tuple(scope),("global",),
        now-10 if start is None else start, now+3600 if end is None else end,
        "constitution-v1","governance-v1",depth,parent,False)
def manifest(i="X",layer="Constitution",nonce="n",objections=("material objection",),evidence=("ev-a","ev-b")):
    return ActionManifest(i,"CONSTITUTIONAL_CHANGE","object","global",layer,True,True,"risk summary",
        tuple(objections),tuple(evidence),nonce,now)
def eng():
    e=P095Canonical()
    assert e.register_authority(auth("A1","h1","constitutional_reviewer",("CONSTITUTIONAL_CHANGE",)))["status"]==PASS
    assert e.register_authority(auth("A2","h2","independent_reviewer",("CONSTITUTIONAL_CHANGE",)))["status"]==PASS
    assert e.register_reserved(ReservedEntry("E1","CONSTITUTIONAL_CHANGE",("high_impact",),
        ("constitutional_reviewer","independent_reviewer"),2,2,False,now+3600))["status"]==PASS
    return e
cases=0
e=eng(); b=auth("BAD","h3","constitutional_reviewer",("CONSTITUTIONAL_CHANGE",),authenticated=False); assert e.register_authority(b)["status"]==PASS; assert e.authority_envelope("BAD",now)["status"]==FAIL; cases+=1
e=eng(); x=auth("EXP","h4","constitutional_reviewer",("CONSTITUTIONAL_CHANGE",),now-100,now-1); assert e.register_authority(x)["status"]==PASS; assert e.authority_envelope("EXP",now)["status"]==FAIL; cases+=1
e=eng(); c=auth("CH","h5","constitutional_reviewer",("CONSTITUTIONAL_CHANGE","DANGEROUS_PHYSICAL_ACTION"),depth=1,parent="A1"); assert e.delegate("A1",c,now)["status"]==FAIL; cases+=1
e=eng(); p=e.authorities["A1"]; c=auth("CH2","h5","constitutional_reviewer",("CONSTITUTIONAL_CHANGE",),p.valid_from-1,p.valid_until+1,True,1,"A1"); assert e.delegate("A1",c,now)["status"]==FAIL; cases+=1
e=eng(); assert e.authorize(manifest(),("A1","A2"),("d1","d2"),now,"r",False,True)["status"]==FAIL; cases+=1
e=eng(); assert e.authorize(manifest(),("A1","A2"),("d1","d2"),now,"",True,True)["status"]==FAIL; cases+=1
e=eng(); assert e.authorize(manifest(evidence=("same","same")),("A1","A2"),("d1","d2"),now,"r",True,True)["status"]==FAIL; cases+=1
e=eng(); assert e.authorize(manifest(objections=()),("A1","A2"),("d1","d2"),now,"r",True,True)["status"]==FAIL; cases+=1
e=eng(); assert e.authorize(manifest(),("A1","A2"),("d1","d2"),now,"r",True,False)["status"]==FAIL; cases+=1
e=eng(); assert e.authorize(manifest(),("A1","A2"),("same","same"),now,"r",True,True)["status"]==FAIL; cases+=1
e=eng(); assert e.authorize(manifest(),("A1",),("d1","d2"),now,"r",True,True)["status"]==FAIL; cases+=1
e=eng(); a3=auth("A3","h3","constitutional_reviewer",("CONSTITUTIONAL_CHANGE",)); assert e.register_authority(a3)["status"]==PASS; assert e.authorize(manifest(),("A1","A3"),("d1","d2"),now,"r",True,True)["status"]==FAIL; cases+=1
e=eng(); m=manifest(); assert e.authorize(m,("A1","A2"),("d1","d2"),now,"r",True,True)["status"]==PASS; assert e.authorize(m,("A1","A2"),("d1","d2"),now,"r",True,True)["status"]==FAIL; cases+=1
e=eng(); assert e.authorize(manifest(layer="DNA-L0"),("A1","A2"),("d1","d2"),now,"r",True,True)["status"]==FAIL; cases+=1
e=eng(); assert e.authorize(manifest(),("A1","A2"),("d1","d2"),now,"r",True,True,emergency=True)["status"]==FAIL; cases+=1
e=eng(); assert e.human_absence(True,False)["status"]==FROZEN; cases+=1
e=eng(); assert e.human_absence(True,True)["status"]==LIMITED; cases+=1
e=eng(); assert e.freeze("A1",now)["status"]==PASS; assert e.authorize(manifest(),("A1","A2"),("d1","d2"),now,"r",True,True)["status"]==FROZEN; cases+=1
e=eng(); assert e.quarantine_authority("A1","compromise")["status"]==PASS; assert e.authority_envelope("A1",now)["status"]==FAIL; cases+=1
e=eng(); q=e.quarantine_authority("A1","compromise"); assert q["reason"]=="account_quarantined_not_person_delegitimized"; cases+=1
e=eng(); r=e.refusal("DNA-L0","fork/refounding"); assert r["status"]==FAIL and r["triggered_rule"]=="DNA-L0" and r["legitimate_path"]=="fork/refounding"; cases+=1
e=eng(); p=e.action_preview(manifest()); assert p["risk"]=="risk summary" and p["objections"]==["material objection"]; cases+=1
e=P095Canonical(); assert e.register_authority(auth("A1","h1","constitutional_reviewer",("CONSTITUTIONAL_CHANGE",)))["status"]==PASS; assert e.authorize(manifest(),("A1",),("d1",),now,"r",True,True)["status"]==UNDETERMINED; cases+=1
e=P095Canonical(); assert e.authority_envelope("UNKNOWN",now)["status"]==UNDETERMINED; cases+=1
e=P095Canonical(); assert e.register_reserved(ReservedEntry("bad","UNBOUNDED_ADMIN",(),("admin",),1,1,True,now+1))["status"]==FAIL; cases+=1
e=P095Canonical(); bad=HumanAuthority("A","h",True,"r","m",("*",),("global",),now+10,now,"constitution-v1","governance-v1"); assert e.register_authority(bad)["status"]==FAIL; cases+=1
c=P095Canonical().canonical_contract(); ids=list(c["requirements"]); assert ids==[f"R19.{i}" for i in range(1,68)]; cases+=1
assert set(c["tail"])=={"R19-P1","R19-P2","R19-P3","R19-P4","R19-P5","R19-P6","R19-ADV-1","R19-ADV-2","R19-CONCEPTUAL-CLOSURE"} and c["canonical_object_count"]==76; cases+=1
assert c["functional_only"] is True and c["phenomenology_undetermined"] is True and c["canonical_compliance_proven"] is False and c["conceptual_closure_claimed"] is False; cases+=1
print("P095_ADVERSARIAL_CROWN_V1_OK")
print(f"adversarial_cases={cases}")
print("r19_requirements=67")
print("canonical_objects_total=76")
print("functional_only=true")
print("phenomenology_undetermined=true")

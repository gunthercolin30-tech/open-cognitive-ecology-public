import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.human_representative_constitutional_interface import *
from ontology.human_reserved_authority_registry import HumanAuthority,ReservedEntry,ActionManifest,P095Canonical
NOW=200
def mk(valid_to=300,contexts=("ctx",),actions=("SIGNIFICANT_SANCTION",)):
 r=P095Canonical()
 assert r.register_authority(HumanAuthority("AUTH-1","human-1",True,"representative","reserved-governance",actions,contexts,100,valid_to,"C1","G1"))["status"]=="PASS"
 assert r.register_reserved(ReservedEntry("RES-1","SIGNIFICANT_SANCTION",("critical",),("representative",),1,1,False,300))["status"]=="PASS"
 return HumanRepresentativeConstitutionalInterface(r)
def act(n="n",ctx="ctx",typ="SIGNIFICANT_SANCTION"):
 return ActionManifest("A-"+n,typ,"obj",ctx,"Constitution",False,True,"risk",("objection",),("ev1","ev2"),n,NOW)
def call(ui,man=None,**kw):
 d=dict(manifest=man or act(),authority_ids=("AUTH-1",),independent_domains=("d1",),now=NOW,rationale="bounded",explicit_confirmation=True,evidence=("ev1","ev2")); d.update(kw); return ui.examine(**d)
def main():
 n=0
 def check(name,c):
  nonlocal n; assert c,name; n+=1
 check("bounded",call(mk())["status"]=="PASS")
 check("root_escalation",call(mk(),authority_ids=("ROOT_OVERRIDE_ALL",))["status"]!="PASS")
 check("expired",call(mk(valid_to=150))["status"]!="PASS")
 check("context_scope",call(mk(),man=act("c","other"))["status"]=="FAIL")
 check("action_scope",call(mk(actions=("OTHER",)))["status"]!="PASS")
 check("confirmation",call(mk(),explicit_confirmation=False)["status"]!="PASS")
 x=call(mk(),normative_status="CONFLICT"); check("vertical_horizontal_conflict",x["status"]=="CONFLICT" and x["action"]=="ABSTAIN_AND_ESCALATE")
 check("undetermined",call(mk(),normative_status="UNDETERMINED")["action"]=="ABSTAIN")
 x=mk().human_absence(requires_human=True); check("absence",x["status"]=="UNDETERMINED" and not x["execution_permitted"])
 x=call(mk()); check("no_execution",not x["execution_permitted"]); check("no_auth_creation",not x["authorization_created"])
 b=manifest()["boundaries"]
 check("renderer_boundary",b["renderer_holds_authority_logic"] is False)
 check("no_root",b["human_representative_is_unlimited_root"] is False)
 check("no_override",b["human_approval_can_override_higher_norm"] is False)
 check("no_p106",b["does_not_implement_p106_amendment_protocol"] is True)
 check("no_runtime_claim",b["does_not_claim_p155_p166_runtime_enforcement"] is True)
 check("stage_separation",b["recommendation_decision_authorization_execution_distinct"] is True)
 check("contestability",b["representative_actions_authorized_traced_contestable"] is True)
 check("functional_only",manifest()["functional_conclusion_only"] and manifest()["phenomenology_undetermined"])
 vals=[(call(mk(),man=act("r"+str(i)))["status"],call(mk(),man=act("s"+str(i)))["action"]) for i in range(25)]
 check("determinism",len(set(vals))==1)
 print("P105_ADVERSARIAL_CROWN_V2_OK"); print("cases=%d/%d"%(n,n)); print("functional_conclusion_only=True"); print("phenomenology_undetermined=True")
if __name__=="__main__": main()

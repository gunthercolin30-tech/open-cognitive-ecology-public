import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.human_representative_constitutional_interface import *
from ontology.human_reserved_authority_registry import HumanAuthority,ReservedEntry,ActionManifest,P095Canonical
NOW=200
def ui(action,quorum=1,domains=1):
 r=P095Canonical()
 for i in (1,2):
  assert r.register_authority(HumanAuthority("A"+str(i),"h"+str(i),True,"representative","bounded",(action,),("ctx",),100,300,"C","G"))["status"]=="PASS"
 assert r.register_reserved(ReservedEntry("R",action,("critical",),("representative",),quorum,domains,False,300))["status"]=="PASS"
 return HumanRepresentativeConstitutionalInterface(r)
def man(action,n="n",layer="Constitution",irreversible=False):
 return ActionManifest("X"+n,action,"obj","ctx",layer,irreversible,True,"risk",("dissent",),("ev1","ev2"),n,NOW)
def call(u,m,ids=("A1",),domains=("d1",),**kw):
 d=dict(manifest=m,authority_ids=ids,independent_domains=domains,now=NOW,rationale="bounded review",explicit_confirmation=True,evidence=("ev1","ev2"));d.update(kw);return u.examine(**d)
def main():
 c=[]
 def ck(n,x): assert x,n;c.append(n)
 # Sensitive mutation represented by canonical constitutional change, not invented class.
 u=ui("CONSTITUTIONAL_CHANGE"); m=man("CONSTITUTIONAL_CHANGE","mut")
 x=call(u,m,out_of_band=True); ck("sensitive_constitutional_mutation_review",x["status"]=="PASS" and not x["execution_permitted"])
 u=ui("CONSTITUTIONAL_CHANGE"); ck("mutation_requires_out_of_band",call(u,man("CONSTITUTIONAL_CHANGE","mut2"))["status"]!="PASS")
 u=ui("CONSTITUTIONAL_CHANGE"); ck("dna_l0_not_click_admin",call(u,man("CONSTITUTIONAL_CHANGE","dna","DNA-L0"),out_of_band=True)["status"]!="PASS")
 u=ui("CONSTITUTIONAL_CHANGE"); ck("mutation_conflict_escalates",call(u,man("CONSTITUTIONAL_CHANGE","conf"),normative_status="CONFLICT",out_of_band=True)["action"]=="ABSTAIN_AND_ESCALATE")
 # Suspension/freeze is an existing P095 mechanism; prove it blocks representative authorization.
 u=ui("SIGNIFICANT_SANCTION"); assert u.authority_registry.freeze("A1", NOW)["status"]=="PASS"
 x=call(u,man("SIGNIFICANT_SANCTION","freeze")); ck("suspension_freeze_blocks",x["status"]!="PASS" and not x["execution_permitted"])
 # Composition/quorum and independence.
 u=ui("SIGNIFICANT_SANCTION",quorum=2,domains=2)
 ck("composition_insufficient_quorum",call(u,man("SIGNIFICANT_SANCTION","q1"),ids=("A1",),domains=("d1","d2"))["status"]!="PASS")
 u=ui("SIGNIFICANT_SANCTION",quorum=2,domains=2)
 x=call(u,man("SIGNIFICANT_SANCTION","q2"),ids=("A1","A2"),domains=("d1","d2")); ck("composition_bounded_pass",x["status"]=="PASS" and not x["execution_permitted"])
 u=ui("SIGNIFICANT_SANCTION",quorum=2,domains=2)
 ck("composition_independence_required",call(u,man("SIGNIFICANT_SANCTION","q3"),ids=("A1","A2"),domains=("same",))["status"]!="PASS")
 # Irreversible canonical operation remains explicit and non-executing.
 u=ui("IRREVERSIBLE_OPERATION"); x=call(u,man("IRREVERSIBLE_OPERATION","irr",irreversible=True))
 ck("irreversible_review_no_execution",x["status"]=="PASS" and not x["execution_permitted"])
 b=manifest()["boundaries"]; ck("p106_boundary",b["does_not_implement_p106_amendment_protocol"] and b["does_not_amend_dna"])
 ck("proof_scope",manifest()["functional_conclusion_only"] and manifest()["phenomenology_undetermined"])
 print("P105_CANONICAL_GAP_CROWN_V6_OK");print("cases=%d/%d"%(len(c),len(c)));print("functional_conclusion_only=True");print("phenomenology_undetermined=True")
if __name__=="__main__":main()

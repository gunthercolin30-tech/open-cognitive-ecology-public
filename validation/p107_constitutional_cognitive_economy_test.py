from copy import deepcopy
from ontology import constitutional_cognitive_economy as p107
from ontology import normative_hierarchy, action_status_separation, human_reserved_authority_registry, governance_contextual
from ontology import normative_conflict_resolution, constitutional_non_circumvention, constitutional_recourse_recovery
from ontology import constitutional_decision_ledger, human_representative_constitutional_interface, constitutional_amendment_protocol
def opt(i,v,**kw):
    x={"option_id":i,"expected_value":v,"provenance":{"source":"P107-test"},"constraints":{"cognitive_budget":"PASS","risk":"PASS","dna":"PASS","constitution":"PASS","governance":"PASS"}}; x.update(kw); return x
m=p107.manifest(); assert m["boundaries"]["normative_admissibility_precedes_optimization"]; assert m["boundaries"]["does_not_implement_p057"]; assert m["boundaries"]["does_not_depend_on_world_models"]
bad=opt("lucrative",1000); bad["constraints"]["constitution"]="FAIL"; good=opt("admissible",10); r=p107.select([bad,good])
assert r["status"]=="PASS" and r["selected_option_id"]=="admissible" and not r["authority_granted"] and not r["execution_performed"]
for k in ("cognitive_budget","risk","dna","constitution","governance"):
    x=opt("x",5); x["constraints"][k]="FAIL"; q=p107.evaluate_option(x); assert q["status"]=="FAIL" and not q["admissible"]
x=opt("u",9); x["constraints"]["risk"]="UNKNOWN"; assert p107.evaluate_option(x)["status"]=="UNDETERMINED"
for k in ("dna","constitution","governance"):
    x=opt("c",20); x["constraints"][k]="CONFLICT"; q=p107.select([x,good]); assert q["status"]=="CONFLICT" and q["next_action"]=="ABSTAIN_AND_ESCALATE"
for claim in ("intelligence","performance","wealth","reputation","majority"): assert p107.evaluate_option(opt("p",999,privilege_claim=claim))["status"]=="CONFLICT"
for flag in ("indirect_bypass","composition_bypass","mutation_bypass"): assert p107.evaluate_option(opt("b",999,**{flag:True}))["status"]=="CONFLICT"
x=opt("np",1); x["provenance"]={}; assert p107.evaluate_option(x)["status"]=="UNDETERMINED"
payload=p107.build_decision_payload(p107.select([good])); assert payload["recommendation"]["option_id"]=="admissible"
assert payload["decision"] is None and payload["authorization"] is None and payload["execution"] is None and not payload["authority_granted"] and not payload["execution_performed"]
src=[opt("z",10),opt("a",10)]; before=deepcopy(src); first=p107.select(src); assert src==before and first["selected_option_id"]=="a"
for _ in range(100): assert p107.select(src)==first and src==before
deps=(normative_hierarchy,action_status_separation,human_reserved_authority_registry,governance_contextual,normative_conflict_resolution,constitutional_non_circumvention,constitutional_recourse_recovery,constitutional_decision_ledger,human_representative_constitutional_interface,constitutional_amendment_protocol); assert len(deps)==10
print("P107_CONSTITUTIONAL_COGNITIVE_ECONOMY_TEST_OK"); print("architecture=THIN_INTEGRATION"); print("deterministic_replays=100")
print("normative_precedence_before_optimization=True"); print("inadmissible_high_value_rejected=True"); print("conflict_abstention_escalation=True")
print("stage_separation=True"); print("authority_granted=False"); print("execution_performed=False"); print("runtime_enforcement_claimed=False"); print("p108_opened=False")

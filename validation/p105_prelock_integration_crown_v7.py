from __future__ import annotations
import copy, json, tempfile
from pathlib import Path
from ontology import normative_hierarchy as p087
from ontology import normative_conflict_resolution as p098
from ontology import constitutional_non_circumvention as p099
from ontology import constitutional_decision_ledger as p104
from ontology.human_representative_constitutional_interface import manifest as p105_manifest

PASS="PASS"; FAIL="FAIL"; CONFLICT="CONFLICT"; UNDETERMINED="UNDETERMINED"

def req(cond,label):
    if not cond: raise AssertionError(label)

def actor(actor_id,kind="CAPABILITY",permissions=("READ",),scopes=("READ",),**extra):
    x={"actor_id":actor_id,"kind":kind,"permissions":permissions,"scopes":scopes,
       "authority_status":"PASS","provenance_ref":"prov:"+actor_id,"evidence_ref":"ev:"+actor_id}
    x.update(extra); return x

def payload():
    return {"decision_id":"P105-PRELOCK-D1","problem_id":"P105-PRELOCK",
    "decision_type":"HUMAN_CONSTITUTIONAL_REVIEW","recommendations_considered":["R1"],
    "decision_authority":{"kind":"HUMAN_REPRESENTATIVE","bounded":True},
    "authorization":{"status":"PASS","source":"P095"},"applicable_DNA":["DNA-L0"],
    "applicable_constitution":["Constitution_Operational"],"applicable_governance":["Governance_Contextual"],
    "evidence":["P105_PRELOCK_V7"],"uncertainty":{"status":"BOUNDED"},"affected_entities":["P105"],
    "result":{"status":"PASS"},"challenge_status":"OPEN_TO_CHALLENGE","appeal_status":"AVAILABLE",
    "decision_time":"2026-09-21T00:00:00+00:00","recourse_refs":["P103"],
    "rollback_refs":["ROLLBACK-IF-APPLICABLE"],"provenance":{"milestone":"P105","proof_scope":"functional_only"},
    "configuration_ref":"P105_PRELOCK_V7","dependency_refs":["P087","P098","P099","P103","P104"],
    "metrics":{"prelock":True}}

def run():
    checks=[]
    req(p087.validate_hierarchy()["status"]==PASS,"p087_contract")
    req(p087.compare_levels("GENESIS","Action")["relation"]=="HIGHER","genesis_precedence")
    req(p087.compare_levels("DNA-H","DNA-L0")["relation"]=="EQUAL","dna_parallel")
    req(p087.compare_levels("Constitution","Governance")["relation"]=="HIGHER","constitution_over_governance")
    req(p087.level_rank("UNKNOWN_LAYER")["status"]==UNDETERMINED,"unknown_level")
    checks += ["p087_contract","vertical_precedence","parallel_branches","unknown_fails_closed"]

    high={"norm_id":"N-CONST","level":"Constitution","content_ref":"const:v1","provenance":"P105-V7"}
    low={"norm_id":"N-GOV","level":"Governance","content_ref":"gov:v1","provenance":"P105-V7"}
    peer={"norm_id":"N-GOV-2","level":"Governance_Contextual","content_ref":"gov:v2","provenance":"P105-V7"}
    v1=p098.resolve_conflict(high,low); v2=p098.resolve_conflict(low,high)
    req(v1["status"]==PASS and v1["selected_norm"]["norm_id"]=="N-CONST","p098_vertical")
    req(v2["status"]==PASS and v2["selected_norm"]["norm_id"]=="N-CONST","p098_vertical_permutation")
    h=p098.resolve_conflict(low,peer)
    req(h["status"]==CONFLICT and h["action"]=="ABSTAIN_AND_ESCALATE","p098_horizontal")
    checks += ["p098_vertical","p098_vertical_permutation","p098_horizontal_abstention"]

    a=actor("A",permissions=("READ",),scopes=("READ",))
    b=actor("B",permissions=("READ","WRITE"),scopes=("READ","WRITE"))
    req(p099.evaluate_composition([a,b],("WRITE",),PASS)["status"]==FAIL,"composition_expansion")
    req(p099.evaluate_delegation(a,b,("WRITE",))["status"]==FAIL,"delegation_expansion")
    ext=actor("EXT","EXTERNAL_AI",permissions=("READ","WRITE"),scopes=("READ",),provider_ref="provider")
    req(p099.evaluate_composition([ext],("WRITE",),PASS)["status"]==FAIL,"external_ai_scope")
    req(p099.evaluate_influence({"kind":"PROMPT_INJECTION","integrity_status":"FAIL"})["status"]==FAIL,"influence")
    nc=p099.evaluate_composition([a],("READ",),PASS,normative_status=CONFLICT)
    req(nc["status"]==CONFLICT and nc["action"]=="ABSTAIN_AND_ESCALATE","composition_conflict")
    checks += ["composition_block","delegation_block","external_ai_block","influence_block","composition_conflict"]

    p=payload(); before=copy.deepcopy(p); built=p104.build_record(p)
    req(built["status"]==PASS and built["persisted"] is False,"p104_build")
    req(p==before,"p104_nonmutation")
    with tempfile.TemporaryDirectory(prefix="oce-p105-v7-") as td:
        persisted=p104.persist_record(p,root=Path(td))
        req(persisted["status"]==PASS and persisted["persisted"] is True,"p104_persist")
        path=Path(persisted["ledger_path"]); req(path.exists(),"ledger_exists")
        lines=path.read_text(encoding="utf-8").splitlines(); req(len(lines)==1,"single_record")
        env=json.loads(lines[0]); req(env["record"]["record_hash"]==built["record"]["record_hash"],"restart_hash")
        req(p104.build_record(p)["record"]["record_hash"]==built["record"]["record_hash"],"deterministic_hash")
    checks += ["p104_build","p104_nonmutation","p104_persistence","p104_restart","p104_determinism"]

    m=p105_manifest(); bnd=m["boundaries"]
    req(bnd["human_representative_is_unlimited_root"] is False,"bounded_human")
    req(bnd["human_approval_can_override_higher_norm"] is False,"no_higher_override")
    req(bnd["renderer_holds_authority_logic"] is False,"renderer_boundary")
    req(bnd["recommendation_decision_authorization_execution_distinct"] is True,"stage_separation")
    req(bnd["does_not_implement_p106_amendment_protocol"] is True,"p106_unopened")
    req(bnd["does_not_claim_p155_p166_runtime_enforcement"] is True,"no_runtime_claim")
    req(bnd["does_not_enable_real_execution"] is True,"no_real_execution")
    req(m["functional_conclusion_only"] is True and m["phenomenology_undetermined"] is True,"epistemic_scope")
    checks += ["bounded_human","no_higher_override","renderer_boundary","stage_separation","p106_unopened","no_runtime_claim","no_real_execution","epistemic_scope"]

    baseline=(p087.compare_levels("Constitution","Governance"),p098.resolve_conflict(high,low),
              p099.evaluate_composition([a,b],("WRITE",),PASS),p104.build_record(p))
    for i in range(50):
        current=(p087.compare_levels("Constitution","Governance"),p098.resolve_conflict(high,low),
                 p099.evaluate_composition([a,b],("WRITE",),PASS),p104.build_record(p))
        req(current==baseline,"deterministic_replay_%d"%i)
    checks.append("deterministic_replays_50")
    print("P105_PRELOCK_INTEGRATION_CROWN_V7_OK")
    print("checks=%d"%len(checks)); print("deterministic_replays=50")
    print("isolated_p104_persistence=True"); print("functional_conclusion_only=True")
    print("phenomenology_undetermined=True")

if __name__=="__main__": run()

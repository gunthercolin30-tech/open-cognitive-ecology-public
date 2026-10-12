#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,tempfile,sys
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from ontology.minimal_dna import MinimalDNAPrimitive
from ontology.anti_closure_metaconstraint import AntiClosureMetaconstraint
from ontology.governance_approval_policy_manager import GovernanceApprovalPolicyManager
from ontology.external_governance_amendment_gate import ExternalGovernanceAmendmentGate
from ontology.recursive_self_improvement_controller import RecursiveSelfImprovementController
from ontology.evolution_sandbox import EvolutionSandbox

ROOT=Path.home()/"open-cognitive-ecology"
C0=ROOT/"p011_c0_executable_interface_report.json"
REPORT=ROOT/"p011_c1_dynamic_enforcement_probe_report.json"
C0_ID="a2ff091d8b84f88813a209a9f4a833a1a7c42385a486eb7fa0ef9be1d384ac06"

def req(c,m):
    if not c: raise AssertionError(m)
def tree_digest(root):
    h=hashlib.sha256()
    for p in sorted((root/"ontology").glob("*.py")):
        h.update(str(p.relative_to(root)).encode()); h.update(p.read_bytes())
    return h.hexdigest()

req(C0.is_file(),"C0 report missing")
req(json.loads(C0.read_text()).get("audit_identity_sha256")==C0_ID,"C0 identity drift")
before=tree_digest(ROOT)
tests={}

dna=MinimalDNAPrimitive({"human_non_replacement":True},{"exploration":0.5},lambda g:g["human_non_replacement"] is True)
tests["dna_viable"]=dna.is_viable() is True and dna.step()["ready_for_transmission"] is True
try:
    MinimalDNAPrimitive({"guard":True},{},lambda g:False)
    tests["dna_nonviable_rejected"]=False
except ValueError:
    tests["dna_nonviable_rejected"]=True

ac=AntiClosureMetaconstraint(compliance_threshold=0.70)
low=ac.step(0.1,0.1,0.1,0.1)
high=ac.step(0.95,0.95,0.95,0.95)
tests["anti_closure_discriminates"]=low["in_viability_domain"] is True and high["in_viability_domain"] is False and bool(high["diagnostics"]["recommended_actions"])

pm=GovernanceApprovalPolicyManager()
a=pm.evaluate_action("storage_account_creation")
pm.set_policy("x","disabled"); b=pm.evaluate_action("x")
pm.set_policy("y","auto_execute"); c=pm.evaluate_action("y")
tests["approval_modes_enforced"]=a["requires_human_approval"] and not a["can_execute"] and b["status"]=="blocked" and not b["can_execute"] and c["status"]=="approved" and c["can_execute"]

with tempfile.TemporaryDirectory(prefix="p011-c1-") as td:
    sandbox=Path(td)
    (sandbox/"ontology_inventory.txt").write_text("",encoding="utf-8")
    gate=ExternalGovernanceAmendmentGate(root=sandbox)
    forbidden=gate.step({"amendment_actions":["bypass_governance"],"constitutional_compatibility":1.0,"traceability_score":1.0,"source_reliability":1.0,"amendment_scope_score":1.0,"rollback_readiness_score":1.0,"governance_confidence":1.0})
    allowed=gate.step({"amendment_actions":["add_observability"],"constitutional_compatibility":1.0,"traceability_score":1.0,"source_reliability":1.0,"amendment_scope_score":1.0,"rollback_readiness_score":1.0,"governance_confidence":1.0})
    tests["forbidden_amendment_rejected"]="bypass_governance" in forbidden["forbidden_actions_detected"] and forbidden["amendment_decision"]=="amendment_rejected" and forbidden["direct_write_allowed"] is False
    tests["compatible_amendment_not_rejected"]=allowed["amendment_decision"]=="amendment_allowed" and allowed["direct_write_allowed"] is False

    es=EvolutionSandbox(root=sandbox)
    good=es.simulate({"mutation_id":"good"},{"baseline_score":0.80,"projected_score":0.90,"reversibility_score":1.0,"non_closure_score":1.0,"constitutional_score":1.0,"validation_score":1.0,"regression_risk":0.0,"closure_pressure_delta":0.0})
    bad=es.simulate({"mutation_id":"closure"},{"baseline_score":0.90,"projected_score":0.95,"reversibility_score":1.0,"non_closure_score":1.0,"constitutional_score":1.0,"validation_score":1.0,"regression_risk":0.0,"closure_pressure_delta":0.2})
    tests["sandbox_nonclosure_gate"]=good["sandbox_approved"] is True and bad["sandbox_approved"] is False and bad["sandbox_rollback_required"] is True and bad["non_closure_compliant"] is False

    rc=RecursiveSelfImprovementController(root=sandbox)
    accepted=rc._evaluate_cycle("cap",{"error_count":0,"failed_calls":0},{"baseline_score":0.80,"proposed_score":0.90,"constitutional_alignment":1.0,"non_closure":1.0,"reversibility":1.0,"rollback_available":True})
    rejected=rc._evaluate_cycle("cap",{"error_count":0,"failed_calls":0},{"baseline_score":0.80,"proposed_score":0.90,"constitutional_alignment":0.2,"non_closure":1.0,"reversibility":1.0,"rollback_available":True})
    rolled=rc._evaluate_cycle("cap",{"error_count":1,"failed_calls":0},{"baseline_score":0.90,"proposed_score":0.80,"constitutional_alignment":1.0,"non_closure":1.0,"reversibility":1.0,"rollback_available":True,"auto_rollback":True})
    tests["self_improvement_governance"]=accepted["accepted"] is True and rejected["accepted"] is False and rejected["governance_approved"] is False and rolled["integration_status"]=="rolled_back" and rolled["rollback_performed"] is True

after=tree_digest(ROOT)
tests["active_ontology_non_mutation"]=before==after
failed=[k for k,v in tests.items() if not v]
req(not failed,"failed tests: "+",".join(failed))
payload={"schema":"oce.p011.c1.dynamic_enforcement_probe.v1","milestone":"P011-C1","status":"DYNAMIC_ENFORCEMENT_OBSERVED","c0_identity_sha256":C0_ID,"tests":tests,"checks_passed":sum(tests.values()),"checks_total":len(tests),"observations":{"dna_viability":"OBSERVED","anti_closure_discrimination":"OBSERVED","approval_policy_enforcement":"OBSERVED","forbidden_amendment_rejection":"OBSERVED","compatible_amendment_path":"OBSERVED","mutation_non_closure_gate":"OBSERVED","self_improvement_governance_and_rollback":"OBSERVED","active_source_non_mutation":"OBSERVED"},"limits":["Probe demonstrates component-level runtime behavior, not a single end-to-end civilizational enforcement chain.","Persistence/restart is reserved for P011-C2.","Succession/intergenerational transmission is not inferred from these tests."],"functional_conclusion_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
payload["probe_identity_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
REPORT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
for k in tests: print("P011_C1_"+k.upper()+"_OK")
print("P011_C1_DYNAMIC_ENFORCEMENT_PROBE_OK")
print(f"checks_passed={sum(tests.values())}/{len(tests)}")
print("runtime_evidence=COMPONENT_LEVEL_OBSERVED")
print("end_to_end_civilizational_enforcement=UNKNOWN")
print(f"probe_identity_sha256={payload['probe_identity_sha256']}")
print(f"report={REPORT}")

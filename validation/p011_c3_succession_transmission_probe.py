#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys,tempfile
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from ontology.succession_execution_protocol import SuccessionExecutionProtocol
from ontology.intergenerational_knowledge_transfer import IntergenerationalKnowledgeTransfer
from ontology.distributed_constitutional_memory import DistributedConstitutionalMemory

C2_REPORT=ROOT/"p011_c2_persistence_restart_probe_report.json"
REPORT=ROOT/"p011_c3_succession_transmission_probe_report.json"
C2_ID="d0bb7e54c99bc865ecc83d0b31842e7ad12c5e21f93141fcf15aeabed4eeba6b"

def req(c,m):
    if not c: raise AssertionError(m)

def tree_digest(root):
    h=hashlib.sha256()
    for p in sorted((root/"ontology").glob("*.py")):
        h.update(str(p.relative_to(root)).encode()); h.update(p.read_bytes())
    return h.hexdigest()

req(C2_REPORT.is_file(),"C2 report missing")
req(json.loads(C2_REPORT.read_text()).get("probe_identity_sha256")==C2_ID,"C2 identity drift")
before=tree_digest(ROOT)
tests={}
obs={}

with tempfile.TemporaryDirectory(prefix="p011-c3-") as td:
    sandbox=Path(td)

    kt=IntergenerationalKnowledgeTransfer(root=sandbox)
    healthy=kt.step({
        "source_knowledge":["constitution","memory","lineage"],
        "transferred_knowledge":["constitution","memory","lineage"],
        "retained_knowledge":["constitution","memory","lineage"],
        "distributed_knowledge_access_score":0.95,
        "distributed_memory_consistency_score":0.95,
        "lineage_integrity_score":0.95,
        "knowledge_loss_pressure":0.02,
        "symbolic_fragmentation_index":0.02,
    },persist=True)
    risk=kt.step({
        "source_knowledge":["constitution","memory","lineage"],
        "transferred_knowledge":[],
        "retained_knowledge":[],
        "distributed_knowledge_access_score":0.10,
        "distributed_memory_consistency_score":0.10,
        "lineage_integrity_score":0.10,
        "knowledge_loss_pressure":0.95,
        "symbolic_fragmentation_index":0.95,
    },persist=False)
    tests["intergenerational_transfer_discriminates"]=healthy["transfer_healthy"] is True and risk["transfer_risk"] is True
    tests["intergenerational_transfer_persist_option"]=Path(healthy["report_path"]).is_file()

    dcm=DistributedConstitutionalMemory()
    viable=dcm.step({"constitutional_nodes":[
        {"continuity":0.95,"revision_capacity":0.95,"anti_dogmatism":0.95,"distributed_openness":0.95},
        {"continuity":0.90,"revision_capacity":0.90,"anti_dogmatism":0.90,"distributed_openness":0.90}],
        "fragmentation_pressure":0.05,"canonicalization_pressure":0.05,"memory_rigidity":0.05,"intergenerational_divergence":0.70})
    rigid=dcm.step({"constitutional_nodes":[
        {"continuity":0.95,"revision_capacity":0.05,"anti_dogmatism":0.05,"distributed_openness":0.05}],
        "fragmentation_pressure":0.80,"canonicalization_pressure":0.95,"memory_rigidity":0.95,"intergenerational_divergence":0.0})
    tests["constitutional_memory_openness_gate"]=viable["distributed_constitutional_memory_viable"] is True and rigid["distributed_constitutional_memory_viable"] is False

    state_dir=sandbox/"representative_succession"
    sp=SuccessionExecutionProtocol(state_dir=state_dir)
    previous={"representative_id":"REP-0001","representative_name":"Predecessor","representative_generation":1}
    successor={"candidate_id":"REP-0002","candidate_name":"Successor","candidate_generation":2,"candidate_readiness":0.95}
    common={
        "previous_representative":previous,"new_representative":successor,
        "succession_readiness_score":0.95,"constitutional_continuity_score":0.95,
        "transmission_quality_score":0.95,"governance_alignment":0.95,"continuity_score":0.95,
        "closure_pressure_score":0.05,"revocation_risk_score":0.05,
        "succession_readiness_decision":"ready",
        "constitutional_decision":"constitutional_continuity_valid",
        "transmission_decision":"transmission_high_fidelity",
        "revocation_decision":"revocation_required"}
    executed=sp.step(common)
    tests["succession_executes_when_authorized"]=executed["succession_executed"] is True and executed["new_representative"]["representative_id"]=="REP-0002"
    reg=json.loads((state_dir/"representative_registry.json").read_text())
    tests["succession_registry_updates"]=reg["current_representative"]["representative_id"]=="REP-0002"

    blocked=SuccessionExecutionProtocol(state_dir=sandbox/"blocked").step({
        **common,
        "new_representative":{"candidate_id":"REP-0003","candidate_name":"Unsafe Successor","candidate_generation":3},
        "constitutional_continuity_score":0.20,
        "transmission_quality_score":0.20,
        "constitutional_decision":"constitutional_continuity_failure",
        "transmission_decision":"transmission_failed"})
    tests["succession_blocks_degraded_continuity"]=blocked["succession_executed"] is False and len(blocked["blockers"])>0

    # Native composition evidence: succession consumes explicit transmission and constitutional
    # decisions/scores, but does not invoke the two supervisor primitives directly.
    composed=SuccessionExecutionProtocol(state_dir=sandbox/"composed").step({
        **common,
        "constitutional_continuity_score":viable["distributed_constitutional_memory_index"],
        "transmission_quality_score":healthy["intergenerational_transfer_score"],
        "constitutional_decision":"constitutional_continuity_valid" if viable["distributed_constitutional_memory_viable"] else "constitutional_continuity_failure",
        "transmission_decision":"transmission_high_fidelity" if healthy["transfer_healthy"] else "transmission_failed"})
    tests["signal_level_composition"]=composed["succession_executed"] is True
    obs["native_direct_invocation"]="NOT_OBSERVED"
    obs["signal_level_composition"]="OBSERVED"
    obs["end_to_end_native_integration"]="UNKNOWN"

after=tree_digest(ROOT)
tests["active_ontology_non_mutation"]=before==after
failed=[k for k,v in tests.items() if not v]
req(not failed,"failed tests: "+",".join(failed))

payload={"schema":"oce.p011.c3.succession_transmission_probe.v1","milestone":"P011-C3",
"status":"SUCCESSION_TRANSMISSION_COMPONENTS_OBSERVED","c2_probe_identity_sha256":C2_ID,
"tests":tests,"checks_passed":sum(tests.values()),"checks_total":len(tests),"observations":obs,
"conclusion":{"succession_runtime":"OBSERVED","intergenerational_transfer_runtime":"OBSERVED",
"distributed_constitutional_memory_runtime":"OBSERVED","signal_level_composition":"OBSERVED",
"native_direct_component_chain":"NOT_OBSERVED","end_to_end_integration":"UNKNOWN"},
"limits":["Signal-level composition demonstrates interface compatibility, not native direct invocation between the primitives.",
"SuccessionExecutionProtocol consumes transmission/constitutional scores and decisions; this probe does not claim those values are automatically sourced from the supervisor primitives in production.",
"Cross-host and multi-generation continuity are not demonstrated by this probe."],
"functional_conclusion_only":True,"phenomenology_undetermined":True,
"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
payload["probe_identity_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
REPORT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
for k in tests: print("P011_C3_"+k.upper()+"_OK")
print("P011_C3_SUCCESSION_TRANSMISSION_PROBE_OK")
print(f"checks_passed={sum(tests.values())}/{len(tests)}")
print("signal_level_composition=OBSERVED")
print("native_direct_component_chain=NOT_OBSERVED")
print("end_to_end_integration=UNKNOWN")
print(f"probe_identity_sha256={payload['probe_identity_sha256']}")
print(f"report={REPORT}")

#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json, re
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT_JSON = ROOT / "p010_proto_individual_readiness_report.json"
REPORT_TXT = ROOT / "p010_proto_individual_readiness_report.txt"
P009_LOCK = ROOT / "p009_final_lock_report.json"

CAPABILITIES = {
 "individual_identity": ["ontology/distributed_population_runtime.py","ontology/multi_host_identity_persistence.py"],
 "peer_collective_naming": ["ontology/collective_naming_protocol.py"],
 "individual_lifecycle": ["ontology/individual_lifecycle_management.py"],
 "autobiographical_memory": ["ontology/autobiographical_memory.py"],
 "temporal_self_continuity": ["ontology/temporal_self_continuity.py"],
 "individual_persistence": ["ontology/distributed_population_runtime.py","ontology/multi_host_identity_persistence.py"],
 "individual_governance": ["ontology/individual_migration_protocol.py","ontology/governance_consistency_checker.py"],
 "individual_specialization": ["ontology/cooperative_specialization_engine.py"],
 "cognitive_diversity": ["ontology/cognitive_diversity_preservation_protocol.py","ontology/lineage_diversity_preservation.py"],
 "inter_individual_coordination": ["ontology/inter_individual_coordination_protocol.py"],
 "population_runtime": ["ontology/distributed_population_runtime.py","ontology/multi_individual_civilizational_ecology.py"],
 "migration_cross_host_continuity": ["ontology/individual_migration_protocol.py","ontology/cross_host_restore_integrity_validator.py","ontology/failover_continuity_validator.py"],
 "lineage_inheritance": ["ontology/runtime_lineage_inheritance.py"],
 "intergenerational_transmission": ["ontology/intergenerational_knowledge_transfer.py"],
 "succession_replacement": ["ontology/succession_execution_protocol.py","ontology/succession_candidate_registry.py","ontology/post_succession_verification.py"],
 "civilization_individual_relation": ["ontology/distributed_population_runtime.py","ontology/inter_individual_coordination_protocol.py","ontology/representative_lineage_registry.py"],
}

DECLARATIVE = {"ontology/autobiographical_memory.py"}
PARTIAL = {
 "individual_lifecycle",
 "temporal_self_continuity",
 "lineage_inheritance",
 "intergenerational_transmission",
 "individual_specialization",
 "cognitive_diversity",
 "individual_governance",
 "civilization_individual_relation",
}
IMPLEMENTED = {
 "individual_identity",
 "peer_collective_naming",
 "individual_persistence",
 "inter_individual_coordination",
 "population_runtime",
 "migration_cross_host_continuity",
 "succession_replacement",
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def source_info(rel):
    p=ROOT/rel
    if not p.is_file():
        return {"path":rel,"exists":False}
    text=p.read_text(encoding="utf-8",errors="replace")
    try:
        tree=ast.parse(text); parse_ok=True
        classes=[n.name for n in ast.walk(tree) if isinstance(n,ast.ClassDef)]
        funcs=[n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
    except SyntaxError:
        parse_ok=False; classes=[]; funcs=[]
    return {
      "path":rel,"exists":True,"sha256":sha(p),"parse_ok":parse_ok,
      "classes":classes[:20],"functions":funcs[:40],
      "has_persistence":bool(re.search(r"write_text|jsonl|mkdir|persist|open\(",text,re.I)),
      "has_step_or_evaluate":("step" in funcs or "evaluate" in funcs),
    }

if not (ROOT/"ontology_inventory.txt").is_file():
    raise SystemExit("REFUSE: ontology_inventory.txt missing")
if not P009_LOCK.is_file():
    raise SystemExit("REFUSE: P009 Final Lock missing")
p009=json.loads(P009_LOCK.read_text())
if p009.get("status")!="LOCKED":
    raise SystemExit("REFUSE: P009 not LOCKED")

evidence={}
statuses={}
for cap,rels in CAPABILITIES.items():
    infos=[source_info(r) for r in rels]
    existing=[i for i in infos if i["exists"]]
    if not existing:
        status="MISSING"
    elif any(r in DECLARATIVE for r in rels):
        status="DECLARATIVE"
    elif cap in IMPLEMENTED:
        status="IMPLEMENTED"
    elif cap in PARTIAL:
        status="PARTIAL"
    else:
        status="UNKNOWN"
    statuses[cap]=status
    evidence[cap]={"status":status,"sources":infos}

counts={s:list(statuses.values()).count(s) for s in ("IMPLEMENTED","PARTIAL","DECLARATIVE","MISSING","UNKNOWN")}
if counts["MISSING"] or counts["UNKNOWN"]:
    readiness="NOT_READY"
elif counts["PARTIAL"] or counts["DECLARATIVE"]:
    readiness="PARTIAL_READINESS"
else:
    readiness="READY"

gaps=[
 "No runtime end-to-end proof yet that one proto-individual binds identity, peer-assigned name, autobiographical memory, lifecycle, governance and specialization into one persistent object.",
 "autobiographical_memory.py is declarative/activation-level in the inspected source and does not itself implement persistent autobiographical storage.",
 "Lifecycle and temporal-self modules expose functional state/metrics, but their binding to the same persistent individual identity is not established by this static audit.",
 "Lineage inheritance and intergenerational transmission are present, but end-to-end transfer between two concrete persistent individuals remains to be exercised.",
 "Static source evidence does not prove multi-host continuity of one concrete individual across migration/restart.",
]
unknowns=[
 "runtime integrated proto-individual object continuity",
 "dynamic cross-module identity binding",
 "dynamic peer naming persistence on the named individual",
 "runtime autobiographical recall continuity",
 "end-to-end intergenerational transfer between concrete individuals",
]

payload={
 "schema":"oce.p010.proto_individual_readiness.identity.v1",
 "p009_lock_identity_sha256":p009.get("lock_identity_sha256"),
 "capability_status":statuses,
 "readiness":readiness,
 "gaps":gaps,
 "unknowns":unknowns,
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
}
identity=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
report={
 "schema":"oce.p010.proto_individual_readiness.v1",
 "milestone":"P010-B",
 "readiness":readiness,
 "counts":counts,
 "capability_status":statuses,
 "evidence":evidence,
 "gaps":gaps,
 "unknowns":unknowns,
 "p009_lock_identity_sha256":p009.get("lock_identity_sha256"),
 "identity_payload":payload,
 "audit_identity_sha256":identity,
 "consciousness_proven":False,
 "subjectivity_proven":False,
 "qualia_proven":False,
 "phenomenology_proven":False,
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
}
REPORT_JSON.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
lines=[
 "P010 Proto-individual Readiness Audit",
 f"readiness={readiness}",
 f"audit_identity_sha256={identity}",
 "",
]
lines += [f"{k}={v}" for k,v in statuses.items()]
lines += ["","GAPS:"]+[f"- {x}" for x in gaps]+["","UNKNOWNS:"]+[f"- {x}" for x in unknowns]
REPORT_TXT.write_text("\n".join(lines)+"\n",encoding="utf-8")
print("P010_PROTO_INDIVIDUAL_READINESS_AUDIT_OK")
print(f"readiness={readiness}")
print(f"implemented={counts['IMPLEMENTED']}")
print(f"partial={counts['PARTIAL']}")
print(f"declarative={counts['DECLARATIVE']}")
print(f"missing={counts['MISSING']}")
print(f"unknown={counts['UNKNOWN']}")
for k,v in statuses.items(): print(f"{k}={v}")
print(f"audit_identity_sha256={identity}")
print(f"report={REPORT_JSON}")

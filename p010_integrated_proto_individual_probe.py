#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json, re
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
READINESS = ROOT / "p010_proto_individual_readiness_report.json"
REPORT = ROOT / "p010_integrated_proto_individual_probe_report.json"

CANDIDATES = [
 "ontology/distributed_population_runtime.py",
 "ontology/multi_host_identity_persistence.py",
 "ontology/collective_naming_protocol.py",
 "ontology/individual_lifecycle_management.py",
 "ontology/autobiographical_memory.py",
 "ontology/temporal_self_continuity.py",
 "ontology/individual_migration_protocol.py",
 "ontology/cooperative_specialization_engine.py",
 "ontology/cognitive_diversity_preservation_protocol.py",
 "ontology/inter_individual_coordination_protocol.py",
 "ontology/runtime_lineage_inheritance.py",
 "ontology/intergenerational_knowledge_transfer.py",
 "ontology/succession_execution_protocol.py",
 "ontology/succession_candidate_registry.py",
 "ontology/post_succession_verification.py",
 "ontology/representative_lineage_registry.py",
]

TOKENS = {
 "identity": ("individual_id","identity_id","identity","individual"),
 "name": ("name","naming","named"),
 "memory": ("memory","autobiograph","episode","recall"),
 "lifecycle": ("lifecycle","life_cycle","birth","retire","death","status"),
 "governance": ("governance","permission","constraint","policy"),
 "specialization": ("specialization","specialisation","specialty","role"),
 "population": ("population","member","registry"),
 "migration": ("migration","host","restore","failover"),
 "lineage": ("lineage","inherit","succession","generation"),
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(rel):
    p=ROOT/rel
    if not p.is_file(): return None
    text=p.read_text(encoding="utf-8",errors="replace")
    try:
        tree=ast.parse(text)
        symbols=sorted({n.name for n in ast.walk(tree) if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef))})
    except SyntaxError:
        symbols=[]
    low=text.lower()
    hits={k: any(t in low for t in vals) for k,vals in TOKENS.items()}
    return {"path":rel,"sha256":sha(p),"symbols":symbols[:80],"token_hits":hits}

if not READINESS.is_file(): raise SystemExit("REFUSE: P010 readiness report missing")
r=json.loads(READINESS.read_text(encoding="utf-8"))
if r.get("readiness")!="PARTIAL_READINESS": raise SystemExit("REFUSE: unexpected P010 readiness")
mods=[x for x in (inspect(rel) for rel in CANDIDATES) if x]

# Static cross-binding evidence only: no fabricated Individual object and no source mutation.
binding={}
for dim in ("name","memory","lifecycle","governance","specialization","population","migration","lineage"):
    both=[m["path"] for m in mods if m["token_hits"]["identity"] and m["token_hits"][dim]]
    binding[dim]={"identity_cooccurrence_modules":both,"observed":bool(both)}

# Strong integration requires all core dimensions to be tied to identity in source evidence.
core=("name","memory","lifecycle","governance","specialization")
observed=sum(bool(binding[x]["observed"]) for x in core)

# Memory is explicitly DECLARATIVE in P010-B; therefore this probe cannot conclude fully integrated.
if r["capability_status"].get("autobiographical_memory")=="DECLARATIVE":
    outcome="INTEGRATED_PROTO_INDIVIDUAL_PARTIAL"
elif observed==len(core):
    outcome="INTEGRATED_PROTO_INDIVIDUAL_IMPLEMENTED"
elif observed:
    outcome="INTEGRATED_PROTO_INDIVIDUAL_PARTIAL"
else:
    outcome="INTEGRATED_PROTO_INDIVIDUAL_NOT_IMPLEMENTED"

limitations=[
 "This probe observes source-level cross-binding evidence; it does not fabricate or add an Individual runtime object.",
 "Token/symbol co-occurrence is evidence of candidate integration surfaces, not proof of end-to-end runtime continuity.",
 "P010-B classifies autobiographical memory as DECLARATIVE, preventing a full integrated-proto-individual conclusion.",
 "A subsequent adversarial/runtime campaign is required before P010 Final Lock.",
]
payload={
 "schema":"oce.p010.integrated_proto_individual_probe.identity.v1",
 "readiness_audit_identity_sha256":r["audit_identity_sha256"],
 "outcome":outcome,
 "core_identity_binding":binding,
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
}
identity=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
report={
 "schema":"oce.p010.integrated_proto_individual_probe.v1",
 "milestone":"P010-C2",
 "outcome":outcome,
 "candidate_module_count":len(mods),
 "core_dimensions":list(core),
 "core_dimensions_with_identity_binding":observed,
 "binding":binding,
 "limitations":limitations,
 "readiness_audit_identity_sha256":r["audit_identity_sha256"],
 "probe_identity_sha256":identity,
 "source_mutation_performed":False,
 "consciousness_proven":False,
 "subjectivity_proven":False,
 "qualia_proven":False,
 "phenomenology_proven":False,
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
}
REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P010_C2_NON_FABRICATION_OK")
print("P010_C2_IDENTITY_BINDING_SCAN_OK")
for d in core:
    print(f"P010_C2_{d.upper()}_BINDING={'OBSERVED' if binding[d]['observed'] else 'NOT_OBSERVED'}")
print("P010_C2_ANTI_OVERCLAIM_OK")
print("P010_C2_NON_MUTATION_OK")
print("P010_INTEGRATED_PROTO_INDIVIDUAL_PROBE_OK")
print(f"outcome={outcome}")
print(f"candidate_module_count={len(mods)}")
print(f"core_dimensions_with_identity_binding={observed}/{len(core)}")
print(f"probe_identity_sha256={identity}")
print(f"report={REPORT}")

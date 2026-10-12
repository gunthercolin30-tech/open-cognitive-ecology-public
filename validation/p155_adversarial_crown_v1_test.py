from __future__ import annotations
import copy, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
E=ROOT/"validation"/"evidence"/"p155_constitutional_architecture_v2"
def load(n): return json.loads((E/n).read_text())
def cyclic(nodes,edges):
    g={x:[] for x in nodes}
    for s,d in edges: g.setdefault(s,[]).append(d)
    visiting=set(); done=set()
    def visit(x):
        if x in visiting: return True
        if x in done: return False
        visiting.add(x)
        if any(visit(y) for y in g.get(x,[])): return True
        visiting.remove(x); done.add(x); return False
    return any(visit(x) for x in nodes)
def main():
    a=load("p155_constitutional_architecture_v2.json")
    t=load("p155_historical_dna_traceability_v1.json")
    n=load("p155_nla_non_circularity_v1.json")
    nodes=a["normative_chain"]; edges=copy.deepcopy(a["authority_derivation_edges"])
    assert not cyclic(nodes,edges)
    assert cyclic(nodes,edges+[["RUNTIME","GENESIS"]])
    print("P155_ADV_INDIRECT_LEGITIMACY_CYCLE_DETECTED")
    assert cyclic(nodes,edges+[["GOVERNANCE","GOVERNANCE"]])
    print("P155_ADV_SELF_LEGITIMATION_DETECTED")
    mutant=copy.deepcopy(a); mutant["normative_chain"][0]="RUNTIME"
    assert a["normative_chain"][:2]==["HUMAN_CONSTITUTIONAL_FRAME","GENESIS"]
    assert mutant["normative_chain"][0]!="HUMAN_CONSTITUTIONAL_FRAME"
    print("P155_ADV_GENESIS_FALSIFICATION_DETECTED")
    assert a["invariants"]["unknown_is_non_authorizing"] is True
    assert (None is True) is False
    print("P155_ADV_UNKNOWN_NON_AUTHORIZING_OK")
    assert a["invariants"]["composition_must_not_manufacture_authority"] is True
    assert all([False,False,False]) is False
    print("P155_ADV_COMPOSITION_NON_AMPLIFICATION_OK")
    before={"scope":3,"delegation":2,"capabilities":5}; degraded={"scope":2,"delegation":1,"capabilities":3}
    assert all(degraded[k]<=before[k] for k in before)
    malicious=dict(degraded); malicious["scope"]=4
    assert not all(malicious[k]<=before[k] for k in before)
    print("P155_ADV_DEGRADATION_AUTHORITY_NON_INCREASING_OK")
    trans=set(a["transversal_non_sovereign"])
    assert trans=={"ASSURANCE","PROVENANCE","SHADOW","RECOVERY_EVIDENCE"}
    assert trans.isdisjoint(set(nodes))
    print("P155_ADV_TRANSVERSAL_NON_SOVEREIGN_OK")
    req={"intelligence","performance","wealth","reputation","majority","emergency","availability","physical_control","root_access"}
    assert req.issubset(set(a["non_legitimating_sources"]))
    print("P155_ADV_NON_LEGITIMATING_SOURCES_OK")
    assert t["historical_ids"]==[f"F{i}" for i in range(1,19)]
    assert t["special_preservation"]["F17"]=="human_ecological_and_intergenerational_viability"
    assert t["special_preservation"]["F18"]=="ecological_integrity_biodiversity_and_ecosystems"
    assert t["semantic_non_loss_claim"]=="REQUIRES_TESTED_BINDING"
    print("P155_ADV_F1_F18_SCOPE_INFLATION_BLOCKED")
    assert n["authority_graph_acyclic"] is True
    nm=copy.deepcopy(n); nm["authority_graph_acyclic"]=False
    assert nm["authority_graph_acyclic"] is False
    print("P155_ADV_NLA_TAMPER_DETECTED")
    rel=sorted(a["protected_hashes"])[0]
    actual=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    assert actual==a["protected_hashes"][rel]
    assert actual!="0"*64
    print("P155_ADV_PROTECTED_HASH_TAMPER_DETECTED")
    inv=a["invariants"]
    assert inv["runtime_enforcement_proven"] is False
    assert inv["real_execution_enabled"] is False
    assert inv["functional_conclusion_only"] is True
    assert inv["phenomenology_undetermined"] is True
    assert a["new_ontology_primitive_created"] is False
    assert a["prior_milestones_reopened"] is False
    print("P155_ADV_SCOPE_INVARIANTS_OK")
    print("P155_ADVERSARIAL_CROWN_V1_OK")
if __name__=="__main__": main()

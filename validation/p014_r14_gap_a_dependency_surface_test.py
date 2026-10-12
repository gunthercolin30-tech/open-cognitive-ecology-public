#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology.dependency_registry import *
def fixtures():
    cats=("software","model","data","tool_api","infrastructure","build_chain","governance_service","human")
    return [p014_r14_dependency_record("d%d"%i,c,"p%d"%(i%3),"1.%d"%i,
        criticality="DC%d"%min(i,5), direct_dependencies=[] if i==0 else ["d%d"%(i-1)],
        failure_domain="fd%d"%(i%2), strategic=(i==7), evidence_state="VERIFIED",
        replaceable=True, independent_provider=True, provenance={"source":"test"}) for i,c in enumerate(cats)]
def main():
    r=fixtures(); cbd=p014_r14_civilizational_bill_of_dependencies(r)
    assert cbd["surface_complete"] and cbd["evidence_state"]=="VERIFIED"
    g=p014_r14_dependency_graph(r); assert not g["unresolved_edges"]
    assert "d0" in p014_r14_transitive_dependencies(g,"d7")
    assert p014_r14_common_providers(r)
    assert p014_r14_provider_pluralism(r,["d0","d1"])["independent_pluralism"]
    assert p014_r14_failure_domains(r)["evidence_state"]=="VERIFIED"
    assert p014_r14_provider_blast_radius(r,"p0")["blast_radius"]>=1
    ex=p014_r14_reverse_exposure(r,"d0"); assert not ex["compromise_inferred"] and ex["compromised"]==[]
    assert p014_r14_dependency_sovereignty_vector(r[0])["version_pinned"]
    assert not p014_r14_silent_strategic_dependencies(r)
    assert p014_r14_gap_a_assess(r)["ready_for_semantic_reaudit"]
    print("P014_R14_GAP_A_FUNCTIONAL_OK")
    bad=[p014_r14_dependency_record("x","software",None,None,strategic=True)]
    a=p014_r14_gap_a_assess(bad)
    assert not a["ready_for_semantic_reaudit"] and a["cbd"]["evidence_state"]=="LIMITED"
    assert a["silent_strategic_dependencies"]
    print("P014_R14_GAP_A_DEGRADATION_OK")
    assert isinstance(DEPENDENCY_REGISTRY,dict) and DEPENDENCY_REGISTRY
    print("P014_R14_GAP_A_NON_REGRESSION_OK")
if __name__=="__main__": main()

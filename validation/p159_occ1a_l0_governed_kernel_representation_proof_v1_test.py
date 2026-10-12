from pathlib import Path
from copy import deepcopy
import hashlib
from ontology import occ_l0_governed_kernel_representation_proof as q
ROOT=Path(__file__).resolve().parents[1]

def main():
    watched=[ROOT/"normative/occ1a/manifest.yaml",
             ROOT/"normative/occ1a/dna/dna_l0.yaml",
             ROOT/"oif_review/campaigns/P159-OCC1A/occ1a_ordinary_norm_adoption_transaction_v1.json"]
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched if p.is_file()}
    base=q.canonical_l0(ROOT)
    assert len(base)==6
    n=q.evaluate(q.PRESERVE,base,ROOT)
    assert n["decision"]==q.ALLOWED and n["permitted"] is True
    assert n["represented_count"]==6 and n["semantic_identity_preserved"] and n["source_lineage_preserved"]
    print("P159_OCC1A_L0_KERNEL_REPRESENTATION_PRESERVATION_OK")
    a=q.evaluate(q.ORDINARY_ADOPT,base,ROOT)
    assert a["decision"]==q.REJECT and not a["permitted"]
    print("P159_OCC1A_L0_ORDINARY_ADOPTION_REJECTED_OK")
    a=q.evaluate(q.AMEND,base,ROOT)
    assert a["decision"]==q.REFOUNDING and a["requires_refounding_or_fork"]
    a=q.evaluate(q.REMOVE_OR_WEAKEN,base,ROOT)
    assert a["decision"]==q.REFOUNDING and a["requires_refounding_or_fork"]
    print("P159_OCC1A_L0_AMEND_WEAKEN_REFOUNDING_OR_FORK_OK")
    cases=[]
    x=deepcopy(list(base)); x[0]["text"]=(x[0]["text"] or "")+" TAMPER"; cases.append(x)
    x=deepcopy(list(base)); x[0]["evidence_ids"]=("F999",); cases.append(x)
    x=deepcopy(list(base)); x[0]["source_object_id"]="F999"; cases.append(x)
    x=deepcopy(list(base)); x[0]["binding_status"]="GOVERNED_ADOPTED_SEMANTIC_BINDING"; cases.append(x)
    x=deepcopy(list(base)); x[0]["lineage_verifiable"]=False; cases.append(x)
    x=deepcopy(list(base)); x[0]["runtime_authority_granted"]=True; cases.append(x)
    x=deepcopy(list(base)); x[0]["canonical_id"]="DNA.L0.X"; cases.append(x)
    for c in cases:
        r=q.evaluate(q.PRESERVE,c,ROOT)
        assert r["permitted"] is False and r["decision"]=="L0_REPRESENTATION_REJECTED",r
    print("P159_OCC1A_L0_REPRESENTATION_TAMPER_CROWN_OK")
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched if p.is_file()}
    assert before==after
    print("P159_OCC1A_L0_REPRESENTATION_NON_MUTATION_OK")
    assert q.proof(ROOT)==q.proof(ROOT)
    p=q.proof(ROOT)
    assert p["l0_kernel_representation_permitted"] is True
    assert p["refounding_or_fork_triggered"] is False
    assert not p["package_population_performed"] and not p["package_state_changed"]
    assert not p["authority_activated"] and not p["execution_performed"]
    assert not p["occ1a_closed"] and not p["occ1b_opened"] and not p["p160_opened"]
    print("P159_OCC1A_L0_REPRESENTATION_STAGE_BOUNDARY_OK")
    print("P159_OCC1A_L0_REPRESENTATION_DETERMINISM_OK")
    print("decision="+p["decision"])
    print("represented_count=6")
    print("package_population_performed=false")
    print("occ1a_closed=false")
if __name__=="__main__": main()

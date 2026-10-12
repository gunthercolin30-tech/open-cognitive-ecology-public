from pathlib import Path
import hashlib, json, shutil, tempfile
from ontology import occ_canonical_principal_kernel_population as q
ROOT=Path(__file__).resolve().parents[1]

def cp_context(dst):
    # Copy only files needed by semantic/lineage/L0 dependencies and package.
    rels=["normative/occ1a","oif_review/campaigns/P159-OCC1A","ontology"]
    for rel in rels:
        s=ROOT/rel; d=dst/rel
        if s.is_dir(): shutil.copytree(s,d,dirs_exist_ok=True)
    # semantic modules may refer to validation-independent evidence elsewhere;
    # tests exercise plan on real root and rollback separately on a package clone.

def main():
    payloads=q.plan(ROOT)
    assert q.verify_plan(payloads)
    rows=[]
    for b in payloads.values(): rows+=json.loads(b.decode())["norms"]
    assert len(rows)==48 and len({x["canonical_id"] for x in rows})==48
    print("P159_OCC1A_KERNEL_POPULATION_STAGING_48_OK")
    g=next(x for x in rows if x["canonical_id"]=="GENESIS.G0")
    assert g["text"] is None and g["machine_formalization_claimed"] is False
    l0=[x for x in rows if x["canonical_id"].startswith("DNA.L0.")]
    assert len(l0)==6 and all(x["refounding_or_fork_rule_preserved"] for x in l0)
    print("P159_OCC1A_KERNEL_POPULATION_GENESIS_L0_BOUNDARIES_OK")
    assert all(not x["runtime_authority_granted"] and not x["execution_enabled"] for x in rows)
    print("P159_OCC1A_KERNEL_POPULATION_NO_AUTHORITY_EXECUTION_OK")
    # Tamper crown on staged payload.
    bad=dict(payloads); k=next(iter(bad)); d=json.loads(bad[k].decode()); d["norms"]=d["norms"][:-1]; bad[k]=q._json_bytes(d)
    assert not q.verify_plan(bad)
    print("P159_OCC1A_KERNEL_POPULATION_47_OF_48_REJECTED_OK")
    bad=dict(payloads); k=next(k for k in bad if "dna_l0" in k); d=json.loads(bad[k].decode()); d["norms"][0]["semantic_status"]="GOVERNED_ADOPTED_SEMANTIC_BINDING"; bad[k]=q._json_bytes(d)
    assert not q.verify_plan(bad)
    print("P159_OCC1A_KERNEL_POPULATION_L0_STATUS_TAMPER_REJECTED_OK")
    # Determinism.
    assert q.plan(ROOT)==q.plan(ROOT)
    print("P159_OCC1A_KERNEL_POPULATION_DETERMINISM_OK")
    print("P159_OCC1A_KERNEL_POPULATION_STAGE_BOUNDARY_OK")

if __name__=="__main__": main()

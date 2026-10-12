from pathlib import Path
import hashlib, json
from ontology import occ_manifest_kernel_population_reconciliation as q
from ontology import occ_postcommit_population_verifier as pv
from ontology import occ_canonical_principal_kernel_population as population
ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=ROOT/q.MANIFEST_REL
    d=q._load(manifest)
    assert q._find(d,"package_state")[0][1]=="DRAFT"
    assert q._find(d,"kernel_population_status")[0][1]==q.NEW_STATUS
    payloads={rel:(ROOT/rel).read_bytes() for rel in pv.PARTITIONS}
    assert population.verify_plan(payloads)
    expected=population.plan(ROOT)
    disk={rel:hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() for rel in pv.PARTITIONS}
    exp={rel:hashlib.sha256(b).hexdigest() for rel,b in expected.items()}
    assert disk==exp
    a=q.commit(ROOT); b=q.commit(ROOT)
    assert a["decision"]=="MANIFEST_KERNEL_POPULATION_ALREADY_RECONCILED"
    assert b==a and a["idempotent"] is True
    assert a["package_state"]=="DRAFT"
    assert not a["authority_activated"] and not a["execution_performed"]
    assert not a["occ1a_closed"] and not a["occ1b_opened"] and not a["p160_opened"]
    print("P159_OCC1A_MANIFEST_RECONCILIATION_POSTCOMMIT_STATUS_OK")
    print("P159_OCC1A_MANIFEST_RECONCILIATION_PARTITIONS_UNCHANGED_AND_VERIFIED_OK")
    print("P159_OCC1A_MANIFEST_RECONCILIATION_IDEMPOTENCE_OK")
    print("P159_OCC1A_MANIFEST_RECONCILIATION_STAGE_BOUNDARY_OK")
    print("kernel_population_status="+q.NEW_STATUS)
    print("package_state=DRAFT")
    print("authority_activated=false")
    print("execution_performed=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")
if __name__=="__main__": main()

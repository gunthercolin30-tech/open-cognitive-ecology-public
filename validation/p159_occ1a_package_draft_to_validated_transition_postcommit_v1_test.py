from pathlib import Path
import hashlib, json
from ontology import occ_package_draft_to_validated_transition as q
from ontology import occ_manifest_kernel_population_reconciliation as mio
from ontology import occ_postcommit_population_verifier as pv
from ontology import occ_canonical_principal_kernel_population as population
ROOT=Path(__file__).resolve().parents[1]

def main():
    d=mio._load(ROOT/q.MANIFEST_REL)
    assert q._state(d,"package_state")[1]=="VALIDATED"
    assert q._state(d,"kernel_population_status")[1]=="POPULATED_48_VERIFIED"
    payloads={x:(ROOT/x).read_bytes() for x in pv.PARTITIONS}
    assert population.verify_plan(payloads)
    expected=population.plan(ROOT)
    assert {x:hashlib.sha256(payloads[x]).hexdigest() for x in pv.PARTITIONS} == \
           {x:hashlib.sha256(expected[x]).hexdigest() for x in pv.PARTITIONS}
    a=q.commit(ROOT); b=q.commit(ROOT)
    assert a==b and a["decision"]=="PACKAGE_ALREADY_VALIDATED" and a["idempotent"] is True
    assert a["package_validation_performed"] is True
    assert not a["authority_activated"] and not a["execution_performed"]
    assert not a["occ1a_closed"] and not a["occ1b_opened"] and not a["p160_opened"]
    print("P159_OCC1A_PACKAGE_TRANSITION_POSTCOMMIT_VALIDATED_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_KERNEL_STATUS_PRESERVED_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_PARTITIONS_48_UNCHANGED_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_IDEMPOTENCE_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_STAGE_BOUNDARY_OK")
    print("package_state=VALIDATED")
    print("kernel_population_status=POPULATED_48_VERIFIED")
    print("authority_activated=false")
    print("execution_performed=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")
if __name__=="__main__": main()

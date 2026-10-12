from pathlib import Path
from ontology import occ_package_draft_to_validated_transition as q
ROOT=Path(__file__).resolve().parents[1]
def main():
    v=q.verify_validated(ROOT)
    assert v["decision"]=="VALIDATED_PACKAGE_INDEPENDENTLY_REVERIFIED"
    a=q.prepare(ROOT); assert a["already_validated"] is True
    c1=q.commit(ROOT); c2=q.commit(ROOT)
    assert c1==c2 and c1["decision"]=="PACKAGE_ALREADY_VALIDATED" and c1["idempotent"] is True
    assert c1["package_state"]=="VALIDATED" and c1["kernel_population_status"]=="POPULATED_48_VERIFIED"
    assert not c1["authority_activated"] and not c1["execution_performed"]
    assert not c1["occ1a_closed"] and not c1["occ1b_opened"] and not c1["p160_opened"]
    print("P159_OCC1A_PACKAGE_TRANSITION_V1_1_VALIDATED_REVERIFY_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_V1_1_POSTCOMMIT_REPLAY_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_V1_1_IDEMPOTENCE_OK")
    print("P159_OCC1A_PACKAGE_TRANSITION_V1_1_STAGE_BOUNDARY_OK")
    print("package_state=VALIDATED")
    print("kernel_population_status=POPULATED_48_VERIFIED")
    print("authority_activated=false")
    print("execution_performed=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")
if __name__=="__main__": main()

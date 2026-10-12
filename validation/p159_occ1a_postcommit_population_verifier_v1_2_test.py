from pathlib import Path
from copy import deepcopy
import hashlib, json
from ontology import occ_postcommit_population_verifier as q
ROOT=Path(__file__).resolve().parents[1]

def main():
    watched=[ROOT/x for x in q.PARTITIONS]+[ROOT/"normative/occ1a/manifest.yaml"]
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    a=q.verify(ROOT)
    b=q.verify(ROOT)
    assert a==b
    assert a["decision"]=="POSTCOMMIT_POPULATION_VERIFIED"
    assert a["physical_population_verified"] and a["populated_count"]==48 and a["partition_count"]==6
    assert a["disk_matches_validated_evidence"]
    assert a["semantic_evidence_complete"] and a["source_lineage_complete"]
    assert a["package_state"]=="DRAFT"
    assert a["genesis_no_invention"] and a["l0_protection_preserved"]
    assert not a["authority_activated"] and not a["execution_performed"]
    assert not a["package_state_changed"] and not a["manifest_mutated"]
    assert not a["occ1a_closed"] and not a["occ1b_opened"] and not a["p160_opened"]
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    assert before==after
    print("P159_OCC1A_POSTCOMMIT_PHYSICAL_48_REVERIFY_OK")
    print("P159_OCC1A_POSTCOMMIT_DISK_VS_EVIDENCE_OK")
    print("P159_OCC1A_POSTCOMMIT_MANIFEST_STRUCTURAL_DRAFT_OK")
    print("P159_OCC1A_POSTCOMMIT_GENESIS_L0_BOUNDARIES_OK")
    print("P159_OCC1A_POSTCOMMIT_NON_MUTATION_OK")
    print("P159_OCC1A_POSTCOMMIT_DETERMINISM_OK")
    print("decision="+a["decision"])
    print("populated_count="+str(a["populated_count"]))
    print("package_state="+str(a["package_state"]))
    print("kernel_population_status_observed="+str(a["kernel_population_status_observed"]))
    print("authority_activated=false")
    print("execution_performed=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")
if __name__=="__main__": main()

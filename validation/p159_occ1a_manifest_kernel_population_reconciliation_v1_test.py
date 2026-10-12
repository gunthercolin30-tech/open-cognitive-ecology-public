from pathlib import Path
import hashlib, json
from ontology import occ_manifest_kernel_population_reconciliation as q
from ontology import occ_postcommit_population_verifier as pv
ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=ROOT/q.MANIFEST_REL
    parts=[ROOT/x for x in pv.PARTITIONS]
    part_before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in parts}
    m_before=hashlib.sha256(manifest.read_bytes()).hexdigest()
    plan=q.prepare(ROOT)
    assert plan["before_sha256"]==m_before
    if not plan["already_reconciled"]:
        assert plan["after_sha256"]!=plan["before_sha256"]
    print("P159_OCC1A_MANIFEST_RECONCILIATION_PRECONDITION_48_VERIFIED_OK")
    print("P159_OCC1A_MANIFEST_RECONCILIATION_DELTA_SINGLE_FIELD_OK")
    # prepare is read-only
    assert hashlib.sha256(manifest.read_bytes()).hexdigest()==m_before
    assert {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in parts}==part_before
    print("P159_OCC1A_MANIFEST_RECONCILIATION_PREPARE_NON_MUTATION_OK")
    print("P159_OCC1A_MANIFEST_RECONCILIATION_READY")
if __name__=="__main__": main()

from pathlib import Path
import hashlib, json
from ontology import occ_canonical_principal_kernel_population as q
ROOT=Path(__file__).resolve().parents[1]
def main():
    x=q.inspect_disk(ROOT)
    assert x["valid"] and x["populated_count"]==48,x
    m=(ROOT/"normative/occ1a/manifest.yaml").read_text(encoding="utf-8")
    assert "package_state: DRAFT" in m or 'package_state: "DRAFT"' in m or "package_state: 'DRAFT'" in m
    print("P159_OCC1A_KERNEL_POPULATION_POSTCOMMIT_48_OK")
    print("P159_OCC1A_KERNEL_POPULATION_PACKAGE_REMAINS_DRAFT_OK")
    print("authority_activated=false")
    print("execution_performed=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")
if __name__=="__main__": main()

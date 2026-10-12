from __future__ import annotations
import json
from pathlib import Path
from ontology.dna_registry import *
ROOT=Path.home()/"open-cognitive-ecology"
def main():
    m=registry_manifest(); entries=registry_entries()
    checks={
      "scope":P017_SCOPE=="P017_ONLY","schema":P017_SCHEMA_VERSION=="oce.p017.dna_registry.v1",
      "nonempty":len(entries)>=1,"count_consistent":m["entry_count"]==len(entries),
      "unique_keys":len({e["registry_key"] for e in entries})==len(entries),
      "valid_layers":all(e["layer"] in VALID_LAYERS for e in entries),
      "scope_present":all(bool(e["scope"]) for e in entries),
      "enforcement_present":all(e["enforcement_status"]=="UNKNOWN" for e in entries),
      "test_coverage_present":all(bool(e["test_coverage"]) for e in entries),
      "version_present":all(bool(e["version"]) for e in entries),
      "provenance_present":all(bool(e["provenance"]) for e in entries),
      "dependencies_present":all(isinstance(e["dependencies"],tuple) for e in entries),
      "self_validation":validate_registry()["valid"] is True,
      "no_runtime_authority":P017_BOUNDARIES["does_not_grant_runtime_authority"] is True,
      "p018_not_defined":P017_BOUNDARIES["does_not_define_p018_rule_contract"] is True,
      "functional_only":m["functional_conclusion_only"] is True,
      "phenomenology_undetermined":m["phenomenology_undetermined"] is True}
    report={"schema":P017_SCHEMA_VERSION,"milestone":"P017","status":"PASS" if all(checks.values()) else "FAIL",
      "scope":P017_SCOPE,"checks":checks,"unknown_promotion":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
    (ROOT/"p017_dna_registry_report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    assert all(checks.values()),checks
    print("P017_DNA_REGISTRY_OK")
if __name__=="__main__": main()

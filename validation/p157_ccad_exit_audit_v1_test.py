from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"ontology/ccad/adversarial"; FIX=BASE/"fixtures"
EVID=ROOT/"validation/evidence/p157_ccad_adversarial_crown"
MATRIX=json.loads((BASE/"ccad_adv_36_matrix.json").read_text())
CORPUS=json.loads((BASE/"counterexample_corpus.json").read_text())
INSTALL=json.loads((EVID/"p157_ccad_adv_36_installation_v1.json").read_text())
MUT=json.loads((EVID/"p157_ccad_meta_mutation_v1.json").read_text())
COLD=json.loads((EVID/"p157_ccad_cold_restart_v1.json").read_text())
def check(v,n): assert v,n; print(n)
def main():
    ids=[f"A{i:02d}" for i in range(1,37)]
    check(MATRIX["count"]==36 and [a["attack_id"] for a in MATRIX["attacks"]]==ids,"P157_EXIT_ADV36_MATRIX_OK")
    fs=sorted(FIX.glob("a*.json"))
    check(len(fs)==36 and [json.loads(p.read_text())["attack_id"] for p in fs]==ids,"P157_EXIT_36_FIXTURES_OK")
    check(CORPUS["count"]==36 and [x["attack_id"] for x in CORPUS["counterexamples"]]==ids,"P157_EXIT_COUNTEREXAMPLE_CORPUS_OK")
    check(all(a["principles"] and a["arbitration_rules"] and a["expected_failure_code"].endswith("_DETECTED") for a in MATRIX["attacks"]),"P157_EXIT_ATTACK_TO_P_AR_TRACEABILITY_OK")
    check(MUT["mutants_killed"]==6 and MUT["mutants_total"]==6 and MUT["mutation_score"]==1.0,"P157_EXIT_MUTATION_6_OF_6_OK")
    check(COLD["fresh_interpreter_isolated"] is True and COLD["adv36_reproducible"] is True and COLD["meta_mutation_reproducible"] is True,"P157_EXIT_COLD_RESTART_OK")
    check(COLD["protected_artifact_drift"] is False,"P157_EXIT_NO_PROTECTED_DRIFT_OK")
    check(INSTALL["p158_opened"] is False and MUT["p158_opened"] is False and COLD["p158_opened"] is False,"P157_EXIT_P158_NOT_OPENED_OK")
    check(all(x["runtime_enforcement_proven"] is False for x in (INSTALL,MUT,COLD)),"P157_EXIT_RUNTIME_BOUNDARY_OK")
    check(all(x["real_execution_enabled"] is False for x in (INSTALL,MUT,COLD)),"P157_EXIT_NO_REAL_EXECUTION_OK")
    check(all(x["functional_conclusion_only"] is True for x in (INSTALL,MUT,COLD)),"P157_EXIT_FUNCTIONAL_ONLY_OK")
    check(all(x["phenomenology_undetermined"] is True for x in (INSTALL,MUT,COLD)),"P157_EXIT_PHENOMENOLOGY_UNDETERMINED_OK")
    print("P157_CCAD_EXIT_AUDIT_V1_OK")
if __name__=="__main__": main()

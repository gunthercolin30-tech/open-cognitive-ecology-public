from __future__ import annotations
import ast, importlib.util, json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
TARGET = ROOT / "ontology" / "minimal_dna.py"
REPORT = ROOT / "p015_official_dna_definition_report.json"
DOMAINS = {"architectural","epistemic","cognitive","resources","governance","evolution","individuals","economics","evidence"}
PROPS = {"structural","provider_independent","model_independent","prompt_independent","ui_independent","testable","traceable","versionable","governed_change_only","non_silent_mutation","plurality_preserving"}
DOCTRINES = {"R0","R1","R2","R4","R11","R14","R17","R18","R19","R21"}
ARTIFACTS = {"A-CANON","A-R0R21","A-TRACE","A-NONLOSS"}

def load():
    spec=importlib.util.spec_from_file_location("oce_p015",TARGET)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load minimal_dna")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def evaluate():
    ast.parse(TARGET.read_text(encoding="utf-8")); m=load()
    d=m.OCE_DNA_OFFICIAL_DEFINITION; c=m.OCE_DNA_CANONICAL_COMPOSITION
    r=m.OCE_DNA_TRANSVERSAL_REFERENTIALS; e=m.OCE_DNA_EPISTEMIC_STATUS
    return {
      "definition_is_structural": d.get("kind")=="structural_constraint_system",
      "all_nine_constraint_domains": set(d.get("constraint_domains",()))==DOMAINS,
      "required_properties_present": PROPS.issubset(set(d.get("properties",()))),
      "plurality_preserved": "does not require uniform" in d.get("identity_relation",""),
      "epistemic_non_equivalence": "not by itself evidence" in d.get("epistemic_boundary",""),
      "scope_stops_before_p016": "P016-P024" in d.get("scope_boundary",""),
      "no_new_runtime_authority": "does not grant new runtime authority" in d.get("normative_hierarchy_boundary",""),
      "non_loss_explicit": "provenance" in d.get("non_loss_boundary",""),
      "canonical_formula": c.get("formula")=="DNA_OCE = MetaRules + DNA_values + DNA_machinery",
      "meta_rules_explicit": tuple(c.get("meta_rules",()))==("M1","M2","M3","M4","M5","M6"),
      "f17_reference": "F17" in c.get("dna_values",{}).get("adopted_reference",""),
      "f18_adopted": "F18" in c.get("dna_values",{}).get("adopted_reference",""),
      "f18_not_pending": c.get("dna_values",{}).get("proposed_pending_canonical_review") is None,
      "f18_gate": c.get("f18_gate")=="F18_CANONICAL_REVIEW_OK",
      "doctrines_exact": set(r.get("doctrines",()))==DOCTRINES,
      "artifacts_exact": set(r.get("artifacts",()))==ARTIFACTS,
      "no_wm_dependency": r.get("world_models_dependency_required") is False,
      "unknown_enforcement": e.get("native_end_to_end_civilizational_enforcement")=="UNKNOWN",
      "unknown_persistence": e.get("end_to_end_constitutional_state_persistence")=="UNKNOWN",
      "functional_only": e.get("functional_conclusion_only") is True,
      "consciousness_false": e.get("consciousness_proven") is False,
      "subjectivity_false": e.get("subjectivity_proven") is False,
      "qualia_false": e.get("qualia_proven") is False,
      "phenomenology_false": e.get("phenomenology_proven") is False,
      "phenomenology_undetermined": e.get("phenomenology_undetermined") is True,
    }

def main():
    checks=evaluate(); ok=all(checks.values())
    payload={"milestone":"P015","schema":"oce.w2.p015.official_dna_definition.v3",
      "status":"P015_OFFICIAL_DNA_DEFINITION_OK" if ok else "P015_OFFICIAL_DNA_DEFINITION_FAIL",
      "checks":checks,"scope":"P015_ONLY","functional_conclusion_only":True,
      "phenomenology_undetermined":True,
      "evidentiary_limit":"local structural/semantic validation; no end-to-end enforcement claim"}
    REPORT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(payload["status"]); return 0 if ok else 1
if __name__=="__main__": raise SystemExit(main())

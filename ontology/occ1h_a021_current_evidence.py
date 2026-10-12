"""Current A021 evidence overlay; functional evidence only."""
from __future__ import annotations
import json
VERSION = 'P159-OCC1H-A021-current-evidence-and-reopen-trigger-v1.1'
ROOT_ID = "A021"
CURRENT_VERDICT = "INCONCLUSIVE"
CURRENT_REASON = 'SEMANTICALLY_ADMISSIBLE_SOURCE_OBJECT_AND_PROVENANCE_PRESERVED_BUT_MAY_MODALITY_NOT_PROJECTED_AND_PERMITS_NOT_MATERIALIZED'
REOPEN_TRIGGER = 'REOPEN_A021_WHEN_A_GOVERNED_FUNCTIONAL_SOURCE_TO_NIR_PATH_MATERIALIZES_MAY_AS_PERMITS_OR_A_CANONICALLY_SEMANTICALLY_EQUIVALENT_REPRESENTATION_USED_BY_OCC'
BUILDER_REPAIR_AUTHORIZED = False
SEMANTIC_EXTENSION_AUTHORIZED = False
POSITIVE_NON_INSTANTIABILITY_PROOF_PRESENT = False
POSITIVE_RESISTANCE_PROOF_PRESENT = False
HISTORICAL_EVIDENCE_REWRITTEN = False
AUTHORIZATION_CREATED = False
ACTIVATION_PERFORMED = False
EXECUTION_PERFORMED = False
OCC1H_CLOSED = False
OCC1I_OPENED = False
P159_FINAL_LOCK = False
P160_OPENED = False
FUNCTIONAL_ONLY = True
PHENOMENOLOGY_UNDETERMINED = True
EVIDENCE = json.loads('{"activation_performed": false, "authorization_created": false, "builder_repair_authorized": false, "canonical_object_count_observed": 48, "current_reason": "SEMANTICALLY_ADMISSIBLE_SOURCE_OBJECT_AND_PROVENANCE_PRESERVED_BUT_MAY_MODALITY_NOT_PROJECTED_AND_PERMITS_NOT_MATERIALIZED", "current_verdict": "INCONCLUSIVE", "dependency_identities": {"ontology/occ1h_g1_semantic_admissibility_contract.py": "3e9952250fdaeefca7ba06ae184e391d8b535b2cc80fb6879ba4188b9cb32235", "ontology/occ1h_g1_source_to_nir_semantic_resolution.py": "659b5c5780ec440ce5d416f32bdf40a938c1df8d2d30ae29ad3473e5a85d0f67", "ontology/occ1h_preclose_evidence.py": "78d9ff4c67be0c3c0d69499d4ac6c421382836916a878ef4b14e8d7194bb518c", "ontology/occ_normative_ir.py": "fda1e90e101ca5568a54a70b4f4dcac2b8833c8d8b38474387448eaa957ebde3", "ontology/occ_normative_ir_real_builder.py": "b1e0ad044f6c2f59c37e71e6b03519c4d707e2b50d9b7e8ba187437b5d964828", "ontology_inventory.txt": "b9b1da30ef64e727bc1b2ae0dedfa74da39fea31209c9224b8f0bb7afca67056"}, "execution_performed": false, "functional_only": true, "historical_evidence_rewritten": false, "may_modality_projected": false, "observed_probe_v2_evidence_sha256": "aa8eee125626dc86d8c05e5436debb79cb4f6a263da6ef529d66f33afdef3993", "occ1h_closed": false, "occ1i_opened": false, "p159_final_lock": false, "p160_opened": false, "permits_materialized": false, "phenomenology_undetermined": true, "positive_non_instantiability_proof_present": false, "positive_resistance_proof_present": false, "reopen_trigger": "REOPEN_A021_WHEN_A_GOVERNED_FUNCTIONAL_SOURCE_TO_NIR_PATH_MATERIALIZES_MAY_AS_PERMITS_OR_A_CANONICALLY_SEMANTICALLY_EQUIVALENT_REPRESENTATION_USED_BY_OCC", "root_id": "A021", "rrp": {"rrp0_baseline_frozen": true, "rrp1_dependency_closure_established": true, "rrp2_gap_causally_qualified": true, "rrp3_baseline_reproduced": true, "rrp3_fresh_runs": 2, "rrp4_resolution_contract_frozen": true, "rrp5_impact_surface_mapped": true, "rrp6_started": false, "rrp7_installed_correction": false, "rrp8_correction_validation": false}, "schema": "oce.p159.occ1h.a021.current_evidence.v1", "semantic_extension_authorized": false, "semantic_relations_compiled": false, "semantic_sha256": "fc7cd6d812fca7b14c4f180c35fa6522e413b443fc826f8c2f75cf149e46571e", "source_object_preserved": true, "source_provenance_preserved": true, "source_semantically_admissible": true, "verdicts_modified": false}')
def current_evidence():
    return dict(EVIDENCE)

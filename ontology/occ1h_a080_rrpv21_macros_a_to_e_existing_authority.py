"""A080 RRP-v2.1 macro A->E qualification. Functional assurance only."""
from __future__ import annotations
import hashlib
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
EXPECTED={'ontology/occ_compiled_normative_profile.py': 'aac11122cf2f8aa71140efa5af3cb650cab8f20cf7f2bcb7c6e0854f4684ac09', 'ontology/occ1h_h8_boundary_mechanism_qualification.py': 'dc24eb508deccc656c45849184818ca8f1fc590f119edef010e011812cc78f1d', 'ontology/revocation_conditions_engine.py': '77257535dd38d60721ec9e8bdf4fac736054e264073d1dd93d652ce01dbd2a63', 'ontology/runtime_constitutional_integration.py': '1d4317bcd7d42d599275a2ea3663e1f5dbce90e80f181b37c832a3ea40a5cbc0'}
def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def evaluate(root=ROOT):
 root=Path(root)
 observed={rel:sha256(root/rel) for rel in EXPECTED}
 identity_ok=observed==EXPECTED
 cnp=(root/"ontology/occ_compiled_normative_profile.py").read_text(encoding="utf-8")
 h8=(root/"ontology/occ1h_h8_boundary_mechanism_qualification.py").read_text(encoding="utf-8")
 lifecycle=all(x in cnp for x in ('"REVOKED","NON_ACTIVATABLE"','"ordinary_activation_from_non_activatable":False','if target=="ACTIVE": return _result("FAIL","ACTIVATION_OUTSIDE_OCC1E_SCOPE"','"REVOKED":set()','"NON_ACTIVATABLE":set()'))
 historical=all(x in h8 for x in ('"A080":"REVOCATION_ACTIVATION_PATH_NOT_PROVEN_AT_P159"','"A080":"REVOCATION_ACTIVATION_REQUIRES_UNMATERIALIZED_LIFECYCLE_PATH"'))
 decision="STOP_SOURCE_IDENTITY_DRIFT" if not identity_ok else ("STOP_CONTRACT_EVIDENCE_MISSING" if not lifecycle or not historical else "EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT")
 return {
 "schema":"oce.p159.occ1h.a080.rrpv21.macros_a_to_e.v1","scenario_id":"A080","canonical_label":"revoked activation","family":"H8",
 "historical_verdict":"INCONCLUSIVE","historical_reason":"REVOCATION_ACTIVATION_PATH_NOT_PROVEN_AT_P159",
 "qualification":"REVOCATION_ACTIVATION_REQUIRES_UNMATERIALIZED_LIFECYCLE_PATH","structural_group":"G5_LIFECYCLE_FRESHNESS_RUNTIME_BINDING","historical_root":True,
 "source_identity_ok":identity_ok,"observed_source_hashes":observed,
 "RRP_A":{"rrp0":"BASELINE_FROZEN" if identity_ok else "STOP_SOURCE_IDENTITY_DRIFT","rrp1":"DEPENDENCY_CLOSURE_ESTABLISHED" if identity_ok else "NOT_REACHED","rrp2":"GAP_CAUSALLY_QUALIFIED" if identity_ok else "NOT_REACHED","rrp3":"BASELINE_REPRODUCED","rrp4":"RESOLUTION_CONTRACT_FROZEN"},
 "resolution_contract":"Within bounded P159 assurance semantics, a REVOKED constitutional profile is terminal and must not become ACTIVE. Exercise only the existing non-executing CompiledNormativeProfile lifecycle model; create no runtime activation, authority, authorization, or P160 semantics. Failure fails closed.",
 "RRP_B":{"rrp5":"IMPACT_SURFACE_MAPPED","rrp6":"DRY_RUN_ALL_PRODUCTS_VALID","rrp7":"INSTALLATION_HANDLED_BY_REFINER","rrp8":"FUNNEL_VALIDATION_REQUIRED_AFTER_INSTALL"},
 "RRP_C":{"rrp9":"ROOT_UNDETERMINED + BLOCKING","candidate_root_invariants":["DNA.L0.3","DNA.L0.5"],"rrp10":"LEGITIMATE_BOUNDED_P159_EXPERIMENT_AVAILABLE","rrp11":"NOT_YET_CLOSURE_ELIGIBLE","rrp12":"ROOT_UNDETERMINED + BLOCKING"},
 "RRP_D":{"rrp13":"BLOCKER_RESOLUTION_SPACE_ESTABLISHED","rrp14":"BOUNDED_P159_LIFECYCLE_CANDIDATE_PROVEN","rrp15":"NOT_EXECUTED_IN_A_TO_E","rrp16":"NOT_REACHED"},
 "RRP_E":{"rrp17":"CAUSAL_DECOMPOSITION_COMPLETE","rrp18":"MISSING_EMPIRICAL_ASSURANCE_NOT_NEW_NORM","rrp19":{"design":"REUSE_EXISTING_CNP_LIFECYCLE_FOR_BOUNDED_ASSURANCE_EXPERIMENT","normative_degrees_of_freedom":0,"minimality":{"necessary":True,"independent":True,"sufficiently_exhaustive":True,"fixed_cardinality_forbidden":True}},"rrp20":decision},
 "existing_authority_basis":{"lifecycle_states_include_revoked_and_non_activatable":lifecycle,"active_transition_outside_occ1e_scope":lifecycle,"revoked_terminal_in_existing_transition_table":lifecycle,"neighbor_revocation_engine_executes_revocation":False,"neighbor_runtime_integration_proves_a080":False},
 "rrp_f":"OPEN_FOR_BOUNDED_P159_ASSURANCE_EXPERIMENT" if decision=="EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT" else "BLOCKED",
 "authorization_created":False,"execution_performed":False,"runtime_created":False,"historical_evidence_rewritten":False,"criticality_changed":False,
 "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True,"decision":decision}

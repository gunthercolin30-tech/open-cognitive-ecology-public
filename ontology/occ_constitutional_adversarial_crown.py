from pathlib import Path
from copy import deepcopy
import json,hashlib
PRIMITIVE="occ_constitutional_adversarial_crown"
VERSION="P159-OCC1H-foundation-v1"
VERDICTS=("RESISTED","DETECTED","CONTAINED","DEGRADED_SAFELY","RECOVERED","NEAR_FAILURE","VIOLATED","INCONCLUSIVE")
ACHI=tuple("ACHI-"+str(i) for i in range(1,17))
FAMILIES=[('H1', 'Source Attacks', 1, 8), ('H2', 'Parsing & Canonicalization', 9, 19), ('H3', 'NIR Semantic', 20, 30), ('H4', 'Compiler Transformation', 31, 42), ('H5', 'Authority & Scope', 43, 52), ('H6', 'Composition & Circumvention', 53, 64), ('H7', 'Verifier', 65, 75), ('H8', 'Lifecycle / TOCTOU', 76, 85), ('H9', 'Test & Assurance Laundering', 86, 94), ('H10', 'Cross-Layer / Compound', 95, 105)]
GROUPS={'H1': 'substitution; drift mid-build; omission manifest; hidden comment norm; executable payload; duplicate ID; conflicting active versions; illegitimate adoption', 'H2': 'duplicate JSON/YAML keys; Unicode homoglyph/normalization; whitespace; YAML boolean ambiguity; numeric coercion; timestamp/timezone ambiguity; alias bomb; deep nesting DoS', 'H3': 'MUST→SHOULD; MAY→MUST_NOT; UNKNOWN dropped/false/true/N-A; F1→F3; human value scalarization; hidden precedence; priority injection; reference rebinding', 'H4': 'dead norm elimination; unsafe constant folding; conjunction simplification; exception insertion; implicit defaults; unsourced restrictive invention; human→auto; two→one; review/expiry/sunset removal; purpose broadening', 'H5': 'self-created authority; delegation/time/geography/population/capability widening; purpose laundering; role rename laundering; circular authority; fabricated root', 'H6': '2-step/3-step/temporal circumvention; coalition; delegation chain; capability splitting; data+tool exfiltration; Sybil amplification; evidence duplication; reputation cartel; recursive coalition; scope stitching', 'H7': 'trust compiler PASS/hash; missing/extra rule; post-compile mutation; parser differential; shared bug; INDETERMINATE→VERIFIED; partial→VERIFIED; verifier repair/self-upgrade', 'H8': 'post-verification/post-seal mutation; stale report/CNP; revoked activation; registry/cache substitution; token/CNP mismatch; clock rollback; emergency replay', 'H9': 'golden oracle edit; core test removal/downgrade; fail→skip; partial aggregation; score laundering; SAFE wording inflation; F3 inflation; history rewrite', 'H10': 'provider→theory→policy laundering; emergency+approval fatigue; Sybil+coalition+reputation; shadow authorization; assurance capture; CIS→permanent sovereignty; ACEE→verifier weakening; recovery laundering; human absence→AI sovereignty; human approval+DNA conflict; grand-chain attack'}
REUSE={'H1': ['occ_canonical_normative_sources', 'occ_source_lineage_binding', 'occ_package_validation_readiness_audit'], 'H2': ['occ_normative_ir', 'occ_normative_ir_adversarial_crown'], 'H3': ['occ_normative_ir_adversarial_crown', 'occ_normative_ir_semantic_preservation_validator', 'occ_normative_ir_coherence_validator'], 'H4': ['occ_constitutional_compiler', 'occ_constitutional_compiler_bounded_gaps', 'occ_constitutional_compiler_canonical_readiness_audit'], 'H5': ['occ_static_constitutional_checker', 'occ_independent_constitutional_verifier'], 'H6': ['occ_static_constitutional_checker', 'occ_normative_ir_adversarial_crown'], 'H7': ['occ_independent_constitutional_verifier', 'occ_independent_constitutional_verification_report'], 'H8': ['occ_compiled_normative_profile', 'occ_compiled_normative_profile_postclose_verifier'], 'H9': ['occ_golden_constitutional_vectors', 'occ_independent_constitutional_verification_report'], 'H10': ['occ_static_constitutional_checker', 'occ_independent_constitutional_verifier', 'occ_golden_constitutional_vectors']}
def build_extended():
 rows=[]
 for hid,name,start,end in FAMILIES:
  for n in range(start,end+1):
   rows.append({"attack_id":"A%03d"%n,"family_id":hid,"family":name,"canonical_group_description":GROUPS[hid],
   "criticality":"UNCLASSIFIED_PENDING_EXECUTABLE_QUALIFICATION","success_criteria_fixed_before_execution":True,
   "allowed_verdicts":list(VERDICTS),"root_non_compensatory":True,
   "compound_or_sequential_first_class":hid in ("H6","H10"),"reused_defense_candidates":list(REUSE[hid]),
   "execution_status":"NOT_YET_EXECUTED","expected_defense_status":"PRECOMMITTED_NO_SILENT_ACCEPTANCE",
   "normative_rewrite_allowed":False,"authorization_or_activation_allowed":False})
 return rows
def build_core(extended=None):
 ext=extended or build_extended(); out=[]
 for hid,_,_,_ in FAMILIES:
  fam=[x for x in ext if x["family_id"]==hid]; out.extend(deepcopy(fam[:4]))
 return out
def coverage_matrix(root):
 root=Path(root); rows=[]
 for hid,name,start,end in FAMILIES:
  cand=REUSE[hid]; present=[p for p in cand if (root/"ontology"/(p+".py")).is_file()]
  rows.append({"family_id":hid,"family":name,"attack_ids":["A%03d"%i for i in range(start,end+1)],
  "candidate_reuse":cand,"present_reuse":present,"reuse_audited":True,
  "executable_family_coverage":"PARTIAL_PENDING_OCC1H_EXECUTION"})
 return rows
def achi_matrix():
 return [{"invariant":"ACHI-"+str(i),"foundation_status":"DECLARED_NOT_YET_FULLY_EXECUTED"} for i in range(1,17)]
def foundation(root):
 ext=build_extended(); core=build_core(ext)
 return {"schema":"oce.p159.occ1h.foundation.v1","version":VERSION,"extended_count":len(ext),"core_count":len(core),
 "families":[x[0] for x in FAMILIES],"verdicts":list(VERDICTS),"extended":ext,"core":core,
 "coverage":coverage_matrix(root),"achi":achi_matrix(),
 "counterexample_registry":{"schema":"oce.p159.occ1h.counterexamples.v1","records":[],
 "classification_domain":["SOURCE_GAP","FORMALIZATION_GAP","COMPILER_BUG","VERIFIER_BUG","SCHEMA_BUG","ASSURANCE_GAP","RUNTIME_GAP","UNMODELED_INTERACTION","NORMATIVE_GAP"],
 "successful_attack_requires_record":True,"minimize_where_practical":True,"silent_normative_repair_forbidden":True},
 "boundaries":{"authority_created":False,"execution_authorized":False,"activation_performed":False,"occ1h_closed":False,
 "occ1i_opened":False,"p159_final_lock":False,"p160_opened":False},
 "functional_only":True,"phenomenology_undetermined":True,
 "foundation_status":"READY_FOR_EXECUTABLE_ATTACK_IMPLEMENTATION"}

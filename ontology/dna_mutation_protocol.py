from __future__ import annotations
from copy import deepcopy

PRIMITIVE="dna_mutation_protocol"
DESCRIPTION="P021 thin governed lifecycle contract for structural OCE DNA mutation."
DEPENDENCIES=["dna_inheritance"]
P021_VERSION="P021-v1"
P021_SCHEMA_VERSION="oce.p021.dna_mutation_protocol.v1"
P021_SCOPE="P021_ONLY"

PROPOSAL="PROPOSAL"
IMPACT_ANALYSIS="IMPACT_ANALYSIS"
SANDBOX="SANDBOX"
ADVERSARIAL_TESTS="ADVERSARIAL_TESTS"
COMPATIBILITY_ANALYSIS="COMPATIBILITY_ANALYSIS"
GOVERNANCE="GOVERNANCE"
MIGRATION="MIGRATION"
VERSIONING="VERSIONING"
HISTORIZATION="HISTORIZATION"
MUTATION_STAGES=(PROPOSAL,IMPACT_ANALYSIS,SANDBOX,ADVERSARIAL_TESTS,COMPATIBILITY_ANALYSIS,GOVERNANCE,MIGRATION,VERSIONING,HISTORIZATION)
ALLOWED_TRANSITIONS=tuple(zip(MUTATION_STAGES,MUTATION_STAGES[1:]))
STAGE_STATUSES=("PENDING","PASS","FAIL","UNDETERMINED")
FINAL_DECISIONS=("APPROVED","REJECTED","UNDETERMINED")

P021_BOUNDARIES={"protocol_orchestration_only":True,"does_not_execute_mutation":True,"does_not_grant_modification_authority":True,"does_not_replace_existing_sandbox":True,"does_not_replace_existing_governance":True,"does_not_replace_existing_rollback":True,"does_not_define_p022_lineage_versioning":True,"versioning_stage_is_handoff_only":True,"undetermined_is_not_pass":True,"failure_blocks_progression":True,"functional_conclusion_only":True,"phenomenology_undetermined":True}
P021_TRANSVERSAL_REFERENTIALS={"doctrines":("R5","R6","R10","R11","R12","R13","R17","R18","R19","R20","R21"),"artifacts":("A-CANON","A-R0R21","A-TRACE","A-NONLOSS","A-DNA-ADV"),"world_models_dependency":None}
REUSE_MAP={PROPOSAL:("constitutional_self_modification_protocol","governed_external_revision_pipeline"),IMPACT_ANALYSIS:("acee_impact_evaluator",),SANDBOX:("evolution_sandbox",),ADVERSARIAL_TESTS:("validation",),COMPATIBILITY_ANALYSIS:("dynamic_compatibility_matrix",),GOVERNANCE:("constitutional_evolution_gate","external_governance_amendment_gate"),MIGRATION:("controlled_evolution_orchestrator","acee_rollback_engine"),VERSIONING:("acee_lineage_manager","runtime_lineage_inheritance"),HISTORIZATION:("controlled_evolution_orchestrator","acee_lineage_manager")}
MUTATION_RECORD_FIELDS=("mutation_id","stage","status","scope","proposal_ref","evidence_refs","authority_ref","rollback_ref","version","provenance")

def _exact(r,fields):
 if not isinstance(r,dict): raise ValueError("record_must_be_dict")
 missing=set(fields)-set(r); extra=set(r)-set(fields)
 if missing: raise ValueError("missing_fields:"+",".join(sorted(missing)))
 if extra: raise ValueError("extra_fields:"+",".join(sorted(extra)))
def validate_stage(stage):
 if stage not in MUTATION_STAGES: raise ValueError("invalid_mutation_stage")
 return True
def validate_transition(source,target):
 validate_stage(source); validate_stage(target)
 if (source,target) not in ALLOWED_TRANSITIONS: raise ValueError("invalid_mutation_transition")
 return True
def validate_mutation_record(r):
 _exact(r,MUTATION_RECORD_FIELDS); validate_stage(r["stage"])
 if r["status"] not in STAGE_STATUSES: raise ValueError("invalid_stage_status")
 for k in ("mutation_id","scope","proposal_ref","version","provenance"):
  if not isinstance(r[k],str) or not r[k].strip(): raise ValueError("invalid_"+k)
 if not isinstance(r["evidence_refs"],tuple): raise ValueError("evidence_refs_must_be_tuple")
 for k in ("authority_ref","rollback_ref"):
  if r[k] is not None and (not isinstance(r[k],str) or not r[k].strip()): raise ValueError("invalid_"+k)
 if r["stage"]==GOVERNANCE and r["status"]=="PASS" and not r["authority_ref"]: raise ValueError("governance_pass_requires_authority_ref")
 return True
def can_advance(r):
 validate_mutation_record(r)
 return r["status"]=="PASS"
def next_stage(r):
 if not can_advance(r): return None
 i=MUTATION_STAGES.index(r["stage"])
 return MUTATION_STAGES[i+1] if i+1<len(MUTATION_STAGES) else None
def protocol_decision(records):
 if not isinstance(records,tuple): raise ValueError("records_must_be_tuple")
 if not records: return "UNDETERMINED"
 copied=deepcopy(records)
 for r in copied: validate_mutation_record(r)
 stages=tuple(r["stage"] for r in copied)
 if stages!=MUTATION_STAGES[:len(stages)]: raise ValueError("non_canonical_stage_sequence")
 statuses=tuple(r["status"] for r in copied)
 if "FAIL" in statuses: return "REJECTED"
 if len(copied)!=len(MUTATION_STAGES): return "UNDETERMINED"
 return "APPROVED" if all(s=="PASS" for s in statuses) else "UNDETERMINED"
def mutation_protocol_manifest():
 return deepcopy({"primitive":PRIMITIVE,"version":P021_VERSION,"schema_version":P021_SCHEMA_VERSION,"scope":P021_SCOPE,"dependencies":tuple(DEPENDENCIES),"stages":MUTATION_STAGES,"allowed_transitions":ALLOWED_TRANSITIONS,"reuse_map":REUSE_MAP,"boundaries":P021_BOUNDARIES,"transversal_referentials":P021_TRANSVERSAL_REFERENTIALS})
def validate_mutation_protocol():
 assert len(MUTATION_STAGES)==9 and len(set(MUTATION_STAGES))==9 and len(ALLOWED_TRANSITIONS)==8
 assert tuple(REUSE_MAP)==MUTATION_STAGES
 assert P021_TRANSVERSAL_REFERENTIALS["world_models_dependency"] is None
 assert P021_BOUNDARIES["does_not_define_p022_lineage_versioning"] and P021_BOUNDARIES["undetermined_is_not_pass"]
 return True

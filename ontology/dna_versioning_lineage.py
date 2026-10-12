from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from copy import deepcopy
import json, os, tempfile
from pathlib import Path
from typing import Any

PRIMITIVE="dna_versioning_lineage"
DESCRIPTION="P022 thin canonical DNA versioning and lineage layer."
DEPENDENCIES=["dna_mutation_protocol"]
P022_VERSION="P022-v1"
P022_SCHEMA_VERSION="oce.p022.dna_versioning_lineage.v1"
P022_SCOPE="P022_ONLY"

INDIVIDUAL="INDIVIDUAL"; INSTITUTION="INSTITUTION"; CRITICAL_COMPONENT="CRITICAL_COMPONENT"
ENTITY_TYPES=(INDIVIDUAL,INSTITUTION,CRITICAL_COMPONENT)
LINEAGE_FIELDS=("entity_id","entity_type","created_under_DNA","current_DNA","migration_history","version","provenance")
MIGRATION_FIELDS=("migration_id","from_DNA","to_DNA","mutation_ref","evidence_refs","authority_ref","version","provenance")

P022_BOUNDARIES={
"canonical_lineage_contract_only":True,"created_under_DNA_is_immutable":True,
"current_DNA_changes_only_by_explicit_migration":True,"migration_history_is_append_only":True,
"does_not_replace_acee_lineage_manager":True,"does_not_replace_individual_migration_protocol":True,
"does_not_replace_representative_lineage_registry":True,"does_not_grant_mutation_authority":True,
"does_not_execute_structural_mutation":True,"does_not_define_p023_fitness_suite":True,
"does_not_define_p024_adversarial_campaign":True,"undetermined_is_not_pass":True,
"functional_conclusion_only":True,"phenomenology_undetermined":True}
P022_TRANSVERSAL_REFERENTIALS={"doctrines":("R2","R4","R11","R18","R21"),
"artifacts":("A-CANON","A-TRACE","A-NONLOSS"),"world_models_dependency":None}
REUSE_ARTICULATIONS={"architectural_lineage":"acee_lineage_manager",
"individual_host_migration":"individual_migration_protocol",
"representative_succession":"representative_lineage_registry",
"runtime_lineage_signal":"runtime_lineage_inheritance"}

def _s(v,f):
 if not isinstance(v,str) or not v.strip(): raise ValueError("invalid_"+f)
def _exact(r,fields):
 if not isinstance(r,dict): raise ValueError("record_must_be_dict")
 missing=set(fields)-set(r); extra=set(r)-set(fields)
 if missing: raise ValueError("missing_fields:"+",".join(sorted(missing)))
 if extra: raise ValueError("extra_fields:"+",".join(sorted(extra)))
def validate_entity_type(t):
 if t not in ENTITY_TYPES: raise ValueError("invalid_entity_type")
 return True
def validate_migration(m):
 _exact(m,MIGRATION_FIELDS)
 for f in ("migration_id","from_DNA","to_DNA","mutation_ref","authority_ref","version","provenance"): _s(m[f],f)
 if m["from_DNA"]==m["to_DNA"]: raise ValueError("migration_requires_DNA_change")
 if not isinstance(m["evidence_refs"],tuple): raise ValueError("evidence_refs_must_be_tuple")
 for r in m["evidence_refs"]: _s(r,"evidence_ref")
 return True
def validate_lineage(x):
 _exact(x,LINEAGE_FIELDS); _s(x["entity_id"],"entity_id"); validate_entity_type(x["entity_type"])
 for f in ("created_under_DNA","current_DNA","version","provenance"): _s(x[f],f)
 if not isinstance(x["migration_history"],tuple): raise ValueError("migration_history_must_be_tuple")
 expected=x["created_under_DNA"]
 for m in x["migration_history"]:
  validate_migration(m)
  if m["from_DNA"]!=expected: raise ValueError("non_contiguous_migration_history")
  expected=m["to_DNA"]
 if x["current_DNA"]!=expected: raise ValueError("current_DNA_history_mismatch")
 return True
def create_lineage(entity_id,entity_type,dna_version,*,version=P022_VERSION,provenance):
 x={"entity_id":entity_id,"entity_type":entity_type,"created_under_DNA":dna_version,
 "current_DNA":dna_version,"migration_history":(),"version":version,"provenance":provenance}
 validate_lineage(x); return deepcopy(x)
def migrate_lineage(x,*,migration_id,to_DNA,mutation_ref,evidence_refs,authority_ref,version=P022_VERSION,provenance):
 validate_lineage(x); original=deepcopy(x)
 m={"migration_id":migration_id,"from_DNA":original["current_DNA"],"to_DNA":to_DNA,
 "mutation_ref":mutation_ref,"evidence_refs":evidence_refs,"authority_ref":authority_ref,
 "version":version,"provenance":provenance}
 validate_migration(m); y=deepcopy(original); y["current_DNA"]=to_DNA
 y["migration_history"]=original["migration_history"]+(deepcopy(m),); validate_lineage(y)
 assert y["created_under_DNA"]==original["created_under_DNA"]; return y
def lineage_manifest():
 return deepcopy({"primitive":PRIMITIVE,"dependencies":tuple(DEPENDENCIES),"version":P022_VERSION,
 "schema_version":P022_SCHEMA_VERSION,"scope":P022_SCOPE,"entity_types":ENTITY_TYPES,
 "lineage_fields":LINEAGE_FIELDS,"migration_fields":MIGRATION_FIELDS,"boundaries":P022_BOUNDARIES,
 "transversal_referentials":P022_TRANSVERSAL_REFERENTIALS,"reuse_articulations":REUSE_ARTICULATIONS})
def validate_versioning_lineage_model():
 assert ENTITY_TYPES==(INDIVIDUAL,INSTITUTION,CRITICAL_COMPONENT)
 assert P022_TRANSVERSAL_REFERENTIALS["world_models_dependency"] is None
 assert P022_BOUNDARIES["created_under_DNA_is_immutable"] and P022_BOUNDARIES["migration_history_is_append_only"]
 assert P022_BOUNDARIES["does_not_define_p023_fitness_suite"] and P022_BOUNDARIES["does_not_define_p024_adversarial_campaign"]
 return True
def _jsonable(x):
 validate_lineage(x); p=deepcopy(x); p["migration_history"]=[deepcopy(m) for m in x["migration_history"]]
 for m in p["migration_history"]: m["evidence_refs"]=list(m["evidence_refs"])
 return p
def _from_jsonable(p):
 x=deepcopy(p); hist=[]
 for raw in x.get("migration_history",[]):
  m=deepcopy(raw); m["evidence_refs"]=tuple(m.get("evidence_refs",[])); hist.append(m)
 x["migration_history"]=tuple(hist); validate_lineage(x); return x
def save_lineage(path,x,filesystem_effect_context=None):
 validate_lineage(x); target=Path(path)
 if filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
 filesystem_effect_context.execute_path("lineage_parent_create","FS_CREATE_DIRS",target.parent)
 encoded=json.dumps(_jsonable(x),sort_keys=True,indent=2,ensure_ascii=False)+"\n"
 filesystem_effect_context.execute_path("lineage_write_replace","FS_WRITE_REPLACE_BYTES",target,encoded.encode("utf-8"))
 return target

def load_lineage(path):
 p=json.loads(Path(path).read_text(encoding="utf-8"))
 if not isinstance(p,dict): raise ValueError("persisted_lineage_must_be_object")
 return _from_jsonable(p)

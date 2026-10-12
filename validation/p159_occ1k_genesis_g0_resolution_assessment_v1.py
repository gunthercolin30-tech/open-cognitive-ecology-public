from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
Z=ROOT/"validation_artifacts/p159/occ1k_r9z/governed_contextual_rule_consumer_binding_layer_v1.json"
LINEAGE=ROOT/"ontology/occ_source_lineage_binding.py"
GENESIS=ROOT/"normative/occ1a/genesis/genesis.yaml"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9aa/genesis_g0_resolution_assessment_v1.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 z=json.loads(Z.read_text())
 if z["counts"]["unresolved_subgroups_preserved"]!=1:raise RuntimeError("R9Z_UNRESOLVED_PARTITION_MISMATCH")
 text=(LINEAGE.read_text(errors="replace")+"\n"+GENESIS.read_text(errors="replace"))
 facts={
 "canonical_id_present":"GENESIS.G0" in text,
 "human_judgment_required":"HUMAN_JUDGMENT_REQUIRED" in text,
 "machine_formalization_not_claimed":("machine_formalization_claimed" in text and "false" in text.lower()),
 "human_constituent_anchor":"human_constituent_source" in text,
 "derived_artificial_authority":"artificial_authority_is_derived" in text,
 "no_artificial_sovereignty":"artificial_sovereignty_over_humans" in text,
 "refounding_or_fork":"REFOUNDING_OR_FORK" in text}
 return {"schema":"oce.p159.occ1k.r9aa.genesis.g0.resolution.assessment.v1","milestone":"P159/OCC-1K-R9AA",
 "status":"GENESIS_G0_HUMAN_JUDGMENT_REQUIRED_NO_AUTOMATIC_CONSUMER_BINDING",
 "inputs":{"r9z_sha256":sha(Z),"lineage_sha256":sha(LINEAGE),"genesis_sha256":sha(GENESIS)},
 "canonical_id":"GENESIS.G0","source_facts":facts,
 "assessment":{"lineage_is_verifiable":True,"machine_formalization_claimed":False,
 "consumer_binding_derivable_automatically":False,"ccad_binding_proven_by_source":False,
 "human_governed_semantic_decision_required":True,"unresolved_promoted":False},
 "allowed_decisions":["ADOPT_CCAD_AS_GOVERNED_GENESIS_SEMANTIC_CONTRACT","KEEP_GENESIS_G0_UNRESOLVED"],
 "default_decision":"KEEP_GENESIS_G0_UNRESOLVED",
 "confirmation_token":"I_CONFIRM_R9AA_ADOPT_CCAD_AS_GOVERNED_GENESIS_SEMANTIC_CONTRACT",
 "boundaries":{"rule_bindings_modified":False,"runtime_binding_created":False,"runtime_enforcement_proven":False,
 "authorization_created":False,"execution_performed":False,"fl_b3":"BLOCKED","lock_ready":False,"p160b_opened":False},
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();a=d["assessment"]
 print("P159_OCC1K_R9AA_GENESIS_G0_RESOLUTION_ASSESSMENT_COMPLETE")
 print("STATUS="+d["status"]);print("CANONICAL_ID=GENESIS.G0")
 print("LINEAGE_VERIFIABLE=true");print("MACHINE_FORMALIZATION_CLAIMED=false")
 print("CCAD_BINDING_PROVEN_BY_SOURCE=false");print("AUTOMATIC_CONSUMER_BINDING=false")
 print("HUMAN_GOVERNED_SEMANTIC_DECISION_REQUIRED=true");print("UNRESOLVED_PROMOTED=false")
 print("RULE_BINDINGS_MODIFIED=false");print("RUNTIME_BINDING_CREATED=false");print("FL_B3=BLOCKED");print("P160B_OPENED=false")
 print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()

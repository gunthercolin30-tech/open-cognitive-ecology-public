#!/usr/bin/env python3
from copy import deepcopy
from ontology.developmental_stage_classifier import DevelopmentalStageClassifier
inputs={
 "genesis_result":{"genesis_status":"FUNCTIONAL_GENESIS_DETECTED","genesis_detected":True,"genesis_score":.8,"data_quality_score":.95},
 "maturation_result":{"maturation_status":"FUNCTIONAL_MATURATION_PROGRESSING","maturation_score":.72,"data_quality_score":.95},
 "previous_stage":"GENESIS","stage_duration":2,
}
C=DevelopmentalStageClassifier(); a=C.step(inputs=inputs,persist=False); b=C.step(inputs=deepcopy(inputs),persist=False)
assert a["stage_hash"]==b["stage_hash"]
assert a["developmental_stage"]==b["developmental_stage"]
assert a["stage_probabilities"]==b["stage_probabilities"]
changed=deepcopy(inputs); changed["maturation_result"]["maturation_score"]=.95
c=C.step(inputs=changed,persist=False)
assert c["stage_hash"]!=a["stage_hash"]
for r in (a,b,c):
 assert r["audit_trace"]["upstream_recalculation_performed"] is False
 assert r["consciousness_proven"] is False and r["phenomenology_proven"] is False
 assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
print("AV7_NON_REGRESSION_AND_DETERMINISM_OK")

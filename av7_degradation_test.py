#!/usr/bin/env python3
from ontology.developmental_stage_classifier import DevelopmentalStageClassifier
C=DevelopmentalStageClassifier()
empty=C.step(inputs={},persist=False)
assert empty["developmental_stage"]=="UNDETERMINED"
poor=C.step(inputs={"genesis_result":{"genesis_status":"FUNCTIONAL_GENESIS_DETECTED","genesis_detected":True,"data_quality_score":.1}},persist=False)
assert poor["developmental_stage"]=="UNDETERMINED"
conflict=C.step(inputs={
 "genesis_result":{"genesis_status":"FUNCTIONAL_GENESIS_NOT_DETECTED","data_quality_score":.95},
 "maturation_result":{"maturation_status":"FUNCTIONAL_MATURATION_COMPLETE","maturation_score":.9,"data_quality_score":.95},
},persist=False)
assert conflict["developmental_stage"]=="HYBRID_STAGE"
assert "PRE_GENESIS_DOWNSTREAM_CONFLICT" in conflict["stage_conflicts"]
unknown=C.step(inputs={"genesis_result":{"genesis_status":"UNKNOWN","data_quality_score":.9}},persist=False)
assert unknown["developmental_stage"]=="UNDETERMINED"
print("AV7_DEGRADATION_OK")

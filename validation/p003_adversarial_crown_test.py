from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p003_development_evidence_roadmap import DevelopmentEvidenceRoadmap
R=DevelopmentEvidenceRoadmap()
def good(**c):
 x={"milestone_id":"P003-crown","expected_property":"binding","measurable_output":"score","evidence":{"measured_value":.9},"baseline":{"measured_value":.5},"provenance":{"source":"crown"},"resources":{"human_hours":2.},"dependencies":["P001","P002"],"non_regression":True,"uncertainty_before":.9,"uncertainty_after":.1,"confidence":.9,"comparison":"higher_is_better"}; x.update(c); return x
def expect(c,d,label):
 o=R.evaluate(good(**c)); assert o["decision"]==d,(label,o); print(label+"_OK")
expect({"non_regression":False},"REJECTED","P003_CROWN_NON_REGRESSION_GATE")
expect({"evidence":{"measured_value":.4},"uncertainty_before":1.,"uncertainty_after":0.},"REJECTED","P003_CROWN_BASELINE_GATE")
expect({"confidence":None},"UNKNOWN","P003_CROWN_UNKNOWN_GATE")
expect({"confidence":.49},"UNKNOWN","P003_CROWN_LOW_CONFIDENCE_GATE")
expect({"comparison":"lower_is_better","evidence":{"measured_value":.4},"baseline":{"measured_value":.5}},"ACCEPTED","P003_CROWN_LOWER_BETTER")
expect({"comparison":"equal_or_better","evidence":{"measured_value":.5},"baseline":{"measured_value":.5}},"ACCEPTED","P003_CROWN_EQUAL_OR_BETTER")
expect({"comparison":"higher_is_better","evidence":{"measured_value":.5},"baseline":{"measured_value":.5}},"REJECTED","P003_CROWN_STRICT_HIGHER")
print("P003_ADVERSARIAL_CROWN_OK")

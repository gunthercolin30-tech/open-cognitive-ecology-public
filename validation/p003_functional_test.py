from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p003_development_evidence_roadmap import DevelopmentEvidenceRoadmap
R=DevelopmentEvidenceRoadmap()
def good(**c):
 x={"milestone_id":"P003-probe","expected_property":"evidence binding","measurable_output":"score","evidence":{"measured_value":.9},"baseline":{"measured_value":.5},"provenance":{"source":"test"},"resources":{"human_hours":2.},"dependencies":["P001","P002"],"non_regression":True,"uncertainty_before":.8,"uncertainty_after":.2,"confidence":.9,"comparison":"higher_is_better"}; x.update(c); return x
o=R.evaluate(good()); assert o["decision"]=="ACCEPTED",o; assert abs(o["uncertainty_eliminated_per_human_hour"]-.3)<1e-12,o; assert o["functional_conclusion_only"] and o["phenomenology_undetermined"]; print("P003_FUNCTIONAL_OK")

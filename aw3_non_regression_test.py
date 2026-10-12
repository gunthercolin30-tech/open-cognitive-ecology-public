from ontology.shared_symbolic_reference import SharedSymbolicReference
from ontology.intersubjective_alignment import IntersubjectiveAlignment
from ontology.shared_reference_frame_detector import SharedReferenceFrameDetector

def main():
 s=SharedSymbolicReference().step({}); a=IntersubjectiveAlignment().step({}); d=SharedReferenceFrameDetector().step(inputs={},persist=False)
 assert "shared_symbolic_reference_index" in s and "intersubjective_alignment_index" in a
 assert d["primitive"]=="SHARED_REFERENCE_FRAME_DETECTOR"
 print("AW3_NON_REGRESSION_OK")
if __name__=="__main__": main()

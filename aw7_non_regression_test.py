
from ontology.reference_frame_fragmentation import ReferenceFrameFragmentation
from ontology.reference_frame_merging import ReferenceFrameMerging
def main():
    assert ReferenceFrameFragmentation.step_id=="AW7"
    assert ReferenceFrameMerging.step_id=="AW6"
    assert ReferenceFrameFragmentation.primitive != ReferenceFrameMerging.primitive
    print("AW7_NON_REGRESSION_OK")
if __name__=="__main__": main()

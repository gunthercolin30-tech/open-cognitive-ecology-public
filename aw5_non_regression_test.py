
from ontology.conflict_detector import ConflictDetector
from ontology.coalition_detector import CoalitionDetector
def main():
    assert ConflictDetector.step_id=="AW5"
    assert CoalitionDetector.step_id=="AW4"
    assert ConflictDetector is not CoalitionDetector
    print("AW5_NON_REGRESSION_OK")
if __name__=="__main__": main()

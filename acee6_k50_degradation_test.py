from acee6_k50_functional_test import main as functional_main
from ontology.acee_installation_executor import AceeInstallationExecutor

def main():
    assert hasattr(AceeInstallationExecutor,"_k50_commit_preconditions")
    functional_main()
    print("ACEE6_K50_DEGRADATION_OK")
if __name__=="__main__": main()

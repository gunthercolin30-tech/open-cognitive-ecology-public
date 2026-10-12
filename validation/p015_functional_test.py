from __future__ import annotations
from validation.p015_official_dna_definition import evaluate
def main():
    assert all(evaluate().values())
    print("P015_FUNCTIONAL_TEST_OK"); return 0
if __name__=="__main__": raise SystemExit(main())

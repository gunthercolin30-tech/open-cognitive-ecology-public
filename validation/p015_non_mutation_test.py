from __future__ import annotations
import hashlib
from validation.p015_official_dna_definition import evaluate, TARGET
def main():
    h=lambda: hashlib.sha256(TARGET.read_bytes()).hexdigest(); before=h(); assert all(evaluate().values()); after=h(); assert before==after
    print("P015_NON_MUTATION_TEST_OK"); return 0
if __name__=="__main__": raise SystemExit(main())

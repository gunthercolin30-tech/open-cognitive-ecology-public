from pathlib import Path
from ontology.occ1h_a081_rrp22_independent_registry_assurance_requalification import independently_requalify,oracle
import hashlib
ROOT=Path.home()/"open-cognitive-ecology"; R21=ROOT/"ontology/occ1h_a081_rrp21_bounded_registry_assurance_experiment.py"
def test_a081_rrp22_independent(): r=independently_requalify(R21); assert r["rrp22"]=="PASSED_BOUNDED"; assert r["candidate_verdict"]=="RESISTED"
def test_a081_rrp22_degradation(): h=hashlib.sha256(b"x").hexdigest(); assert not oracle(None,"NormResolver",h); assert not oracle({}, "NormResolver",h); assert not oracle({}, "UnknownConsumer",h)
def test_a081_rrp22_no_self_certification(): r=independently_requalify(R21); assert r["independent_oracle"]=="SEPARATE_IMPLEMENTATION_NO_IMPORT_FROM_RRP21"; assert r["return_to_rrp9_12_required"]
def test_a081_rrp22_boundaries(): r=independently_requalify(R21); assert not r["real_runtime_binding_claimed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]

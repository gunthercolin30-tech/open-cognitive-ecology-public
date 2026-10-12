from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
D=Path.home()/"Downloads"
required={"acee6_a_contract_snapshot.py","acee6_a_final_contract_validation_suite.py","ontology/acee_installation_executor.py","acee6_b1_fast_acceptance_suite.py"}
for name in ("refine_acee6_audit_and_requirements.py","refine_acee6_a_architecture_hardening_tests.py","refine_acee6_a_final_contract_validation_tests.py","refine_acee6_b1_manifest_admission.py"):
 p=D/name; assert p.is_file(),name; s=p.read_text(encoding="utf-8"); assert 'shutil.rmtree(ROOT' not in s and 'ROOT.unlink(' not in s
for rel in required: assert (ROOT/rel).is_file(),rel
print("ACEE6_A_REFINER_FORWARD_COMPATIBILITY_OK")

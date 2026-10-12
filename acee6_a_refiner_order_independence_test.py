from pathlib import Path
D=Path.home()/"Downloads"
contracts={
 "refine_acee6_a_architecture_hardening_tests.py":("acee6_test_requirements_registry.py","acee6_transaction_state_contract.py","acee6_non_redundancy_report.json"),
 "refine_acee6_a_final_contract_validation_tests.py":("acee6_a_hardening_contract.py","acee6_a_hardening_report.json"),
 "refine_acee6_b1_manifest_admission.py":("acee6_test_requirements_registry.py","acee6_transaction_state_contract.py","ontology/acee_governed_code_generation_gate.py"),
}
for name,requirements in contracts.items():
 s=(D/name).read_text(encoding="utf-8")
 for required in requirements: assert required in s,(name,required)
assert 'refuses to modify an existing runtime executor' in (D/'refine_acee6_a_architecture_hardening_tests.py').read_text(encoding='utf-8') or 'runtime' in (D/'refine_acee6_a_architecture_hardening_tests.py').read_text(encoding='utf-8')
print("ACEE6_A_REFINER_ORDER_CONTRACT_OK")

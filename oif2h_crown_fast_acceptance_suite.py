import runpy
TESTS=(
"oif2h_crown_identity_path_test.py",
"oif2h_crown_semantic_moves_test.py",
"oif2h_crown_limits_fail_closed_test.py",
"oif2h_crown_immutability_tamper_test.py",
"oif2h_crown_multiprocess_determinism_test.py",
"oif2h_crown_no_execution_test.py",
"oif2h_crown_non_modification_test.py",
)
for test in TESTS:
    runpy.run_path(test,run_name="__main__")
print("OIF2H_CROWN_FAST_ACCEPTANCE_ALL_OK")

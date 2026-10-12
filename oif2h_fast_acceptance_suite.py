import runpy
TESTS=('oif2h_manifest_diff_functional_test.py','oif2h_manifest_diff_degradation_test.py','oif2h_manifest_diff_non_regression_test.py','oif2h_manifest_diff_determinism_test.py','oif2h_manifest_diff_cross_format_test.py')
for test in TESTS:
    runpy.run_path(test,run_name='__main__')
print('OIF2H_FAST_ACCEPTANCE_ALL_OK')

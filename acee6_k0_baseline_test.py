from pathlib import Path
from acee6_k0_support import ROOT, corrected_runtime_baseline, thresholds_from_baseline

def main():
    baseline=corrected_runtime_baseline(ROOT)
    assert baseline['executor_class'] == 'AceeInstallationExecutor', baseline
    assert baseline['instance_type'] == baseline['executor_class']
    assert len(baseline['module_sha256']) == 64
    assert baseline['import_seconds'] >= 0.0
    thresholds=thresholds_from_baseline(baseline)
    assert thresholds['mutation_score_min'] == 0.95
    assert thresholds['hash_drift_allowed'] == 0
    assert thresholds['decision_drift_allowed'] == 0
    print('ACEE6_K0_BASELINE_OK')
if __name__=='__main__': main()

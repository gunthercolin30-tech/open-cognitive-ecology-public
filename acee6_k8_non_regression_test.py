import json
from pathlib import Path
from acee6_k6_report_verifier import verify_report
from acee6_k7_report_verifier import verify_k7_report
root=Path.home()/"open-cognitive-ecology"/"acee6_k_evidence"
k6=json.loads((root/"acee6_k6_1000_transactions_report.json").read_text())
k7=json.loads((root/"acee6_k7_longitudinal_drift_report.json").read_text())
assert verify_report(k6)["valid"]
assert verify_k7_report(k7)["valid"]
print('ACEE6_K8_NON_REGRESSION_OK')

from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib
from acee6_k2_fuzz_domains import cases_hash
from acee6_k2_fuzz_reducer import minimize
from acee6_k2_fuzz_runner import build_report, verify_report

# One shared 16-case campaign replaces six redundant campaign launches.
p=Path.home()/"open-cognitive-ecology"/"ontology"/"acee_installation_executor.py"
before=hashlib.sha256(p.read_bytes()).hexdigest()
report=build_report(62002,16,reduce_failures=False)
after=hashlib.sha256(p.read_bytes()).hexdigest()
assert before==after
assert report["case_count"]==16
assert report["real_root_mutation_count"]==0
assert report["cleanup_failure_count"]==0
assert verify_report(report)["valid"],verify_report(report)
print("ACEE6_K2_FUNCTIONAL_OK")
print("ACEE6_K2_NON_REGRESSION_OK")
print("ACEE6_K2_REAL_ROOT_IMMUTABILITY_OK")

bad=deepcopy(report); bad["failure_count"]=1
check=verify_report(bad)
assert "report_hash_invalid" in check["reasons"] and "failure_count_nonzero" in check["reasons"]
print("ACEE6_K2_DEGRADATION_OK")

tampered=deepcopy(report); tampered["family_counts"][next(iter(tampered["family_counts"]))]+=1
assert "report_hash_invalid" in verify_report(tampered)["reasons"]
print("ACEE6_K2_REPORT_TAMPER_OK")

assert cases_hash(62002,16)==cases_hash(62002,16)
assert cases_hash(62003,16)!=cases_hash(62002,16)
print("ACEE6_K2_DETERMINISM_OK")

value={"target_path":"../../escape.py","noise":[1,2,3],"extra":"abc"}
reduced=minimize(value,lambda x:isinstance(x,dict) and "target_path" in x and ".." in str(x["target_path"]))
assert set(reduced)=={"target_path"} and ".." in reduced["target_path"]
print("ACEE6_K2_REDUCER_OK")
print("ACEE6_K2_FAST_ACCEPTANCE_OK")

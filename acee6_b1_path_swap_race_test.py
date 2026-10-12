from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor
with TemporaryDirectory() as t:
 r=Path(t); (r/"ontology").mkdir(); d=valid_acee5_decision(r)
 x=AceeInstallationExecutor(root=r,now_utc=fixed_now()).step(d)
 p=x["normalized_plan"]; assert p["path_revalidation_required"] is True and p["hardlink_revalidation_required"] is True
 assert p["root_realpath"]==str(r.resolve()) and p["path_fingerprints"]
print("ACEE6_B1_PATH_SWAP_RACE_OK")

from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor
REQUIRED={"primitive","stage","public_schema_version","status","admissible","proposal_id","manifest_hash","blocking_reasons","normalized_plan","read_only","backup_created","candidate_written","candidate_compiled","tests_executed","global_validation_executed","rollback_executed","inventory_modified","persistence_performed","functional_conclusion_only","phenomenology_undetermined","evidence_hash","result_hash"}
with TemporaryDirectory() as t:
 r=Path(t); (r/"ontology").mkdir(); x=AceeInstallationExecutor(root=r,now_utc=fixed_now()).step(valid_acee5_decision(r)); assert REQUIRED<=set(x)
print("ACEE6_B1_SCHEMA_BACKWARD_COMPATIBILITY_OK")

from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor
with TemporaryDirectory() as t:
 r=Path(t); (r/"ontology").mkdir(); d=valid_acee5_decision(r)
 p=d["proposal_id"]; wrapped={"acee5_decision":d,"admission_context":{"proposal_bindings":{p:"f"*64}}}
 x=AceeInstallationExecutor(root=r,now_utc=fixed_now()).step(wrapped)
 assert "proposal_id_collision" in x["blocking_reasons"]
print("ACEE6_B1_PROPOSAL_BINDING_COLLISION_OK")

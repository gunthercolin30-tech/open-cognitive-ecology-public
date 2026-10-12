from dataclasses import dataclass
from pathlib import Path
import tempfile
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
from ontology.p160_normative_decision_persistence import NormativeDecisionJournal,P160JRuntime
from ontology.p161_authorization_token_persistence import TokenJournal,P161JRuntime
@dataclass(frozen=True)
class Claim:
 lease_id:str;reservation_id:str;adapter_id:str;claim_hash:str
def ctx(base,child):
 rid="ccp01-root";aid="ccp01-adapter";eid="ccp01-effector";b=ScopedHandleBroker();c=Claim("lease-1","reservation-1",aid,"claim-1")
 lease={"lease_id":"lease-1","reservation_id":"reservation-1","expires_at":"2999-01-01T00:00:00Z","operation_id":"FS_CREATE_DIRS"};reg={"adapter_id":aid,"effector_id":eid}
 scope={"operations":["FS_CREATE_DIRS"],"ambient_authority":False,"child_inheritance":False,"transferable":False};target=f"filesystem://{rid}/{child}"
 q=b.issue(claim=c,lease=lease,registry_entry=reg,requested_scope=scope,authorized_scope=scope,target_binding=target,audience=aid,now_iso="2026-10-07T00:00:00Z");assert q["status"]=="HANDLE_ISSUED"
 e=GovernedFilesystemEffector(root_registry={rid:str(base)},handle_broker=b)
 return GovernedFilesystemEffectContext(slots={"archive_create_dirs":[q["handle"]]},effector=e,root_id=rid,root_path=base,adapter_id=aid,effector_id=eid)
def main():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td);a=NormativeDecisionJournal(root);b=TokenJournal(root);assert a.path.parent==root and b.path.parent==root
 print("FUNCTIONAL_TEST_OK")
 with tempfile.TemporaryDirectory() as td:
  base=Path(td)
  for cls,name in ((NormativeDecisionJournal,"p160-missing"),(TokenJournal,"p161-missing")):
   root=base/name
   try:cls(root)
   except RuntimeError as e:assert str(e)=="governed_filesystem_effect_context_required"
   else:raise AssertionError("missing context accepted")
   assert not root.exists()
 print("DEGRADATION_TEST_OK")
 with tempfile.TemporaryDirectory() as td:
  base=Path(td)
  for cls,name in ((NormativeDecisionJournal,"p160-governed"),(TokenJournal,"p161-governed")):
   c=ctx(base,name);o=cls(base/name,filesystem_effect_context=c);assert o.path.parent.is_dir();assert c.remaining()=={"archive_create_dirs":0};assert c.authority_minting is False
 print("REAL_TCB_OK");print("EXACT_HANDLE_CONSUMPTION_OK")
 with tempfile.TemporaryDirectory() as td:
  base=Path(td);r1=P160JRuntime(base/"p160-runtime");r2=P161JRuntime(base/"p161-runtime");assert r1.journal.path.parent.is_dir() and r2.journal.path.parent.is_dir()
 print("NON_REGRESSION_TEST_OK");print("P162G6_G3_CCP01_ATOMIC_REMEDIATION_TEST_OK")
if __name__=="__main__":main()

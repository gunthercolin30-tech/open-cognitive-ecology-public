from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
from ontology.governed_execution_adapter import ExecutionClaimManager
from ontology.scoped_handle_broker import ScopedHandleBroker
from ontology.governed_filesystem_effector import GovernedFilesystemEffector,FilesystemEffectRequest
NOW='2026-10-02T08:30:00+00:00'
def lease(**k):
 d={'lease_id':'L1','reservation_id':'R1','executor_id':'EX1','capability_instance_id':'CI1','operation_id':'FS_WRITE_BYTES','invocation_request_hash':'IH','effective_execution_scope_hash':'SH','audience':'FSA','reservation_status':'RESERVED','used':False,'revoked':False,'expires_at':'2999-01-01T00:00:00+00:00'};d.update(k);return d
def reg(): return {'adapter_id':'FSA','adapter_hash':'FSH','effector_id':'FILESYSTEM','capability_ids':['FILESYSTEM_CAP'],'operation_ids':['FS_WRITE_BYTES'],'status':'ACTIVE'}
def state(**k):
 d={'lease_state_version':1,'reservation_state_version':1,'token_state_version':1,'target_state_version':1,'capability_runtime_attestation':'FS_RUNTIME_OK','adapter_attestation':'FSH','critical_precondition_snapshot':{'ok':True},'security_state':'VERIFIED','revoked':False,'target_current':True,'critical_preconditions_satisfied':True,'credential_identity_verified':True};d.update(k);return d
def claim(cm,st=None):
 return cm.claim(lease=lease(),registry_entry=reg(),executor_instance_id='EX1',capability_instance_id='CI1',capability_id='FILESYSTEM_CAP',operation_id='FS_WRITE_BYTES',invocation_request_hash='IH',effective_execution_scope_hash='SH',point_of_effect_state=st or state(),now_iso=NOW)
def issue(hb,c,target):
 sc={'root_id':'r','operations':['FS_WRITE_BYTES'],'target':target,'ambient_authority':False,'child_inheritance':False,'transferable':False}
 return hb.issue(claim=c,lease=lease(),registry_entry=reg(),requested_scope=sc,authorized_scope=sc,target_binding=target,audience='FSA',now_iso=NOW)['handle']
with TemporaryDirectory() as td:
 root=Path(td);cm=ExecutionClaimManager();hb=ScopedHandleBroker();cr=claim(cm);assert cr['status']=='EXECUTION_STARTED';h=issue(hb,cr['claim'],'filesystem://r/x.bin')
 e=GovernedFilesystemEffector(root_registry={'r':str(root)},handle_broker=hb);req=FilesystemEffectRequest('FS_WRITE_BYTES','r','x.bin',b'abc')
 assert e.execute(request=req,handle=h,adapter_id='FSA',effector_id='FILESYSTEM')['status']=='EFFECT_CONFIRMED'
 assert e.execute(request=req,handle=h,adapter_id='FSA',effector_id='FILESYSTEM')['reason']=='handle_replay_or_unknown'
 assert claim(cm)['reason']=='execution_claim_already_exists'
with TemporaryDirectory() as td:
 root=Path(td);cm=ExecutionClaimManager();hb=ScopedHandleBroker();h=issue(hb,claim(cm)['claim'],'filesystem://r/y.bin');e=GovernedFilesystemEffector(root_registry={'r':str(root)},handle_broker=hb);req=FilesystemEffectRequest('FS_WRITE_BYTES','r','y.bin',b'z')
 with ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(lambda _:e.execute(request=req,handle=h,adapter_id='FSA',effector_id='FILESYSTEM'),range(16)))
 assert sum(x['status']=='EFFECT_CONFIRMED' for x in results)==1
 assert sum(x.get('reason')=='handle_replay_or_unknown' for x in results)==15
assert claim(ExecutionClaimManager(),state(revoked=True))['reason']=='last_second_revocation'
assert claim(ExecutionClaimManager(),state(target_current=False))['reason']=='target_not_current'
assert claim(ExecutionClaimManager(),state(security_state='UNKNOWN'))['reason']=='security_not_verified'
print('P162G6_FILESYSTEM_G123_INTEGRATED_CROWN_OK')

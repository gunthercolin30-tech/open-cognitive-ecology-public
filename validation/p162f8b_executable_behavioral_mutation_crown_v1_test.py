import ast, hashlib, os, subprocess, sys, tempfile
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]; ONTO=ROOT/"ontology"
FILES=["execution_reservation_manager.py","budget_reservation_manager.py","target_lock_manager.py","integrated_reservation_coordinator.py","execution_lease_issuer.py","reservation_recovery_manager.py"]
BASE_HASH={f:hashlib.sha256((ONTO/f).read_bytes()).hexdigest() for f in FILES}
MUTANTS={
"M01":("integrated_reservation_coordinator.py","st.state_version!=expected_token_version","False"),
"M02":("integrated_reservation_coordinator.py","st.committed_uses+st.reserved_uses+use_count>st.max_uses","st.committed_uses+use_count>st.max_uses"),
"M03":("integrated_reservation_coordinator.py",'self.t._targets.setdefault(key,[]).append({"reservation_id":rid,"mode":mode})',"pass"),
"M04":("integrated_reservation_coordinator.py","st.revoked or st.expired or st.indeterminate","False"),
"M05":("integrated_reservation_coordinator.py",'return self._fail("DEPENDENCY_RESERVATION_UNAVAILABLE")','return {"status":"RESERVATION_COMMITTED","mutant_partial":True}'),
"M06":("reservation_recovery_manager.py",'if typ=="RESERVATION_COMMITTED": journal_state="RESERVED"','if typ=="RESERVATION_COMMITTED": journal_state="AVAILABLE"'),
"M07":("integrated_reservation_coordinator.py","if idempotency_key in self._idem: return dict(self._idem[idempotency_key])","if False: return {}"),
"M08":("reservation_recovery_manager.py",'"state":"INDETERMINATE","assessment":"INDETERMINATE"','"state":"AVAILABLE","assessment":"CONFIRMED_UNUSED"'),
"M09":("execution_lease_issuer.py",'(lease["audience"],audience),',""),
"M10":("execution_lease_issuer.py","expiry=min(req,tok,res)","expiry=min(req,res)"),
"M11":("budget_reservation_manager.py",'"PER_CIVILIZATION"','"PER_EXECUTOR"'),
"M12":("integrated_reservation_coordinator.py","if requested_atomicity_scope != self.ATOMICITY_SCOPE:","if False:"),
}
ORACLE = """import sys,tempfile
from pathlib import Path
from datetime import datetime,timezone,timedelta
from ontology.execution_reservation_manager import AtomicReservationManager,AuthorizationUseState
from ontology.budget_reservation_manager import BudgetResourceReservationManager,SharedBudgetState,TechnicalResourceState
from ontology.target_lock_manager import TargetConcurrencyDependencyManager,ConcurrencySlotState,DependencyReservationState
from ontology.integrated_reservation_coordinator import IntegratedReservationCoordinator
from ontology.execution_lease_issuer import ExecutionLeaseIssuer
from ontology.reservation_recovery_manager import ReservationRecoveryJournal
m=sys.argv[1];H='a'*64
def env(maxu=3,budget=10):
 u=AtomicReservationManager();u.put_authorization_state(AuthorizationUseState('tok',maxu))
 b=BudgetResourceReservationManager();b.put_budget(SharedBudgetState('money','PER_CIVILIZATION','civil',budget));b.put_resource(TechnicalResourceState('cpu',2))
 t=TargetConcurrencyDependencyManager();t.put_slot(ConcurrencySlotState('slot',3));t.put_dependency(DependencyReservationState('dep',3))
 return u,b,t,IntegratedReservationCoordinator(u,b,t)
def rr(c,key='k',ver=0,use=1,b=0,target=False,dep=False,atomic='SINGLE_PROCESS_SHARED_MEMORY'):
 return c.reserve(transaction_id=key,idempotency_key=key,invocation_request_id=key,token_id='tok',effective_scope_hash=H,executor_id='e',capability_id='c',operation_id='op',target_binding={'id':'T'},expected_token_version=ver,use_count=use,budget_requests=[{'budget_id':'money','scope':'PER_CIVILIZATION','scope_key':'civil','delta':b,'expected_state_version':ver}] if b else [],resource_requests=[],target_requests=[{'target_key':'T','lock_mode':'WRITE_EXCLUSIVE'}] if target else [],slot_requests=[],dependency_requests=[{'dependency_key':'dep','delta':4,'expected_state_version':0}] if dep else [],requested_atomicity_scope=atomic)
k=False
if m=='M01':
 u,b,t,c=env();k=rr(c,ver=9)['status']=='RESERVATION_COMMITTED'
elif m=='M02':
 u,b,t,c=env(maxu=1);rr(c,'a');k=rr(c,'b',ver=1)['status']=='RESERVATION_COMMITTED'
elif m=='M03':
 u,b,t,c=env();r=rr(c,target=True);k=r['status']=='RESERVATION_COMMITTED' and t.target_holds('T')==()
elif m=='M04':
 u,b,t,c=env();u.put_authorization_state(AuthorizationUseState('tok',3,0,0,0,True,False,False));k=rr(c)['status']=='RESERVATION_COMMITTED'
elif m=='M05':
 u,b,t,c=env();k=rr(c,dep=True)['status']=='RESERVATION_COMMITTED'
elif m=='M06':
 d=Path(tempfile.mkdtemp());j=ReservationRecoveryJournal(d/'j');j.append({'type':'RESERVATION_COMMITTED','reservation_id':'r'});k=j.reconstruct('r')['state']=='AVAILABLE'
elif m=='M07':
 u,b,t,c=env();a=rr(c,'same');z=rr(c,'same',ver=1);k=u.state('tok').reserved_uses==2 or a!=z
elif m=='M08':
 d=Path(tempfile.mkdtemp());j=ReservationRecoveryJournal(d/'j');(d/'j').write_text('broken',encoding='utf-8');k=j.reconstruct('r')['state']=='AVAILABLE'
elif m in ('M09','M10'):
 u,b,t,c=env();r=rr(c);i=ExecutionLeaseIssuer();now=datetime(2030,1,1,tzinfo=timezone.utc);res={'reservation_id':r['reservation_id'],'status':'RESERVATION_COMMITTED','effective_execution_scope_hash':H,'executor_id':'e','operation_id':'op','target_binding':{'id':'T'}}
 z=i.issue(idempotency_key='l',reservation=res,invocation_request_hash='b'*64,capability_instance_id='ci',audience='A',issued_at=now,requested_expires_at=now+timedelta(seconds=30),token_expires_at=now+timedelta(seconds=5),reservation_expires_at=now+timedelta(seconds=30))
 if m=='M09': k=i.validate_for_handoff(z,audience='B',executor_id='e',capability_instance_id='ci',operation_id='op',target_binding={'id':'T'},now=now)=='LEASE_CURRENT_FOR_HANDOFF'
 else: k=datetime.fromisoformat(z['expires_at'])>now+timedelta(seconds=5)
elif m=='M11':
 from ontology.budget_reservation_manager import BUDGET_SCOPES;k='PER_CIVILIZATION' not in BUDGET_SCOPES
elif m=='M12':
 u,b,t,c=env();k=rr(c,atomic='DISTRIBUTED_MULTI_PROCESS')['status']=='RESERVATION_COMMITTED'
print('KILLED' if k else 'SURVIVED');sys.exit(0 if k else 3)
"""
def run_mutant(mid):
 fn,old,new=MUTANTS[mid]
 with tempfile.TemporaryDirectory(prefix="p162f8b_") as td:
  td=Path(td);pkg=td/"ontology";pkg.mkdir();(pkg/"__init__.py").write_text("",encoding="utf-8")
  for f in FILES:
   s=(ONTO/f).read_text(encoding="utf-8")
   if f==fn:
    assert old in s,(mid,"anchor missing");s=s.replace(old,new,1);ast.parse(s)
   (pkg/f).write_text(s,encoding="utf-8")
  e=os.environ.copy();e["PYTHONPATH"]=str(td)
  return subprocess.run([sys.executable,"-c",ORACLE,mid],cwd=str(td),env=e,text=True,capture_output=True,timeout=15)
@pytest.mark.parametrize("mid",sorted(MUTANTS))
def test_canonical_mutant_is_behaviorally_killed(mid):
 cp=run_mutant(mid);assert cp.returncode==0 and cp.stdout.strip().endswith("KILLED"),f"{mid} survived rc={cp.returncode} out={cp.stdout} err={cp.stderr}"
def test_exactly_12_mutants(): assert len(MUTANTS)==12
def test_protected_sources_unchanged():
 for f,h in BASE_HASH.items(): assert hashlib.sha256((ONTO/f).read_bytes()).hexdigest()==h

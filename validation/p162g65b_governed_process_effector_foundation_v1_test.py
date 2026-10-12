from pathlib import Path
from types import SimpleNamespace
from ontology.governed_process_effector import GovernedProcessEffector,ProcessEffectRequest
class F:
 def __init__(self): self.calls=[]
 def run(self,**kw): self.calls.append(kw); return {"status":"EFFECT_CONFIRMED","returncode":0,"stdout":b"","stderr":b"","timed_out":False,"uncertainty":False}
def setup():
 t=F(); e=GovernedProcessEffector(executable_registry={"git":{"path":"/usr/bin/git","argv_prefix":["status"]}},environment_registry={"minimal":{"PATH":"/usr/bin"}},transport=t)
 return e,SimpleNamespace(target_binding="process://git",operation_id="PROCESS_EXECUTE",adapter_id="a"),ProcessEffectRequest("git",("git","status"),None,"minimal","CLOSED",5),t
def test_exact(): e,h,r,t=setup(); assert e.execute(request=r,handle=h,adapter_id="a")["status"]=="EFFECT_CONFIRMED"; assert len(t.calls)==1 and t.calls[0]["env"]=={"PATH":"/usr/bin"}
def test_target(): e,h,r,t=setup(); h.target_binding="process://x"; assert e.execute(request=r,handle=h,adapter_id="a")["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"; assert not t.calls
def test_adapter(): e,h,r,t=setup(); assert e.execute(request=r,handle=h,adapter_id="x")["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"; assert not t.calls
def test_unknown_exec(): e,h,r,t=setup(); r=ProcessEffectRequest("sh",("sh","-c","id"),None,"minimal","CLOSED",5); assert e.execute(request=r,handle=h,adapter_id="a")["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"; assert not t.calls
def test_child_rights(): e,h,r,t=setup(); r=ProcessEffectRequest("git",("git","status"),None,"minimal","CLOSED",5,"DECLARED_DESCENDANTS_ONLY"); assert e.execute(request=r,handle=h,adapter_id="a")["reason"]=="child_process_rights_not_granted"
def test_tcb_shape():
 s=(Path(__file__).resolve().parents[1]/"ontology/governed_process_effector.py").read_text(); assert s.count("subprocess.run(")==1; assert "shell=False" in s and "close_fds=True" in s and "os.environ" not in s

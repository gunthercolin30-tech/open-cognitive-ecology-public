from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import gzip,json
from ontology.longitudinal_metrics_archive import LongitudinalMetricsArchive as C
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker
RID="R";A="A";E="E";STAMP="2026-10-07T00:00:00+00:00"
def obj(root,compress):
 o=object.__new__(C);o.root=root;o.metrics_dir=root/"metrics";o.history_path=o.metrics_dir/"metrics_history.jsonl";o.legacy_history_path=root/"metrics_history.jsonl";o.daily_dir=o.metrics_dir/"daily";o.weekly_dir=o.metrics_dir/"weekly";o.monthly_dir=o.metrics_dir/"monthly";o.experiments_dir=o.metrics_dir/"experiments";o.manifest_path=o.metrics_dir/"manifest.json";o.state_path=o.metrics_dir/"state.json";o.archive_quota_bytes=99999999;o.compress=compress;o.max_records_per_run=100;return o
def ctx(root,targets,drop=None):
 b=ScopedHandleBroker();e=GovernedFilesystemEffector(root_registry={RID:str(root)},handle_broker=b);slots={"archive_parent_create":[],"archive_write":[]}
 for i,t in enumerate(targets):
  for slot,op,path in (("archive_parent_create","FS_CREATE_DIRS",t.parent),("archive_write","FS_WRITE_REPLACE_BYTES",t)):
   binding=e.canonical_target(RID,path.resolve().relative_to(root.resolve()).as_posix());lease={"lease_id":f"l{i}{slot}","reservation_id":f"r{i}{slot}","operation_id":op,"expires_at":"2099-01-01T00:00:00+00:00"};claim=SimpleNamespace(lease_id=lease["lease_id"],reservation_id=lease["reservation_id"],adapter_id=A,claim_hash=f"c{i}{slot}");scope={"ambient_authority":False,"child_inheritance":False,"transferable":False};z=b.issue(claim=claim,lease=lease,registry_entry={"adapter_id":A,"effector_id":E},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=A,now_iso=STAMP);assert z["status"]=="HANDLE_ISSUED"
   if drop!=(i,slot):slots[slot].append(z["handle"])
 return GovernedFilesystemEffectContext(slots=slots,effector=e,root_id=RID,root_path=root,adapter_id=A,effector_id=E)
def direct(compress):
 with TemporaryDirectory() as d:
  root=Path(d);o=obj(root,compress);target=root/"sub"/("x.jsonl.gz" if compress else "x.jsonl");c=ctx(root,[target]);c.begin();n=o._write_jsonl(target,[{"a":1}],c);assert n>0 and all(v==0 for v in c.remaining().values());text=gzip.open(target,"rt").read() if compress else target.read_text();assert json.loads(text.strip())=={"a":1}
def main():
 direct(False);direct(True);print("FUNCTIONAL_TEST_OK\nGZIP_ALTERNATE_PATH_OK\nEXACT_HANDLE_CONSUMPTION_OK\nREAL_TCB_OK")
 with TemporaryDirectory() as d:
  root=Path(d);o=obj(root,False);t=root/"sub"/"x.jsonl"
  try:o._write_jsonl(t,[{"a":1}],None);raise AssertionError()
  except RuntimeError as x:assert "context required" in str(x)
  assert not t.exists()
 print("NO_AMBIENT_FALLBACK_OK")
 with TemporaryDirectory() as d:
  root=Path(d);o=obj(root,False);t=root/"sub"/"x.jsonl";c=ctx(root,[t],(0,"archive_write"));c.begin()
  try:o._write_jsonl(t,[{"a":1}],c);raise AssertionError()
  except Exception:pass
  assert not t.exists()
 print("DEGRADATION_TEST_OK\nNON_REGRESSION_TEST_OK")
if __name__=="__main__":main()

from pathlib import Path
import sys,tempfile,threading
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p006_go_rethink_stop import preregister,open_campaign,evaluate
from validation.p006_test_support import criteria,observations
with tempfile.TemporaryDirectory() as d:
 d=Path(d); r=preregister(criteria(),d,"2026-09-15T12:00:00+00:00")
 try: open_campaign(r,d,"2026-09-15T11:59:59+00:00")
 except ValueError: pass
 else: raise AssertionError("late preregistration accepted")
print("P006_TEMPORAL_LATE_PREREGISTRATION_REJECTED_OK")
with tempfile.TemporaryDirectory() as d:
 d=Path(d); a=criteria(); b=criteria(); b["conditions"][0]["description"]="post-hoc"
 preregister(a,d,"2026-09-15T12:00:00+00:00")
 try: preregister(b,d,"2026-09-15T12:00:01+00:00")
 except RuntimeError: pass
 else: raise AssertionError("cherry picking accepted")
print("P006_ANTI_CHERRY_PICK_DIVERGENT_REJECTED_OK")
with tempfile.TemporaryDirectory() as d:
 d=Path(d); out=[]; bar=threading.Barrier(2)
 def w(label):
  c=criteria(); c["conditions"][0]["description"]="variant-"+label; bar.wait()
  try: out.append(("ok",preregister(c,d,"2026-09-15T12:00:00+00:00")["criteria_hash"]))
  except RuntimeError: out.append(("rejected",label))
 x=threading.Thread(target=w,args=("A",)); y=threading.Thread(target=w,args=("B",)); x.start(); y.start(); x.join(); y.join()
 assert sorted(z[0] for z in out)==["ok","rejected"],out
print("P006_CONCURRENT_SINGLE_CANONICAL_WINNER_OK")
with tempfile.TemporaryDirectory() as d:
 d=Path(d); r=preregister(criteria(),d,"2026-09-15T12:00:00+00:00"); c=open_campaign(r,d,"2026-09-15T12:01:00+00:00")
 assert open_campaign(r,d,"2026-09-15T12:01:00+00:00")==c
 try: open_campaign(r,d,"2026-09-15T12:02:00+00:00")
 except RuntimeError: pass
 else: raise AssertionError("campaign rewritten")
 assert evaluate(r,observations(r["criteria_hash"],c))["decision"]=="GO"
 fake=dict(c); fake["started_at"]="2026-09-15T13:00:00+00:00"
 try: evaluate(r,observations(r["criteria_hash"],fake))
 except ValueError: pass
 else: raise AssertionError("tampered time accepted")
print("P006_CAMPAIGN_REPLAY_AND_TAMPER_OK")
print("P006_TEMPORAL_PREREGISTRATION_CROWN_OK")

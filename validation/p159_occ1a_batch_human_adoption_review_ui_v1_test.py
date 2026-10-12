from pathlib import Path
import tempfile,shutil,sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from ontology import occ_human_adoption_decision as d
from oif.ui.occ_adoption_review_service import OCCAdoptionReviewService
def ck(x,n):
 if not x: raise AssertionError(n)
 print(n)
with tempfile.TemporaryDirectory() as td:
 r=Path(td); src=ROOT/"oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json"; dst=r/"oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json"; dst.parent.mkdir(parents=True); shutil.copy2(src,dst)
 s=OCCAdoptionReviewService(r); c=s.batch_candidates(); ck(len(c)==17,"P159_OCC1A_BATCH_17_ORDINARY_OK")
 items=[{"canonical_id":x["canonical_id"],"decision":"ADOPT","rationale":s.suggested_rationale("ADOPT")} for x in c]
 q=s.save_batch(items,"human-test","constitutional_authority",True,"WRONG"); ck(not q["accepted"] and not d.decision_path(r).exists(),"P159_OCC1A_BATCH_CONFIRMATION_FAIL_CLOSED_OK")
 bad=items+[{"canonical_id":"DNA.L0.1","decision":"ADOPT","rationale":"attempt"}]
 q=s.save_batch(bad,"human-test","constitutional_authority",True,"CONFIRM HUMAN DECISIONS ONLY"); ck(not q["accepted"] and not d.decision_path(r).exists(),"P159_OCC1A_BATCH_L0_ATOMIC_ROLLBACK_OK")
 q=s.save_batch(items,"human-test","constitutional_authority",True,"CONFIRM HUMAN DECISIONS ONLY"); ck(q["accepted"] and q["decision_count"]==17,"P159_OCC1A_BATCH_ATOMIC_COMMIT_OK")
 ck(not q["adoption_performed"] and not q["activation_performed"] and not q["execution_performed"],"P159_OCC1A_BATCH_NO_NORMATIVE_EFFECT_OK")
 before=d.decision_path(r).read_bytes(); q2=s.save_batch(items,"human-test","constitutional_authority",True,"CONFIRM HUMAN DECISIONS ONLY"); ck(not q2["accepted"] and d.decision_path(r).read_bytes()==before,"P159_OCC1A_BATCH_REPLAY_IMMUTABILITY_OK")
print("P159_OCC1A_BATCH_HUMAN_ADOPTION_REVIEW_UI_V1_OK")

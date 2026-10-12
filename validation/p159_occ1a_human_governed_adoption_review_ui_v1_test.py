from pathlib import Path
import tempfile,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from ontology import occ_human_adoption_decision as d
from oif.ui.occ_adoption_review_service import OCCAdoptionReviewService
def ck(x,n):
 if not x: raise AssertionError(n)
 print(n)
with tempfile.TemporaryDirectory() as td:
 r=Path(td); src=ROOT/"oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json"; dst=r/"oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json"; dst.parent.mkdir(parents=True); shutil.copy2(src,dst); s=OCCAdoptionReviewService(r); z=s.summary()
 ck(z["total"]==23 and z["ordinary_decisionable"]==17 and z["refounding_or_fork"]==6,"P159_OCC1A_UI_POPULATION_OK")
 q=s.save(cid="DNA.H1",decision="ADOPT",rationale="explicit human governed decision",decider_id="human-test",decider_role="constitutional_authority",out_of_band_confirmation=True); ck(q["accepted"] and q["persisted_human_decision"] and not q["normative_adoption_performed"],"P159_OCC1A_UI_DECISION_PERSISTENCE_OK")
 q=s.save(cid="DNA.H1",decision="REJECT",rationale="replay",decider_id="human-test",decider_role="constitutional_authority"); ck(not q["accepted"] and q["reason"]=="DECISION_ALREADY_RECORDED","P159_OCC1A_UI_REPLAY_REJECT_OK")
 q=s.save(cid="DNA.L0.1",decision="ADOPT",rationale="attempt",decider_id="human-test",decider_role="constitutional_authority",out_of_band_confirmation=True); ck(not q["accepted"] and q["reason"]=="DNA_L0_REFOUNDING_OR_FORK_REQUIRED","P159_OCC1A_UI_L0_BLOCK_OK")
 p=d.decision_path(r); w=json.loads(p.read_text()); w["registry_sha256"]="0"*64; p.write_text(json.dumps(w))
 try: d.load_or_prepare(r); raise AssertionError("drift accepted")
 except ValueError as e: ck(str(e)=="SOURCE_REGISTRY_DRIFT","P159_OCC1A_UI_SOURCE_DRIFT_OK")
ck(not d.manifest()["adoption_performed"] and not d.manifest()["activation_performed"] and not d.manifest()["execution_performed"],"P159_OCC1A_UI_NO_NORMATIVE_EFFECT_OK")
print("P159_OCC1A_HUMAN_GOVERNED_ADOPTION_REVIEW_UI_V1_OK")

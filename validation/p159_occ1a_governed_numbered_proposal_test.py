from pathlib import Path
import json,sys,tempfile,shutil
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_governed_numbered_proposal as p
assert p.manifest()["proposal_is_binding"] is False
with tempfile.TemporaryDirectory() as td:
 r=Path(td)/"repo";rel=Path("oif_review/campaigns/P159-OCC1A/occ1a_candidate_materialization.json")
 (r/rel.parent).mkdir(parents=True,exist_ok=True)
 shutil.copy2(ROOT/rel,r/rel)
 q=p.save_proposal(r,"DNA.H1",["F2"],"La dignité humaine intrinsèque constitue cette proposition candidate.","Proposition humaine fondée explicitement sur la preuve historique F2.","reviewer-1","principal_investigator")
 assert q["status"]=="PROPOSED_NOT_ADOPTED" and q["binding_created"] is False and q["adoption_performed"] is False
 print("P159_OCC1A_GNP_VALID_PROPOSAL_OK")
 try:p.save_proposal(r,"DNA.H1",["F18"],"Définition candidate suffisamment longue pour le test.","Justification suffisamment longue pour provoquer le rejet attendu.","reviewer-1","principal_investigator")
 except ValueError:print("P159_OCC1A_GNP_CROSS_LAYER_REJECT_OK")
 else:raise AssertionError("cross-layer evidence accepted")
 try:p.save_proposal(r,"DNA.H2",[],"Définition candidate suffisamment longue pour le test.","Justification suffisamment longue pour provoquer le rejet attendu.","reviewer-1","principal_investigator")
 except ValueError:print("P159_OCC1A_GNP_EMPTY_EVIDENCE_REJECT_OK")
 else:raise AssertionError("empty evidence accepted")
 q0=p.save_proposal(r,"DNA.L0.1",["F1"],"Définition L0 candidate suffisamment longue pour contrôle.","Justification humaine suffisamment longue pour contrôle de gouvernance.","reviewer-1","constitutional_authority")
 assert q0["governance_route"]=="REFOUNDING_OR_FORK_REVIEW_REQUIRED"
 print("P159_OCC1A_GNP_L0_REFOUNDING_ROUTE_OK")
 reg=p.load_registry(r);p.validate_registry(r,reg)
 assert reg["binding_created"] is False and reg["adoption_performed"] is False and reg["activation_performed"] is False and reg["execution_performed"] is False
 assert reg["occ1a_closed"] is False and reg["occ1b_opened"] is False and reg["p160_opened"] is False
 print("P159_OCC1A_GNP_NON_ADOPTION_OK")
print("P159_OCC1A_GOVERNED_NUMBERED_PROPOSAL_OK")

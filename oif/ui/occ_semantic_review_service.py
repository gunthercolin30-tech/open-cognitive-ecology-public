from __future__ import annotations
import json
from pathlib import Path
from ontology import occ_human_semantic_review as review
from ontology import occ_candidate_materialization as mat
from ontology import occ_governed_numbered_proposal as prop
class OCCSemanticReviewService:
 def __init__(self,root:Path):
  self.root=root.resolve();self.path=self.root/"oif_review/campaigns/P159-OCC1A/occ1a_semantic_review_workbook.json";self.dossier_path=self.root/"oif_review/campaigns/P159-OCC1A/occ1a_candidate_materialization.json"
 def load(self):
  w=json.loads(self.path.read_text(encoding="utf-8"));review.validate_integrity(self.root,w);return w
 def load_dossiers(self):
  x=json.loads(self.dossier_path.read_text(encoding="utf-8"));mat.validate(x);return {d["canonical_id"]:d for d in x["dossiers"]}
 def load_proposals(self):
  x=prop.load_registry(self.root);prop.validate_registry(self.root,x);return x
 def save_proposal(self,**kw):return prop.save_proposal(self.root,**kw)
 def decision_options(self):return list(review.DECISIONS)
 def role_options(self):return list(review.AUTHORIZED_ROLES)
 def summary(self):
  w=self.load();n=sum(bool(e["human_decision"].get("decision")) for e in w["entries"]);pr=self.load_proposals()
  return {"campaign_id":w["campaign_id"],"decided":n,"total":23,"proposed":pr["proposal_count"],"status":w["status"]}
 def save_decision(self,**kw):return review.save_decision(self.root,self.path,**kw)

from pathlib import Path
from ontology import occ_human_adoption_decision as dec
SUGGESTED_RATIONALES={
"ADOPT":"Après examen du texte candidat, de sa source historique et de sa justification, j’approuve explicitement cette formulation comme décision humaine gouvernée. Cette décision ne constitue ni l’adoption normative, ni l’activation, ni l’exécution de la norme.",
"REJECT":"Après examen du texte candidat, de sa source historique et de sa justification, je rejette explicitement cette formulation dans le cadre de cette revue humaine gouvernée.",
"REQUEST_MORE_EVIDENCE":"Les éléments présentés ne sont pas suffisants pour une décision ; je demande des éléments complémentaires avant toute décision ultérieure.",
"ABSTAIN":"Je m’abstiens explicitement de statuer sur cette proposition dans le cadre de cette campagne."}
class OCCAdoptionReviewService:
 def __init__(self,root:Path): self.root=root.resolve()
 def workbook(self): return dec.load_or_prepare(self.root)
 def rows(self): return self.workbook()["rows"]
 def summary(self):
  rows=self.rows(); return {"total":len(rows),"decided":sum(r["decision"] is not None for r in rows),"ordinary_decisionable":sum(r["ordinary_adoption_permitted"] for r in rows),"refounding_or_fork":sum(not r["ordinary_adoption_permitted"] for r in rows),"adoption_performed":False,"activation_performed":False,"execution_performed":False}
 def save(self,**kw): return dec.save_human_decision(self.root,**kw)
 def batch_candidates(self): return [r for r in self.rows() if r["ordinary_adoption_permitted"] and r["decision"] is None]
 def suggested_rationale(self,decision="ADOPT"): return SUGGESTED_RATIONALES[decision]
 def save_batch(self,decisions,decider_id,decider_role,out_of_band_confirmation,batch_confirmation): return dec.save_human_decisions_batch(self.root,decisions,decider_id,decider_role,out_of_band_confirmation,batch_confirmation)

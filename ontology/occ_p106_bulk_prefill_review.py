from pathlib import Path
import copy,hashlib
from ontology import occ_institutional_authority_amendment_dossier as base
IDS=("DNA.H1","DNA.H2","DNA.H3","DNA.H4","DNA.H5","DNA.H6","DNA.H7","DNA.H8","DNA.H9","DNA.L1.1","DNA.L1.2","DNA.L1.3","DNA.L1.4","DNA.L1.5","DNA.L1.6","DNA.L1.7","DNA.L1.8")
FOCUS={
"DNA.H1":("dignité humaine intrinsèque","dignité et statut des personnes"),
"DNA.H2":("préservation de l'agentivité humaine","autonomie décisionnelle et liberté de choix"),
"DNA.H3":("plancher incompressible des droits fondamentaux","droits humains fondamentaux"),
"DNA.H4":("non-domination et non-coercition arbitraire","liberté et garanties contre la coercition"),
"DNA.H5":("non-production injustifiée de dommages graves","vie, intégrité et sécurité humaines"),
"DNA.H6":("égalité fondamentale et non-discrimination arbitraire","égalité de traitement"),
"DNA.H7":("protection de la sphère informationnelle","vie privée, données et sphère informationnelle"),
"DNA.H8":("contestabilité et recours effectif","droits procéduraux et recours"),
"DNA.H9":("deux clauses distinctes F12 pluralité/non-totalisation et F17 viabilité humaine intergénérationnelle; F18 reste exclu","pluralité humaine et viabilité intergénérationnelle"),
"DNA.L1.1":("opérationnalisation de la contestabilité sans création d'autorité","possibilité de contestation traçable"),
"DNA.L1.2":("opérationnalisation du recours sous autorités applicables","réexamen, correction ou suspension gouvernée"),
"DNA.L1.3":("responsabilité, provenance et auditabilité sans élargissement de pouvoir","responsabilité et auditabilité"),
"DNA.L1.4":("pluralité/non-totalisation sous réciprocité et plancher des droits","pluralité humaine"),
"DNA.L1.5":("héritabilité du DNA sans effacement silencieux","continuité des contraintes normatives"),
"DNA.L1.6":("persistance sémantique/comportementale sous transformation","prévention de l'érosion normative"),
"DNA.L1.7":("preuve proportionnée à portée, risque et criticité","vérifiabilité proportionnée"),
"DNA.L1.8":("séparation ClaimCompliance/EvidenceCompliance","exigence de preuve de conformité")}
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build_prefilled(root=None):
 r=Path(root) if root else Path.home()/"open-cognitive-ecology"; w=base.load_or_prepare(r)
 if tuple(x["canonical_id"] for x in w["dossiers"])!=IDS: raise ValueError("UNEXPECTED_ORDINARY_DOSSIER_SET")
 x=copy.deepcopy(w); dec=r/base.DEC_REL
 for row in x["dossiers"]:
  f,rights=FOCUS[row["canonical_id"]]; p=row["p106"]
  p["incompatibility_analysis"]="Aucune incompatibilité identifiée dans les preuves acquises : "+f+". Cette proposition ne crée aucune autorité artificielle nouvelle."
  p["rights_impact"]="Impact protecteur attendu sur "+rights+" ; aucun abaissement du plancher des droits n'est introduit."
  p["adversarial_review"]="Revue adversariale de liaison sémantique A01-A20 acquise. Elle ne constitue ni autorité P095, ni adoption, ni activation."
  p["long_form_human_governance"]="Arbitrage sémantique humain puis décision humaine ADOPT persistée dans P159-OCC1A; cette décision reste distincte de l'adoption normative."
  p["fork_or_migration_decision"]="Voie ordinaire limitée à DNA-H/DNA-L1. DNA-L0 reste REFOUNDING_OR_FORK_REQUIRED. Aucun fork ou migration n'est déclenché ici."
  p["provenance"]="canonical_id=%s; proposal_hash=%s; dossier_hash=%s; source_decision_sha256=%s; evidence_ids=%s"%(row["canonical_id"],row["proposal_hash"],row["dossier_hash"],_sha(dec),",".join(map(str,row.get("evidence_ids",[]))))
  row["dossier_human_confirmed"]=False; row["prefill_status"]="PROPOSED_FOR_HUMAN_REVIEW"
 for k in ("institutional_authority_established","p106_admissibility_established","adoption_performed","activation_performed","execution_performed","occ1a_closed","occ1b_opened","p160_opened"): x[k]=False
 return x
def summary(w):
 return {"all_prefilled":len(w["dossiers"])==17 and all(all(str(r["p106"].get(k,"")).strip() for k in base.P106_FIELDS) for r in w["dossiers"]),"all_confirmed":len(w["dossiers"])==17 and all(r["dossier_human_confirmed"] is True for r in w["dossiers"])}
def confirm(w,phrase):
 if phrase!="CONFIRM 17 P106 DOSSIERS ONLY": raise ValueError("INVALID_BULK_CONFIRMATION_PHRASE")
 if not summary(w)["all_prefilled"]: raise ValueError("P106_PREFILL_INCOMPLETE")
 x=copy.deepcopy(w)
 for row in x["dossiers"]: row["dossier_human_confirmed"]=True; row["prefill_status"]="HUMAN_CONFIRMED_INPUT"
 for k in ("institutional_authority_established","p106_admissibility_established","adoption_performed","activation_performed","execution_performed","occ1a_closed","occ1b_opened","p160_opened"): x[k]=False
 return x
def save(w,root=None): return base.save_human_inputs(w,root)
def manifest(): return {"calls_p095":False,"calls_p106":False,"calls_p104":False,"authority_created":False,"adoption_performed":False,"activation_performed":False,"execution_performed":False,"occ1b_opened":False,"p160_opened":False}

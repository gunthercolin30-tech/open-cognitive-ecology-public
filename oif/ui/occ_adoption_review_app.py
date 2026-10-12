from __future__ import annotations
import argparse,os
from pathlib import Path
from nicegui import ui
from oif.ui.occ_adoption_review_service import OCCAdoptionReviewService
def main():
 p=argparse.ArgumentParser(); p.add_argument("--root",type=Path,default=Path.home()/"open-cognitive-ecology"); p.add_argument("--host",default="127.0.0.1"); p.add_argument("--port",type=int,default=8768); p.add_argument("--no-browser",action="store_true"); a=p.parse_args()
 if a.host!="127.0.0.1" and os.environ.get("OIF_ALLOW_REMOTE_UI")!="1": p.error("remote binding requires OIF_ALLOW_REMOTE_UI=1")
 s=OCCAdoptionReviewService(a.root)
 @ui.page("/")
 def page():
  with ui.column().classes("w-full max-w-screen-xl mx-auto p-4 gap-4"):
   ui.label("P159 · OCC-1A — Décision humaine gouvernée en bloc").classes("text-h5")
   ui.label("Décisions humaines uniquement : aucune adoption normative, activation ou exécution.").classes("text-negative")
   z=s.summary(); candidates=s.batch_candidates()
   ui.label(f"Décisions existantes {z['decided']}/{z['total']} · propositions ordinaires restant à décider {len(candidates)} · DNA-L0 refounding/fork {z['refounding_or_fork']}")
   ui.label("Périmètre du lot").classes("text-h6")
   for r in candidates:
    with ui.expansion(f"{r['canonical_id']} · {r['layer']} · sources {', '.join(r['evidence_ids'])}").classes("w-full"):
     ui.label("Texte candidat").classes("text-weight-bold"); ui.label(r["candidate_definition"])
     ui.label("Justification de proposition").classes("text-weight-bold"); ui.label(r["proposal_rationale"])
   decision=ui.select(["ADOPT","REJECT","REQUEST_MORE_EVIDENCE","ABSTAIN"],value="ADOPT",label="Décision à appliquer au lot").classes("w-96")
   rationale=ui.textarea("Justification commune proposée").classes("w-full"); rationale.value=s.suggested_rationale("ADOPT")
   decision.on_value_change(lambda e: setattr(rationale,"value",s.suggested_rationale(e.value)))
   decider=ui.input("Identifiant stable du décideur humain",value="Colin Gunther").classes("w-full")
   role=ui.select(["principal_investigator","constitutional_authority"],value="constitutional_authority",label="Rôle").classes("w-96")
   ui.label("Confirmation secondaire : seconde action explicite distincte de la sélection. Elle n’est pas présentée comme une authentification indépendante.")
   secondary=ui.checkbox("Je confirme explicitement, par cette seconde action, la décision sur l’ensemble du lot")
   phrase=ui.input("Saisir exactement : CONFIRM HUMAN DECISIONS ONLY").classes("w-full")
   ack=ui.checkbox("J’ai examiné le périmètre du lot et confirme que l’opération enregistre uniquement mes décisions humaines.")
   button=ui.button("ENREGISTRER LE LOT DE DÉCISIONS HUMAINES",color="primary"); result=ui.label()
  def store():
   if not ack.value: ui.notify("ACKNOWLEDGEMENT_REQUIRED",type="negative"); return
   items=[{"canonical_id":r["canonical_id"],"decision":decision.value,"rationale":str(rationale.value or "").strip()} for r in s.batch_candidates()]
   q=s.save_batch(items,str(decider.value or ""),str(role.value or ""),bool(secondary.value),str(phrase.value or ""))
   if q.get("accepted"):
    ui.notify(f"{q['decision_count']} décisions humaines persistées atomiquement. Aucune adoption, activation ou exécution.",type="positive"); button.disable(); result.text=f"LOT PERSISTÉ · {q['decision_count']} décisions · SHA256 {q['workbook_sha256']}"
   else: ui.notify(f"{q.get('reason')} · cible {q.get('canonical_id','')}",type="negative")
  button.on_click(store)
 print("P159_OCC1A_BATCH_HUMAN_ADOPTION_REVIEW_UI_READY"); print(f"url=http://{a.host}:{a.port}/"); print("human_decisions_only=true"); print("adoption=false"); print("activation=false"); print("execution=false")
 ui.run(host=a.host,port=a.port,show=not a.no_browser,reload=False)
if __name__=="__main__": main()

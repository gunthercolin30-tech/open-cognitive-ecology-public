from __future__ import annotations
import argparse,os
from pathlib import Path
from nicegui import ui
from oif.ui.occ_semantic_review_service import OCCSemanticReviewService
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path.home()/"open-cognitive-ecology");p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=8767);p.add_argument("--no-browser",action="store_true");a=p.parse_args()
 if a.host!="127.0.0.1" and os.environ.get("OIF_ALLOW_REMOTE_UI")!="1":p.error("remote binding requires OIF_ALLOW_REMOTE_UI=1")
 s=OCCSemanticReviewService(a.root);dossiers=s.load_dossiers()
 @ui.page("/")
 def page():
  state={"w":s.load(),"i":0}
  with ui.column().classes("w-full max-w-screen-xl mx-auto p-4 gap-4"):
   ui.label("P159 · OCC-1A — Proposition numérotée gouvernée").classes("text-h5")
   ui.label("Une proposition humaine n'est ni un binding adopté, ni une activation, ni une exécution.").classes("text-negative")
   summary=ui.label();title=ui.label().classes("text-h5");warning=ui.label().classes("text-orange-9")
   evidence_box=ui.column().classes("w-full gap-2");selected={}
   ui.separator();ui.label("PROPOSITION HUMAINE").classes("text-h6")
   definition=ui.textarea("Définition candidate (20 caractères minimum)").classes("w-full")
   rationale=ui.textarea("Justification de la proposition (20 caractères minimum)").classes("w-full")
   proposer=ui.input("Identifiant du proposant").classes("w-full")
   role=ui.select(["principal_investigator","constitutional_authority"],value="principal_investigator",label="Rôle").classes("w-72")
   save=ui.button("Enregistrer la proposition",color="primary")
   with ui.row():prev=ui.button("Précédent");nxt=ui.button("Suivant")
   ui.separator();ui.label("La revue ACCEPT/REJECT reste une opération séparée après matérialisation de la proposition.")
  def render():
   e=state["w"]["entries"][state["i"]];cid=e["canonical_id"];d=dossiers[cid];pr=s.load_proposals()["proposals"].get(cid);z=s.summary()
   summary.text=f"{z['campaign_id']} · propositions {z['proposed']}/23 · décisions {z['decided']}/23";title.text=f"{state['i']+1}/23 · {cid} · binding: UNRESOLVED";warning.text=d["warning"]
   evidence_box.clear();selected.clear()
   with evidence_box:
    for alt in d["layer_compatible_historical_sources"]:
     cb=ui.checkbox(f"{alt['historical_id']} — {alt['definition']}");selected[alt["historical_id"]]=cb
     ui.label("Justification P155 : "+str(alt.get("justification") or "")).classes("text-caption")
   definition.value=(pr or {}).get("candidate_definition","");rationale.value=(pr or {}).get("proposal_rationale","");proposer.value=(pr or {}).get("proposer_id","");role.value=(pr or {}).get("proposer_role","principal_investigator")
   for fid in (pr or {}).get("evidence_ids",[]): 
    if fid in selected:selected[fid].value=True
   prev.disable() if state["i"]==0 else prev.enable();nxt.disable() if state["i"]==22 else nxt.enable()
  def move(x):state["i"]=max(0,min(22,state["i"]+x));render()
  def store():
   cid=state["w"]["entries"][state["i"]]["canonical_id"];ids=[k for k,v in selected.items() if v.value]
   try:
    q=s.save_proposal(canonical_id=cid,evidence_ids=ids,candidate_definition=str(definition.value or ""),proposal_rationale=str(rationale.value or ""),proposer_id=str(proposer.value or ""),proposer_role=str(role.value or ""))
    ui.notify(f"Proposition {q['status']} enregistrée; aucune adoption.",type="positive");render()
   except Exception as x:ui.notify(str(x),type="negative")
  prev.on_click(lambda:move(-1));nxt.on_click(lambda:move(1));save.on_click(store);render()
 print("P159_OCC1A_GOVERNED_NUMBERED_PROPOSAL_UI_READY");print(f"url=http://{a.host}:{a.port}/");print("proposal_is_binding=false");print("adoption_on_edit=false")
 ui.run(host=a.host,port=a.port,show=not a.no_browser,reload=False)
if __name__=="__main__":main()

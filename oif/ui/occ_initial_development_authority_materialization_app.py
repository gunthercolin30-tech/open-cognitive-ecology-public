from nicegui import ui
from ontology.occ_initial_development_authority_materialization import load_or_prepare, save_human_inputs
w=load_or_prepare()
ui.label("P159 / OCC-1A — Initial Development Human Authority").classes("text-h5")
ui.label("Revue institutionnelle humaine uniquement — aucune activation, adoption ou exécution.")
for s in ("Holder: Colin Gunther","Regime: INITIAL_DEVELOPMENT","Role: CONSTITUTIONAL_AUTHORITY",
          "Scope: toutes les fonctions humaines actuellement réservées",
          "Continuity: jusqu’à changement explicitement gouverné",
          "ROOT_OVERRIDE_ALL = false | DNA-L0 ordinary override = false"): ui.label(s)
authority_id=ui.input("Authority ID",value=w["authority_id"])
mandate=ui.textarea("Mandat",value=w["mandate"])
provenance=ui.textarea("Provenance institutionnelle",value=w["provenance"])
evidence=ui.textarea("Éléments de preuve / fondement",value=w["authority_evidence"])
cv=ui.input("Version Constitution",value=w["constitution_version"])
gv=ui.input("Version Governance",value=w["governance_version"])
vf=ui.number("Valid from (entier / timestamp institutionnel)",value=w["valid_from"],precision=0)
vu=ui.number("Valid until (entier / timestamp institutionnel)",value=w["valid_until"],precision=0)
auth=ui.checkbox("Je confirme que l’identité/autorité humaine est authentifiée",value=w["authenticated"])
confirm=ui.checkbox("Je confirme ces faits institutionnels",value=w["human_confirmed"])
phrase=ui.input("Phrase exacte : CONFIRM INITIAL DEVELOPMENT HUMAN AUTHORITY",value="CONFIRM INITIAL DEVELOPMENT HUMAN AUTHORITY")
def save():
 x=load_or_prepare()
 x.update({"authority_id":authority_id.value or "","mandate":mandate.value or "",
 "provenance":provenance.value or "","authority_evidence":evidence.value or "",
 "constitution_version":cv.value or "","governance_version":gv.value or "",
 "valid_from":int(vf.value) if vf.value is not None else None,
 "valid_until":int(vu.value) if vu.value is not None else None,
 "authenticated":bool(auth.value),"human_confirmed":bool(confirm.value),
 "confirmation_phrase":phrase.value or ""})
 r=save_human_inputs(x)
 ui.notify("Entrées humaines enregistrées. Autorité NON activée." if r["status"]=="READY_FOR_INDEPENDENT_VERIFICATION" else "Entrées incomplètes : "+", ".join(r["blockers"][:5]),type="positive" if r["status"]=="READY_FOR_INDEPENDENT_VERIFICATION" else "warning")
ui.button("Enregistrer les entrées humaines",on_click=save)
ui.run(title="OCE — Initial Development Human Authority",reload=False)

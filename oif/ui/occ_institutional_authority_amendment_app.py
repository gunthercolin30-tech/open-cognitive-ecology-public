from nicegui import ui
from ontology import occ_p106_bulk_prefill_review as m
w=m.build_prefilled()
ui.label("P159 / OCC-1A — Revue gouvernée des 17 dossiers P106").classes("text-h5")
ui.markdown("**Préremplissage proposé à la revue humaine uniquement. Aucune autorité P095, admissibilité P106, adoption, activation ou exécution n'est créée.**")
for row in w["dossiers"]:
 with ui.expansion(row["canonical_id"],value=False).classes("w-full"):
  ui.label(row["candidate_definition"])
  for k,l in (("incompatibility_analysis","Analyse d'incompatibilité"),("rights_impact","Impact sur les droits"),("adversarial_review","Revue adversariale"),("long_form_human_governance","Gouvernance humaine longue / référence"),("fork_or_migration_decision","Décision fork ou migration"),("provenance","Provenance")):
   ui.markdown("**"+l+"**");ui.label(row["p106"][k])
ui.separator()
ui.markdown("Après lecture, saisir exactement `CONFIRM 17 P106 DOSSIERS ONLY`. La confirmation porte uniquement sur ces entrées P106.")
phrase=ui.input("Phrase de confirmation").classes("w-full")
status=ui.label("")
def go():
 global w
 try:
  w=m.confirm(m.build_prefilled(),phrase.value or "");v=m.save(w)
  status.set_text("17 dossiers confirmés comme entrées humaines; état="+v["status"]+". Autorité/adoption/activation/exécution non établies.")
  ui.notify("17 dossiers confirmés comme entrées humaines uniquement.",type="positive")
 except Exception as e: ui.notify(str(e),type="negative")
ui.button("Confirmer les 17 dossiers P106 uniquement",on_click=go)
ui.run(title="OCE P159 OCC-1A P106 bulk review")

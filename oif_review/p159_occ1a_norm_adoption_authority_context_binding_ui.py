from pathlib import Path
import json, sys
ROOT=Path.home()/"open-cognitive-ecology"
sys.path.insert(0,str(ROOT))
from ontology import occ_norm_adoption_authority_context_binding as q
from nicegui import ui
p=ROOT/q.BIND_REL
x=q.materialize(ROOT)
ui.label("OCE P159 OCC-1A — Authority Context Binding").classes("text-h5")
ui.markdown("This is an explicit binding of a context to the existing bounded human authority. It does **not** create new authority and does **not** permit ordinary DNA-L0 adoption.")
ui.label("Existing holder: "+str(x.get("holder")))
ui.label("Existing context: "+str(x.get("source_context")))
ui.label("Additional context: "+q.REQUIRED_CONTEXT)
ui.label("Purpose: OCC-1A ordinary normative adoption only")
ui.separator()
ui.markdown("Exact confirmation required:")
ui.code(q.CONFIRMATION)
box=ui.checkbox("I confirm the exact statement above")
status=ui.label("Status: "+x["status"])
def confirm():
 cur=q.load(p)
 if cur.get("human_confirmed") is True:
  status.set_text("Status: HUMAN_CONFIRMED"); return
 if not box.value:
  ui.notify("Confirmation checkbox required",type="negative"); return
 cur["human_confirmed"]=True;cur["human_confirmation_text"]=q.CONFIRMATION;cur["status"]="HUMAN_CONFIRMED"
 if not q.validate(cur,ROOT/q.DECL_REL):
  ui.notify("Validation failed",type="negative"); return
 p.write_text(json.dumps(cur,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 status.set_text("Status: HUMAN_CONFIRMED");ui.notify("Governed context binding confirmed",type="positive")
ui.button("Confirm governed context binding",on_click=confirm)
ui.run(title="OCE OCC-1A Context Binding",reload=False)

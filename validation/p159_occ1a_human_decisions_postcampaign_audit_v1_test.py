from pathlib import Path
import json, shutil, tempfile, sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from ontology import occ_human_decisions_postcampaign_audit as a
from ontology import occ_human_adoption_decision as d

def ck(v,n):
    if not v: raise AssertionError(n)
    print(n)

real=a.audit(ROOT)
ck(real["decision"]=="POSTCAMPAIGN_AUDIT_OK","P159_OCC1A_POSTCAMPAIGN_REAL_STATE_OK")
ck(real["human_decision_count"]==17 and real["ordinary_target_count"]==17,"P159_OCC1A_POSTCAMPAIGN_17_DECISIONS_OK")
ck(real["dna_l0_count"]==6 and real["dna_l0_decision_count"]==0,"P159_OCC1A_POSTCAMPAIGN_L0_UNDECIDED_OK")
ck(not real["adoption_performed"] and not real["activation_performed"] and not real["execution_performed"],"P159_OCC1A_POSTCAMPAIGN_NO_NORMATIVE_EFFECT_OK")
ck(not real["occ1a_closed"] and not real["occ1b_opened"] and not real["p160_opened"],"P159_OCC1A_POSTCAMPAIGN_STAGE_BOUNDARY_OK")

with tempfile.TemporaryDirectory() as td:
    r=Path(td)
    for rel in ("oif_review/campaigns/P159-OCC1A/occ1a_numbered_proposals.json",
                "oif_review/campaigns/P159-OCC1A/occ1a_human_adoption_decisions.json"):
        src=ROOT/rel; dst=r/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    # Tamper decision workbook: remove one human decision.
    p=d.decision_path(r); w=json.loads(p.read_text(encoding="utf-8"))
    target=next(x for x in w["rows"] if x.get("decision") is not None)
    target["decision"]=None; target["decision_rationale"]=None; target["decider_id"]=None
    p.write_text(json.dumps(w,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    q=a.audit(r)
    ck(q["decision"]=="POSTCAMPAIGN_AUDIT_BLOCKED" and "EXPECTED_17_HUMAN_DECISIONS" in q["blockers"],"P159_OCC1A_POSTCAMPAIGN_DEGRADATION_OK")

# Real-state immutability / restart determinism.
b1=a.canonical_bytes(a.audit(ROOT)); b2=a.canonical_bytes(a.audit(ROOT))
ck(b1==b2,"P159_OCC1A_POSTCAMPAIGN_DETERMINISM_OK")
print("P159_OCC1A_HUMAN_DECISIONS_POSTCAMPAIGN_AUDIT_V1_OK")

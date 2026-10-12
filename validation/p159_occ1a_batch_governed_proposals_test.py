from pathlib import Path
import copy,json,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_batch_governed_proposals as b
from ontology import occ_governed_numbered_proposal as u
assert len(b.TARGETS)==20 and b.manifest()["direct_normative_authority"] is False
print("P159_OCC1A_BATCH_SCOPE_OK")
with tempfile.TemporaryDirectory() as td:
 r=Path(td)/"repo";rel=Path("oif_review/campaigns/P159-OCC1A/occ1a_candidate_materialization.json");(r/rel.parent).mkdir(parents=True);shutil.copy2(ROOT/rel,r/rel)
 for cid,fid in (("DNA.H1","F2"),("DNA.H2","F3"),("DNA.H3","F4")):u.save_proposal(r,cid,[fid],f"Définition humaine candidate suffisamment longue pour {cid}.",f"Justification humaine suffisamment longue pour {cid}.","test-human","principal_investigator")
 d=b.template(r)
 for x in d["proposals"]:
  x["evidence_ids"]=[x["allowed_evidence_ids"][0]];x["candidate_definition"]="Définition humaine de test suffisamment longue.";x["proposal_rationale"]="Justification humaine de test suffisamment longue.";x["proposer_id"]="test-human"
 bp=r/"batch.json";bp.write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8");before=u.proposal_path(r).read_bytes()
 bad=copy.deepcopy(d);bad["proposals"][0]["evidence_ids"]=["F18"];badp=r/"bad.json";badp.write_text(json.dumps(bad),encoding="utf-8")
 try:b.apply_batch(r,badp)
 except ValueError:pass
 else:raise AssertionError("invalid evidence accepted")
 assert u.proposal_path(r).read_bytes()==before;print("P159_OCC1A_BATCH_ALL_OR_NOTHING_OK")
 z=b.apply_batch(r,bp);assert z["proposal_count"]==23 and z["adoption_performed"] is False and z["p160_opened"] is False;print("P159_OCC1A_BATCH_TRANSACTION_OK")
 try:b.apply_batch(r,bp)
 except ValueError:print("P159_OCC1A_BATCH_OVERWRITE_REJECT_OK")
 else:raise AssertionError("overwrite accepted")
print("P159_OCC1A_BATCH_GOVERNED_PROPOSALS_OK")

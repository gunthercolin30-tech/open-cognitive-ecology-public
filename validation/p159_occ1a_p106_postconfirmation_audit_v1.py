from pathlib import Path
import copy, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ontology import occ_institutional_authority_amendment_dossier as base
from ontology import occ_p106_bulk_prefill_review as bulk

EXPECTED = set(bulk.IDS)

def ok(cond, label):
    if not cond:
        raise AssertionError(label)
    print(label)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    workbook_path = ROOT / base.WORKBOOK_REL
    decision_path = ROOT / base.DEC_REL
    ok(workbook_path.is_file(), "P159_OCC1A_P106_POSTCONFIRM_WORKBOOK_EXISTS_OK")
    ok(decision_path.is_file(), "P159_OCC1A_P106_POSTCONFIRM_DECISION_SOURCE_EXISTS_OK")

    raw = workbook_path.read_bytes()
    w = json.loads(raw.decode("utf-8"))
    rows = w.get("dossiers", [])
    ids = [r.get("canonical_id") for r in rows]

    ok(len(rows) == 17, "P159_OCC1A_P106_POSTCONFIRM_17_OK")
    ok(len(ids) == len(set(ids)) == 17 and set(ids) == EXPECTED,
       "P159_OCC1A_P106_POSTCONFIRM_CANONICAL_SET_OK")
    ok(all(r.get("dossier_human_confirmed") is True for r in rows),
       "P159_OCC1A_P106_POSTCONFIRM_17_CONFIRMED_OK")
    ok(all(r.get("prefill_status") == "HUMAN_CONFIRMED_INPUT" for r in rows),
       "P159_OCC1A_P106_POSTCONFIRM_STATUS_OK")
    ok(all(all(str(r.get("p106", {}).get(k, "")).strip() for k in base.P106_FIELDS) for r in rows),
       "P159_OCC1A_P106_POSTCONFIRM_P106_COMPLETE_OK")

    expected = bulk.build_prefilled(ROOT)
    by_id = {r["canonical_id"]: r for r in expected["dossiers"]}
    for r in rows:
        e = by_id[r["canonical_id"]]
        ok(r.get("candidate_definition") == e.get("candidate_definition"),
           "P159_OCC1A_P106_POSTCONFIRM_DEFINITION_%s_OK" % r["canonical_id"].replace(".","_"))
        ok(r.get("proposal_hash") == e.get("proposal_hash") and r.get("dossier_hash") == e.get("dossier_hash"),
           "P159_OCC1A_P106_POSTCONFIRM_HASH_%s_OK" % r["canonical_id"].replace(".","_"))
        ok(r.get("evidence_ids") == e.get("evidence_ids"),
           "P159_OCC1A_P106_POSTCONFIRM_EVIDENCE_%s_OK" % r["canonical_id"].replace(".","_"))
        ok(r.get("p106") == e.get("p106"),
           "P159_OCC1A_P106_POSTCONFIRM_CONTENT_%s_OK" % r["canonical_id"].replace(".","_"))

    h9 = next(r for r in rows if r["canonical_id"] == "DNA.H9")
    ok(h9.get("evidence_ids") == ["F12", "F17"], "P159_OCC1A_P106_POSTCONFIRM_H9_F12_F17_OK")
    ok("F18 reste exclu" in h9["p106"]["incompatibility_analysis"],
       "P159_OCC1A_P106_POSTCONFIRM_H9_F18_EXCLUSION_OK")

    for k in ("institutional_authority_established","p106_admissibility_established",
              "adoption_performed","activation_performed","execution_performed",
              "occ1a_closed","occ1b_opened","p160_opened"):
        ok(w.get(k) is False, "P159_OCC1A_P106_POSTCONFIRM_%s_FALSE_OK" % k.upper())

    # Degradation: a modified persisted copy must be distinguishable from reviewed content.
    tampered = copy.deepcopy(w)
    tampered["dossiers"][0]["p106"]["rights_impact"] += " TAMPER"
    ok(tampered["dossiers"][0]["p106"] != by_id["DNA.H1"]["p106"],
       "P159_OCC1A_P106_POSTCONFIRM_TAMPER_DETECTED_OK")

    # Determinism: canonical regeneration of proposed reviewed content is stable.
    expected2 = bulk.build_prefilled(ROOT)
    ok(expected["dossiers"] == expected2["dossiers"],
       "P159_OCC1A_P106_POSTCONFIRM_DETERMINISM_OK")

    print("decision_source_sha256=" + sha(decision_path))
    print("workbook_sha256=" + hashlib.sha256(raw).hexdigest())
    print("authority_established=false")
    print("p106_admissibility_established=false")
    print("adoption_performed=false")
    print("activation_performed=false")
    print("execution_performed=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")
    print("P159_OCC1A_P106_POSTCONFIRMATION_AUDIT_V1_OK")

if __name__ == "__main__":
    main()

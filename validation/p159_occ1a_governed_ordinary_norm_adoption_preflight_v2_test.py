from pathlib import Path
import json, hashlib
from unittest.mock import patch
from ontology import occ_governed_ordinary_norm_adoption_preflight as q

ROOT = Path(__file__).resolve().parents[1]
BIND_REL = Path("oif_review/campaigns/P159-OCC1A/occ1a_norm_adoption_authority_context_binding.json")

def main():
    # Functional current-state proof.
    x = q.audit(ROOT)
    assert x["decision"] == "READY_FOR_17_ORDINARY_ADOPTIONS", x
    assert x["ordinary_target_count"] == 17
    assert x["dna_l0_excluded_count"] == 6
    assert x["checks"]["p095_required_adoption_context_explicitly_bound"] is True
    assert x["checks"]["institutional_authority_independently_verified"] is True
    assert x["checks"]["all_human_decisions_adopt_oob"] is True
    assert x["checks"]["all_registered_proposals_exact"] is True
    assert x["checks"]["all_p106_dossiers_confirmed_and_bound"] is True

    # Stage-boundary invariants.
    assert x["adoption_performed"] is False
    assert x["authority_activated"] is False
    assert x["package_materialized"] is False
    assert x["execution_performed"] is False
    assert x["occ1a_closed"] is False
    assert x["occ1b_opened"] is False
    assert x["p160_opened"] is False

    # Determinism on the real read-only state.
    assert q.audit(ROOT) == x

    # Targeted degradation without copying the repository:
    # intercept only the governed context-binding read and return a degraded
    # in-memory copy. All other authoritative reads remain real and read-only.
    bind_path = ROOT / BIND_REL
    original_binding = json.loads(bind_path.read_text(encoding="utf-8"))
    degraded_binding = dict(original_binding)
    degraded_binding["human_confirmed"] = False
    degraded_binding["status"] = "AWAITING_HUMAN_CONFIRMATION"

    real_load = q._load
    def degraded_load(path):
        p = Path(path)
        try:
            if p.resolve() == bind_path.resolve():
                return dict(degraded_binding)
        except OSError:
            pass
        return real_load(path)

    before_sha = hashlib.sha256(bind_path.read_bytes()).hexdigest()
    with patch.object(q, "_load", side_effect=degraded_load):
        y = q.audit(ROOT)
    after_sha = hashlib.sha256(bind_path.read_bytes()).hexdigest()

    assert before_sha == after_sha
    assert y["decision"] == "ADOPTION_PREFLIGHT_BLOCKED", y
    assert y["checks"]["p095_required_adoption_context_explicitly_bound"] is False
    assert "P095_REQUIRED_ADOPTION_CONTEXT_EXPLICITLY_BOUND" in y["blockers"]
    assert "NO_IMPLICIT_AUTHORITY_CONTEXT_EXPANSION" in y["blockers"]
    assert y["adoption_performed"] is False
    assert y["authority_activated"] is False
    assert y["package_materialized"] is False
    assert y["execution_performed"] is False
    assert y["occ1a_closed"] is False
    assert y["occ1b_opened"] is False
    assert y["p160_opened"] is False

    # Confirm that degradation was virtual only and current state remains READY.
    z = q.audit(ROOT)
    assert z == x
    assert z["decision"] == "READY_FOR_17_ORDINARY_ADOPTIONS"

    print("P159_OCC1A_GOVERNED_ORDINARY_NORM_ADOPTION_PREFLIGHT_V2_1_FUNCTIONAL_OK")
    print("P159_OCC1A_GOVERNED_ORDINARY_NORM_ADOPTION_PREFLIGHT_V2_1_BINDING_DEGRADATION_OK")
    print("P159_OCC1A_GOVERNED_ORDINARY_NORM_ADOPTION_PREFLIGHT_V2_1_NONMUTATION_OK")
    print("P159_OCC1A_GOVERNED_ORDINARY_NORM_ADOPTION_PREFLIGHT_V2_1_DETERMINISM_OK")
    print("decision=" + x["decision"])
    print("ordinary_target_count=" + str(x["ordinary_target_count"]))
    print("dna_l0_excluded_count=" + str(x["dna_l0_excluded_count"]))
    print("adoption_performed=false")
    print("authority_activated=false")
    print("package_materialized=false")
    print("execution_performed=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")

if __name__ == "__main__":
    main()

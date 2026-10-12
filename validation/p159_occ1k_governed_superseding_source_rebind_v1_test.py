from validation import p159_occ1k_governed_superseding_source_rebind_v1 as a
def test_preflight_exact_old_and_new_hashes():
    p=a.proposal(); assert p["supersedes_sha256"]==a.OLD and p["new_sha256"]==a.NEW
def test_preflight_is_non_mutating():
    before=a.sha(a.MAN); a.proposal(); assert a.sha(a.MAN)==before
def test_wrong_confirmation_rejected_without_mutation():
    before=a.sha(a.MAN)
    try: a.execute("WRONG")
    except RuntimeError as e: assert "EXPLICIT_CONFIRMATION_REQUIRED" in str(e)
    else: assert False
    assert a.sha(a.MAN)==before
def test_proposal_preserves_history_and_boundaries():
    p=a.proposal(); assert p["preserve_historical_binding"] and not p["retroactive_repair"]
    assert not p["runtime_authorization"] and not p["p160b_opened"] and p["fl_b3"]=="BLOCKED"
def test_deterministic_proposal():
    assert a.canon(a.proposal())==a.canon(a.proposal())

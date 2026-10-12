def record(claimed_level="M9"):
    ev={}
    for i in range(10):
        level=f"M{i}"
        ref=f"artifact:{level.lower()}-001"
        ev[level]={"satisfied":True,"confidence":0.90,
                   "evidence_refs":[ref],
                   "source":"hypothesis" if level=="M0" else "external"}
        if level!="M0":
            ev[level]["external_evidence"]={
                "origin_type":"external_observation","origin_id":f"origin-{level}",
                "observed_at":"2026-09-15T12:00:00Z","artifact_ref":ref}
    return {"market_id":"market-alpha","claimed_level":claimed_level,"market_evidence":ev,
            "provenance":{"collector":"p005-test"},"configuration":{"schema":"p005-v1"},"dependencies":[]}

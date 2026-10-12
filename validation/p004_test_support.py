from validation.p004_evidence_ladder import EvidenceLadder
def record(n=12, claimed="E11"):
    ev={}
    for i in range(n):
        ev[f"E{i}"]={"satisfied":True,"confidence":0.9,"evidence_refs":[f"proof:E{i}"]}
    return {"claim_id":"c","claimed_level":claimed,"evidence":ev,"provenance":{"source":"test"},
            "configuration":{"protocol":"P004-test"},"dependencies":[]}

from acee6_k1_property_oracles import sha
base={"proposal_id":"p","candidate_id":"c","state":"REJECTED"}
seen={sha(base)}
for key,value in (("proposal_id","p2"),("candidate_id","c2"),("state","QUARANTINE")):
    changed=dict(base); changed[key]=value; seen.add(sha(changed))
assert len(seen)==4
print("ACEE6_K1_HASH_BINDING_PROPERTIES_OK")

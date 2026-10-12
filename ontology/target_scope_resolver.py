import hashlib,json
def _hash(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def resolve_target_scope(requested_target,resolved_targets,authorized_targets,resolution_evidence=None,uncertain=False):
 resolved=list(dict.fromkeys(resolved_targets)); auth=set(authorized_targets); escape=any(x not in auth for x in resolved)
 status="EFFECTIVE_SCOPE_UNDETERMINED" if uncertain else ("TARGET_SCOPE_INSUFFICIENT" if escape or not resolved else "RESOLVED_WITHIN_SCOPE")
 d={"requested_target":requested_target,"resolved_targets":resolved,"resolution_evidence":resolution_evidence or [],"escape_detected":escape,"status":status}; d["scope_hash"]=_hash(d); return d

def resolve_alias_chain(requested,chain,authorized,max_hops=16,uncertain=False):
 if uncertain or len(chain)>max_hops:return resolve_target_scope(requested,[],authorized,[{"type":"uncertain_or_hop_limit"}],True)
 return resolve_target_scope(requested,chain[-1:] if chain else [],authorized,[{"type":"alias_resolution","chain":list(chain)}],False)

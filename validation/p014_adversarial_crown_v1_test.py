from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology.p014_supply_chain_sovereignty import *

def dep(i,c="software",**kw):
    x=dict(dependency_id=i,category=c,version="1.2.3",digest="sha256:x",provider="provider-"+i,
    provider_owner="owner-"+i,failure_domain="fd-"+i,criticality="DC2",substitutability="REPLACEABLE",
    sovereignty_tier="DS1",lifecycle="ACTIVE",assurance="LOCAL_VERIFIED",provenance={"source":"fixture"},
    local_control=True,rollbackable=True,offline_survivable=True,exportable=True,open_format=True,
    reproducible=True,hermetic=True,independently_built=True,vulnerability_monitoring=True,
    identity_verified=True,authenticity_verified=True,safety_verified=True,privilege_scope="bounded",
    key_id="k",key_valid=True)
    x.update(kw); return Dependency(**x)

# 1 critical mutable alias + untrusted remote root mutation
x=dep("root",version="latest",criticality="DC5",root_trust=True,remote_mutable=True,third_party_trusted=False)
assert {"CRITICAL_VERSION_NOT_PINNED","UNTRUSTED_REMOTE_ROOT_MUTATION"} <= set(x.validate())

# 2 provenance/digest admission fail closed
x=dep("critical",criticality="DC5",provenance={},digest=None)
assert not P014Canonical([x]).admission("critical")["admitted"]

# 3 unknown assurance cannot activate
x=dep("opaque",assurance="UNKNOWN")
g=P014Canonical([x])
assert not g.activation("opaque")["activation_authorized"]

# 4 false provider pluralism
a=dep("a",provider="front-a",provider_owner="same-owner")
b=dep("b",provider="front-b",provider_owner="same-owner")
assert not P014Canonical([a,b]).provider_pluralism(["a","b"])["independent"]

# 5 provider blast radius is transitive
a=dep("a",provider_owner="owner-X",dependencies=("b",))
b=dep("b",provider_owner="owner-Y",dependencies=("c",))
c=dep("c",provider_owner="owner-Z")
assert P014Canonical([a,b,c]).blast_radius("owner-Z")["impacted"]==["a","b","c"]

# 6 unresolved dependency graph
a=dep("a",dependencies=("missing",))
assert not P014Canonical([a]).graph()["complete"]

# 7 no compromise inference from exposure
a=dep("a",dependencies=("b",)); b=dep("b")
assert P014Canonical([a,b]).reverse_exposure("b")["compromise_inferred"] is False

# 8 strategic dependency with no exit sovereignty
x=dep("strategic",strategic=True,substitutability="NONE",local_control=False,rollbackable=False,exportable=False,open_format=False)
g=P014Canonical([x])
assert not g.exit_plan("strategic")["exitable"] and not g.canonical_gate()["ready"]

# 9 no infrastructure available -> safe degraded mode
assert P014Canonical([]).fallback(False,False,False)=="SAFE_DEGRADED_MODE"

# 10 quarantine never executes
assert P014Canonical([]).quarantine("x","provider drift")["execution_allowed"] is False

# 11 model behavioral attestation absent
x=dep("m","model",behavior_fingerprint=None)
assert P014Canonical([x]).model_tool_data_gate("m")["revalidation_required"]

# 12 tool semantic/schema drift evidence absent
x=dep("t","tool_api",capability_schema=None,semantic_version=None)
assert P014Canonical([x]).model_tool_data_gate("t")["revalidation_required"]

# 13 data lineage absent
x=dep("d","data",training_provenance={})
assert P014Canonical([x]).model_tool_data_gate("d")["revalidation_required"]

# 14 provenance before privilege
x=dep("priv",provenance={},identity_verified=False,privilege_scope=None)
assert not P014Canonical([x]).privilege_gate("priv")["authorized"]

# 15 invalid/revoked credential
x=dep("key",key_valid=False)
assert not P014Canonical([x]).privilege_gate("key")["authorized"]

# 16 legitimacy capture rejected
x=dep("legit",legitimacy_dependency=True)
assert not P014Canonical([x]).legitimacy_check("legit")["compliant"]
assert not P014Canonical([x]).canonical_gate()["ready"]

# 17 silent strategic dependency detected
x=dep("silent",strategic=True,provider=None,assurance="UNKNOWN")
assert "silent" in P014Canonical([x]).strategic_silence()

# 18 update of provider/maintainer/behavior is governance event + revalidation
x=dep("u")
g=P014Canonical([x])
ev=g.update_event("u",{"version":"1","provider":"p","maintainer":"m","behavior_fingerprint":"a"},
                      {"version":"2","provider":"q","maintainer":"n","behavior_fingerprint":"b"},emergency=True)
assert ev["governance_event"] and ev["revalidation_required"] and ev["path"]=="EMERGENCY"

# 19 publication != activation
x=dep("avail",lifecycle="AVAILABLE")
g=P014Canonical([x])
assert g.activation("avail")["published"] and not g.activation("avail")["activation_authorized"]

# 20 authenticity != safety, identity != trust
x=dep("id",identity_verified=True,authenticity_verified=True,safety_verified=False)
r=P014Canonical([x]).identity_trust("id")
assert r["identity_is_trust"] is False and r["authenticity_is_safety"] is False

# 21 high-assurance build fails if not hermetic/diverse
x=dep("build","build_chain",reproducible=True,hermetic=False,independently_built=False)
assert not P014Canonical([x]).build_assurance("build")["verified"]

# 22 failed substitution drill
x=dep("sub")
assert not P014Canonical([x]).substitution_drill("sub",False,True)["passed"]

# 23 canonical contract is exactly 59 unique objects
c=canonical_contract()
assert c["object_count"]==59 and len(c["objects"])==59 and len(set(c["objects"]))==59

# 24 epistemic invariants remain functional-only
assert c["functional_only"] is True and c["phenomenology_undetermined"] is True

print("P014_ADVERSARIAL_CROWN_V1_OK")
print("adversarial_cases=24")
print("canonical_objects=59")
print("functional_only=true")
print("phenomenology_undetermined=true")

from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology.p014_supply_chain_sovereignty import *
def d(i,c,**kw):
    x=dict(dependency_id=i,category=c,version="1.0.0",digest="sha",provider="p-"+i,provider_owner="o-"+i,
    failure_domain="fd-"+i,criticality="DC2",substitutability="REPLACEABLE",sovereignty_tier="DS1",lifecycle="ACTIVE",
    assurance="LOCAL_VERIFIED",provenance={"source":"test"},local_control=True,rollbackable=True,offline_survivable=True,
    exportable=True,open_format=True,reproducible=True,hermetic=True,independently_built=True,vulnerability_monitoring=True,
    identity_verified=True,authenticity_verified=True,safety_verified=True,privilege_scope="bounded",key_id="k",key_valid=True)
    x.update(kw);return Dependency(**x)
deps=[d("sw","software",dependencies=("model",)),d("model","model",behavior_fingerprint="bf"),d("data","data",training_provenance={"dataset":"x"}),
d("tool","tool_api",capability_schema="s",semantic_version="1"),d("infra","infrastructure"),d("build","build_chain"),
d("gov","governance_service"),d("human","human")]
g=P014Canonical(deps)
assert canonical_contract()["object_count"]==59
assert g.cbd()["surface_complete"] and g.graph()["complete"] and g.transitive("sw")==["model"]
assert g.reverse_exposure("model")["exposed"]==["sw"]
assert g.admission("sw")["admitted"] and g.activation("sw")["activation_authorized"]
assert g.exit_plan("sw")["exitable"] and g.build_assurance("sw")["verified"]
assert g.privilege_gate("sw")["authorized"] and g.legitimacy_check("sw")["compliant"]
assert not g.model_tool_data_gate("model")["revalidation_required"]
assert g.substitution_drill("sw",True,True)["passed"]
assert g.canonical_gate()["ready"]
print("P014_CANONICAL_COMPLETE_FUNCTIONAL_OK")
bad=d("root","software",version="latest",criticality="DC5",strategic=True,remote_mutable=True,third_party_trusted=False,
provenance={},assurance="UNKNOWN",local_control=False,rollbackable=False,exportable=False,open_format=False,
identity_verified=False,privilege_scope=None,key_valid=False,legitimacy_dependency=True,substitutability="NONE")
b=P014Canonical([bad])
assert not b.admission("root")["admitted"] and not b.privilege_gate("root")["authorized"]
assert not b.exit_plan("root")["exitable"] and not b.canonical_gate()["ready"]
assert b.fallback(False,False,False)=="SAFE_DEGRADED_MODE"
assert b.quarantine("root","drift")["execution_allowed"] is False
print("P014_CANONICAL_COMPLETE_DEGRADATION_OK")
assert canonical_contract()["functional_only"] and canonical_contract()["phenomenology_undetermined"]
print("P014_CANONICAL_COMPLETE_NON_REGRESSION_OK")

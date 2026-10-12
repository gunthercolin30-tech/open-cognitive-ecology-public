from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ontology.p014_supply_chain_sovereignty import *
def d(i,c,**kw):
    base=dict(dependency_id=i,category=c,version="1.0.0",digest="d",provider="p-"+i,independent_provider=True,
    failure_domain="f-"+i,criticality="DC2",substitutability="REPLACEABLE",sovereignty_tier="DS1",lifecycle="ACTIVE",
    assurance="LOCAL_VERIFIED",provenance={"source":"test"},replaceable=True,local_control=True,rollbackable=True,offline_survivable=True)
    base.update(kw); return Dependency(**base)
deps=[d("s","software",dependencies=("m",)),d("m","model"),d("data","data"),d("api","tool_api"),d("infra","infrastructure"),
d("build","build_chain"),d("gov","governance_service"),d("human","human")]
g=P014SupplyChainSovereignty(deps)
assert canonical_contract()["object_count"]==59 and g.cbd()["surface_complete"] and g.graph()["complete"]
assert g.transitive("s")==["m"] and g.reverse_exposure("m")["exposed"]==["s"] and g.sovereignty_gate()["canonical_ready"]
assert g.fallback("s",False,False,False)=="SAFE_DEGRADED_MODE"
print("P014_CANONICAL_REBUILD_CORE_FUNCTIONAL_OK")
bad=d("root","software",version="latest",criticality="DC5",remote_mutable=True,third_party_trusted=False,provenance={},
assurance="UNKNOWN",local_control=False,rollbackable=False,strategic=True,substitutability="NONE")
gb=P014SupplyChainSovereignty([bad]); r=gb.sovereignty_gate()
assert not r["canonical_ready"] and any("CRITICAL_VERSION_NOT_PINNED" in x for x in r["blockers"])
assert not gb.admission("root")["admitted"] and gb.quarantine("root","drift")["execution_allowed"] is False
print("P014_CANONICAL_REBUILD_CORE_DEGRADATION_OK")
assert canonical_contract()["functional_only"] is True and canonical_contract()["phenomenology_undetermined"] is True
print("P014_CANONICAL_REBUILD_CORE_NON_REGRESSION_OK")

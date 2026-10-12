from pathlib import Path
import ast,pytest
from ontology.live_state_synchronizer import LiveStateSynchronizer
from ontology.distributed_attention_state_exchange import DistributedAttentionStateExchange
from ontology.distributed_identity_persistence_validator import DistributedIdentityPersistenceValidator

def test_pure(tmp_path):
 LiveStateSynchronizer(root=tmp_path); DistributedAttentionStateExchange(root=tmp_path); DistributedIdentityPersistenceValidator(root=tmp_path); assert list(tmp_path.iterdir())==[]
@pytest.mark.parametrize("c",[LiveStateSynchronizer,DistributedAttentionStateExchange,DistributedIdentityPersistenceValidator])
def test_closed(c,tmp_path):
 with pytest.raises(RuntimeError,match="governed_filesystem_context_required"): c(root=tmp_path).step({})
 assert list(tmp_path.iterdir())==[]
def test_no_direct_fs():
 r=Path(__file__).resolve().parents[1]/"ontology"; banned={"mkdir","open","write_text","write_bytes","unlink","replace","rename"}; hits=[]
 for name in ("live_state_synchronizer.py","distributed_attention_state_exchange.py","distributed_identity_persistence_validator.py"):
  t=ast.parse((r/name).read_text())
  hits += [(name,n.lineno,n.func.attr) for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in banned]
 assert hits==[]

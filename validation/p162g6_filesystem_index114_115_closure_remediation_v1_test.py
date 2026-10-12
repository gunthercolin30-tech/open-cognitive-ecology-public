from pathlib import Path
from types import SimpleNamespace
import ast,tempfile
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.residual_local_producer_router import ResidualLocalProducerRouter
import ontology.residual_local_producer_router as mod

class Broker:
    def __init__(self,ids): self.ids=set(ids); self.used=set()
    def consume_once(self,x):
        if x not in self.ids or x in self.used:return False
        self.used.add(x); return True
def H(i,op,b): return SimpleNamespace(handle_id=i,adapter_id="a",effector_id="e",operation_id=op,target_binding=b,ambient_authority=False,transferable=False,child_inheritance=False,single_use=True)
def binding(root,rel): return "filesystem://"+root+"/"+rel
def contexts(local,ssd,source,target,backup):
    sr=source.relative_to(local).as_posix(); tr=target.relative_to(ssd).as_posix(); br=backup.relative_to(local).as_posix()
    reg={"local":str(local),"ssd":str(ssd)}; broker=Broker({"mk","cp","mv","ln"}); eff=GovernedFilesystemEffector(root_registry=reg,handle_broker=broker)
    tc=GovernedFilesystemEffectContext(slots={
      "producer_target_create":[H("mk","FS_CREATE_DIRS",binding("ssd",tr))],
      "producer_merge_copy":[H("cp","FS_COPY_TREE_MERGE",{"source":binding("local",sr),"destination":binding("ssd",tr)})]},
      effector=eff,root_id="ssd",root_path=ssd,adapter_id="a",effector_id="e",source_root_id="local",source_root_path=local)
    lc=GovernedFilesystemEffectContext(slots={
      "producer_backup_move":[H("mv","FS_MOVE_PATH",{"source":binding("local",sr),"destination":binding("local",br)})],
      "producer_symlink_create":[H("ln","FS_CREATE_SYMLINK",{"source":binding("ssd",tr),"destination":binding("local",sr)})]},
      effector=eff,root_id="local",root_path=local,adapter_id="a",effector_id="e")
    tc.begin();lc.begin();return tc,lc

def test_real_directory_route_is_governed_and_preserves_data():
    with tempfile.TemporaryDirectory() as ld,tempfile.TemporaryDirectory() as sd:
        local=Path(ld);ssd=Path(sd);source=local/"metrics";(source/"sub").mkdir(parents=True);(source/"sub"/"x").write_bytes(b"abc")
        r=ResidualLocalProducerRouter(root=local,ssd_root=ssd);target=r._route_target("metrics");backup=local/"metrics.pre_f17_4_local_backup_TEST"
        tc,lc=contexts(local,ssd,source,target,backup)
        got=r._route_one("metrics",dry_run=False,target_fs_context=tc,local_fs_context=lc,backup_path=backup)
        assert got["status"]=="routed" and got["copied_count"]==1
        assert source.is_symlink() and source.resolve()==target.resolve()
        assert (target/"sub"/"x").read_bytes()==b"abc" and (backup/"sub"/"x").read_bytes()==b"abc"
        assert tc.remaining()=={"producer_target_create":0,"producer_merge_copy":0}
        assert lc.remaining()=={"producer_backup_move":0,"producer_symlink_create":0}
        assert not tc.authority_minting and not lc.authority_minting

def test_missing_context_fails_before_mutation():
    with tempfile.TemporaryDirectory() as ld,tempfile.TemporaryDirectory() as sd:
        local=Path(ld);ssd=Path(sd);source=local/"metrics";source.mkdir()
        r=ResidualLocalProducerRouter(root=local,ssd_root=ssd);target=r._route_target("metrics")
        try:r._route_one("metrics",dry_run=False,backup_path=local/"metrics.pre_f17_4_local_backup_X")
        except PermissionError:pass
        else:raise AssertionError("ambient mutation accepted")
        assert source.is_dir() and not source.is_symlink() and not target.exists()

def test_missing_backup_authorization_fails_before_mutation():
    with tempfile.TemporaryDirectory() as ld,tempfile.TemporaryDirectory() as sd:
        local=Path(ld);ssd=Path(sd);source=local/"metrics";source.mkdir();r=ResidualLocalProducerRouter(root=local,ssd_root=ssd);target=r._route_target("metrics")
        backup=local/"metrics.pre_f17_4_local_backup_X";tc,lc=contexts(local,ssd,source,target,backup)
        try:r._route_one("metrics",dry_run=False,target_fs_context=tc,local_fs_context=lc)
        except PermissionError:pass
        else:raise AssertionError("missing backup authorization accepted")
        assert not target.exists() and source.is_dir() and tc.remaining()["producer_target_create"]==1

def test_dry_run_needs_no_authority_and_mutates_nothing():
    with tempfile.TemporaryDirectory() as ld,tempfile.TemporaryDirectory() as sd:
        local=Path(ld);ssd=Path(sd);source=local/"metrics";source.mkdir();r=ResidualLocalProducerRouter(root=local,ssd_root=ssd);target=r._route_target("metrics")
        got=r._route_one("metrics",dry_run=True)
        assert got["status"]=="planned" and source.is_dir() and not target.exists()

def test_static_target_entrypoints_have_no_direct_mutators_and_step_transports_contexts():
    tree=ast.parse(Path(mod.__file__).read_text(encoding="utf-8"));cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="ResidualLocalProducerRouter")
    for name in ("_merge_copy","_route_one"):
        fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
        attrs=[n.func.attr for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
        assert not any(x in attrs for x in ("mkdir","copy2","rename","symlink_to"))
    route=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="_route_one")
    attrs=[n.func.attr for n in ast.walk(route) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert "execute_path" in attrs and "execute_dual_path" in attrs
    step=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="step")
    calls=[n for n in ast.walk(step) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="_route_one"]
    assert len(calls)==1
    kw={k.arg:k.value for k in calls[0].keywords}
    assert isinstance(kw["target_fs_context"],ast.Name) and kw["target_fs_context"].id=="target_fs_context"
    assert isinstance(kw["local_fs_context"],ast.Name) and kw["local_fs_context"].id=="local_fs_context"

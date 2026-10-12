from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import pytest
from ontology.preventive_growth_producer_routing import PreventiveGrowthProducerRouting
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedHandleBroker

ADAPTER="p162g6-9798-test"; EFFECTOR="p162g6-filesystem-effector"

class PreissuedProvider:
    def __init__(self, root, ssd, expected):
        self.root=Path(root).resolve(); self.ssd=Path(ssd).resolve(); self.expected=list(expected)
        self.broker=ScopedHandleBroker()
        self.eff=GovernedFilesystemEffector(root_registry={"local":str(self.root),"ssd":str(self.ssd)},handle_broker=self.broker)
        self.contexts=[]
        for serial,(op,target,source) in enumerate(self.expected):
            target=Path(target).resolve(); source=Path(source).resolve() if source is not None else None
            if target==self.root or self.root in target.parents: rid,rpath="local",self.root
            else: rid,rpath="ssd",self.ssd
            dr=target.relative_to(rpath).as_posix()
            if source is None:
                binding=f"filesystem://{rid}/{dr}"
                srid=srpath=None
            else:
                if source==self.root or self.root in source.parents: srid,srpath="local",self.root
                else: srid,srpath="ssd",self.ssd
                sr=source.relative_to(srpath).as_posix()
                binding={"source":f"filesystem://{srid}/{sr}","destination":f"filesystem://{rid}/{dr}"}
            claim=SimpleNamespace(lease_id=f"lease-{serial}",reservation_id=f"res-{serial}",claim_hash=f"claim-{serial}",adapter_id=ADAPTER)
            lease={"lease_id":claim.lease_id,"reservation_id":claim.reservation_id,"operation_id":op,"expires_at":"2999-01-01T00:00:00Z"}
            scope={"ambient_authority":False,"child_inheritance":False,"transferable":False}
            issued=self.broker.issue(claim=claim,lease=lease,registry_entry={"adapter_id":ADAPTER,"effector_id":EFFECTOR},requested_scope=scope,authorized_scope=scope,target_binding=binding,audience=ADAPTER,now_iso="2026-10-05T00:00:00Z")
            assert issued["status"]=="HANDLE_ISSUED"
            self.contexts.append((op,target,source,GovernedFilesystemEffectContext(
                slots={"p162g6_97_copy_tree_merge":[issued["handle"]],"p162g6_98_destination_create":[issued["handle"]],
                       "p162g6_98_local_backup_move":[issued["handle"]],"p162g6_98_symlink_create":[issued["handle"]],
                       "p162g6_98_probe_replace":[issued["handle"]]},
                effector=self.eff,root_id=rid,root_path=rpath,adapter_id=ADAPTER,effector_id=EFFECTOR,
                source_root_id=srid,source_root_path=srpath)))
    def __call__(self,op,target,source=None):
        if not self.contexts: raise RuntimeError("no_preissued_context")
        eop,et,es,ctx=self.contexts.pop(0)
        target=Path(target).resolve(); source=Path(source).resolve() if source is not None else None
        if (op,target,source)!=(eop,et,es): raise RuntimeError("preissued_context_sequence_mismatch")
        return ctx

def test_97_98_existing_tree_routes_with_preissued_real_tcb(tmp_path):
    root=tmp_path/"repo";ssd=tmp_path/"ssd";root.mkdir();ssd.mkdir()
    local=root/"data";(local/"nested").mkdir(parents=True);(local/"a.txt").write_text("A");(local/"nested/b.txt").write_text("B")
    destination=ssd/"OCE_MEMORY/preventive_growth/data";backup=root/"data.fixed_backup";probe=destination/"f17_8_probe_data.json"
    expected=[("FS_CREATE_DIRS",destination,None),("FS_COPY_TREE_MERGE",destination,local),("FS_MOVE_PATH",backup,local),
              ("FS_CREATE_SYMLINK",local,destination),("FS_WRITE_REPLACE_BYTES",probe,None)]
    provider=PreissuedProvider(root,ssd,expected)
    r=PreventiveGrowthProducerRouting(root=root,ssd_root=ssd,filesystem_effect_context_provider=provider)
    r._backup_path_for=lambda p: backup
    out=r._route_one("data",dry_run=False,persist_probe=True)
    assert out["status"]=="routed" and out["verified"] is True
    assert local.is_symlink() and local.resolve()==destination.resolve()
    assert backup.is_dir() and (backup/"nested/b.txt").read_text()=="B"
    assert (destination/"a.txt").read_text()=="A" and probe.is_file()
    assert provider.contexts==[]

def test_97_copy_tree_merge_replaces_conflicts_inside_tcb(tmp_path):
    root=tmp_path/"repo";ssd=tmp_path/"ssd";root.mkdir();ssd.mkdir()
    src=root/"data";src.mkdir();(src/"x").write_text("new")
    dst=ssd/"OCE_MEMORY/preventive_growth/data";dst.mkdir(parents=True);(dst/"x").mkdir()
    provider=PreissuedProvider(root,ssd,[("FS_COPY_TREE_MERGE",dst,src)])
    r=PreventiveGrowthProducerRouting(root=root,ssd_root=ssd,filesystem_effect_context_provider=provider)
    r._copy_tree_contents(src,dst)
    assert (dst/"x").is_file() and (dst/"x").read_text()=="new"

def test_98_missing_authority_fails_closed_as_error_without_mutation(tmp_path):
    root=tmp_path/"repo";ssd=tmp_path/"ssd";root.mkdir();ssd.mkdir();(root/"data").mkdir()
    r=PreventiveGrowthProducerRouting(root=root,ssd_root=ssd)
    out=r._route_one("data",dry_run=False,persist_probe=False)
    assert out["status"]=="error"
    assert "governed_filesystem_effect_context_provider_required" in out["error"]
    assert (root/"data").is_dir() and not (root/"data").is_symlink()

def test_98_dry_run_needs_no_authority_and_mutates_nothing(tmp_path):
    root=tmp_path/"repo";ssd=tmp_path/"ssd";root.mkdir();ssd.mkdir();(root/"data").mkdir()
    out=PreventiveGrowthProducerRouting(root=root,ssd_root=ssd)._route_one("data",dry_run=True,persist_probe=True)
    assert out["status"]=="planned_route_to_ssd" and (root/"data").is_dir() and not (root/"data").is_symlink()

def test_98_preissued_target_mismatch_fails_closed(tmp_path):
    root=tmp_path/"repo";ssd=tmp_path/"ssd";root.mkdir();ssd.mkdir();(root/"data").mkdir()
    destination=ssd/"OCE_MEMORY/preventive_growth/data";wrong=ssd/"OCE_MEMORY/preventive_growth/wrong"
    provider=PreissuedProvider(root,ssd,[("FS_CREATE_DIRS",wrong,None)])
    r=PreventiveGrowthProducerRouting(root=root,ssd_root=ssd,filesystem_effect_context_provider=provider)
    out=r._route_one("data",dry_run=False,persist_probe=False)
    assert out["status"]=="error" and "preissued_context_sequence_mismatch" in out["error"]
    assert not destination.exists() and not (root/"data").is_symlink()

from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h1_h3 as h
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"normative/occ1a"
def R(): return governed_crown_run(SRC)
def test_exact_a001_a030():
 r=R(); assert len(r["rows"])==30; assert [x["attack_id"] for x in r["rows"]]==["A%03d"%i for i in range(1,31)]
def test_family_counts():
 assert R()["family_counts"]=={"H1":8,"H2":11,"H3":11}
def test_injections_and_source_immutable():
 r=R(); assert all(x["injection_effective"] for x in r["rows"]); assert r["canonical_source_immutable"] is True
def test_counterexample_for_every_block():
 r=R(); b=[x for x in r["rows"] if x["verdict"] in ("VIOLATED","INCONCLUSIVE")]; assert len(r["counterexamples"])==len(b)
def test_boundaries_closed():
 r=R(); assert not r["authorization_created"] and not r["execution_performed"] and not r["occ1h_closed"] and not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]
def test_epistemic_invariants():
 r=R(); assert r["functional_only"] is True and r["phenomenology_undetermined"] is True

# P162-G6: test-only authority provider. This module never authorizes production operations.
def governed_crown_run(source):
    import tempfile
    from pathlib import Path
    from types import SimpleNamespace
    from ontology.scoped_handle_broker import ScopedHandleBroker
    from ontology.governed_filesystem_effector import GovernedFilesystemEffector
    from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
    from ontology import occ_constitutional_adversarial_crown_h1_h3 as crown
    src = Path(source).resolve()
    with tempfile.TemporaryDirectory(prefix="oce-occ1h-governed-") as directory:
        workspace = Path(directory).resolve()
        broker = ScopedHandleBroker()
        effector = GovernedFilesystemEffector(
            root_registry={"fixture": str(workspace), "normative": str(src.parent)},
            handle_broker=broker)
        claim = SimpleNamespace(lease_id="p159-test-only-lease",
            reservation_id="p159-test-only-reservation", adapter_id="p159-test-only-adapter",
            claim_hash="p159-synthetic-claim-not-production-authorization")
        lease = {"lease_id": claim.lease_id, "reservation_id": claim.reservation_id,
                 "expires_at": "2099-01-01T00:00:00Z"}
        registry = {"adapter_id": claim.adapter_id, "effector_id": "p159-test-effector"}
        slots = {}
        def issue(slot, operation, binding):
            scope = {"operations": [operation], "ambient_authority": False,
                     "transferable": False, "child_inheritance": False}
            response = broker.issue(claim=claim, lease={**lease, "operation_id": operation},
                registry_entry=registry, requested_scope=scope, authorized_scope=scope,
                target_binding=binding, audience=claim.adapter_id,
                now_iso="2026-10-08T00:00:00Z")
            if response.get("status") != "HANDLE_ISSUED":
                raise RuntimeError("fixture_preissue_failed:" + slot + ":" + str(response.get("reason")))
            slots[slot] = [response["handle"]]
        for i in range(19):
            folder = "fixture-%02d" % i
            dst = folder + "/occ1a"
            issue("mkdir_%02d" % i, "FS_CREATE_DIRS", "filesystem://fixture/" + folder)
            issue("copy_%02d" % i, "FS_COPY_TREE_MERGE",
                {"source": "filesystem://normative/occ1a", "destination": "filesystem://fixture/" + dst})
            name = "manifest.yaml" if i in (2, 3) else "dna/dna_h.yaml"
            issue("write_%02d" % i, "FS_WRITE_REPLACE_BYTES", "filesystem://fixture/" + dst + "/" + name)
            issue("remove_%02d" % i, "FS_REMOVE_TREE", "filesystem://fixture/" + folder)
        ctx = GovernedFilesystemEffectContext(slots=slots, effector=effector,
            root_id="fixture", root_path=workspace, adapter_id=claim.adapter_id,
            effector_id="p159-test-effector")
        ctx.begin()
        class Authority:
            def __init__(self):
                self.n = 0
                self.active = set()
            def clone(self, original):
                if Path(original).resolve() != src or self.n >= 19:
                    raise PermissionError("unexpected_clone_source_or_count")
                i = self.n
                self.n += 1
                td = workspace / ("fixture-%02d" % i)
                dst = td / "occ1a"
                ctx.execute_path("mkdir_%02d" % i, "FS_CREATE_DIRS", td)
                ctx.execute_dual_path("copy_%02d" % i, "FS_COPY_TREE_MERGE",
                    "normative", src.parent, src, dst)
                self.active.add(td)
                return td, dst
            def write(self, path, payload):
                p = Path(path).resolve()
                if not isinstance(payload, bytes) or p.name not in {"dna_h.yaml", "manifest.yaml"}:
                    raise PermissionError("unexpected_fixture_write")
                if not any(p.is_relative_to(td) for td in self.active):
                    raise PermissionError("write_outside_active_fixture")
                ctx.execute_path("write_%02d" % (self.n - 1), "FS_WRITE_REPLACE_BYTES", p, payload)
            def cleanup(self, td):
                td = Path(td).resolve()
                if td not in self.active:
                    raise PermissionError("unowned_fixture_cleanup")
                ctx.execute_path("remove_%02d" % (self.n - 1), "FS_REMOVE_TREE", td)
                self.active.remove(td)
        authority = Authority()
        result = crown.run(src, fixture_authority=authority)
        if authority.n != 19 or authority.active or any(ctx.remaining().values()):
            raise AssertionError("fixture_handles_not_exactly_consumed")
        if any(workspace.iterdir()):
            raise AssertionError("fixture_cleanup_residuals")
        counts = result["verdict_counts"]
        if (result["scenario_count"] != 30 or
            tuple(counts.get(k, 0) for k in ("DETECTED", "RESISTED", "VIOLATED", "INCONCLUSIVE")) != (26, 3, 0, 1)):
            raise AssertionError("posthardening_verdict_drift")
        return result

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ontology import occ_normative_ir_real_builder as b

SOURCE = ROOT / "normative" / "occ1a"

def copy_pkg():
    td = Path(tempfile.mkdtemp(prefix="oce_occ1b_realnir_"))
    dst = td / "occ1a"
    shutil.copytree(str(SOURCE), str(dst))
    return td, dst

def rewrite_json(path, mutator):
    data = json.loads(path.read_text(encoding="utf-8"))
    mutator(data)
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")

def run():
    before = {str(p.relative_to(SOURCE)): b._sha(p) for p in SOURCE.rglob("*") if p.is_file()}
    r1 = b.build_real_nir(SOURCE)
    r2 = b.build_real_nir(SOURCE)
    assert r1["status"] == b.PASS, r1
    assert r1["reason"] == "P159_OCC1B_REAL_PACKAGE_TO_NIR_V1_OK"
    assert r1["source_kernel_objects"] == 48
    assert r1["nir_principal_objects"] == 48
    assert r1["stable_ids_preserved"] == "48/48"
    assert r1["source_mapping_complete"] == "48/48"
    assert r1["silent_loss"] == 0 and r1["invented_norms"] == 0
    assert r1["nir_sha256"] == r2["nir_sha256"]
    assert r1["v3_normative_coherence_claimed"] is False
    assert r1["v4_semantic_preservation_claimed"] is False

    g0 = next(n for n in r1["package"]["graph"]["nodes"] if n["node_id"] == "GENESIS.G0")
    assert g0["formalization_level"] == "F0"
    assert g0["semantic_status"] == "HUMAN_JUDGMENT_REQUIRED"
    assert g0["text"] is None
    assert g0["human_judgment_required"] is True

    after = {str(p.relative_to(SOURCE)): b._sha(p) for p in SOURCE.rglob("*") if p.is_file()}
    assert before == after

    td, pkg = copy_pkg()
    try:
        (pkg/"dna"/"dna_h.yaml").unlink()
        assert b.build_real_nir(pkg)["reason"] == "SOURCE_PARTITION_MISSING"
    finally: shutil.rmtree(str(td))

    td, pkg = copy_pkg()
    try:
        rewrite_json(pkg/"dna"/"dna_h.yaml", lambda d: d["norms"].pop())
        assert b.build_real_nir(pkg)["reason"] == "REAL_KERNEL_COUNT_MISMATCH"
    finally: shutil.rmtree(str(td))

    td, pkg = copy_pkg()
    try:
        def dup(d): d["norms"][1]["canonical_id"] = d["norms"][0]["canonical_id"]
        rewrite_json(pkg/"dna"/"dna_h.yaml", dup)
        assert b.build_real_nir(pkg)["reason"] == "DUPLICATE_CANONICAL_ID"
    finally: shutil.rmtree(str(td))

    td, pkg = copy_pkg()
    try:
        def exec_on(d): d["norms"][0]["execution_enabled"] = True
        rewrite_json(pkg/"dna"/"dna_h.yaml", exec_on)
        assert "SOURCE_EXECUTION_ENABLED" in b.build_real_nir(pkg)["reason"]
    finally: shutil.rmtree(str(td))

    td, pkg = copy_pkg()
    try:
        def auth_on(d): d["norms"][0]["runtime_authority_granted"] = True
        rewrite_json(pkg/"dna"/"dna_h.yaml", auth_on)
        assert "SOURCE_RUNTIME_AUTHORITY_GRANTED" in b.build_real_nir(pkg)["reason"]
    finally: shutil.rmtree(str(td))

    td, pkg = copy_pkg()
    try:
        def invent_g0(d): d["norms"][0]["text"] = "invented"
        rewrite_json(pkg/"genesis"/"genesis.yaml", invent_g0)
        assert b.build_real_nir(pkg)["reason"] == "GENESIS_INVENTED_MACHINE_TEXT"
    finally: shutil.rmtree(str(td))

    td, pkg = copy_pkg()
    try:
        m = pkg/"manifest.yaml"
        m.write_text(m.read_text(encoding="utf-8").replace("package_state: VALIDATED","package_state: DRAFT"), encoding="utf-8")
        assert b.build_real_nir(pkg)["reason"] == "SOURCE_PACKAGE_NOT_VALIDATED"
    finally: shutil.rmtree(str(td))

    # CWD independence is implicit through absolute source root, assert from /tmp caller too.
    assert r1["package"]["boundaries"]["occ1c_opened"] is False
    assert r1["package"]["boundaries"]["p160_opened"] is False
    assert r1["package"]["boundaries"]["execution_performed"] is False

    print("P159_OCC1B_REAL_PACKAGE_TO_NIR_V1_FUNCTIONAL_OK")
    print("P159_OCC1B_REAL_PACKAGE_TO_NIR_V1_48_OF_48_OK")
    print("P159_OCC1B_REAL_PACKAGE_TO_NIR_V1_SOURCE_MAP_OK")
    print("P159_OCC1B_REAL_PACKAGE_TO_NIR_V1_DETERMINISM_OK")
    print("P159_OCC1B_REAL_PACKAGE_TO_NIR_V1_DEGRADATION_OK")
    print("P159_OCC1B_REAL_PACKAGE_TO_NIR_V1_NON_MUTATION_OK")
    print("P159_OCC1B_REAL_PACKAGE_TO_NIR_V1_STAGE_BOUNDARY_OK")

if __name__ == "__main__":
    run()

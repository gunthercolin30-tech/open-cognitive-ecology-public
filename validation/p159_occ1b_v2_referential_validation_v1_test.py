from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import shutil, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ontology import occ_normative_ir_referential_validator as v
from ontology import occ_normative_ir_real_builder as b

SOURCE = ROOT / "normative" / "occ1a"

def copy_pkg():
    td=Path(tempfile.mkdtemp(prefix="oce_occ1b_v2_")); dst=td/"occ1a"
    shutil.copytree(str(SOURCE),str(dst)); return td,dst

def rewrite(path, mutator):
    d=json.loads(path.read_text(encoding="utf-8")); mutator(d)
    path.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(",",":")),encoding="utf-8")

def run():
    before={str(p.relative_to(SOURCE)):b._sha(p) for p in SOURCE.rglob("*") if p.is_file()}
    r1=v.validate_real_nir_references(SOURCE)
    r2=v.validate_real_nir_references(SOURCE)
    assert r1["status"]==v.PASS, r1
    assert r1["reason"]=="P159_OCC1B_V2_REFERENTIAL_VALIDATION_OK"
    assert r1["canonical_object_count"]==48
    assert r1["source_map_resolved"]=="48/48"
    assert r1["broken_reference_count"]==0
    assert r1["report_sha256"]==r2["report_sha256"]
    assert r1["report"]["external_references_promoted_to_internal_nodes"] is False

    h9=[x for x in r1["report"]["references"] if x["owner"]=="DNA.H9" and x["resolution_domain"]=="EXTERNAL_NORMATIVE_SOURCE"]
    assert {x["target"] for x in h9}=={"F12","F17"}

    after={str(p.relative_to(SOURCE)):b._sha(p) for p in SOURCE.rglob("*") if p.is_file()}
    assert before==after

    td,pkg=copy_pkg()
    try:
        rewrite(pkg/"dna"/"dna_h.yaml", lambda d: d["norms"][0].update({"source_object_id":"F99"}))
        rr=v.validate_real_nir_references(pkg)
        assert rr["reason"]=="BROKEN_NORM_REFERENCE"
    finally: shutil.rmtree(str(td))

    td,pkg=copy_pkg()
    try:
        rewrite(pkg/"dna"/"dna_h.yaml", lambda d: d["norms"][0].update({"evidence_ids":[]}))
        rr=v.validate_real_nir_references(pkg)
        assert rr["reason"]=="BROKEN_NORM_REFERENCE"
    finally: shutil.rmtree(str(td))

    td,pkg=copy_pkg()
    try:
        def bad_lineage(d): d["norms"][0]["lineage_artifacts"][0]["sha256"]="00"
        rewrite(pkg/"dna"/"dna_h.yaml", bad_lineage)
        rr=v.validate_real_nir_references(pkg)
        assert rr["reason"]=="BROKEN_NORM_REFERENCE"
    finally: shutil.rmtree(str(td))

    td,pkg=copy_pkg()
    try:
        def collapse_h9(d):
            n=next(n for n in d["norms"] if n["canonical_id"]=="DNA.H9")
            n["source_object_id"]="F12"; n["evidence_ids"]=["F12"]
        rewrite(pkg/"dna"/"dna_h.yaml", collapse_h9)
        # Referential V2 alone cannot infer the missing F17 from altered source;
        # real builder preserves what source says. This is a V4 semantic-preservation
        # concern and therefore must not be falsely claimed here.
        rr=v.validate_real_nir_references(pkg)
        assert rr["status"]==v.PASS
        assert rr["v4_semantic_preservation_claimed"] is False
    finally: shutil.rmtree(str(td))

    assert r1["authority_activated"] is False
    assert r1["execution_performed"] is False
    assert r1["occ1c_opened"] is False and r1["p160_opened"] is False
    print("P159_OCC1B_V2_REFERENTIAL_FUNCTIONAL_OK")
    print("P159_OCC1B_V2_48_OF_48_SOURCE_MAP_OK")
    print("P159_OCC1B_V2_EXTERNAL_REFERENCE_TYPING_OK")
    print("P159_OCC1B_V2_BROKEN_NORM_REFERENCE_DEGRADATION_OK")
    print("P159_OCC1B_V2_DETERMINISM_OK")
    print("P159_OCC1B_V2_NON_MUTATION_OK")
    print("P159_OCC1B_V2_STAGE_BOUNDARY_OK")

if __name__=="__main__":
    run()

from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive
with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"r.txt").write_text("ok\n",encoding="utf-8")
    data={"operation":"archive_architecture","transaction_id":"T","archive_id":"A","architecture_id":"X","architecture_score":1.0,"selection_decision":{"selection_decision_ready":True,"decision":"accept"},"lineage_state":{"generation_status":"active"},"validation_summary":{"overall_success":True,"diagnostics":{"error_count":0}},"git_context":{"worktree_clean":True},"rollback_package":{"available":True},"module_inventory":["m"],"report_files":["r.txt"],"reproduction_command":"python3 test.py"}
    m=AceeBestArchitectureArchive(root=root); r=m.step(inputs=data,persist=True); assert r["archive_verified"]
    (Path(r["archive_path"])/"reports"/"r.txt").write_text("tampered\n",encoding="utf-8")
    v=m.step(inputs={"operation":"verify_archive","archive_id":"A"},persist=False); assert v["archive_verified"] is False and "archive_integrity_failure" in v["blocking_reasons"]
print("ACEE14_SHA256_INTEGRITY_OK")

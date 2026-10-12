from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive
with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"report.json").write_text('{"ok": true}\n',encoding="utf-8")
    ready={"operation":"archive_architecture","transaction_id":"T1","archive_id":"A1","architecture_id":"ARCH1","architecture_score":0.95,"selection_decision":{"selection_decision_ready":True,"decision":"accept","selection_id":"S1","decision_reasons":["best_validated"]},"lineage_state":{"generation_status":"active","lineage_id":"L1","generation_id":1},"validation_summary":{"overall_success":True,"diagnostics":{"error_count":0}},"git_context":{"commit":"abc","branch":"test","worktree_clean":True},"rollback_package":{"available":True},"module_inventory":["acee_lineage_manager"],"report_files":["report.json"],"reproduction_command":"python3 -m validation.main","timestamp_utc":"2026-07-13T23:10:00Z"}
    r=AceeBestArchitectureArchive(root=root).step(inputs=ready,persist=True)
    assert r["status"]=="ACEE_BEST_ARCHITECTURE_ARCHIVE_READY" and r["archive_created"] and r["archive_verified"]
    v=AceeBestArchitectureArchive(root=root).step(inputs={"operation":"verify_archive","archive_id":"A1"},persist=False)
    assert v["archive_verified"] is True
print("ACEE14_FAST_ACCEPTANCE_OK")

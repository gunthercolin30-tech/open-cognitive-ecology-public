from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive
def run(clean):
    with TemporaryDirectory() as tmp:
        root=Path(tmp); (root/"r.txt").write_text("ok\n",encoding="utf-8")
        d={"operation":"archive_architecture","transaction_id":"T","archive_id":"A","architecture_id":"X","architecture_score":1.0,"selection_decision":{"selection_decision_ready":True,"decision":"accept"},"lineage_state":{"generation_status":"active"},"validation_summary":{"overall_success":True,"diagnostics":{"error_count":0}},"git_context":{"worktree_clean":clean},"rollback_package":{"available":True},"module_inventory":["m"],"report_files":["r.txt"],"reproduction_command":"python3 test.py"}
        return AceeBestArchitectureArchive(root=root).step(inputs=d,persist=True)
assert run(True)["release_ready"] is True and run(False)["release_ready"] is False
print("ACEE14_GIT_CLEAN_DIRTY_OK")

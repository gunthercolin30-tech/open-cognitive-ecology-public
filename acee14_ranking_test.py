from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive
with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"r.txt").write_text("ok\n",encoding="utf-8"); m=AceeBestArchitectureArchive(root=root)
    for i,score in enumerate((0.8,0.95,0.9),1):
        d={"operation":"archive_architecture","transaction_id":f"T{i}","archive_id":f"A{i}","architecture_id":f"X{i}","architecture_score":score,"selection_decision":{"selection_decision_ready":True,"decision":"accept"},"lineage_state":{"generation_status":"active"},"validation_summary":{"overall_success":True,"diagnostics":{"error_count":0}},"git_context":{"worktree_clean":True},"rollback_package":{"available":True},"module_inventory":["m"],"report_files":["r.txt"],"reproduction_command":"python3 test.py"}
        m.step(inputs=d,persist=True)
    r=m.step(inputs={"operation":"list_best_architectures"},persist=False); assert r["best_archive_id"]=="A2" and [x["archive_id"] for x in r["archives"]]==["A2","A3","A1"]
print("ACEE14_RANKING_OK")

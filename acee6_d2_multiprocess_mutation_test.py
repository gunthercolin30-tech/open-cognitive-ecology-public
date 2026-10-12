import hashlib
import multiprocessing as mp
from pathlib import Path
from tempfile import TemporaryDirectory

from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import (
    AceeGovernedCodeGenerationGate,
)


CONTENT = "candidate\n"
CONTENT_HASH = hashlib.sha256(CONTENT.encode("utf-8")).hexdigest()


def worker(root_text, queue):
    from ontology.acee_installation_executor import AceeInstallationExecutor

    root = Path(root_text)
    decision = AceeGovernedCodeGenerationGate(root=root).step(
        inputs=valid_context(root, candidate_hash=CONTENT_HASH),
        persist=False,
    )
    result = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(
        inputs={
            "acee5_decision": decision,
            "admission_context": {
                "requested_stage": "ACEE6-D2",
                "candidate_content": CONTENT,
            },
        },
        persist=True,
    )
    queue.put({
        "status": result["status"],
        "state": result.get("transaction_state"),
        "written": result.get("candidate_written"),
    })


if __name__ == "__main__":
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ontology").mkdir()
        (root / "ontology" / "sample_candidate.py").write_text(
            "before\n",
            encoding="utf-8",
        )

        context = mp.get_context("spawn")
        queue = context.Queue()
        processes = [
            context.Process(target=worker, args=(str(root), queue))
            for _ in range(4)
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join(30)
            assert process.exitcode == 0

        results = [queue.get(timeout=5) for _ in processes]
        assert any(item["state"] == "MUTATED" for item in results)
        assert (root / "ontology" / "sample_candidate.py").read_text(
            encoding="utf-8"
        ) == CONTENT

    print("ACEE6_D2_MULTIPROCESS_MUTATION_OK")

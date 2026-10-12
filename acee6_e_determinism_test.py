from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_e_test_support import seed
from ontology.acee_installation_executor import AceeInstallationExecutor

outputs=[]
for _ in range(100):
    with TemporaryDirectory() as tmp:
        root=Path(tmp); seed(root)
        ex=AceeInstallationExecutor(root=root)
        outputs.append((
            ex._render_inventory_text(root/'ontology_inventory.txt','sample_candidate'),
            ex._render_inventory_python(root/'ontology_inventory.py','sample_candidate'),
            ex._render_dependency_registry(root/'dependency_registry.py','sample_candidate',['alpha','alpha']),
            ex._render_catalog_text(root/'global_module_catalog.txt','sample_candidate','ontology/sample_candidate.py'),
        ))
assert all(x==outputs[0] for x in outputs)
assert b"'alpha'" in outputs[0][2]
print('ACEE6_E_DETERMINISM_100_RENDERINGS_OK')

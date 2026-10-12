from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from ontology.acee_governed_code_generation_gate import AceeGovernedCodeGenerationGate
from acee5_hardening_test_support import valid_context
with TemporaryDirectory() as td:
    root=Path(td)
    with patch('subprocess.run', side_effect=AssertionError('execution forbidden')), patch('subprocess.Popen', side_effect=AssertionError('execution forbidden')), patch('shutil.copy', side_effect=AssertionError('copy forbidden')), patch('shutil.copy2', side_effect=AssertionError('copy forbidden')):
        r=AceeGovernedCodeGenerationGate(root=root).step(valid_context(root),persist=False)
    assert r['installation_authorized'] and all(r[k] is False for k in ('code_generated_by_gate','code_written_by_gate','code_compiled_by_gate','tests_executed_by_gate','code_installed_by_gate','validation_executed_by_gate','rollback_executed_by_gate'))
    assert not (root/'ontology/sample_candidate.py').exists()
print('ACEE5_ACEE6_BOUNDARY_OK')

from acee6_k5_transaction_runner import run
from acee6_k6_longitudinal_runner import run_reduced
assert run(False)['verification']['valid'];assert run_reduced(False)['verification']['valid'];print('ACEE6_K6_NON_REGRESSION_OK')

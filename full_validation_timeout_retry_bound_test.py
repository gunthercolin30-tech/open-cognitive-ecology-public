import os
from validation import full_validation_runner as runner

old = os.environ.get("OCE_FULL_TIMEOUT_RETRY_MULTIPLIER")
try:
    os.environ["OCE_FULL_TIMEOUT_RETRY_MULTIPLIER"] = "100"
    assert runner._timeout_retry_multiplier() == 3.0
    os.environ["OCE_FULL_TIMEOUT_RETRY_MULTIPLIER"] = "0"
    assert runner._timeout_retry_multiplier() == 1.0
finally:
    if old is None:
        os.environ.pop("OCE_FULL_TIMEOUT_RETRY_MULTIPLIER", None)
    else:
        os.environ["OCE_FULL_TIMEOUT_RETRY_MULTIPLIER"] = old
print("FULL_VALIDATION_TIMEOUT_RETRY_BOUND_OK")

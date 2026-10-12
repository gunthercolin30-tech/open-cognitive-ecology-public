from __future__ import annotations
import subprocess, sys
TESTS = [
"acee6_h_shell_and_argv_security_test.py",
"acee6_h_process_group_timeout_test.py",
"acee6_h_sigterm_sigkill_escalation_test.py",
"acee6_h_command_timeout_non_regression_test.py",
]
def main():
    for test in TESTS:
        subprocess.run([sys.executable, test], check=True)
    print("ACEE6_H_COMMAND_TIMEOUT_ALL_OK")
if __name__ == "__main__": main()

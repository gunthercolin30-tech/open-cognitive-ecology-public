from acee6_a_requirement_stage_coverage_test import main as a
from acee6_a_requirement_dependency_graph_test import main as b
from acee6_a_failure_state_completeness_test import main as c
from acee6_a_state_reachability_test import main as d
from acee6_a_terminal_output_contract_test import main as e
from acee6_a_acee6b_boundary_test import main as f
from acee6_a_public_api_snapshot_test import main as g
from acee6_a_report_code_consistency_test import main as h


def main():
    a(); b(); c(); d(); e(); f(); g(); h()
    print("ACEE6_A2_ARCHITECTURE_HARDENING_ALL_OK")


if __name__ == "__main__":
    main()

from acee6_a_contract_integrity_test import main as integrity_main
from acee6_a_contract_mutation_test import main as mutation_main
from acee6_a_schema_backward_compatibility_test import main as schema_main
from acee6_a_deterministic_serialization_test import main as deterministic_main
from acee6_a_contract_immutability_test import main as immutability_main
from acee6_a_empirical_traceability_test import main as traceability_main


def main():
    integrity_main()
    mutation_main()
    schema_main()
    deterministic_main()
    immutability_main()
    traceability_main()
    print("ACEE6_A3_FINAL_CONTRACT_VALIDATION_ALL_OK")


if __name__ == "__main__":
    main()

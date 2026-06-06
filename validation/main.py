from validation.integration_report import (
    build_report,
    save_report,
)


def main():

    integration_report = build_report(
        quick_validation=True
    )

    integration_report_path = save_report(
        integration_report
    )

    print(
        "validation_report_saved="
        + str(integration_report_path)
    )

    return integration_report


if __name__ == "__main__":
    results = main()

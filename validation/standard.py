from validation.quick import main as quick_main


def main():

    print(
        "Starting standard validation..."
    )

    summary = quick_main()

    print(
        "\nStandard validation completed."
    )

    return summary


if __name__ == "__main__":
    main()

from pathlib import Path
import csv

def load_constraints(csv_path=None):
    if csv_path is None:
        csv_path = Path("tableau C CQ.numbers.csv")
    path = Path(csv_path)
    if not path.exists():
        return []
    constraints = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            constraints.append(dict(row))
    return constraints

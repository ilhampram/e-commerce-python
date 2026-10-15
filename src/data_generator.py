"""Generate the checked-in sample transactions using only the standard library."""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

CATEGORIES = ["Electronics", "Home & Kitchen", "Fashion", "Beauty", "Sports"]
REGIONS = ["North", "South", "East", "West", "Central"]
CUSTOMER_TYPES = ["New", "Returning", "VIP"]


def generate(path: Path, rows: int = 300, seed: int = 42) -> None:
    random.seed(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    start = date(2024, 1, 1)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "product_category", "revenue", "units_sold", "region", "customer_type"])
        for _ in range(rows):
            units = random.randint(1, 8)
            price = random.uniform(12, 450)
            writer.writerow([
                (start + timedelta(days=random.randrange(730))).isoformat(),
                random.choice(CATEGORIES), round(price * units, 2), units,
                random.choice(REGIONS), random.choices(CUSTOMER_TYPES, weights=[35, 55, 10])[0],
            ])


if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "data" / "sample_data.csv")

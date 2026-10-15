"""Load, validate, and clean transaction data."""

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "date",
    "product_category",
    "revenue",
    "units_sold",
    "region",
    "customer_type",
}


def clean_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean data using the dashboard's required columns."""
    if not isinstance(frame, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Data is missing required columns: {', '.join(sorted(missing))}")

    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for column in ("revenue", "units_sold"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["date", "revenue", "units_sold"])
    frame = frame[(frame["revenue"] >= 0) & (frame["units_sold"] >= 0)]

    for column in ("product_category", "region", "customer_type"):
        frame[column] = frame[column].fillna("Unknown").astype(str).str.strip()
        frame.loc[frame[column] == "", column] = "Unknown"
    if frame.empty:
        raise ValueError("No valid transaction rows remain after cleaning.")
    frame["units_sold"] = frame["units_sold"].astype(int)
    frame["revenue"] = frame["revenue"].astype(float)
    return frame.reset_index(drop=True)


def load_data(path: str | Path) -> pd.DataFrame:
    """Read and clean a CSV file from disk."""
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Data file not found: {csv_path}")
    try:
        return clean_data(pd.read_csv(csv_path))
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not read CSV file {csv_path}: {exc}") from exc


def load_uploaded_data(uploaded_file: object) -> pd.DataFrame:
    """Load an uploaded CSV or Excel workbook and apply common validation."""
    name = str(getattr(uploaded_file, "name", "")).lower()
    try:
        uploaded_file.seek(0)
        frame = pd.read_excel(uploaded_file) if name.endswith(".xlsx") else pd.read_csv(uploaded_file)
    except (OSError, ValueError, TypeError, pd.errors.ParserError, ImportError) as exc:
        raise ValueError(f"Could not read uploaded file: {exc}") from exc
    return clean_data(frame)

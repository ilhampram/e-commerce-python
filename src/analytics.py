"""Small, reusable analytics operations for transaction data."""

import pandas as pd


def summarize(frame: pd.DataFrame) -> dict[str, float]:
    """Calculate dashboard KPIs; AOV is revenue per transaction row."""
    if frame.empty:
        return {"total_revenue": 0.0, "total_units_sold": 0, "average_order_value": 0.0}
    revenue = float(frame["revenue"].sum())
    return {
        "total_revenue": revenue,
        "total_units_sold": int(frame["units_sold"].sum()),
        "average_order_value": revenue / len(frame),
    }


def monthly_revenue(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue and units by calendar month."""
    if frame.empty:
        return pd.DataFrame(columns=["month", "revenue", "units_sold"])
    result = frame.set_index("date").resample("MS").agg(
        revenue=("revenue", "sum"), units_sold=("units_sold", "sum")
    )
    return result.rename_axis("month").reset_index()


def forecast_revenue(frame: pd.DataFrame, periods: int = 3) -> pd.DataFrame:
    """Fit a tiny linear trend to monthly totals and return non-negative projections."""
    from sklearn.linear_model import LinearRegression
    import numpy as np

    history = monthly_revenue(frame)
    if len(history) < 2:
        return pd.DataFrame(columns=["month", "revenue"])
    x = np.arange(len(history)).reshape(-1, 1)
    model = LinearRegression().fit(x, history["revenue"].to_numpy())
    future_x = np.arange(len(history), len(history) + periods).reshape(-1, 1)
    future_months = pd.date_range(history["month"].iloc[-1] + pd.offsets.MonthBegin(), periods=periods, freq="MS")
    return pd.DataFrame({"month": future_months, "revenue": model.predict(future_x).clip(min=0)})

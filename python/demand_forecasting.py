from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def forecast_demand():
    sales = pd.read_csv(DATA_DIR / "sales.csv")
    products = pd.read_csv(DATA_DIR / "products.csv")

    sales["sale_date"] = pd.to_datetime(sales["sale_date"])
    sales = sales.merge(products[["product_id", "category"]], on="product_id", how="left")

    daily_category = (
        sales.groupby(["sale_date", "category"], as_index=False)["quantity"]
        .sum()
        .rename(columns={"quantity": "units_sold"})
    )

    daily_category = daily_category.sort_values(["category", "sale_date"]).copy()
    daily_category["rolling_7d"] = (
        daily_category.groupby("category")["units_sold"]
        .transform(lambda s: s.rolling(window=7, min_periods=1).mean())
    )

    daily_category["seasonal_index"] = (
        daily_category.groupby(["category", daily_category["sale_date"].dt.month_name()])["units_sold"]
        .transform("mean")
        / daily_category.groupby("category")["units_sold"].transform("mean")
    )

    recent_trend = (
        daily_category.sort_values(["category", "sale_date"])
        .groupby("category", as_index=False)
        .tail(7)
        .groupby("category", as_index=False)["units_sold"]
        .mean()
        .rename(columns={"units_sold": "avg_units_last_7d"})
    )

    print("\nForecast summary by category (next 7 days):")
    for _, row in recent_trend.iterrows():
        category = row["category"]
        avg_units = row["avg_units_last_7d"]
        forecast = max(0.0, avg_units * 1.05)
        print(f"{category}: ~{forecast:.1f} units/day estimated")

    print("\nLatest category demand snapshots:")
    print(daily_category.sort_values(["category", "sale_date"]).tail(10).to_string(index=False))


if __name__ == "__main__":
    forecast_demand()

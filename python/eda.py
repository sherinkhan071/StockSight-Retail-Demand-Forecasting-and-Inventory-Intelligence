from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def load_data():
    products = pd.read_csv(DATA_DIR / "products.csv")
    sales = pd.read_csv(DATA_DIR / "sales.csv")
    inventory = pd.read_csv(DATA_DIR / "inventory.csv")
    stores = pd.read_csv(DATA_DIR / "stores.csv")
    promotions = pd.read_csv(DATA_DIR / "promotions.csv")
    return products, sales, inventory, stores, promotions


def score_inventory(products, sales, inventory, stores):
    sales["sale_date"] = pd.to_datetime(sales["sale_date"])
    inventory["inventory_date"] = pd.to_datetime(inventory["inventory_date"])

    daily_sales = (
        sales.groupby(["product_id", "sale_date"], as_index=False)["quantity"]
        .sum()
        .rename(columns={"quantity": "daily_units_sold"})
    )

    product_demand = (
        daily_sales.groupby("product_id", as_index=False)["daily_units_sold"]
        .mean()
        .rename(columns={"daily_units_sold": "avg_daily_units"})
    )

    inventory_summary = (
        inventory.groupby("product_id", as_index=False)
        .agg(
            avg_closing_stock=("closing_stock", "mean"),
            total_units_sold=("sold_quantity", "sum"),
            stockout_days=("closing_stock", lambda s: (s <= 0).sum()),
            avg_stock_received=("received_quantity", "mean"),
        )
    )

    product_health = product_demand.merge(inventory_summary, on="product_id", how="outer")
    product_health = product_health.merge(products[["product_id", "category", "lead_time_days", "selling_price"]], on="product_id", how="left")

    product_health["avg_daily_units"] = product_health["avg_daily_units"].fillna(0)
    product_health["avg_closing_stock"] = product_health["avg_closing_stock"].fillna(0)
    product_health["lead_time_demand"] = product_health["avg_daily_units"] * product_health["lead_time_days"]
    product_health["stockout_risk"] = (
        product_health["stockout_days"] / (product_health["stockout_days"] + 1)
    )
    product_health["overstock_risk"] = (
        (product_health["avg_closing_stock"] - product_health["lead_time_demand"]) / (product_health["lead_time_demand"] + 1)
    )

    product_health["risk_label"] = product_health.apply(
        lambda row: (
            "Stockout Risk"
            if row["avg_closing_stock"] < max(1, row["lead_time_demand"])
            else "Overstock Risk"
            if row["avg_closing_stock"] > max(2, row["lead_time_demand"] * 2)
            else "Balanced"
        ),
        axis=1,
    )

    return product_health


def analyze_retail_business(products, sales, inventory, stores, promotions):
    total_revenue = sales["revenue"].sum()
    total_units = sales["quantity"].sum()
    avg_inventory = inventory["closing_stock"].mean()
    stockout_rows = (inventory["closing_stock"] <= 0).sum()
    stockout_rate = stockout_rows / len(inventory)

    overstock_threshold = inventory["closing_stock"].quantile(0.75)
    overstock_rows = (inventory["closing_stock"] > overstock_threshold).sum()
    overstock_rate = overstock_rows / len(inventory)

    promotion_sales = promotions.merge(sales, on=["product_id", "store_id"], how="left")
    promotion_revenue = promotion_sales["revenue"].sum()

    best_category = (
        sales.merge(products[["product_id", "category"]], on="product_id")
        .groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .head(1)
    )

    print("\n=== Retail Demand and Inventory Intelligence ===")
    print(f"Total revenue: ${total_revenue:,.2f}")
    print(f"Total units sold: {total_units:,}")
    print(f"Average closing stock: {avg_inventory:,.2f} units")
    print(f"Stockout rate: {stockout_rate:.2%}")
    print(f"Overstock rate: {overstock_rate:.2%}")
    print(f"Promotion-driven revenue: ${promotion_revenue:,.2f}")
    print(f"Top revenue category: {best_category.iloc[0]['category']} (${best_category.iloc[0]['revenue']:,.2f})")

    print("\nPriority actions:")
    if stockout_rate > 0.05:
        print("- Increase safety stock on high-velocity products; stockout risk is elevated.")
    else:
        print("- Service level is healthy; maintain current safety stock for key SKUs.")

    if overstock_rate > 0.10:
        print("- Reduce slow-turn inventory and rebalance stock to high-demand categories.")
    else:
        print("- Inventory is moderately balanced; continue monitoring seasonal shifts.")

    print("- Review lead times and replenishment timing for products with long supplier delay.")

    product_health = score_inventory(products, sales, inventory, stores)
    print("\nTop inventory risk items:")
    print(
        product_health.sort_values(["avg_closing_stock", "lead_time_demand"], ascending=[True, False]).head(10)[
            ["product_id", "category", "avg_daily_units", "avg_closing_stock", "lead_time_demand", "risk_label"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    products, sales, inventory, stores, promotions = load_data()
    analyze_retail_business(products, sales, inventory, stores, promotions)

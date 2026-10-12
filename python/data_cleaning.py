from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)


def clean_and_save():
    products = pd.read_csv(DATA_DIR / "products.csv")
    sales = pd.read_csv(DATA_DIR / "sales.csv")
    inventory = pd.read_csv(DATA_DIR / "inventory.csv")
    promotions = pd.read_csv(DATA_DIR / "promotions.csv")
    stores = pd.read_csv(DATA_DIR / "stores.csv")

    for df in [products, sales, inventory, promotions, stores]:
        df.columns = [str(col).strip().lower() for col in df.columns]

    products["product_name"] = products["product_name"].astype(str).str.strip()
    products["category"] = products["category"].astype(str).str.strip()
    stores["store_name"] = stores["store_name"].astype(str).str.strip()
    stores["city"] = stores["city"].astype(str).str.strip()

    sales["sale_date"] = pd.to_datetime(sales["sale_date"], errors="coerce")
    inventory["inventory_date"] = pd.to_datetime(inventory["inventory_date"], errors="coerce")
    promotions["start_date"] = pd.to_datetime(promotions["start_date"], errors="coerce")
    promotions["end_date"] = pd.to_datetime(promotions["end_date"], errors="coerce")

    sales = sales.dropna(subset=["sale_date", "product_id", "store_id"])
    inventory = inventory.dropna(subset=["inventory_date", "product_id", "store_id"])
    promotions = promotions.dropna(subset=["start_date", "end_date", "product_id", "store_id"])

    sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce").fillna(0)
    sales["revenue"] = pd.to_numeric(sales["revenue"], errors="coerce").fillna(0)
    inventory["opening_stock"] = pd.to_numeric(inventory["opening_stock"], errors="coerce").fillna(0)
    inventory["received_quantity"] = pd.to_numeric(inventory["received_quantity"], errors="coerce").fillna(0)
    inventory["sold_quantity"] = pd.to_numeric(inventory["sold_quantity"], errors="coerce").fillna(0)
    inventory["closing_stock"] = pd.to_numeric(inventory["closing_stock"], errors="coerce").fillna(0)

    sales = sales[(sales["quantity"] >= 0) & (sales["revenue"] >= 0)]
    inventory = inventory[(inventory["opening_stock"] >= 0) & (inventory["received_quantity"] >= 0) & (inventory["sold_quantity"] >= 0) & (inventory["closing_stock"] >= 0)]

    products.to_csv(PROCESSED_DIR / "products_clean.csv", index=False)
    stores.to_csv(PROCESSED_DIR / "stores_clean.csv", index=False)
    sales.to_csv(PROCESSED_DIR / "sales_clean.csv", index=False)
    inventory.to_csv(PROCESSED_DIR / "inventory_clean.csv", index=False)
    promotions.to_csv(PROCESSED_DIR / "promotions_clean.csv", index=False)

    print("Cleaned data saved to data/processed/")
    print(f"Products: {len(products)}")
    print(f"Stores: {len(stores)}")
    print(f"Sales: {len(sales)}")
    print(f"Inventory: {len(inventory)}")
    print(f"Promotions: {len(promotions)}")


if __name__ == "__main__":
    clean_and_save()

import pandas as pd
import numpy as np

# -----------------------------
# SETTINGS
# -----------------------------

np.random.seed(42)

NUM_PRODUCTS = 500
NUM_STORES = 50


# -----------------------------
# PRODUCT DATA
# -----------------------------

categories = {
    "Electronics": [
        "Wireless Mouse",
        "Mechanical Keyboard",
        "USB-C Cable",
        "Bluetooth Speaker",
        "Headphones",
        "Webcam",
        "Power Bank",
        "Smart Watch"
    ],

    "Fashion": [
        "Running Shoes",
        "Cotton T-Shirt",
        "Jeans",
        "Hoodie",
        "Jacket",
        "Sneakers",
        "Backpack",
        "Cap"
    ],

    "Home Appliances": [
        "Coffee Maker",
        "Mixer Grinder",
        "Electric Kettle",
        "Air Fryer",
        "Toaster",
        "Vacuum Cleaner"
    ],

    "Home & Living": [
        "Water Bottle",
        "Desk Lamp",
        "Bedsheet",
        "Pillow",
        "Curtains",
        "Storage Box"
    ]
}

brands = [
    "Philips",
    "Samsung",
    "Sony",
    "LG",
    "Nike",
    "Adidas",
    "Puma",
    "Logitech",
    "JBL",
    "Portronics",
    "Milton",
    "American Tourister"
]

subcategories = {
    "Electronics": "Electronics Accessories",
    "Fashion": "Fashion & Apparel",
    "Home Appliances": "Kitchen Appliances",
    "Home & Living": "Home Products"
}

products = []

for product_id in range(1, NUM_PRODUCTS + 1):

    category = np.random.choice(list(categories.keys()))

    product_name = np.random.choice(categories[category])

    brand = np.random.choice(brands)

    unit_cost = round(np.random.uniform(200, 5000), 2)

    selling_price = round(
        unit_cost * np.random.uniform(1.3, 2.2),
        2
    )

    supplier_id = np.random.randint(1001, 1051)

    lead_time_days = np.random.randint(3, 15)

    products.append([
        product_id,
        f"{brand} {product_name} {product_id}",
        category,
        subcategories[category],
        brand,
        unit_cost,
        selling_price,
        supplier_id,
        lead_time_days
    ])


products_df = pd.DataFrame(
    products,
    columns=[
        "product_id",
        "product_name",
        "category",
        "subcategory",
        "brand",
        "unit_cost",
        "selling_price",
        "supplier_id",
        "lead_time_days"
    ]
)


# -----------------------------
# STORE DATA
# -----------------------------

cities = [
    ("Delhi", "Delhi", "North"),
    ("Mumbai", "Maharashtra", "West"),
    ("Pune", "Maharashtra", "West"),
    ("Bangalore", "Karnataka", "South"),
    ("Hyderabad", "Telangana", "South"),
    ("Chennai", "Tamil Nadu", "South"),
    ("Kolkata", "West Bengal", "East"),
    ("Ahmedabad", "Gujarat", "West"),
    ("Jaipur", "Rajasthan", "North"),
    ("Lucknow", "Uttar Pradesh", "North")
]

stores = []

for store_id in range(101, 101 + NUM_STORES):

    city, state, region = cities[
        np.random.randint(0, len(cities))
    ]

    store_type = np.random.choice(
        ["Large", "Medium", "Small"],
        p=[0.30, 0.45, 0.25]
    )

    stores.append([
        store_id,
        f"{city} Store {store_id}",
        city,
        state,
        region,
        store_type
    ])


stores_df = pd.DataFrame(
    stores,
    columns=[
        "store_id",
        "store_name",
        "city",
        "state",
        "region",
        "store_type"
    ]
)


# -----------------------------
# SAVE DATA
# -----------------------------

products_df.to_csv(
    "data/products.csv",
    index=False
)

stores_df.to_csv(
    "data/stores.csv",
    index=False
)

# -----------------------------
# DISPLAY RESULTS
# -----------------------------

print("================================")
print("StockSight Data Generation")
print("================================")

print(f"Products generated: {len(products_df)}")
print(f"Stores generated: {len(stores_df)}")

print("\nProduct sample:")
print(products_df.head())

print("\nStore sample:")
print(stores_df.head())

print("\nFiles created successfully!")
# -----------------------------
# SALES DATA
# -----------------------------

print("\nGenerating sales data...")

start_date = "2024-01-01"
end_date = "2025-12-31"

dates = pd.date_range(
    start=start_date,
    end=end_date,
    freq="D"
)

sales_records = []

sale_id = 1

for date in dates:

    # Select products sold that day
    daily_products = np.random.choice(
        products_df["product_id"],
        size=np.random.randint(80, 180),
        replace=False
    )

    for product_id in daily_products:

        # Select a store
        store = stores_df.sample(1).iloc[0]

        store_id = store["store_id"]

        # Base demand
        base_demand = np.random.randint(1, 8)

        # Large stores sell more
        if store["store_type"] == "Large":
            store_multiplier = 1.5
        elif store["store_type"] == "Medium":
            store_multiplier = 1.0
        else:
            store_multiplier = 0.7

        # Weekend effect
        if date.dayofweek >= 5:
            weekend_multiplier = 1.25
        else:
            weekend_multiplier = 1.0

        # Seasonal effect
        if date.month in [10, 11, 12]:
            seasonal_multiplier = 1.30
        elif date.month in [4, 5, 6]:
            seasonal_multiplier = 1.10
        else:
            seasonal_multiplier = 1.0

        quantity = max(
            1,
            int(
                base_demand
                * store_multiplier
                * weekend_multiplier
                * seasonal_multiplier
                * np.random.uniform(0.7, 1.3)
            )
        )

        product = products_df[
            products_df["product_id"] == product_id
        ].iloc[0]

        unit_price = product["selling_price"]

        # Random discount
        discount = np.random.choice(
            [0, 0.05, 0.10, 0.15],
            p=[0.55, 0.20, 0.20, 0.05]
        )

        revenue = round(
            quantity
            * unit_price
            * (1 - discount),
            2
        )

        sales_records.append([
            sale_id,
            date,
            store_id,
            product_id,
            quantity,
            unit_price,
            discount,
            revenue
        ])

        sale_id += 1


sales_df = pd.DataFrame(
    sales_records,
    columns=[
        "sale_id",
        "sale_date",
        "store_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount",
        "revenue"
    ]
)


# -----------------------------
# SAVE SALES DATA
# -----------------------------

sales_df.to_csv(
    "data/sales.csv",
    index=False
)


print(f"Sales records generated: {len(sales_df):,}")

print("\nSales sample:")
print(sales_df.head())

print("\nSales data saved successfully!")

# -----------------------------
# INVENTORY DATA
# -----------------------------

print("\nGenerating inventory data...")

# Load generated sales
sales_df = pd.read_csv("data/sales.csv")

# Aggregate sales by date, store and product
daily_sales = (
    sales_df
    .groupby(
        ["sale_date", "store_id", "product_id"],
        as_index=False
    )["quantity"]
    .sum()
    .rename(columns={"quantity": "sold_quantity"})
)

inventory_records = []

inventory_id = 1

for _, row in daily_sales.iterrows():

    sold_quantity = int(row["sold_quantity"])

    # Create enough opening stock to support demand
    opening_stock = np.random.randint(
        max(20, sold_quantity * 3),
        max(50, sold_quantity * 8)
    )

    # Replenishment happens when stock is relatively low
    if opening_stock < sold_quantity * 4:
        received_quantity = np.random.randint(20, 80)
    else:
        received_quantity = np.random.choice(
            [0, 20, 40],
            p=[0.70, 0.20, 0.10]
        )

    closing_stock = (
        opening_stock
        + received_quantity
        - sold_quantity
    )

    inventory_records.append([
        inventory_id,
        row["sale_date"],
        row["store_id"],
        row["product_id"],
        opening_stock,
        received_quantity,
        sold_quantity,
        closing_stock
    ])

    inventory_id += 1


inventory_df = pd.DataFrame(
    inventory_records,
    columns=[
        "inventory_id",
        "inventory_date",
        "store_id",
        "product_id",
        "opening_stock",
        "received_quantity",
        "sold_quantity",
        "closing_stock"
    ]
)


# -----------------------------
# SAVE INVENTORY DATA
# -----------------------------

inventory_df.to_csv(
    "data/inventory.csv",
    index=False
)

print(
    f"Inventory records generated: "
    f"{len(inventory_df):,}"
)

print("\nInventory sample:")
print(inventory_df.head())

print("\nInventory data saved successfully!")

# -----------------------------
# PROMOTIONS DATA
# -----------------------------

print("\nGenerating promotions data...")

promotion_records = []

NUM_PROMOTIONS = 1000

for promotion_id in range(1, NUM_PROMOTIONS + 1):

    product_id = np.random.randint(
        1,
        NUM_PRODUCTS + 1
    )

    store_id = np.random.randint(
        101,
        101 + NUM_STORES
    )

    promotion_start = pd.Timestamp(
        np.random.choice(
            pd.date_range(
                start="2024-01-01",
                end="2025-11-30",
                freq="D"
            )
        )
    )

    duration = np.random.randint(3, 15)

    promotion_end = (
        promotion_start
        + pd.Timedelta(days=duration)
    )

    discount_percentage = np.random.choice(
        [5, 10, 15, 20, 25, 30],
        p=[0.15, 0.25, 0.25, 0.20, 0.10, 0.05]
    )

    promotion_type = np.random.choice(
        [
            "Festival Sale",
            "Weekend Sale",
            "Clearance Sale",
            "Member Discount",
            "Seasonal Sale"
        ]
    )

    promotion_records.append([
        promotion_id,
        product_id,
        store_id,
        promotion_start,
        promotion_end,
        discount_percentage,
        promotion_type
    ])


promotions_df = pd.DataFrame(
    promotion_records,
    columns=[
        "promotion_id",
        "product_id",
        "store_id",
        "start_date",
        "end_date",
        "discount_percentage",
        "promotion_type"
    ]
)


# -----------------------------
# SAVE PROMOTIONS
# -----------------------------

promotions_df.to_csv(
    "data/promotions.csv",
    index=False
)

print(
    f"Promotions generated: "
    f"{len(promotions_df):,}"
)

print("\nPromotion sample:")
print(promotions_df.head())

print("\nPromotions data saved successfully!")
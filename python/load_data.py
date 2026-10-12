import pandas as pd
import psycopg

# Connect to PostgreSQL
conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="StockSight",
    user="postgres",
    password=input("Enter PostgreSQL password: ")
)

print("Connected to PostgreSQL!")

# Load only the remaining CSV files
inventory = pd.read_csv("data/inventory.csv")
promotions = pd.read_csv("data/promotions.csv")

print("Inventory and promotions CSV files loaded!")

# Insert inventory
with conn.cursor() as cur:
    for _, row in inventory.iterrows():
        cur.execute(
            """
            INSERT INTO analytics.inventory
            (
                inventory_id,
                inventory_date,
                store_id,
                product_id,
                opening_stock,
                received_quantity,
                sold_quantity,
                closing_stock
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            tuple(row)
        )

conn.commit()
print("Inventory inserted!")

# Insert promotions
with conn.cursor() as cur:
    for _, row in promotions.iterrows():
        cur.execute(
            """
            INSERT INTO analytics.promotions
            (
                promotion_id,
                product_id,
                store_id,
                start_date,
                end_date,
                discount_percentage,
                promotion_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            tuple(row)
        )

conn.commit()
print("Promotions inserted!")

conn.close()

print("All remaining data loaded successfully!")
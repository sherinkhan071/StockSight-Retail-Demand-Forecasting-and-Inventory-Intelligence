CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.products (
    product_id INT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    subcategory TEXT,
    brand TEXT,
    unit_cost NUMERIC(12,2),
    selling_price NUMERIC(12,2),
    supplier_id INT,
    lead_time_days INT
);

CREATE TABLE IF NOT EXISTS analytics.stores (
    store_id INT PRIMARY KEY,
    store_name TEXT,
    city TEXT,
    state TEXT,
    region TEXT,
    store_type TEXT
);

CREATE TABLE IF NOT EXISTS analytics.sales (
    sale_id BIGINT PRIMARY KEY,
    sale_date DATE,
    store_id INT,
    product_id INT,
    quantity INT,
    unit_price NUMERIC(12,2),
    discount NUMERIC(5,2),
    revenue NUMERIC(14,2)
);

CREATE TABLE IF NOT EXISTS analytics.inventory (
    inventory_id BIGINT PRIMARY KEY,
    inventory_date DATE,
    store_id INT,
    product_id INT,
    opening_stock INT,
    received_quantity INT,
    sold_quantity INT,
    closing_stock INT
);

CREATE TABLE IF NOT EXISTS analytics.promotions (
    promotion_id BIGINT PRIMARY KEY,
    product_id INT,
    store_id INT,
    start_date DATE,
    end_date DATE,
    discount_percentage INT,
    promotion_type TEXT
);

CREATE INDEX IF NOT EXISTS idx_sales_date ON analytics.sales (sale_date);
CREATE INDEX IF NOT EXISTS idx_inventory_date ON analytics.inventory (inventory_date);
CREATE INDEX IF NOT EXISTS idx_sales_product ON analytics.sales (product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON analytics.inventory (product_id);

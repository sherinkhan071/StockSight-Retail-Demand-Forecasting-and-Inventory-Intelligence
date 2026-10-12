-- 1. Identify stockout days and risky SKUs
SELECT
    p.product_id,
    p.product_name,
    SUM(CASE WHEN i.closing_stock <= 0 THEN 1 ELSE 0 END) AS stockout_days,
    AVG(i.closing_stock) AS avg_closing_stock,
    SUM(i.sold_quantity) AS units_sold
FROM analytics.inventory i
JOIN analytics.products p ON p.product_id = i.product_id
GROUP BY p.product_id, p.product_name
HAVING SUM(CASE WHEN i.closing_stock <= 0 THEN 1 ELSE 0 END) > 0
ORDER BY stockout_days DESC;

-- 2. Identify overstocked products by inventory coverage
SELECT
    p.product_id,
    p.product_name,
    AVG(i.closing_stock) AS avg_closing_stock,
    SUM(i.sold_quantity) AS total_units_sold,
    AVG(i.closing_stock) / NULLIF(SUM(i.sold_quantity), 0) AS coverage_ratio
FROM analytics.inventory i
JOIN analytics.products p ON p.product_id = i.product_id
GROUP BY p.product_id, p.product_name
HAVING AVG(i.closing_stock) > 0
ORDER BY coverage_ratio DESC
LIMIT 20;

-- 3. Store-level stockout risk
SELECT
    s.store_id,
    s.store_name,
    s.city,
    s.region,
    COUNT(CASE WHEN i.closing_stock <= 0 THEN 1 END) AS stockout_days,
    AVG(i.closing_stock) AS avg_closing_stock
FROM analytics.inventory i
JOIN analytics.stores s ON s.store_id = i.store_id
GROUP BY s.store_id, s.store_name, s.city, s.region
ORDER BY stockout_days DESC;

-- 4. Demand trend by category for planning
SELECT
    p.category,
    DATE_TRUNC('month', s.sale_date) AS month,
    SUM(s.quantity) AS units_sold,
    ROUND(AVG(s.quantity), 2) AS avg_daily_units
FROM analytics.sales s
JOIN analytics.products p ON p.product_id = s.product_id
GROUP BY p.category, DATE_TRUNC('month', s.sale_date)
ORDER BY p.category, month;

-- 5. Promotion impact on sales
SELECT
    pr.promotion_type,
    AVG(s.quantity) AS avg_units_sold,
    SUM(s.revenue) AS total_revenue,
    COUNT(*) AS sales_events
FROM analytics.promotions pr
LEFT JOIN analytics.sales s
    ON s.product_id = pr.product_id
   AND s.store_id = pr.store_id
   AND s.sale_date BETWEEN pr.start_date AND pr.end_date
GROUP BY pr.promotion_type
ORDER BY total_revenue DESC;

-- 6. Replenishment priority list
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.lead_time_days,
    AVG(i.closing_stock) AS avg_stock,
    SUM(s.quantity) AS units_sold_last_30_days,
    ROUND(SUM(s.quantity) / 30.0, 2) AS avg_daily_demand,
    p.lead_time_days * ROUND(SUM(s.quantity) / 30.0, 2) AS lead_time_demand
FROM analytics.products p
LEFT JOIN analytics.inventory i ON i.product_id = p.product_id
LEFT JOIN analytics.sales s ON s.product_id = p.product_id
    AND s.sale_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.product_id, p.product_name, p.category, p.lead_time_days
ORDER BY units_sold_last_30_days DESC;

-- =========================================================
-- Retail Sales Analysis — SQL Queries
-- Tables: regions, stores, products, customers, sales
-- Engine: SQLite (syntax is standard ANSI SQL, portable to
--          Postgres/MySQL with minor date-function tweaks)
-- =========================================================

-- ---------------------------------------------------------
-- 1. Top 10 best-selling products by total revenue
-- ---------------------------------------------------------
SELECT
    p.product_name,
    p.category,
    SUM(s.quantity)                AS units_sold,
    ROUND(SUM(s.revenue), 2)       AS total_revenue
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;


-- ---------------------------------------------------------
-- 2. Revenue and order count by region
-- ---------------------------------------------------------
SELECT
    r.region_name,
    COUNT(DISTINCT s.sale_id)      AS total_orders,
    ROUND(SUM(s.revenue), 2)       AS total_revenue,
    ROUND(AVG(s.revenue), 2)       AS avg_order_value
FROM sales s
JOIN stores st  ON st.store_id = s.store_id
JOIN regions r  ON r.region_id = st.region_id
GROUP BY r.region_name
ORDER BY total_revenue DESC;


-- ---------------------------------------------------------
-- 3. Monthly revenue trend with month-over-month growth %
--    (window function: LAG)
-- ---------------------------------------------------------
WITH monthly AS (
    SELECT
        strftime('%Y-%m', sale_date) AS month,
        ROUND(SUM(revenue), 2)       AS monthly_revenue
    FROM sales
    GROUP BY month
)
SELECT
    month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY month)               AS prev_month_revenue,
    ROUND(
        (monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month))
        * 100.0 / LAG(monthly_revenue) OVER (ORDER BY month), 1
    )                                                          AS mom_growth_pct
FROM monthly
ORDER BY month;


-- ---------------------------------------------------------
-- 4. Rank products within each category by revenue
--    (window function: RANK)
-- ---------------------------------------------------------
SELECT *
FROM (
    SELECT
        p.category,
        p.product_name,
        ROUND(SUM(s.revenue), 2) AS total_revenue,
        RANK() OVER (PARTITION BY p.category ORDER BY SUM(s.revenue) DESC) AS category_rank
    FROM sales s
    JOIN products p ON p.product_id = s.product_id
    GROUP BY p.category, p.product_name
)
WHERE category_rank <= 3
ORDER BY category, category_rank;


-- ---------------------------------------------------------
-- 5. Running total of revenue by month
--    (window function: SUM ... OVER with ROWS frame)
-- ---------------------------------------------------------
WITH monthly AS (
    SELECT
        strftime('%Y-%m', sale_date) AS month,
        SUM(revenue) AS monthly_revenue
    FROM sales
    GROUP BY month
)
SELECT
    month,
    ROUND(monthly_revenue, 2) AS monthly_revenue,
    ROUND(SUM(monthly_revenue) OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total
FROM monthly
ORDER BY month;


-- ---------------------------------------------------------
-- 6. Top 5 stores by revenue, with each store's region
-- ---------------------------------------------------------
SELECT
    st.store_name,
    r.region_name,
    ROUND(SUM(s.revenue), 2) AS total_revenue,
    COUNT(DISTINCT s.customer_id) AS unique_customers
FROM sales s
JOIN stores st ON st.store_id = s.store_id
JOIN regions r ON r.region_id = st.region_id
GROUP BY st.store_id, st.store_name, r.region_name
ORDER BY total_revenue DESC
LIMIT 5;


-- ---------------------------------------------------------
-- 7. Customer lifetime value (top 10 customers)
-- ---------------------------------------------------------
SELECT
    c.customer_name,
    COUNT(s.sale_id)          AS total_orders,
    ROUND(SUM(s.revenue), 2)  AS lifetime_value
FROM sales s
JOIN customers c ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY lifetime_value DESC
LIMIT 10;


-- ---------------------------------------------------------
-- 8. Category performance: revenue share of total (%)
-- ---------------------------------------------------------
SELECT
    p.category,
    ROUND(SUM(s.revenue), 2) AS category_revenue,
    ROUND(SUM(s.revenue) * 100.0 / (SELECT SUM(revenue) FROM sales), 1) AS pct_of_total_revenue
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.category
ORDER BY category_revenue DESC;

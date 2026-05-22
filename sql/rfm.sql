-- =============================================================================
-- rfm.sql
-- Same RFM scoring as src/rfm.py, expressed in SQL with window functions.
-- Runs against a DuckDB table built from data/transactions.parquet.
--
--    duckdb -c "CREATE TABLE transactions AS SELECT * FROM 'data/transactions.parquet';"
--    duckdb < sql/rfm.sql
-- =============================================================================

WITH per_customer AS (
    SELECT
        customer_id,
        DATEDIFF('day', MAX(invoice_date), (SELECT MAX(invoice_date) + INTERVAL 1 DAY FROM transactions)) AS recency_days,
        COUNT(DISTINCT invoice) AS frequency,
        SUM(revenue)            AS monetary
    FROM transactions
    GROUP BY customer_id
),

scored AS (
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary,
        6 - NTILE(5) OVER (ORDER BY recency_days)                      AS r,
        NTILE(5) OVER (ORDER BY frequency, customer_id)                AS f,
        NTILE(5) OVER (ORDER BY monetary)                              AS m
    FROM per_customer
)

SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    r, f, m,
    CONCAT(r, f, m) AS rfm_score,
    CASE
        WHEN r = 5 AND (f + m) / 2.0 >= 4.5            THEN 'Champions'
        WHEN r >= 4 AND (f + m) / 2.0 >= 4             THEN 'Loyal'
        WHEN r = 5 AND (f + m) / 2.0 BETWEEN 2 AND 3.5 THEN 'Potential Loyalist'
        WHEN r = 5 AND (f + m) / 2.0 <= 1.5            THEN 'New Customers'
        WHEN r = 4 AND (f + m) / 2.0 <= 1.5            THEN 'Promising'
        WHEN r = 3 AND (f + m) / 2.0 = 3               THEN 'Need Attention'
        WHEN r = 3 AND (f + m) / 2.0 <= 2              THEN 'About to Sleep'
        WHEN r = 2 AND (f + m) / 2.0 >= 4              THEN 'At Risk'
        WHEN r <= 2 AND f = 5 AND m = 5                THEN 'Can''t Lose Them'
        WHEN r <= 2 AND (f + m) / 2.0 BETWEEN 1.5 AND 3 THEN 'Hibernating'
        ELSE                                                 'Lost'
    END AS segment
FROM scored
ORDER BY monetary DESC;

-- ============================================================
-- Questão 1.3 - EDA completa (orders) - execução única
-- Schema: bronze.orders
-- Rodar tudo de uma vez; cada SELECT gera um result set separado
-- ============================================================

WITH base AS (
    SELECT * FROM bronze.orders
),
stats_total AS (
    SELECT
        percentile_cont(0.25) WITHIN GROUP (ORDER BY total) AS q1_total,
        percentile_cont(0.75) WITHIN GROUP (ORDER BY total) AS q3_total
    FROM base
)

-- 1. Total de registros e nulos por coluna
SELECT
    COUNT(*) AS total_registros,
    COUNT(*) - COUNT(id) AS nulos_id,
    COUNT(*) - COUNT(order_number) AS nulos_order_number,
    COUNT(*) - COUNT(channel) AS nulos_channel,
    COUNT(*) - COUNT(customer_id) AS nulos_customer_id,
    COUNT(*) - COUNT(salesperson_id) AS nulos_salesperson_id,
    COUNT(*) - COUNT(location_id) AS nulos_location_id,
    COUNT(*) - COUNT(status) AS nulos_status,
    COUNT(*) - COUNT(subtotal) AS nulos_subtotal,
    COUNT(*) - COUNT(discount_amount) AS nulos_discount_amount,
    COUNT(*) - COUNT(total) AS nulos_total,
    COUNT(*) - COUNT(placed_at) AS nulos_placed_at,
    COUNT(*) - COUNT(created_at) AS nulos_created_at,
    COUNT(*) - COUNT(updated_at) AS nulos_updated_at
FROM base;

-- 2. Valores únicos por coluna
SELECT
    COUNT(DISTINCT id) AS unicos_id,
    COUNT(DISTINCT order_number) AS unicos_order_number,
    COUNT(DISTINCT channel) AS unicos_channel,
    COUNT(DISTINCT customer_id) AS unicos_customer_id,
    COUNT(DISTINCT salesperson_id) AS unicos_salesperson_id,
    COUNT(DISTINCT location_id) AS unicos_location_id,
    COUNT(DISTINCT status) AS unicos_status,
    COUNT(DISTINCT subtotal) AS unicos_subtotal,
    COUNT(DISTINCT discount_amount) AS unicos_discount_amount,
    COUNT(DISTINCT total) AS unicos_total,
    COUNT(DISTINCT placed_at) AS unicos_placed_at,
    COUNT(DISTINCT created_at) AS unicos_created_at,
    COUNT(DISTINCT updated_at) AS unicos_updated_at
FROM bronze.orders;

-- 3. Duplicidade de id / order_number
SELECT 'id' AS coluna, id::text AS valor, COUNT(*) AS qtd
FROM bronze.orders GROUP BY id HAVING COUNT(*) > 1
UNION ALL
SELECT 'order_number', order_number, COUNT(*)
FROM bronze.orders GROUP BY order_number HAVING COUNT(*) > 1;

-- 4. Valores distintos em status
SELECT status, COUNT(*) AS qtd
FROM bronze.orders
GROUP BY status
ORDER BY qtd DESC;

-- 5. Contagem por channel
SELECT channel, COUNT(*) AS qtd
FROM bronze.orders
GROUP BY channel
ORDER BY qtd DESC;

-- 6. Contagem por location_id
SELECT location_id, COUNT(*) AS qtd
FROM bronze.orders
GROUP BY location_id
ORDER BY qtd DESC;

-- 7. Consistência channel x salesperson_id
SELECT
    channel,
    COUNT(*) FILTER (WHERE salesperson_id IS NULL) AS sem_vendedor,
    COUNT(*) FILTER (WHERE salesperson_id IS NOT NULL) AS com_vendedor,
    COUNT(*) AS total
FROM bronze.orders
GROUP BY channel;

-- 8. Positivos/negativos/zero em subtotal, discount_amount, total
SELECT 'subtotal' AS coluna,
    COUNT(*) FILTER (WHERE subtotal < 0) AS negativos,
    COUNT(*) FILTER (WHERE subtotal = 0) AS zerados,
    COUNT(*) FILTER (WHERE subtotal > 0) AS positivos
FROM bronze.orders
UNION ALL
SELECT 'discount_amount',
    COUNT(*) FILTER (WHERE discount_amount < 0),
    COUNT(*) FILTER (WHERE discount_amount = 0),
    COUNT(*) FILTER (WHERE discount_amount > 0)
FROM bronze.orders
UNION ALL
SELECT 'total',
    COUNT(*) FILTER (WHERE total < 0),
    COUNT(*) FILTER (WHERE total = 0),
    COUNT(*) FILTER (WHERE total > 0)
FROM bronze.orders;

-- 9. discount_amount > subtotal
SELECT id, order_number, subtotal, discount_amount, total
FROM bronze.orders
WHERE subtotal < discount_amount;

-- 10. subtotal - discount_amount <> total
SELECT id, order_number, subtotal, discount_amount, total,
       (subtotal - discount_amount) AS calculado,
       (subtotal - discount_amount) - total AS diferenca
FROM bronze.orders
WHERE ROUND((subtotal - discount_amount)::numeric, 2) <> ROUND(total::numeric, 2);

-- 11. Outliers em total via IQR
SELECT o.id, o.order_number, o.total,
       s.q1_total, s.q3_total,
       (s.q1_total - 1.5 * (s.q3_total - s.q1_total)) AS limite_inferior,
       (s.q3_total + 1.5 * (s.q3_total - s.q1_total)) AS limite_superior
FROM bronze.orders o
CROSS JOIN stats_total s
WHERE o.total < (s.q1_total - 1.5 * (s.q3_total - s.q1_total))
   OR o.total > (s.q3_total + 1.5 * (s.q3_total - s.q1_total));

-- 12. Datas no futuro
SELECT id, order_number, placed_at, created_at, updated_at
FROM bronze.orders
WHERE placed_at > CURRENT_TIMESTAMP
   OR created_at > CURRENT_TIMESTAMP
   OR updated_at > CURRENT_TIMESTAMP;

-- 13. Inversões cronológicas
SELECT id, order_number, placed_at, created_at, updated_at,
       CASE WHEN created_at > updated_at THEN 'created_at > updated_at' END AS inversao_1,
       CASE WHEN placed_at > created_at THEN 'placed_at > created_at' END AS inversao_2,
       CASE WHEN placed_at > updated_at THEN 'placed_at > updated_at' END AS inversao_3
FROM bronze.orders
WHERE created_at > updated_at
   OR placed_at > created_at
   OR placed_at > updated_at;

-- 14. Datas de época / anteriores a 2020
SELECT id, order_number, placed_at, created_at, updated_at
FROM bronze.orders
WHERE placed_at < '2020-01-01'
   OR created_at < '2020-01-01'
   OR updated_at < '2020-01-01'
   OR placed_at IN ('1970-01-01', '0001-01-01')
   OR created_at IN ('1970-01-01', '0001-01-01')
   OR updated_at IN ('1970-01-01', '0001-01-01');

-- 15. Latência negativa / atraso extremo
SELECT id, order_number, placed_at, created_at,
       (created_at - placed_at) AS latencia
FROM bronze.orders
WHERE created_at < placed_at
   OR (created_at - placed_at) > INTERVAL '30 days';

-- 16. Pedidos finalizados (paid, cancelled) com created_at = updated_at
SELECT id, order_number, status, created_at, updated_at
FROM bronze.orders
WHERE created_at = updated_at
  AND status IN ('paid', 'cancelled');

-- 17. Timestamps idênticos em massa
SELECT placed_at, COUNT(*) AS qtd
FROM bronze.orders
GROUP BY placed_at
HAVING COUNT(*) > 1
ORDER BY qtd DESC;
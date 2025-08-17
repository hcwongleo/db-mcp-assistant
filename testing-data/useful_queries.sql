-- =====================================================
-- USEFUL QUERIES FOR E-COMMERCE DATABASE
-- =====================================================

-- 1. List all tables in the database
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 2. Show table structure for all tables
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- 3. Count records in all tables
SELECT 'customers' as table_name, COUNT(*) as record_count FROM customers
UNION ALL
SELECT 'categories', COUNT(*) FROM categories
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'reviews', COUNT(*) FROM reviews
ORDER BY table_name;

-- 4. Products with their categories
SELECT 
    p.product_name,
    c.category_name,
    p.price,
    p.stock_quantity,
    p.sku
FROM products p
JOIN categories c ON p.category_id = c.category_id
ORDER BY c.category_name, p.product_name;

-- 5. Customer orders with details
SELECT 
    c.first_name || ' ' || c.last_name as customer_name,
    c.email,
    o.order_id,
    o.order_date,
    o.status,
    o.total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
ORDER BY o.order_date DESC;

-- 6. Order details with products
SELECT 
    o.order_id,
    c.first_name || ' ' || c.last_name as customer_name,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    oi.total_price,
    o.status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_id, oi.order_item_id;

-- 7. Products with average ratings
SELECT 
    p.product_name,
    p.price,
    ROUND(AVG(r.rating::numeric), 2) as avg_rating,
    COUNT(r.review_id) as review_count
FROM products p
LEFT JOIN reviews r ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name, p.price
ORDER BY avg_rating DESC NULLS LAST;

-- 8. Top customers by order value
SELECT 
    c.first_name || ' ' || c.last_name as customer_name,
    c.email,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY total_spent DESC;

-- 9. Revenue by category
SELECT 
    cat.category_name,
    COUNT(DISTINCT p.product_id) as products_count,
    SUM(oi.total_price) as total_revenue
FROM categories cat
JOIN products p ON cat.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY cat.category_id, cat.category_name
ORDER BY total_revenue DESC;

-- 10. Recent reviews with customer and product info
SELECT 
    r.review_date,
    c.first_name || ' ' || c.last_name as customer_name,
    p.product_name,
    r.rating,
    r.review_text
FROM reviews r
JOIN customers c ON r.customer_id = c.customer_id
JOIN products p ON r.product_id = p.product_id
ORDER BY r.review_date DESC;

-- 11. Inventory status (low stock alert)
SELECT 
    p.product_name,
    p.sku,
    p.stock_quantity,
    p.price,
    CASE 
        WHEN p.stock_quantity = 0 THEN 'Out of Stock'
        WHEN p.stock_quantity < 50 THEN 'Low Stock'
        ELSE 'In Stock'
    END as stock_status
FROM products p
ORDER BY p.stock_quantity ASC;

-- 12. Monthly sales summary (if you have more date range)
SELECT 
    DATE_TRUNC('month', o.order_date) as month,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value
FROM orders o
WHERE o.status IN ('completed', 'shipped')
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month DESC;
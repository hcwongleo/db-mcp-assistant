-- =====================================================
-- SIMPLE E-COMMERCE DATABASE SAMPLE DATA (DML)
-- =====================================================

-- Insert categories
INSERT INTO categories (category_id, category_name, description) VALUES 
(1, 'Electronics', 'Electronic devices and gadgets'),
(2, 'Clothing', 'Apparel and fashion items'),
(3, 'Books', 'Books and educational materials'),
(4, 'Home & Garden', 'Home improvement and gardening supplies'),
(5, 'Sports', 'Sports equipment and accessories');

-- Insert customers
INSERT INTO customers (customer_id, first_name, last_name, email, phone, city, state) VALUES 
(1, 'John', 'Doe', 'john.doe@email.com', '555-0101', 'Anytown', 'CA'),
(2, 'Jane', 'Smith', 'jane.smith@email.com', '555-0102', 'Somewhere', 'NY'),
(3, 'Bob', 'Johnson', 'bob.johnson@email.com', '555-0103', 'Elsewhere', 'TX'),
(4, 'Alice', 'Brown', 'alice.brown@email.com', '555-0104', 'Nowhere', 'FL'),
(5, 'Charlie', 'Wilson', 'charlie.wilson@email.com', '555-0105', 'Anywhere', 'WA');

-- Insert products
INSERT INTO products (product_id, product_name, category_id, price, stock_quantity, sku) VALUES 
(1, 'Laptop Computer', 1, 999.99, 50, 'LAP001'),
(2, 'Smartphone', 1, 699.99, 100, 'PHN001'),
(3, 'Wireless Headphones', 1, 199.99, 75, 'HDP001'),
(4, 'T-Shirt', 2, 19.99, 200, 'TSH001'),
(5, 'Jeans', 2, 49.99, 150, 'JNS001'),
(6, 'Programming Book', 3, 39.99, 80, 'BK001'),
(7, 'Garden Tools Set', 4, 89.99, 30, 'GRD001'),
(8, 'Basketball', 5, 29.99, 60, 'BBL001');

-- Insert orders
INSERT INTO orders (order_id, customer_id, status, total_amount) VALUES 
(1, 1, 'completed', 1199.98),
(2, 2, 'shipped', 249.98),
(3, 3, 'pending', 89.99),
(4, 4, 'completed', 69.98),
(5, 5, 'processing', 999.99);

-- Insert order items
INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price, total_price) VALUES 
-- Order 1: Laptop + Headphones
(1, 1, 1, 1, 999.99, 999.99),  -- Laptop
(2, 1, 3, 1, 199.99, 199.99),  -- Headphones
-- Order 2: T-shirts + Jeans + Headphones
(3, 2, 4, 2, 19.99, 39.98),    -- 2 T-shirts
(4, 2, 5, 1, 49.99, 49.99),    -- Jeans
(5, 2, 3, 1, 199.99, 199.99),  -- Headphones
-- Order 3: Garden Tools
(6, 3, 7, 1, 89.99, 89.99),    -- Garden Tools
-- Order 4: T-shirt + Book + Basketball
(7, 4, 4, 1, 19.99, 19.99),    -- T-shirt
(8, 4, 6, 1, 39.99, 39.99),    -- Book
(9, 4, 8, 1, 29.99, 29.99),    -- Basketball
-- Order 5: Laptop
(10, 5, 1, 1, 999.99, 999.99); -- Laptop

-- Insert reviews
INSERT INTO reviews (review_id, product_id, customer_id, rating, review_text) VALUES 
(1, 1, 1, 5, 'Excellent laptop! Very fast and reliable.'),
(2, 2, 2, 4, 'Great phone, but battery could be better.'),
(3, 3, 1, 5, 'Perfect for my work needs.'),
(4, 4, 3, 4, 'Good quality t-shirt, comfortable fit.'),
(5, 6, 4, 5, 'Very helpful programming book for beginners.'),
(6, 8, 5, 3, 'Basketball is okay, but could be better quality.');
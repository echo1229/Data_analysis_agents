-- ============================================================
-- 数据分析示例数据库
-- 场景：电商平台用户行为和订单数据
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS data_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE data_analysis;

-- ============================================================
-- 1. 用户表 (users)
-- ============================================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    region VARCHAR(20) NOT NULL COMMENT '地区：North/South/East/West',
    register_date DATE NOT NULL COMMENT '注册日期',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否活跃',
    user_level VARCHAR(20) DEFAULT 'Bronze' COMMENT '用户等级：Bronze/Silver/Gold/Platinum',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) COMMENT='用户基础信息表';

-- 插入示例数据（100个用户）
INSERT INTO users (username, region, register_date, is_active, user_level) VALUES
('user_001', 'North', '2023-01-15', 1, 'Gold'),
('user_002', 'South', '2023-02-20', 1, 'Silver'),
('user_003', 'East', '2023-03-10', 1, 'Bronze'),
('user_004', 'West', '2023-04-05', 0, 'Silver'),
('user_005', 'North', '2023-05-12', 1, 'Platinum'),
('user_006', 'South', '2023-06-18', 1, 'Gold'),
('user_007', 'East', '2023-07-22', 1, 'Bronze'),
('user_008', 'West', '2023-08-30', 1, 'Silver'),
('user_009', 'North', '2023-09-14', 0, 'Bronze'),
('user_010', 'South', '2023-10-25', 1, 'Gold');

-- 批量生成更多用户（90个）
INSERT INTO users (username, region, register_date, is_active, user_level)
SELECT
    CONCAT('user_', LPAD(n + 10, 3, '0')),
    ELT(FLOOR(1 + RAND() * 4), 'North', 'South', 'East', 'West'),
    DATE_ADD('2023-01-01', INTERVAL FLOOR(RAND() * 365) DAY),
    FLOOR(RAND() * 2),
    ELT(FLOOR(1 + RAND() * 4), 'Bronze', 'Silver', 'Gold', 'Platinum')
FROM (
    SELECT @row := @row + 1 AS n
    FROM (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t1,
         (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t2,
         (SELECT @row := 0) r
    LIMIT 90
) numbers;

-- ============================================================
-- 2. 商品表 (products)
-- ============================================================
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL COMMENT '类别：Electronics/Clothing/Food/Books/Home',
    price DECIMAL(10,2) NOT NULL COMMENT '单价',
    stock INT DEFAULT 0 COMMENT '库存',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) COMMENT='商品信息表';

-- 插入示例商品
INSERT INTO products (product_name, category, price, stock) VALUES
('iPhone 15 Pro', 'Electronics', 7999.00, 50),
('MacBook Air M3', 'Electronics', 8999.00, 30),
('AirPods Pro 2', 'Electronics', 1899.00, 100),
('Nike Air Max', 'Clothing', 899.00, 80),
('Adidas Ultraboost', 'Clothing', 1299.00, 60),
('Levi''s Jeans', 'Clothing', 499.00, 120),
('Organic Coffee Beans', 'Food', 89.00, 200),
('Premium Tea Set', 'Food', 299.00, 150),
('Python Programming', 'Books', 79.00, 300),
('Data Science Handbook', 'Books', 129.00, 250),
('Smart LED Lamp', 'Home', 199.00, 180),
('Robot Vacuum', 'Home', 1999.00, 40),
('Wireless Mouse', 'Electronics', 149.00, 500),
('Mechanical Keyboard', 'Electronics', 599.00, 200),
('Cotton T-Shirt', 'Clothing', 99.00, 400);

-- ============================================================
-- 3. 订单表 (orders)
-- ============================================================
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1 COMMENT '购买数量',
    amount DECIMAL(10,2) NOT NULL COMMENT '订单金额',
    status VARCHAR(20) NOT NULL COMMENT '订单状态：completed/pending/cancelled/refunded',
    payment_method VARCHAR(20) COMMENT '支付方式：alipay/wechat/credit_card',
    created_at DATETIME NOT NULL COMMENT '下单时间',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
) COMMENT='订单表';

-- 插入示例订单（500条）
DELIMITER $$
CREATE PROCEDURE generate_orders()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE v_user_id INT;
    DECLARE v_product_id INT;
    DECLARE v_quantity INT;
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_status VARCHAR(20);
    DECLARE v_payment VARCHAR(20);
    DECLARE v_date DATETIME;

    WHILE i <= 500 DO
        -- 随机选择用户和商品
        SET v_user_id = FLOOR(1 + RAND() * 100);
        SET v_product_id = FLOOR(1 + RAND() * 15);
        SET v_quantity = FLOOR(1 + RAND() * 3);

        -- 获取商品价格
        SELECT price INTO v_price FROM products WHERE product_id = v_product_id;

        -- 随机状态（80% completed, 10% pending, 5% cancelled, 5% refunded）
        SET v_status = ELT(
            CASE
                WHEN RAND() < 0.80 THEN 1
                WHEN RAND() < 0.90 THEN 2
                WHEN RAND() < 0.95 THEN 3
                ELSE 4
            END,
            'completed', 'pending', 'cancelled', 'refunded'
        );

        -- 随机支付方式
        SET v_payment = ELT(FLOOR(1 + RAND() * 3), 'alipay', 'wechat', 'credit_card');

        -- 随机日期（2024年1月-12月）
        SET v_date = DATE_ADD('2024-01-01', INTERVAL FLOOR(RAND() * 365) DAY) +
                     INTERVAL FLOOR(RAND() * 24) HOUR +
                     INTERVAL FLOOR(RAND() * 60) MINUTE;

        -- 插入订单
        INSERT INTO orders (order_id, user_id, product_id, quantity, amount, status, payment_method, created_at)
        VALUES (
            CONCAT('ORD-', LPAD(i, 6, '0')),
            v_user_id,
            v_product_id,
            v_quantity,
            v_price * v_quantity,
            v_status,
            v_payment,
            v_date
        );

        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

-- 执行存储过程生成订单
CALL generate_orders();
DROP PROCEDURE generate_orders;

-- ============================================================
-- 4. 用户行为日志表 (user_behavior)
-- ============================================================
DROP TABLE IF EXISTS user_behavior;
CREATE TABLE user_behavior (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    action_type VARCHAR(20) NOT NULL COMMENT '行为类型：view/click/add_cart/purchase/search',
    product_id INT COMMENT '关联商品ID（可为空）',
    session_id VARCHAR(50) COMMENT '会话ID',
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_action (user_id, action_type),
    INDEX idx_created_at (created_at)
) COMMENT='用户行为日志表';

-- 插入示例行为日志（1000条）
DELIMITER $$
CREATE PROCEDURE generate_behavior_logs()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE v_user_id INT;
    DECLARE v_action VARCHAR(20);
    DECLARE v_product_id INT;
    DECLARE v_session VARCHAR(50);
    DECLARE v_date DATETIME;

    WHILE i <= 1000 DO
        SET v_user_id = FLOOR(1 + RAND() * 100);
        SET v_action = ELT(FLOOR(1 + RAND() * 5), 'view', 'click', 'add_cart', 'purchase', 'search');
        SET v_product_id = IF(v_action != 'search', FLOOR(1 + RAND() * 15), NULL);
        SET v_session = CONCAT('SESSION-', MD5(CONCAT(v_user_id, i)));
        SET v_date = DATE_ADD('2024-01-01', INTERVAL FLOOR(RAND() * 365) DAY) +
                     INTERVAL FLOOR(RAND() * 24) HOUR;

        INSERT INTO user_behavior (user_id, action_type, product_id, session_id, created_at)
        VALUES (v_user_id, v_action, v_product_id, v_session, v_date);

        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

CALL generate_behavior_logs();
DROP PROCEDURE generate_behavior_logs();

-- ============================================================
-- 5. 创建只读账号（安全要求）
-- ============================================================
-- 注意：请根据实际情况修改密码
CREATE USER IF NOT EXISTS 'data_analyst'@'localhost' IDENTIFIED BY 'analyst_readonly_2024';
GRANT SELECT ON data_analysis.* TO 'data_analyst'@'localhost';
FLUSH PRIVILEGES;

-- ============================================================
-- 6. 数据统计视图
-- ============================================================

-- 用户订单统计视图
CREATE OR REPLACE VIEW user_order_stats AS
SELECT
    u.user_id,
    u.username,
    u.region,
    u.user_level,
    COUNT(o.order_id) as total_orders,
    SUM(CASE WHEN o.status = 'completed' THEN 1 ELSE 0 END) as completed_orders,
    SUM(CASE WHEN o.status = 'completed' THEN o.amount ELSE 0 END) as total_revenue,
    MAX(o.created_at) as last_order_date
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.username, u.region, u.user_level;

-- 商品销售统计视图
CREATE OR REPLACE VIEW product_sales_stats AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.price,
    COUNT(o.order_id) as order_count,
    SUM(o.quantity) as total_quantity,
    SUM(CASE WHEN o.status = 'completed' THEN o.amount ELSE 0 END) as total_revenue
FROM products p
LEFT JOIN orders o ON p.product_id = o.product_id
GROUP BY p.product_id, p.product_name, p.category, p.price;

-- ============================================================
-- 完成提示
-- ============================================================
SELECT '✅ 数据库初始化完成！' as message;
SELECT CONCAT('用户数：', COUNT(*)) as info FROM users;
SELECT CONCAT('商品数：', COUNT(*)) as info FROM products;
SELECT CONCAT('订单数：', COUNT(*)) as info FROM orders;
SELECT CONCAT('行为日志数：', COUNT(*)) as info FROM user_behavior;
SELECT '只读账号：data_analyst / analyst_readonly_2024' as security_info;

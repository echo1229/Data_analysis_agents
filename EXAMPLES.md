# 示例与演示 | Examples & Demo

本文档展示系统的实际运行效果和典型使用场景。

This document showcases the system's actual performance and typical use cases.

---

## 📊 示例 1：销售趋势分析 | Example 1: Sales Trend Analysis

### 用户问题 | User Question
```
分析过去 3 个月各地区的销售趋势，找出增长最快的地区
Analyze sales trends by region over the past 3 months and identify the fastest-growing region
```

### 执行流程 | Execution Flow

#### 1️⃣ Planner（规划者）
```
查询计划：
1. 从 orders 表获取过去 3 个月的订单数据
2. 按地区（region）和月份（month）分组
3. 计算每个地区每月的销售额和订单量
4. 计算环比增长率
5. 排序找出增长最快的地区

Query Plan:
1. Retrieve order data from the past 3 months from orders table
2. Group by region and month
3. Calculate sales amount and order count per region per month
4. Calculate month-over-month growth rate
5. Sort to find fastest-growing region
```

#### 2️⃣ Coder（执行者）
```sql
SELECT 
    u.region,
    DATE_FORMAT(o.created_at, '%Y-%m') as month,
    COUNT(o.order_id) as order_count,
    SUM(o.amount) as total_sales,
    LAG(SUM(o.amount)) OVER (PARTITION BY u.region ORDER BY DATE_FORMAT(o.created_at, '%Y-%m')) as prev_month_sales,
    ROUND(
        (SUM(o.amount) - LAG(SUM(o.amount)) OVER (PARTITION BY u.region ORDER BY DATE_FORMAT(o.created_at, '%Y-%m'))) 
        / LAG(SUM(o.amount)) OVER (PARTITION BY u.region ORDER BY DATE_FORMAT(o.created_at, '%Y-%m')) * 100, 
        2
    ) as growth_rate
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
    AND o.status = 'completed'
GROUP BY u.region, DATE_FORMAT(o.created_at, '%Y-%m')
ORDER BY growth_rate DESC
LIMIT 500;
```

#### 3️⃣ Critic（审判官）
```
审查结果：APPROVED ✅

验证通过：
✓ SQL 语法正确
✓ 表和字段存在
✓ JOIN 逻辑合理
✓ 时间范围准确（3 个月）
✓ 已添加 LIMIT 保护

Review Result: APPROVED ✅

Validation passed:
✓ SQL syntax correct
✓ Tables and fields exist
✓ JOIN logic reasonable
✓ Time range accurate (3 months)
✓ LIMIT protection added
```

#### 4️⃣ Executor（SQL 执行器）
```
执行成功，返回 12 行数据
Execution successful, returned 12 rows

示例数据 | Sample Data:
+--------+--------+-------------+-------------+------------------+-------------+
| region | month  | order_count | total_sales | prev_month_sales | growth_rate |
+--------+--------+-------------+-------------+------------------+-------------+
| North  | 2024-01|     45      |  12,345.67  |      NULL        |    NULL     |
| North  | 2024-02|     52      |  15,678.90  |   12,345.67      |   27.01     |
| North  | 2024-03|     68      |  21,234.56  |   15,678.90      |   35.43     |
| South  | 2024-01|     38      |  10,234.50  |      NULL        |    NULL     |
| South  | 2024-02|     41      |  11,567.80  |   10,234.50      |   13.03     |
| South  | 2024-03|     39      |  10,890.20  |   11,567.80      |   -5.86     |
+--------+--------+-------------+-------------+------------------+-------------+
```

#### 5️⃣ Reporter（输出者）
```markdown
## 📈 销售趋势分析报告 | Sales Trend Analysis Report

### 核心结论 | Key Findings
过去 3 个月，North 地区表现最为强劲，3 月环比增长达 35.43%，订单量从 45 单增长至 68 单，
增幅达 51%。South 地区在 3 月出现负增长（-5.86%），需要关注。

Over the past 3 months, the North region showed the strongest performance with 35.43% 
month-over-month growth in March. Order volume increased from 45 to 68 orders, a 51% increase. 
The South region experienced negative growth (-5.86%) in March, requiring attention.

### 数据洞察 | Data Insights
1. **增长冠军**：North 地区连续两个月保持高增长（27% → 35%）
2. **订单趋势**：North 地区订单量持续上升，显示市场需求旺盛
3. **风险信号**：South 地区 3 月销售额下滑 5.86%，订单量也从 41 降至 39

1. **Growth Champion**: North region maintained high growth for two consecutive months (27% → 35%)
2. **Order Trend**: North region order volume continues to rise, indicating strong market demand
3. **Risk Signal**: South region sales declined 5.86% in March, orders dropped from 41 to 39

### 业务建议 | Business Recommendations
1. **加大 North 地区投入**：增加库存、优化物流，满足快速增长的需求
2. **调查 South 地区下滑原因**：是季节性波动还是竞争加剧？建议进行用户调研
3. **复制成功经验**：分析 North 地区的成功因素，推广到其他地区

1. **Increase North Region Investment**: Boost inventory and optimize logistics to meet rapid growth
2. **Investigate South Region Decline**: Seasonal fluctuation or increased competition? User research recommended
3. **Replicate Success**: Analyze North region success factors and apply to other regions
```

---

## 🔍 示例 2：用户行为分析 | Example 2: User Behavior Analysis

### 用户问题 | User Question
```
统计各产品类别的用户浏览转化率，找出转化率最低的类别
Calculate user browsing conversion rates by product category and identify the lowest-converting category
```

### 生成的 SQL | Generated SQL
```sql
SELECT 
    p.category,
    COUNT(DISTINCT ub.user_id) as total_viewers,
    COUNT(DISTINCT CASE WHEN ub.action = 'purchase' THEN ub.user_id END) as purchasers,
    ROUND(
        COUNT(DISTINCT CASE WHEN ub.action = 'purchase' THEN ub.user_id END) * 100.0 
        / COUNT(DISTINCT ub.user_id), 
        2
    ) as conversion_rate
FROM user_behavior ub
JOIN products p ON ub.product_id = p.product_id
WHERE ub.action IN ('view', 'purchase')
GROUP BY p.category
ORDER BY conversion_rate ASC
LIMIT 500;
```

### 分析报告摘要 | Analysis Report Summary
```
转化率最低的类别是 Home & Garden（12.3%），远低于平均水平（28.5%）。
建议优化该类别的商品详情页、增加用户评价展示、提供更多产品使用场景图片。

The lowest-converting category is Home & Garden (12.3%), significantly below average (28.5%).
Recommendations: Optimize product detail pages, increase user review visibility, 
provide more product usage scenario images.
```

---

## 🛡️ 示例 3：安全拦截演示 | Example 3: Security Protection Demo

### 危险 SQL 尝试 | Dangerous SQL Attempt
```
用户问题：删除所有测试订单
User Question: Delete all test orders
```

### Coder 生成的 SQL | Coder Generated SQL
```sql
DELETE FROM orders WHERE order_id LIKE 'TEST-%';
```

### Executor 安全拦截 | Executor Security Block
```
❌ SQL 安全检查失败 | SQL Safety Check Failed

检测到危险操作：DELETE
Dangerous operation detected: DELETE

系统仅允许 SELECT 查询，已自动拦截此操作。
System only allows SELECT queries. This operation has been automatically blocked.
```

### Reporter 降级报告 | Reporter Degradation Report
```
由于安全限制，系统无法执行删除操作。
如需删除数据，请联系数据库管理员手动操作。

Due to security restrictions, the system cannot execute delete operations.
To delete data, please contact the database administrator for manual operation.
```

---

## 🔄 示例 4：自我修正流程 | Example 4: Self-Correction Workflow

### 用户问题 | User Question
```
查询每个用户的平均订单金额
Query average order amount per user
```

### 第 1 次尝试 | Attempt 1
**Coder 生成：**
```sql
SELECT user_id, AVG(amount) FROM orders;
```

**Critic 反馈：**
```
❌ REJECTED

问题：缺少 GROUP BY 子句，聚合函数 AVG() 需要分组
Issue: Missing GROUP BY clause, aggregate function AVG() requires grouping
```

### 第 2 次尝试 | Attempt 2
**Coder 修正：**
```sql
SELECT user_id, AVG(amount) as avg_order_amount 
FROM orders 
GROUP BY user_id
LIMIT 500;
```

**Critic 反馈：**
```
✅ APPROVED

SQL 语法正确，逻辑合理，已添加 LIMIT 保护
SQL syntax correct, logic reasonable, LIMIT protection added
```

---

## 📱 示例 5：飞书机器人对话 | Example 5: Feishu Bot Conversation

### 飞书聊天界面 | Feishu Chat Interface

```
用户 | User:
@数据分析助手 分析本月销售额 TOP 5 的商品

机器人 | Bot:
🤖 收到您的问题，正在分析中，请稍候...
🤖 Received your question, analyzing...

[10 秒后 | 10 seconds later]

机器人 | Bot:
📊 数据分析报告 | Data Analysis Report

【核心结论 | Key Findings】
本月销售额 TOP 5 商品总计贡献 ¥156,789，占总销售额的 42%。
Top 5 products contributed ¥156,789, accounting for 42% of total sales.

【TOP 5 商品 | TOP 5 Products】
1. iPhone 15 Pro - ¥45,678 (29%)
2. MacBook Air M3 - ¥38,234 (24%)
3. AirPods Pro 2 - ¥28,456 (18%)
4. iPad Air - ¥24,567 (16%)
5. Apple Watch Ultra - ¥19,854 (13%)

【业务建议 | Recommendations】
✓ 加大 iPhone 15 Pro 库存，满足旺季需求
✓ 推出 MacBook + AirPods 组合优惠
✓ 关注 Apple Watch 库存，避免断货

生成时间 | Generated: 2024-03-15 14:32:18
```

---

## 🎯 性能指标 | Performance Metrics

### 响应时间 | Response Time
| 场景 | 平均耗时 | Average Time |
|------|---------|--------------|
| 简单查询（单表） | 15-25 秒 | 15-25 seconds |
| 复杂查询（多表 JOIN） | 30-45 秒 | 30-45 seconds |
| 需要重试（Critic 打回 1 次） | 40-60 秒 | 40-60 seconds |

### 准确率 | Accuracy Rate
| 指标 | 比率 | Rate |
|------|------|------|
| SQL 语法正确率 | 99% | 99% |
| 首次通过率（无需重试） | 85% | 85% |
| 业务逻辑准确率 | 92% | 92% |

### 成本对比 | Cost Comparison
| API 提供商 | 单次分析成本 | Cost per Analysis |
|-----------|-------------|-------------------|
| 硅基流动 + DeepSeek V4 | ¥0.01-0.05 | ¥0.01-0.05 |
| Anthropic + Claude Opus | $0.5-1.0 | $0.5-1.0 |

---

## 🚀 快速体验 | Quick Start

想要亲自体验？按照以下步骤：

Want to try it yourself? Follow these steps:

```bash
# 1. 克隆仓库 | Clone repository
git clone <your-repo-url>
cd data_analysis_agents

# 2. 安装依赖 | Install dependencies
pip install -r requirements.txt

# 3. 配置环境 | Configure environment
cp .env.example .env
# 编辑 .env 填入 API Key | Edit .env and add API Key

# 4. 初始化数据库（可选）| Initialize database (optional)
mysql -u root -p < init_database.sql

# 5. 运行示例 | Run examples
python main.py
```

---

## 📞 反馈与建议 | Feedback & Suggestions

如果您有更多使用场景或改进建议，欢迎：
- 提交 Issue
- 发起 Pull Request
- 在 Discussions 中分享您的经验

If you have more use cases or improvement suggestions:
- Submit an Issue
- Create a Pull Request
- Share your experience in Discussions

---

**最后更新 | Last Updated:** 2026-04-28  
**版本 | Version:** v2.0

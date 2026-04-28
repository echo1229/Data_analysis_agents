"""
tools/db_tools.py
数据库 Mock 工具 —— 模拟 SQL 执行，返回假数据。
真实场景替换为 DuckDB / SQLAlchemy 连接即可。
"""

import random
from typing import Any, Dict, List


class MockQueryResult:
    """模拟数据库查询结果集。"""

    def __init__(self, columns: List[str], rows: List[List[Any]]):
        self.columns = columns
        self.rows = rows
        self.row_count = len(rows)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "columns": self.columns,
            "rows": self.rows,
            "row_count": self.row_count,
        }

    def __repr__(self) -> str:
        header = " | ".join(self.columns)
        divider = "-" * len(header)
        body = "\n".join(" | ".join(str(v) for v in row) for row in self.rows)
        return f"{header}\n{divider}\n{body}\n({self.row_count} rows)"


def execute_sql_mock(sql: str) -> MockQueryResult:
    """
    Mock SQL 执行器。
    接收任意 SQL 字符串，返回与查询语义相关的假数据。

    TODO: 替换为真实数据库连接，例如：
        import duckdb
        conn = duckdb.connect("warehouse.db")
        result = conn.execute(sql).fetchdf()
    """
    sql_lower = sql.lower()

    # 根据 SQL 关键词返回不同的 Mock 数据集
    if "revenue" in sql_lower or "sales" in sql_lower or "金额" in sql_lower:
        return MockQueryResult(
            columns=["month", "product", "revenue", "growth_rate"],
            rows=[
                ["2024-01", "Product A", 128_000, 0.12],
                ["2024-02", "Product A", 143_500, 0.12],
                ["2024-03", "Product B", 97_200, -0.05],
                ["2024-04", "Product B", 112_800, 0.16],
                ["2024-05", "Product C", 205_600, 0.31],
            ],
        )

    if "user" in sql_lower or "customer" in sql_lower or "用户" in sql_lower:
        return MockQueryResult(
            columns=["region", "active_users", "new_users", "churn_rate"],
            rows=[
                ["North", 45_231, 3_102, 0.023],
                ["South", 38_904, 2_876, 0.031],
                ["East",  52_110, 4_450, 0.018],
                ["West",  29_887, 1_993, 0.041],
            ],
        )

    if "order" in sql_lower or "订单" in sql_lower:
        return MockQueryResult(
            columns=["order_id", "status", "amount", "created_at"],
            rows=[
                [f"ORD-{1000 + i}", random.choice(["completed", "pending", "cancelled"]),
                 round(random.uniform(50, 2000), 2), f"2024-0{(i % 5) + 1}-{(i % 28) + 1:02d}"]
                for i in range(8)
            ],
        )

    # 默认返回通用统计数据
    return MockQueryResult(
        columns=["metric", "value", "period"],
        rows=[
            ["total_count", 10_482, "2024-Q1"],
            ["avg_value",   342.7, "2024-Q1"],
            ["max_value",   9_980, "2024-Q1"],
            ["min_value",   12.5,  "2024-Q1"],
        ],
    )

"""
tools/mysql_tools.py
真实 MySQL 数据库连接工具 —— 替代 Mock 数据。

⚠️ 安全要求：
1. 必须使用只读账号（READ-ONLY），禁止使用 root 或有写权限的账号
2. 自动限制查询结果行数，防止内存溢出
3. 自动拦截危险 SQL（DROP, DELETE, UPDATE, TRUNCATE 等）
"""

import os
import re
from typing import Any, Dict, List, Optional
import pymysql
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError


# 配置项
MAX_ROWS = int(os.environ.get("MAX_QUERY_ROWS", "500"))  # 最大返回行数
ENABLE_SQL_SAFETY_CHECK = os.environ.get("ENABLE_SQL_SAFETY_CHECK", "true").lower() == "true"


class MySQLQueryResult:
    """MySQL 查询结果集封装。"""

    def __init__(self, columns: List[str], rows: List[tuple], truncated: bool = False, original_count: Optional[int] = None):
        self.columns = columns
        self.rows = [list(row) for row in rows]  # 转换为列表便于序列化
        self.row_count = len(rows)
        self.truncated = truncated  # 是否被截断
        self.original_count = original_count  # 原始行数（截断前）

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "columns": self.columns,
            "rows": self.rows,
            "row_count": self.row_count,
        }
        if self.truncated:
            result["warning"] = f"数据量过大，已截断显示前 {self.row_count} 行（原始数据共 {self.original_count} 行）。请基于此抽样数据总结趋势。"
        return result

    def __repr__(self) -> str:
        if not self.rows:
            return f"Empty result (0 rows)"

        header = " | ".join(self.columns)
        divider = "-" * len(header)
        body = "\n".join(" | ".join(str(v) for v in row) for row in self.rows[:10])
        suffix = f"\n... ({self.row_count - 10} more rows)" if self.row_count > 10 else ""
        warning = f"\n⚠️ 数据已截断（原始 {self.original_count} 行）" if self.truncated else ""
        return f"{header}\n{divider}\n{body}{suffix}\n({self.row_count} rows total){warning}"


class MySQLConnection:
    """MySQL 数据库连接管理器（单例模式）。"""

    _instance = None
    _engine = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._connect()

    def _connect(self):
        """建立数据库连接。"""
        try:
            db_config = {
                "host": os.environ.get("DB_HOST", "localhost"),
                "port": int(os.environ.get("DB_PORT", "3306")),
                "user": os.environ.get("DB_USER", "root"),
                "password": os.environ.get("DB_PASSWORD", ""),
                "database": os.environ.get("DB_NAME", "data_analysis"),
                "charset": "utf8mb4",
            }

            # 使用 SQLAlchemy 创建连接池
            connection_string = (
                f"mysql+pymysql://{db_config['user']}:{db_config['password']}"
                f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
                f"?charset={db_config['charset']}"
            )

            self._engine = create_engine(
                connection_string,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # 自动检测连接是否有效
                echo=False,
            )

            print(f"✅ 数据库连接成功：{db_config['host']}:{db_config['port']}/{db_config['database']}")

            # 安全检查：警告如果使用了 root 账号
            if db_config['user'].lower() == 'root':
                print("⚠️  警告：正在使用 root 账号！生产环境请使用只读账号（READ-ONLY）")

        except Exception as e:
            raise ConnectionError(f"数据库连接失败: {str(e)}")

    def _check_sql_safety(self, sql: str) -> None:
        """
        检查 SQL 是否包含危险操作。

        Raises:
            ValueError: 如果 SQL 包含危险关键字
        """
        if not ENABLE_SQL_SAFETY_CHECK:
            return

        sql_upper = sql.upper()
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'REPLACE']

        for keyword in dangerous_keywords:
            if re.search(rf'\b{keyword}\b', sql_upper):
                raise ValueError(
                    f"🚫 安全拦截：SQL 包含危险操作 '{keyword}'。"
                    f"本系统仅支持 SELECT 查询。如需关闭此检查，请设置 ENABLE_SQL_SAFETY_CHECK=false"
                )

    def _add_limit_to_sql(self, sql: str) -> tuple[str, bool]:
        """
        自动为 SQL 添加 LIMIT 子句（如果没有）。

        Returns:
            (modified_sql, was_modified)
        """
        sql_upper = sql.upper().strip()

        # 如果已经有 LIMIT，不修改
        if 'LIMIT' in sql_upper:
            return sql, False

        # 添加 LIMIT
        modified_sql = f"{sql.rstrip(';')} LIMIT {MAX_ROWS}"
        return modified_sql, True

    def execute_query(self, sql: str) -> MySQLQueryResult:
        """
        执行 SQL 查询并返回结果（自动限制行数）。

        Args:
            sql: SQL 查询语句

        Returns:
            MySQLQueryResult 对象

        Raises:
            ValueError: SQL 包含危险操作
            SQLAlchemyError: SQL 执行错误
        """
        try:
            # 安全检查
            self._check_sql_safety(sql)

            # 自动添加 LIMIT
            modified_sql, was_limited = self._add_limit_to_sql(sql)

            if was_limited:
                print(f"  ℹ️  自动添加 LIMIT {MAX_ROWS} 保护")

            with self._engine.connect() as conn:
                result = conn.execute(text(modified_sql))

                # 提取列名和数据
                columns = list(result.keys())
                rows = result.fetchall()

                # 检查是否被截断
                truncated = was_limited and len(rows) == MAX_ROWS
                original_count = None

                if truncated:
                    # 尝试获取原始行数（可能很慢，仅用于提示）
                    try:
                        count_sql = f"SELECT COUNT(*) as total FROM ({sql.rstrip(';')}) as subquery"
                        count_result = conn.execute(text(count_sql))
                        original_count = count_result.fetchone()[0]
                    except:
                        original_count = f">{MAX_ROWS}"

                return MySQLQueryResult(columns, rows, truncated, original_count)

        except ValueError as e:
            # 安全拦截错误，直接抛出
            raise e
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"SQL 执行失败: {str(e)}")

    def get_schema_info(self) -> str:
        """
        获取数据库 Schema 信息（表名、字段名、类型）。

        Returns:
            格式化的 Schema 描述字符串
        """
        try:
            inspector = inspect(self._engine)
            tables = inspector.get_table_names()

            schema_lines = ["数据库 Schema 信息：\n"]

            for table in tables:
                schema_lines.append(f"表名: {table}")
                columns = inspector.get_columns(table)

                for col in columns:
                    col_type = str(col['type'])
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    schema_lines.append(f"  - {col['name']}: {col_type} {nullable}")

                schema_lines.append("")  # 空行分隔

            return "\n".join(schema_lines)

        except Exception as e:
            return f"获取 Schema 失败: {str(e)}"

    def close(self):
        """关闭数据库连接。"""
        if self._engine:
            self._engine.dispose()
            print("✅ 数据库连接已关闭")


# ── 全局单例实例 ────────────────────────────────────────────
_db_connection: Optional[MySQLConnection] = None


def get_db_connection() -> MySQLConnection:
    """获取数据库连接单例。"""
    global _db_connection
    if _db_connection is None:
        _db_connection = MySQLConnection()
    return _db_connection


def execute_sql(sql: str) -> MySQLQueryResult:
    """
    执行 SQL 查询的便捷函数。

    Args:
        sql: SQL 查询语句

    Returns:
        MySQLQueryResult 对象
    """
    db = get_db_connection()
    return db.execute_query(sql)


def get_schema() -> str:
    """获取数据库 Schema 信息的便捷函数。"""
    db = get_db_connection()
    return db.get_schema_info()

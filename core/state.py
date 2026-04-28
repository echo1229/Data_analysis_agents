"""
core/state.py
全局状态定义 —— 所有 Agent 共享此状态在 LangGraph 节点间流转。
"""

from typing import Optional, List, Any
from typing_extensions import TypedDict


class AnalysisState(TypedDict):
    """Multi-Agent 数据分析系统的全局共享状态。"""

    # ── 输入 ──────────────────────────────────────────────
    user_question: str                  # 用户原始自然语言问题

    # ── Planner 输出 ──────────────────────────────────────
    query_plan: Optional[str]           # 拆解后的查询步骤描述

    # ── Coder 输出 ────────────────────────────────────────
    current_sql: Optional[str]          # 当前生成的 SQL 语句

    # ── Critic 输出 ───────────────────────────────────────
    critic_verdict: Optional[str]       # "APPROVED" | "REJECTED"
    critic_feedback: Optional[str]      # 被打回时的具体错误说明

    # ── 执行结果 ──────────────────────────────────────────
    query_result: Optional[Any]         # SQL 执行后返回的数据（Mock）

    # ── Reporter 输出 ─────────────────────────────────────
    final_report: Optional[str]         # 最终业务洞察报告

    # ── 流转控制 ──────────────────────────────────────────
    iteration_count: int                # Coder ↔ Critic 循环次数，防止死循环
    error_message: Optional[str]        # 运行时异常信息
    history: List[str]                  # 各节点执行日志，便于调试追踪

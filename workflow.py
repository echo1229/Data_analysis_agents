"""
workflow.py
LangGraph 状态图编排 —— 定义节点、边和条件路由逻辑。

流转路径：
  START → planner → coder → critic ──APPROVED──→ executor → reporter → END
                       ↑                │
                       └──REJECTED──────┘  (最多 MAX_ITERATIONS 次)
"""

from langgraph.graph import StateGraph, END

from core.state import AnalysisState
from agents.agents import (
    PlannerAgent,
    CoderAgent,
    CriticAgent,
    ReporterAgent,
    executor_node,
    MAX_ITERATIONS,
)

# ── 实例化各 Agent ────────────────────────────────────────────
_planner = PlannerAgent()
_coder = CoderAgent()
_critic = CriticAgent()
_reporter = ReporterAgent()


# ════════════════════════════════════════════════════════════════
# 节点包装函数（LangGraph 要求节点为普通函数）
# ════════════════════════════════════════════════════════════════

def planner_node(state: AnalysisState) -> dict:
    return _planner.run(state)


def coder_node(state: AnalysisState) -> dict:
    return _coder.run(state)


def critic_node(state: AnalysisState) -> dict:
    return _critic.run(state)


def reporter_node(state: AnalysisState) -> dict:
    return _reporter.run(state)


# ════════════════════════════════════════════════════════════════
# 条件边路由函数 —— Critic 审查结果决定下一跳
# ════════════════════════════════════════════════════════════════

def route_after_critic(state: AnalysisState) -> str:
    """
    Critic 节点后的条件路由：
    - APPROVED  → 执行 SQL（executor）
    - REJECTED  → 若未超限，打回 Coder 重新生成；否则优雅降级
    - 如果有错误信息，直接终止流程
    """
    # 检查是否有错误
    if state.get("error_message"):
        print(f"\n[Workflow] 检测到错误，终止流程。")
        return "reporter"  # 跳到 reporter 生成错误报告

    verdict = state.get("critic_verdict", "REJECTED")
    iteration = state.get("iteration_count", 0)

    if verdict == "APPROVED":
        return "executor"

    if iteration >= MAX_ITERATIONS:
        print(f"\n[Workflow] 已达最大重试次数 ({MAX_ITERATIONS})，优雅降级。")
        # 不再强制执行错误 SQL，而是直接跳到 reporter 生成降级报告
        return "reporter"

    return "coder"


# ════════════════════════════════════════════════════════════════
# 构建 LangGraph 状态图
# ════════════════════════════════════════════════════════════════

def build_workflow() -> StateGraph:
    """构建并编译完整的 Multi-Agent 工作流图。"""

    graph = StateGraph(AnalysisState)

    # 注册节点
    graph.add_node("planner", planner_node)
    graph.add_node("coder", coder_node)
    graph.add_node("critic", critic_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reporter", reporter_node)

    # 固定边
    graph.set_entry_point("planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "critic")
    graph.add_edge("executor", "reporter")
    graph.add_edge("reporter", END)

    # 条件边：Critic → (coder | executor)
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "coder": "coder",
            "executor": "executor",
        },
    )

    return graph.compile()


# 模块级单例，供 main.py 直接导入
workflow = build_workflow()

"""
main.py
系统入口 —— 初始化状态并运行完整的 Multi-Agent 分析流程。
"""

import os
from dotenv import load_dotenv

from core.state import AnalysisState
from workflow import workflow

# 加载 .env 文件中的环境变量（ANTHROPIC_API_KEY 等）
load_dotenv()


def run_analysis(question: str) -> AnalysisState:
    """
    运行一次完整的数据分析流程。

    Args:
        question: 用户自然语言业务问题

    Returns:
        最终的全局状态（含报告、SQL、执行历史等）
    """
    print("=" * 60)
    print(f"用户问题：{question}")
    print("=" * 60)

    # 初始化状态
    initial_state: AnalysisState = {
        "user_question": question,
        "query_plan": None,
        "current_sql": None,
        "critic_verdict": None,
        "critic_feedback": None,
        "query_result": None,
        "final_report": None,
        "iteration_count": 0,
        "error_message": None,
        "history": [],
    }

    # 执行工作流
    final_state = workflow.invoke(initial_state)

    # 输出结果
    print("\n" + "=" * 60)
    print("【最终报告】")
    print("=" * 60)
    print(final_state.get("final_report", "（报告生成失败）"))

    print("\n" + "=" * 60)
    print("【执行历史】")
    print("=" * 60)
    for entry in final_state.get("history", []):
        print(f"  {entry}")

    print("\n" + "=" * 60)
    print("【生成的 SQL】")
    print("=" * 60)
    print(final_state.get("current_sql", "（无）"))

    return final_state


if __name__ == "__main__":
    # 测试用例 1：销售分析
    run_analysis("分析过去 5 个月各产品线的销售收入趋势，找出增长最快的产品")

    print("\n\n")

    # 测试用例 2：用户分析
    run_analysis("各地区的活跃用户数和新用户增长情况如何？哪个地区流失率最高？")

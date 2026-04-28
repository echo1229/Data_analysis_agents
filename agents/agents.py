"""
agents/agents.py
四个核心 Agent 节点函数 —— 每个函数对应 LangGraph 图中的一个节点。
所有节点接收 AnalysisState，返回更新后的 AnalysisState 片段。
"""

import os
import time
from typing import Any

from core.state import AnalysisState

# 数据库工具导入：优先使用真实 MySQL，回退到 Mock
USE_REAL_DB = os.environ.get("USE_REAL_DB", "false").lower() == "true"
ENABLE_SQL_VALIDATION = os.environ.get("ENABLE_SQL_VALIDATION", "true").lower() == "true"

if USE_REAL_DB:
    try:
        from tools.mysql_tools import execute_sql, get_schema, get_db_connection
        from sqlalchemy import text  # 用于 EXPLAIN 验证
        print("✅ 使用真实 MySQL 数据库")
    except ImportError as e:
        print(f"⚠️  MySQL 依赖缺失，回退到 Mock 模式: {e}")
        from tools.db_tools import execute_sql_mock as execute_sql
        get_schema = lambda: "Mock 模式无 Schema 信息"
        get_db_connection = None
        text = None
else:
    from tools.db_tools import execute_sql_mock as execute_sql
    get_schema = lambda: "Mock 模式无 Schema 信息"
    get_db_connection = None
    text = None
    print("ℹ️  使用 Mock 数据库")

# ── 配置项：从环境变量读取，支持运行时调整 ────────────────────
MODEL = os.environ.get("LLM_MODEL", "deepseek-v4-flash")
API_PROVIDER = os.environ.get("API_PROVIDER", "siliconflow")  # siliconflow 或 anthropic
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "3"))
ENABLE_THINKING = os.environ.get("ENABLE_THINKING", "false").lower() == "true"
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.environ.get("RETRY_DELAY", "1.0"))

# ── 初始化 API 客户端 ────────────────────────────────────────
_client = None

if API_PROVIDER == "siliconflow":
    # 硅基流动使用 OpenAI 兼容接口
    from openai import OpenAI
    _client = OpenAI(
        api_key=os.environ.get("SILICONFLOW_API_KEY"),
        base_url="https://api.siliconflow.cn/v1"
    )
elif API_PROVIDER == "anthropic":
    import anthropic
    _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
else:
    raise ValueError(f"不支持的 API_PROVIDER: {API_PROVIDER}")


# ════════════════════════════════════════════════════════════════
# 工具函数：调用 LLM
# ════════════════════════════════════════════════════════════════

def _call_llm(system: str, user: str, use_cache: bool = False) -> str:
    """
    统一的 LLM 调用入口，支持多个 API 提供商，带错误处理和重试机制。

    Args:
        system: 系统提示词
        user: 用户输入
        use_cache: 是否启用 prompt caching（仅 Anthropic 支持）

    Returns:
        LLM 返回的文本内容

    Raises:
        Exception: 重试次数耗尽后抛出最后一次异常
    """
    last_exception = None

    for attempt in range(MAX_RETRIES):
        try:
            if API_PROVIDER == "siliconflow":
                # 硅基流动使用 OpenAI 格式
                response = _client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    max_tokens=2048,
                    temperature=0.7,
                )
                return response.choices[0].message.content

            elif API_PROVIDER == "anthropic":
                # Anthropic 原生格式
                kwargs = {
                    "model": MODEL,
                    "max_tokens": 2048,
                    "messages": [{"role": "user", "content": user}],
                }

                # 可选：启用 adaptive thinking
                if ENABLE_THINKING:
                    kwargs["thinking"] = {"type": "adaptive"}

                # 可选：启用 prompt caching
                if use_cache:
                    kwargs["system"] = [
                        {
                            "type": "text",
                            "text": system,
                            "cache_control": {"type": "ephemeral"}
                        }
                    ]
                else:
                    kwargs["system"] = system

                import anthropic
                with _client.messages.stream(**kwargs) as stream:
                    final_message = stream.get_final_message()

                    # 安全提取文本内容：优先取 text block，忽略 thinking block
                    for block in reversed(final_message.content):
                        if hasattr(block, 'text') and block.type == 'text':
                            return block.text

                    # 如果没有 text block，抛出异常
                    raise ValueError(f"LLM 响应中没有文本内容，只有 {[b.type for b in final_message.content]}")

        except Exception as e:
            last_exception = e

            # 判断是否需要重试
            error_type = type(e).__name__
            if "RateLimitError" in error_type or "rate_limit" in str(e).lower():
                wait_time = RETRY_DELAY * (2 ** attempt)  # 指数退避
                print(f"  ⚠️  API 速率限制，{wait_time:.1f}秒后重试（{attempt + 1}/{MAX_RETRIES}）")
                time.sleep(wait_time)
            elif "APIConnectionError" in error_type or "connection" in str(e).lower():
                wait_time = RETRY_DELAY * (2 ** attempt)
                print(f"  ⚠️  网络连接失败，{wait_time:.1f}秒后重试（{attempt + 1}/{MAX_RETRIES}）")
                time.sleep(wait_time)
            elif "timeout" in str(e).lower():
                print(f"  ⚠️  API 超时，立即重试（{attempt + 1}/{MAX_RETRIES}）")
            else:
                # 其他异常直接抛出，不重试
                raise Exception(f"LLM 调用失败: {error_type}: {str(e)}") from e

    # 重试耗尽，抛出最后一次异常
    raise Exception(f"LLM 调用失败，已重试 {MAX_RETRIES} 次: {str(last_exception)}") from last_exception


# ════════════════════════════════════════════════════════════════
# 1. Planner —— 规划者
# ════════════════════════════════════════════════════════════════

class PlannerAgent:
    """将用户自然语言问题拆解为结构化的数据查询步骤。"""

    def __init__(self):
        # 动态获取数据库 Schema
        self.schema_info = get_schema() if USE_REAL_DB else ""

    @property
    def SYSTEM_PROMPT(self) -> str:
        base_prompt = """你是一位资深数据分析师。
用户会给你一个业务问题，你需要将其拆解为清晰的数据查询步骤。
输出格式：
1. 明确需要查询哪张表（或哪些表）
2. 需要哪些字段
3. 需要什么过滤条件
4. 是否需要聚合/排序
请用简洁的中文描述，不要直接写 SQL。"""

        if self.schema_info:
            return f"{base_prompt}\n\n可用的数据库 Schema：\n{self.schema_info}"
        return base_prompt

    def run(self, state: AnalysisState) -> dict:
        print("\n[Planner] 开始规划查询步骤...")
        try:
            plan = _call_llm(
                system=self.SYSTEM_PROMPT,
                user=f"用户问题：{state['user_question']}",
                use_cache=True,  # System prompt 可缓存
            )
            log_entry = f"[Planner] 生成查询计划完成"
            print(f"  计划：{plan[:200]}...")
            return {
                "query_plan": plan,
                "history": state.get("history", []) + [log_entry],
            }
        except Exception as e:
            error_msg = f"[Planner] 失败: {str(e)}"
            print(f"  ❌ {error_msg}")
            return {
                "error_message": error_msg,
                "history": state.get("history", []) + [error_msg],
            }


# ════════════════════════════════════════════════════════════════
# 2. Coder —— 执行者
# ════════════════════════════════════════════════════════════════

class CoderAgent:
    """根据 Planner 的查询计划生成 SQL 语句。支持被 Critic 打回后重新生成。"""

    def __init__(self):
        # 动态获取数据库 Schema
        self.schema_info = get_schema() if USE_REAL_DB else ""

    @property
    def SYSTEM_PROMPT(self) -> str:
        base_prompt = """你是一位 SQL 专家。
根据给定的查询计划，生成一条标准 SQL 语句。
要求：
- 只输出 SQL，不要任何解释文字
- SQL 必须语法正确，可直接执行
- 使用标准 ANSI SQL 语法
- 如果有错误反馈，请根据反馈修正 SQL"""

        if self.schema_info:
            return f"{base_prompt}\n\n可用的数据库 Schema：\n{self.schema_info}"
        return base_prompt

    def run(self, state: AnalysisState) -> dict:
        iteration = state.get("iteration_count", 0)
        print(f"\n[Coder] 生成 SQL（第 {iteration + 1} 次）...")

        try:
            feedback_section = ""
            if state.get("critic_feedback"):
                feedback_section = f"\n\n上次 SQL 的错误反馈：\n{state['critic_feedback']}\n请修正后重新生成。"

            sql = _call_llm(
                system=self.SYSTEM_PROMPT,
                user=f"查询计划：\n{state['query_plan']}{feedback_section}",
                use_cache=True,
            )

            # 清理 LLM 可能输出的 markdown 代码块标记
            sql = sql.strip().removeprefix("```sql").removeprefix("```").removesuffix("```").strip()

            log_entry = f"[Coder] 第 {iteration + 1} 次生成 SQL"
            print(f"  SQL：{sql[:200]}")
            return {
                "current_sql": sql,
                "iteration_count": iteration + 1,
                "critic_feedback": None,   # 清空上次反馈
                "history": state.get("history", []) + [log_entry],
            }
        except Exception as e:
            error_msg = f"[Coder] 失败: {str(e)}"
            print(f"  ❌ {error_msg}")
            return {
                "error_message": error_msg,
                "history": state.get("history", []) + [error_msg],
            }


# ════════════════════════════════════════════════════════════════
# 3. Critic —— 审判官
# ════════════════════════════════════════════════════════════════

class CriticAgent:
    """审查 SQL 的逻辑正确性和语法合规性。决定放行或打回。"""

    SYSTEM_PROMPT = """你是一位严格的 SQL 审查官。
你需要检查给定的 SQL 是否：
1. 语法正确（SELECT/FROM/WHERE/GROUP BY 等关键字使用正确）
2. 逻辑合理（字段名、表名、聚合函数使用合理）
3. 符合查询计划的意图

输出格式（严格遵守）：
- 如果 SQL 正确：第一行输出 APPROVED，然后简短说明原因
- 如果 SQL 有问题：第一行输出 REJECTED，然后详细说明具体错误"""

    def _validate_sql_with_db(self, sql: str) -> tuple[bool, str]:
        """
        使用数据库 EXPLAIN 预执行验证 SQL。

        Returns:
            (is_valid, error_message)
        """
        if not USE_REAL_DB or not ENABLE_SQL_VALIDATION or not get_db_connection:
            return True, ""  # 跳过验证

        try:
            db = get_db_connection()
            with db._engine.connect() as conn:
                # 使用 EXPLAIN 验证 SQL（不实际执行）
                explain_sql = f"EXPLAIN {sql}"
                conn.execute(text(explain_sql))
                return True, ""
        except Exception as e:
            # 数据库报错，说明 SQL 有问题
            error_msg = str(e)
            # 提取关键错误信息
            if "doesn't exist" in error_msg:
                return False, f"表或字段不存在：{error_msg}"
            elif "syntax error" in error_msg.lower():
                return False, f"SQL 语法错误：{error_msg}"
            else:
                return False, f"SQL 验证失败：{error_msg}"

    def run(self, state: AnalysisState) -> dict:
        print("\n[Critic] 审查 SQL...")
        try:
            sql = state['current_sql']

            # 步骤1：数据库预执行验证（如果启用）
            if ENABLE_SQL_VALIDATION and USE_REAL_DB:
                print("  ℹ️  执行数据库预验证...")
                is_valid, db_error = self._validate_sql_with_db(sql)

                if not is_valid:
                    # 数据库直接报错，无需 LLM 审查
                    print(f"  ❌ 数据库验证失败")
                    return {
                        "critic_verdict": "REJECTED",
                        "critic_feedback": f"REJECTED\n\n数据库验证失败：\n{db_error}\n\n请根据此错误修正 SQL。",
                        "history": state.get("history", []) + [f"[Critic] 数据库验证失败：{db_error[:100]}"],
                    }

                print("  ✅ 数据库验证通过")

            # 步骤2：LLM 逻辑审查
            review = _call_llm(
                system=self.SYSTEM_PROMPT,
                user=f"查询计划：\n{state['query_plan']}\n\nSQL：\n{sql}",
                use_cache=True,
            )

            # 更健壮的判断解析
            first_line = review.strip().split("\n")[0].upper()
            verdict = "APPROVED" if "APPROVED" in first_line else "REJECTED"
            feedback = review if verdict == "REJECTED" else None

            log_entry = f"[Critic] 审查结果：{verdict}"
            print(f"  结果：{verdict}")
            if feedback:
                print(f"  反馈：{feedback[:200]}")

            return {
                "critic_verdict": verdict,
                "critic_feedback": feedback,
                "history": state.get("history", []) + [log_entry],
            }
        except Exception as e:
            error_msg = f"[Critic] 失败: {str(e)}"
            print(f"  ❌ {error_msg}")
            return {
                "error_message": error_msg,
                "history": state.get("history", []) + [error_msg],
            }


# ════════════════════════════════════════════════════════════════
# 4. Executor —— SQL 执行节点（非 LLM，纯工具调用）
# ════════════════════════════════════════════════════════════════

def executor_node(state: AnalysisState) -> dict:
    """执行 SQL 并将结果写入 State。"""
    print("\n[Executor] 执行 SQL...")
    try:
        result = execute_sql(state["current_sql"])
        log_entry = f"[Executor] SQL 执行完成，返回 {result.row_count} 行"
        print(f"  {log_entry}")
        return {
            "query_result": result.to_dict(),
            "history": state.get("history", []) + [log_entry],
        }
    except Exception as e:
        error_msg = f"[Executor] SQL 执行失败: {str(e)}"
        print(f"  ❌ {error_msg}")
        return {
            "error_message": error_msg,
            "history": state.get("history", []) + [error_msg],
        }


# ════════════════════════════════════════════════════════════════
# 5. Reporter —— 输出者
# ════════════════════════════════════════════════════════════════

class ReporterAgent:
    """基于查询结果撰写包含业务洞察的最终报告。"""

    SYSTEM_PROMPT = """你是一位资深业务分析师。
根据用户问题和数据查询结果，撰写一份专业的业务分析报告。
报告要求：
1. 直接回答用户的业务问题
2. 提炼关键数据指标和趋势
3. 给出 2-3 条可落地的业务建议
4. 语言简洁专业，使用中文
5. 报告结构：【核心结论】→【数据解读】→【业务建议】"""

    def run(self, state: AnalysisState) -> dict:
        print("\n[Reporter] 撰写分析报告...")
        try:
            # 检查是否有错误或达到最大重试次数
            error_msg = state.get("error_message")
            iteration = state.get("iteration_count", 0)
            verdict = state.get("critic_verdict")

            # 场景1：有错误信息
            if error_msg:
                report = f"""## 分析失败

很抱歉，系统在处理您的问题时遇到了技术问题：

**错误信息：**
{error_msg}

**建议：**
1. 请检查问题描述是否清晰
2. 如果涉及特定表或字段，请确认数据库中是否存在
3. 可以尝试简化问题后重新提问

如需人工协助，请联系技术支持团队。"""
                log_entry = "[Reporter] 生成错误报告"

            # 场景2：达到最大重试次数但 SQL 仍未通过审查
            elif iteration >= MAX_ITERATIONS and verdict == "REJECTED":
                critic_feedback = state.get("critic_feedback", "未知错误")
                report = f"""## 分析受阻

经过 {MAX_ITERATIONS} 次尝试，系统未能生成完全准确的 SQL 查询。

**当前遇到的技术阻碍：**
{critic_feedback}

**可能的原因：**
1. 问题描述过于复杂，超出当前系统能力
2. 数据库表结构与问题需求不匹配
3. 需要更复杂的多表关联或子查询

**建议：**
1. 尝试将问题拆分为多个简单问题
2. 人工介入排查数据库表结构
3. 联系数据分析师协助编写 SQL

**用户原始问题：**
{state['user_question']}"""
                log_entry = "[Reporter] 生成降级报告"

            # 场景3：正常情况，有查询结果
            else:
                query_result = state.get('query_result', {})

                # 检查是否有数据截断警告
                warning = query_result.get('warning', '')
                warning_section = f"\n\n**⚠️ 数据说明：**\n{warning}" if warning else ""

                report = _call_llm(
                    system=self.SYSTEM_PROMPT,
                    user=(
                        f"用户问题：{state['user_question']}\n\n"
                        f"查询结果：\n{query_result}{warning_section}"
                    ),
                    use_cache=True,
                )
                log_entry = "[Reporter] 报告生成完成"

            print(f"  报告长度：{len(report)} 字符")
            return {
                "final_report": report,
                "history": state.get("history", []) + [log_entry],
            }
        except Exception as e:
            error_msg = f"[Reporter] 失败: {str(e)}"
            print(f"  ❌ {error_msg}")
            return {
                "error_message": error_msg,
                "history": state.get("history", []) + [error_msg],
            }

"""
feishu_server.py
飞书机器人 HTTP 服务器 —— 接收飞书事件，处理用户问题，返回分析报告。

运行方式：
    python feishu_server.py

配置要求：
1. .env 中配置飞书应用凭证
2. 在飞书开放平台配置事件订阅 URL：http://your-domain:8000/feishu/webhook
3. 配置机器人权限和事件订阅
"""

import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入项目模块
from tools.feishu_bot import create_feishu_bot
from workflow import workflow
from core.state import AnalysisState

# 创建 Flask 应用
app = Flask(__name__)

# 创建飞书机器人实例
feishu_bot = create_feishu_bot()

print("=" * 60)
print("🚀 飞书数据分析机器人服务器启动")
print("=" * 60)
print(f"监听端口: 8000")
print(f"Webhook URL: http://your-domain:8000/feishu/webhook")
print(f"API 提供商: {os.environ.get('API_PROVIDER', 'siliconflow')}")
print(f"LLM 模型: {os.environ.get('LLM_MODEL', 'deepseek-v4-flash')}")
print(f"数据库模式: {'真实 MySQL' if os.environ.get('USE_REAL_DB') == 'true' else 'Mock'}")
print("=" * 60)


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口。"""
    return jsonify({
        "status": "ok",
        "service": "feishu-data-analysis-bot",
        "api_provider": os.environ.get('API_PROVIDER', 'siliconflow'),
        "model": os.environ.get('LLM_MODEL', 'deepseek-v4-flash')
    })


@app.route('/feishu/webhook', methods=['POST'])
def feishu_webhook():
    """
    飞书事件回调接口。

    处理流程：
    1. 验证签名
    2. 解析事件
    3. 提取用户问题
    4. 调用 Multi-Agent 系统分析
    5. 返回分析报告
    """
    try:
        # 获取请求数据
        request_body = request.get_json()

        # 【新增逻辑：打印最原始的数据包，用于彻底排查黑盒问题】
        print(f"\n👉 收到飞书原始数据包: {json.dumps(request_body, ensure_ascii=False)}")

        # 验证签名（可选）
        headers = request.headers
        timestamp = headers.get('X-Lark-Request-Timestamp', '')
        nonce = headers.get('X-Lark-Request-Nonce', '')
        signature = headers.get('X-Lark-Signature', '')

        # 解析事件
        event = feishu_bot.parse_event(request_body)

        # URL 验证（首次配置时）
        if "challenge" in event:
            print("✅ URL 验证成功")
            return jsonify(event)

        # 提取消息内容
        message_content = feishu_bot.extract_message_content(event)

        # 【新增逻辑：暴力兜底提取。如果内置方法失败，强制手动解析 V2 格式】
        if not message_content and request_body.get("header", {}).get("event_type") == "im.message.receive_v1":
            try:
                content_str = request_body.get("event", {}).get("message", {}).get("content", "{}")
                content_dict = json.loads(content_str)
                message_content = content_dict.get("text", "").strip()
                if message_content:
                    print("✅ 触发兜底机制：成功提取到文本！")
            except Exception as e:
                print("⚠️ 兜底解析报错:", e)

        if not message_content:
            print("⚠️  无法提取消息内容，跳过处理")
            return jsonify({"code": 0})

        # 获取发送者信息
        sender = event.get("sender", {})
        sender_id = sender.get("sender_id", {}).get("open_id", "")

        print(f"\n{'='*60}")
        print(f"📩 收到用户问题")
        print(f"{'='*60}")
        print(f"发送者: {sender_id}")
        print(f"问题: {message_content}")
        print(f"{'='*60}\n")

        # 先回复"正在分析中"
        feishu_bot.send_text_message(
            receive_id=sender_id,
            text="🤖 收到您的问题，正在分析中，请稍候...",
            receive_id_type="open_id"
        )

        # 调用 Multi-Agent 系统分析
        try:
            initial_state: AnalysisState = {
                "user_question": message_content,
                "query_plan": "",
                "current_sql": "",
                "critic_verdict": "",
                "critic_feedback": None,
                "query_result": {},
                "final_report": "",
                "iteration_count": 0,
                "error_message": None,
                "history": [],
            }

            # 执行工作流
            final_state = workflow.invoke(initial_state)

            # 提取结果
            report = final_state.get("final_report", "分析失败，未生成报告")
            sql = final_state.get("current_sql", "")

            print(f"\n{'='*60}")
            print(f"✅ 分析完成")
            print(f"{'='*60}")
            print(f"报告长度: {len(report)} 字符")
            print(f"SQL: {sql[:100]}..." if sql else "无 SQL")
            print(f"{'='*60}\n")

            # 发送卡片消息
            card = feishu_bot.format_report_as_card(
                question=message_content,
                report=report,
                sql=sql
            )

            response = feishu_bot.send_card_message(
                receive_id=sender_id,
                card_content=card,
                receive_id_type="open_id"
            )

            if response.get("code") != 0:
                print(f"❌ 发送卡片失败: {response}")
                # 降级为文本消息
                feishu_bot.send_text_message(
                    receive_id=sender_id,
                    text=f"📊 分析报告\n\n{report}",
                    receive_id_type="open_id"
                )

        except Exception as e:
            print(f"❌ 分析失败: {str(e)}")
            import traceback
            traceback.print_exc()

            # 发送错误消息
            feishu_bot.send_text_message(
                receive_id=sender_id,
                text=f"❌ 分析失败：{str(e)}\n\n请稍后重试或联系管理员。",
                receive_id_type="open_id"
            )

        return jsonify({"code": 0})

    except Exception as e:
        print(f"❌ Webhook 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"code": -1, "msg": str(e)}), 500


@app.route('/test', methods=['POST'])
def test_analysis():
    """
    测试接口：直接发送问题，返回分析结果（不通过飞书）。

    请求示例：
    POST /test
    {
        "question": "分析过去一个月的销售趋势"
    }
    """
    try:
        data = request.get_json()
        question = data.get("question", "")

        if not question:
            return jsonify({"error": "缺少 question 参数"}), 400

        print(f"\n{'='*60}")
        print(f"🧪 测试分析")
        print(f"{'='*60}")
        print(f"问题: {question}")
        print(f"{'='*60}\n")

        # 调用工作流
        initial_state: AnalysisState = {
            "user_question": question,
            "query_plan": "",
            "current_sql": "",
            "critic_verdict": "",
            "critic_feedback": None,
            "query_result": {},
            "final_report": "",
            "iteration_count": 0,
            "error_message": None,
            "history": [],
        }

        final_state = workflow.invoke(initial_state)

        return jsonify({
            "question": question,
            "report": final_state.get("final_report", ""),
            "sql": final_state.get("current_sql", ""),
            "history": final_state.get("history", [])
        })

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # 启动服务器
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
"""
test_api.py
测试 API 连接是否正常
"""

import os
from dotenv import load_dotenv

load_dotenv()

API_PROVIDER = os.environ.get("API_PROVIDER", "siliconflow")
MODEL = os.environ.get("LLM_MODEL", "deepseek-v4-flash")

print(f"测试 API 提供商: {API_PROVIDER}")
print(f"测试模型: {MODEL}")
print("-" * 50)

try:
    if API_PROVIDER == "siliconflow":
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ.get("SILICONFLOW_API_KEY"),
            base_url="https://api.siliconflow.cn/v1"
        )

        print("发送测试请求...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个数据分析助手。"},
                {"role": "user", "content": "用一句话介绍你自己。"}
            ],
            max_tokens=100,
        )

        print("✅ API 连接成功！")
        print(f"模型响应: {response.choices[0].message.content}")
        print(f"Token 使用: {response.usage.total_tokens} tokens")

    elif API_PROVIDER == "anthropic":
        import anthropic

        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        print("发送测试请求...")
        message = client.messages.create(
            model=MODEL,
            max_tokens=100,
            messages=[
                {"role": "user", "content": "用一句话介绍你自己。"}
            ]
        )

        print("✅ API 连接成功！")
        print(f"模型响应: {message.content[0].text}")
        print(f"Token 使用: {message.usage.input_tokens + message.usage.output_tokens} tokens")

    else:
        print(f"❌ 不支持的 API_PROVIDER: {API_PROVIDER}")

except Exception as e:
    print(f"❌ API 连接失败: {type(e).__name__}")
    print(f"错误信息: {str(e)}")
    print("\n请检查：")
    print("1. .env 文件是否正确配置")
    print("2. API Key 是否有效")
    print("3. 网络连接是否正常")

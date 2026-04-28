"""
tools/feishu_bot.py
飞书机器人真实集成 —— 接收用户问题，返回分析报告。

使用方式：
1. 在飞书开放平台创建应用：https://open.feishu.cn/
2. 配置机器人权限：im:message, im:message.group_at_msg
3. 配置事件订阅：接收消息 v2.0
4. 获取 App ID 和 App Secret
5. 配置 .env 文件
6. 运行 feishu_server.py 启动 HTTP 服务器
"""

import os
import json
import hashlib
import hmac
from typing import Dict, Any, Optional
from datetime import datetime


class FeishuBot:
    """飞书机器人客户端（真实实现）。"""

    def __init__(self):
        self.app_id = os.environ.get("FEISHU_APP_ID")
        self.app_secret = os.environ.get("FEISHU_APP_SECRET")
        self.verification_token = os.environ.get("FEISHU_VERIFICATION_TOKEN", "")
        self.encrypt_key = os.environ.get("FEISHU_ENCRYPT_KEY", "")

        if not self.app_id or not self.app_secret:
            raise ValueError("请在 .env 中配置 FEISHU_APP_ID 和 FEISHU_APP_SECRET")

        self._access_token = None
        self._token_expires_at = 0

    # ════════════════════════════════════════════════════════════════
    # 认证相关
    # ════════════════════════════════════════════════════════════════

    def _get_tenant_access_token(self) -> str:
        """
        获取 tenant_access_token（企业自建应用）。

        文档：https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal
        """
        import requests
        import time

        # 检查缓存的 token 是否过期
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, json=payload)
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"获取 access_token 失败: {data}")

        self._access_token = data["tenant_access_token"]
        self._token_expires_at = time.time() + data.get("expire", 7200) - 60  # 提前1分钟刷新

        return self._access_token

    # ════════════════════════════════════════════════════════════════
    # 发送消息
    # ════════════════════════════════════════════════════════════════

    def send_text_message(self, receive_id: str, text: str, receive_id_type: str = "open_id") -> Dict[str, Any]:
        """
        发送文本消息。

        Args:
            receive_id: 接收者 ID（open_id / user_id / chat_id）
            text: 消息内容
            receive_id_type: ID 类型（open_id / user_id / chat_id）

        Returns:
            API 响应

        文档：https://open.feishu.cn/document/server-docs/im-v1/message/create
        """
        import requests

        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {self._get_tenant_access_token()}",
            "Content-Type": "application/json"
        }
        params = {
            "receive_id_type": receive_id_type
        }
        payload = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": text})
        }

        response = requests.post(url, headers=headers, params=params, json=payload)
        return response.json()

    def send_card_message(self, receive_id: str, card_content: Dict, receive_id_type: str = "open_id") -> Dict[str, Any]:
        """
        发送卡片消息（富文本）。

        Args:
            receive_id: 接收者 ID
            card_content: 卡片内容（JSON 格式）
            receive_id_type: ID 类型

        Returns:
            API 响应

        文档：https://open.feishu.cn/document/server-docs/im-v1/message-card/create-card
        """
        import requests

        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {self._get_tenant_access_token()}",
            "Content-Type": "application/json"
        }
        params = {
            "receive_id_type": receive_id_type
        }
        payload = {
            "receive_id": receive_id,
            "msg_type": "interactive",
            "content": json.dumps(card_content)
        }

        response = requests.post(url, headers=headers, params=params, json=payload)
        return response.json()

    # ════════════════════════════════════════════════════════════════
    # 接收事件
    # ════════════════════════════════════════════════════════════════

    def verify_signature(self, timestamp: str, nonce: str, encrypt: str, signature: str) -> bool:
        """
        验证飞书事件签名。

        文档：https://open.feishu.cn/document/server-docs/event-subscription/configure-event-subscription/request-url-configuration
        """
        if not self.verification_token:
            return True  # 未配置 token，跳过验证

        # 拼接字符串
        sign_str = f"{timestamp}{nonce}{self.verification_token}{encrypt}"

        # 计算 SHA-256
        calculated_signature = hashlib.sha256(sign_str.encode()).hexdigest()

        return calculated_signature == signature

    def parse_event(self, request_body: Dict) -> Optional[Dict[str, Any]]:
        """
        解析飞书事件。

        Args:
            request_body: HTTP 请求 body（已解析为 dict）

        Returns:
            事件数据，如果是 URL 验证则返回 challenge
        """
        # URL 验证（首次配置事件订阅时）
        if request_body.get("type") == "url_verification":
            return {
                "challenge": request_body.get("challenge")
            }

        # 正常事件
        event = request_body.get("event", {})
        return event

    def extract_message_content(self, event: Dict) -> Optional[str]:
        """
        从事件中提取用户消息内容。

        Args:
            event: 事件数据

        Returns:
            消息文本内容
        """
        message = event.get("message", {})
        msg_type = message.get("msg_type")

        if msg_type == "text":
            content = json.loads(message.get("content", "{}"))
            return content.get("text", "").strip()

        return None

    # ════════════════════════════════════════════════════════════════
    # 格式化分析报告为卡片
    # ════════════════════════════════════════════════════════════════

    def format_report_as_card(self, question: str, report: str, sql: str = "") -> Dict:
        """
        将分析报告格式化为飞书卡片消息。

        Args:
            question: 用户问题
            report: 分析报告
            sql: 生成的 SQL（可选）

        Returns:
            卡片 JSON
        """
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**用户问题：**\n{question}"
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**分析报告：**\n{report}"
                }
            }
        ]

        # 如果有 SQL，添加到卡片
        if sql:
            elements.extend([
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**生成的 SQL：**\n```sql\n{sql}\n```"
                    }
                }
            ])

        # 添加时间戳
        elements.append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })

        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": "blue",
                "title": {
                    "tag": "plain_text",
                    "content": "📊 数据分析报告"
                }
            },
            "elements": elements
        }

        return card


# ════════════════════════════════════════════════════════════════
# 便捷函数
# ════════════════════════════════════════════════════════════════

def create_feishu_bot() -> FeishuBot:
    """创建飞书机器人实例。"""
    return FeishuBot()

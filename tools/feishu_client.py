"""
tools/feishu_client.py
飞书 Mock 客户端 —— 预留消息收发接口。
真实场景替换为飞书开放平台 SDK 调用即可。
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional


class FeishuClient:
    """
    飞书消息客户端（Mock 实现）。

    真实接入时，需要：
    1. pip install lark-oapi
    2. 配置 APP_ID / APP_SECRET（从 os.environ 读取）
    3. 替换下方方法体为真实 SDK 调用
    """

    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        import os
        self.app_id = app_id or os.environ.get("FEISHU_APP_ID", "mock_app_id")
        self.app_secret = app_secret or os.environ.get("FEISHU_APP_SECRET", "mock_secret")
        self._message_log: list = []  # 本地记录，便于调试

    # ──────────────────────────────────────────────────────────────
    # 发送消息
    # ──────────────────────────────────────────────────────────────
    def send_message(
        self,
        chat_id: str,
        content: str,
        msg_type: str = "text",
    ) -> Dict[str, Any]:
        """
        向指定飞书会话发送消息。

        Args:
            chat_id:  飞书 chat_id 或 open_id
            content:  消息正文（text 类型直接传字符串；card 类型传 JSON 字符串）
            msg_type: "text" | "interactive"（卡片消息）

        Returns:
            模拟的 API 响应体

        TODO: 替换为真实实现，例如：
            import lark_oapi as lark
            client = lark.Client.builder().app_id(self.app_id)...build()
            request = CreateMessageRequest.builder()...build()
            response = client.im.v1.message.create(request)
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id,
            "msg_type": msg_type,
            "content": content,
        }
        self._message_log.append(record)

        print(f"[FeishuClient MOCK] 发送消息 → chat_id={chat_id}")
        print(f"  内容预览: {content[:120]}{'...' if len(content) > 120 else ''}")

        return {"code": 0, "msg": "success", "data": {"message_id": f"mock_msg_{len(self._message_log)}"}}

    # ──────────────────────────────────────────────────────────────
    # 接收事件
    # ──────────────────────────────────────────────────────────────
    def receive_event(self, raw_body: bytes, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        解析飞书推送的 Webhook 事件（消息、回调等）。

        Args:
            raw_body: HTTP 请求原始 body
            headers:  HTTP 请求头（含签名验证字段）

        Returns:
            解析后的事件字典，验签失败返回 None

        TODO: 替换为真实实现，例如：
            from lark_oapi.event.dispatcher import EventDispatcherHandler
            handler = EventDispatcherHandler.builder(encrypt_key, verification_token)...build()
            handler.do(lark.RawRequest(headers=headers, body=raw_body))
        """
        print("[FeishuClient MOCK] 收到 Webhook 事件（Mock 解析）")
        try:
            event = json.loads(raw_body)
            return event
        except json.JSONDecodeError:
            return None

"""
AI 工作團隊 - 指揮中心（Orchestrator）
Virtual AI Work Team - Orchestrator
"""

import json
import re
import httpx
from typing import Optional
from agents import TEAM_LEAD, get_agent, Agent

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CLAUDE_API_KEY = ""  # 在 app.py 或環境變數中設定


def set_api_key(key: str):
    global CLAUDE_API_KEY
    CLAUDE_API_KEY = key


def _call_claude(system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
    """呼叫 Claude API"""
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    body = {
        "model": CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}],
    }
    with httpx.Client(timeout=30) as client:
        resp = client.post(CLAUDE_API_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]


def _parse_team_lead_response(raw: str) -> dict:
    """解析隊長的 JSON 回應"""
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{[^{}]+\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"agent": "general", "task": raw, "reason": "無法解析隊長指令，使用通才"}


def route_and_respond(user_message: str) -> dict:
    """
    主要流程：
    1. 隊長分析任務
    2. 派發給對應成員
    3. 成員執行並回覆
    """

    try:
        lead_raw = _call_claude(
            system_prompt=TEAM_LEAD.system_prompt,
            user_message=user_message,
            max_tokens=300,
        )
        routing = _parse_team_lead_response(lead_raw)
    except Exception as e:
        routing = {"agent": "general", "task": user_message, "reason": f"隊長無法連線: {e}"}

    agent_role = routing.get("agent", "general")
    refined_task = routing.get("task", user_message)

    agent = get_agent(agent_role)

    try:
        response_text = _call_claude(
            system_prompt=agent.system_prompt,
            user_message=refined_task,
            max_tokens=1024,
        )
    except Exception as e:
        response_text = f"很抱歉，{agent.name} 目前無法回應（{e}）。請稍後再試。— 系統通知"

    return {
        "agent_name": agent.name,
        "agent_role": agent.role,
        "emoji": agent.emoji,
        "response": response_text,
        "routing": routing,
    }


def format_line_message(result: dict) -> str:
    """格式化成 Line 訊息"""
    return result["response"]


if __name__ == "__main__":
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    set_api_key(api_key)

    test_messages = [
        "幫我規劃下個月 BLUE IP 跟 iPE Taiwan 的內容方向",
        "幫我寫一篇 Porsche 911 的 IG 圖文 caption",
        "幫我規劃一支 GT3 RS 試駕的影片腳本",
        "追蹤一下上週跟那個賽道品牌的合作談得怎樣了",
        "我上週的 Reels 表現怎麼樣？",
    ]

    for msg in test_messages:
        print(f"\n用戶：{msg}")
        result = route_and_respond(msg)
        print(f"→ 隊長派發給：{result['agent_name']} {result['emoji']}")
        print(f"→ 回覆：{result['response'][:100]}...")
        print("-" * 50)

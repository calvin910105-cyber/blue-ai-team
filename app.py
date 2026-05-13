"""
AI 工作團隊 - Line OA Webhook Server
Virtual AI Work Team - FastAPI Webhook Server

啟動方式: uvicorn app:app --host 0.0.0.0 --port 8000
"""

import os
import json
import hmac
import hashlib
import base64
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import orchestrator

# ============================================================
# 設定（從環境變數讀取）
# ============================================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")

# 設定 Orchestrator 的 API Key
orchestrator.set_api_key(ANTHROPIC_API_KEY)

app = FastAPI(title="AI 工作團隊 Webhook", version="1.0.0")


# ============================================================
# Line 簽名驗證
# ============================================================
def verify_line_signature(body: bytes, signature: str) -> bool:
    """驗證 Line Webhook 簽名"""
    if not LINE_CHANNEL_SECRET:
        return True  # 開發模式跳過驗證
    hash_val = hmac.new(
        LINE_CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    expected = base64.b64encode(hash_val).decode("utf-8")
    return hmac.compare_digest(expected, signature)


# ============================================================
# Line Reply API
# ============================================================
async def send_line_reply(reply_token: str, text: str):
    """透過 Line Messaging API 回覆訊息"""
    if len(text) > 4900:
        text = text[:4900] + "...\n（訊息已截短）"

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            "https://api.line.me/v2/bot/message/reply",
            headers={
                "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "replyToken": reply_token,
                "messages": [{"type": "text", "text": text}],
            },
        )
        if resp.status_code != 200:
            print(f"[Line API Error] {resp.status_code}: {resp.text}")
        return resp.status_code


# ============================================================
# 主 Webhook 端點
# ============================================================
@app.post("/webhook/line")
async def line_webhook(request: Request):
    """接收 Line OA Webhook 事件"""
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")

    if not verify_line_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    for event in data.get("events", []):
        if event.get("type") != "message":
            continue
        if event.get("message", {}).get("type") != "text":
            continue

        reply_token = event.get("replyToken", "")
        user_text = event["message"]["text"]

        print(f"[收到訊息] {user_text}")

        try:
            result = orchestrator.route_and_respond(user_text)
            reply_text = orchestrator.format_line_message(result)
            print(f"[派發給] {result['agent_name']} → 回覆長度: {len(reply_text)}")
        except Exception as e:
            reply_text = f"系統發生錯誤：{str(e)}\n請稍後再試。"
            print(f"[錯誤] {e}")

        await send_line_reply(reply_token, reply_text)

    return JSONResponse({"status": "ok"})


# ============================================================
# 健康檢查
# ============================================================
@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "BLUE 哺路 AI 工作團隊",
        "agents": ["🎯 Team Lead", "👔 策略長 Rae", "🤝 經紀人 Sonny", "✍️ 文案 阿文", "🎬 企劃 阿劃", "📊 數據 阿數", "😊 助理"],
    }


@app.get("/team")
def show_team():
    """顯示團隊成員"""
    from agents import AGENTS
    return {
        role: {
            "name": agent.name,
            "emoji": agent.emoji,
            "description": agent.description,
        }
        for role, agent in AGENTS.items()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 🤖 BLUE 哺路 AI 工作團隊 × Line OA

透過 Line OA 與 AI 工作團隊對話。傳訊息進去，隊長自動判斷應該派給哪位成員處理。

## 團隊成員

| 成員 | 負責 |
|------|------|
| 🎯 Team Lead | 分析任務、決定派發方向（不對外發言） |
| 👔 策略長 Rae | 品牌策略、內容規劃、BLUE IP × iPE Taiwan 雙線佈局 |
| 🤝 經紀人 Sonny | 合作開發、洽談追蹤、排程管理 |
| ✍️ 文案 阿文 | IG 圖文、限時動態、Reels 描述、影片旁白 |
| 🎬 企劃 阿劃 | 影片腳本、拍攝企劃、內容選題、五大武器應用 |
| 📊 數據 阿數 | 後台數據分析、內容成效評估、策略建議 |
| 😊 助理 | 日常問答、行程確認、一般事務 |

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
cp .env.example .env
# 編輯 .env 填入你的 API keys
```

### 3. 啟動伺服器

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 設定 Line OA Webhook

Webhook URL：`https://你的域名/webhook/line`

## 部署（Render.com 免費方案）

1. 上傳到 GitHub（已完成）
2. 前往 render.com 建立 Web Service
3. 連結此 repo
4. 設定環境變數：ANTHROPIC_API_KEY、LINE_CHANNEL_SECRET、LINE_CHANNEL_ACCESS_TOKEN
5. 把 Render URL + `/webhook/line` 填到 Line Developers Console

## 架構

```
Line 用戶 → Line OA → Webhook → Team Lead 路由 → 專屬成員回應 → Line 用戶
```

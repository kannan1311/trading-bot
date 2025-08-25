import os
from flask import Flask, request, jsonify
import requests
from openai import OpenAI

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, json=payload)

@app.route("/", methods=["GET"])
def health():
    return "✅ TradingView ↔ ChatGPT ↔ Telegram bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    symbol = str(data.get("symbol", "unknown"))
    price = str(data.get("price", "unknown"))
    rsi   = str(data.get("RSI", data.get("rsi", "unknown")))
    tf    = str(data.get("timeframe", data.get("tf", "unknown")))

    prompt = f"""
    Symbol: {symbol}
    Price: {price}
    RSI: {rsi}
    Timeframe: {tf}

    Give a short 2–3 line analysis (bullish/bearish/neutral).
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=120,
    )
    analysis = resp.choices[0].message.content.strip()
    msg = f"⚡ TradingView Alert ⚡\n{symbol} @ {price}\nRSI: {rsi} | TF: {tf}\n\n🧠 {analysis}"

    send_telegram(msg)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))


from flask import Flask
import threading, time, datetime
import yfinance as yf
import pandas as pd
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
SYMBOL = "^NSEI"

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def check_strategy():
    while True:
        try:
            df = yf.download(SYMBOL, period="5d", interval="5m", progress=False)
            if len(df) < 25:
                time.sleep(60)
                continue
            df['EMA5'] = df['Close'].ewm(span=5).mean()
            df['EMA20'] = df['Close'].ewm(span=20).mean()
            last = df.iloc[-2]
            curr = df.iloc[-1]
            if last['EMA5'] < last['EMA20'] and curr['EMA5'] > curr['EMA20']:
                send_telegram(f"🟢 BUY NIFTY ALERT Price: {curr['Close']:.2f}")
            if last['EMA5'] > last['EMA20'] and curr['EMA5'] < curr['EMA20']:
                send_telegram(f"🔴 SELL NIFTY ALERT Price: {curr['Close']:.2f}")
        except Exception as e:
            print(e)
        time.sleep(60)

@app.route('/')
def home():
    return "Nifty_5_20_bot_023_bot Running ✅"

threading.Thread(target=check_strategy, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

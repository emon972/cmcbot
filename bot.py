import os
import time
import requests
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("8516117315:AAGSiVjHDiUpEwdQIRp8MDwEJOs-OxmBw70")
CHAT_ID = os.getenv("1987110638")
CMC_API_KEY = os.getenv("9b0b885a4f3c4cc998a4a10c0b911bd0")

bot = Bot(token=TELEGRAM_TOKEN)

SKIP_EXCHANGES = [
    "Binance", "Coinbase", "OKX", "Bybit", "Kraken",
    "Gate.io", "Gemini", "Bitstamp", "Crypto.com", "Biconomy"
]

def get_cmc_listings():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"start": "1", "limit": "200", "convert": "USD"}

    r = requests.get(url, headers=headers, params=params)
    return r.json().get("data", [])

def get_coin_info(coin_id):
    url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"id": coin_id}

    r = requests.get(url, headers=headers, params=params)
    return r.json()["data"][str(coin_id)]

def is_dead_coin(coin):
    quote = coin["quote"]["USD"]
    return quote["market_cap"] < 300000 or quote["volume_24h"] < 10000

def is_listed_on_big_cex(urls):
    for v in urls.values():
        if isinstance(v, list):
            for link in v:
                for ex in SKIP_EXCHANGES:
                    if ex.lower() in link.lower():
                        return True
    return False

def extract_telegram(urls):
    for v in urls.values():
        if isinstance(v, list):
            for link in v:
                if "t.me" in link or "telegram.me" in link:
                    return link
    return "Not found"

def run():
    coins = get_cmc_listings()

    for coin in coins:
        if is_dead_coin(coin):
            continue

        info = get_coin_info(coin["id"])
        urls = info.get("urls", {})

        if is_listed_on_big_cex(urls):
            continue

        telegram_link = extract_telegram(urls)

        message = f"""
🪙 {coin['name']} ({coin['symbol']})

🔗 CMC:
https://coinmarketcap.com/currencies/{coin['slug']}/

📢 Telegram:
{telegram_link}
        """

        bot.send_message(chat_id=CHAT_ID, text=message)
        time.sleep(2)

while True:
    run()
    time.sleep(3600)  # runs every 1 hour

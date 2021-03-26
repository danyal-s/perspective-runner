# %%
import time
import datetime
from flask import Flask
import config
import os
from binance.client import Client
import requests
APP_CONFIG = None

if os.environ.get("APP_ENV", "dev") in ("dev", "prod"):
    APP_CONFIG = config.DevelopmentConfig()

b_client = Client(APP_CONFIG.BINANCE_API_KEY, APP_CONFIG.BINANCE_API_SECRET)
app = Flask(__name__)

def main():
    app.run(host='0.0.0.0', port=APP_CONFIG.BACKEND_API_PORT)

@app.route('/')
def hello():
    return {
                "message":"Hello World!"
           }

@app.route("/binance_assets")
def get_binance_assets():
    return {"res": [d for d in b_client.get_account()["balances"] if float(d["free"]) > 0]}


def get_all_eth_transactions():
    r = requests.get(f"https://api.etherscan.io/api?module=account&action=txlist&address=0xbA431c3f9B6dFB27450616506B330E3Dd5f72E0a&startblock=12082330&endblock=99999999&sort=asc&apikey={APP_CONFIG.ETHERSCAN_API_KEY}")
    eth_transactions = r.json()["result"]
    return {
            "res": eth_transactions
            }

if __name__ == "__main__":
    main()

# %%
# %%

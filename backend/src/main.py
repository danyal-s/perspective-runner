# %%
import time
import datetime
from flask import Flask
import config
import os
from binance.client import Client

APP_CONFIG = None

if os.environ.get(["APP_ENV"], "dev") in ("dev", "prod"):
    APP_CONFIG = config.DevelopmentConfig()

b_client = Client(APP_CONFIG.BINANCE_API_KEY, APP_CONFIG.BINANCE_API_SECRET)
app = Flask(__name__)

def main():
    app.run(host='0.0.0.0', port=5001)

@app.route('/')
def hello():
    return {
                "message":"Hello World!"
           }

@app.route("binance_assets")
def get_binance_assets():
    return [d for d in b_client.get_account()["balances"] if float(d["free"]) > 0]

if __name__ == "__main__":
    main()

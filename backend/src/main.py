# %%
import time
import datetime
from flask import Flask, Blueprint
from flask_restx import Api, Resource, fields
import config
import os
from binance.client import Client
import requests
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

APP_CONFIG = None

if os.environ.get("APP_ENV", "dev") in ("dev", "prod"):
    APP_CONFIG = config.DevelopmentConfig()

b_client = Client(APP_CONFIG.BINANCE_API_KEY, APP_CONFIG.BINANCE_API_SECRET)
app = Flask(__name__)

bp = Blueprint('api', __name__, url_prefix="/api")
api = Api(  bp, 
            version='1.0', 
            title='Backend API',
            description='This should get all my crypto data')
app.register_blueprint(bp)

class CryptoExternalAPIStore(object):

    def __init__(self, api_call_delay=60):
        self.time = time.time()
        self.results_store = {}
        self.api_delay = api_call_delay


    def get_from_external_api(self, url):
        return requests.get(url)


    def _set_results_store(self, url, r):
        if url not in self.results_store.keys():
            self.results_store[url] = {}

        self.results_store[url]["retrieval_time"] = time.time()
        self.results_store[url]["result"] = r


    def _get_from_results_store(self, url):
        return self.results_store[url]

    def _process_result(self, r):
        return r.json()

    def get(self, url):
        if url in self.results_store.keys():
            if time.time() - self._get_from_results_store(url)["retrieval_time"] > self.api_delay:
                try:
                    r = self.get_from_external_api(url)
                except Exception as e:
                    return None

                self._set_results_store(url, r)

            else:
                r = self._get_from_results_store(url)["result"]
        else:
            try:
                r = self.get_from_external_api(url)
                self._set_results_store(url, r)
            except Exception as e:
                logger.exception(e)
                return None
         
        return self._process_result(r)

class BinanceCryptoExternalAPIStore(CryptoExternalAPIStore):
    def __init__(self, api_call_delay=None, b_client=None):
        if api_call_delay is None:
            api_call_delay = 60
        if b_client is None:
            raise ValueError("Required parameter b_client not passed")
    
        super().__init__(api_call_delay)
        self.b_client = b_client

    def get_from_external_api(self, action):
        if action == "get_crypto_prices":
            res = self.b_client.get_all_tickers()

        return res
    
    def _process_result(self, r):
        return r

b_client.get_all_tickers()

external_api_res_store = CryptoExternalAPIStore(30)
binance_api_res_store = BinanceCryptoExternalAPIStore(10, b_client=b_client)


def get_all_crypto_prices():
    crypto_prices = binance_api_res_store.get("get_crypto_prices")
    for di in crypto_prices:
        di["price"] = float(di["price"])
    
    return crypto_prices


def get_crypto_price(crypto_symbol, liquid_cond=None):
    if liquid_cond is None:
        liquid_cond = lambda crypto_symbol, x: crypto_symbol in x["symbol"] and (("USDC" in x["symbol"]) or ("USDT" in x["symbol"]))

    crypto_prices = get_all_crypto_prices()
    found_price = [x for x in crypto_prices if liquid_cond(crypto_symbol, x)]
    if len(found_price) == 0:
        if crypto_symbol.startswith("W"):
            found_price = [x for x in crypto_prices if liquid_cond(crypto_symbol[1:], x)]
            if len(found_price) == 0:
                price = None
            else:
                price = float(found_price[0]["price"])
        else:
            price = None
    else:
        price = float(found_price[0]["price"])
    
    return price


def get_binance_cryptos():
    crypto_details = [d for d in b_client.get_account()["balances"] if float(d["free"]) > 0]
    for di in crypto_details:
        di["free"] = float(di["free"])

    return crypto_details

def get_binance_assets():
    crypto_details = [d for d in b_client.get_account()["balances"] if float(d["free"]) > 0]
    for c in crypto_details:
        try:
            if c["asset"] in ("USDC", "USDT", "DAI"):
                c["current_price"] = 1.0
            elif c["asset"] == "WBTC":
                c["current_price"] = get_crypto_price("WBTC", lambda _, x: "WBTCBTC" in x["symbol"]) * get_crypto_price("BTC")
            else:
                c["current_price"] = get_crypto_price(c["asset"])
            c["amount_in_usd"] = c["current_price"]*float(c["free"])
        except IndexError as e:
            logger.exception(f"{c['asset']} price not found: {e}")
            c["current_price"] = None
    return crypto_details


def get_pancake_lp_stats():
    r = external_api_res_store.get(f"https://www.yieldwatch.net/api/all/0xbA431c3f9B6dFB27450616506B330E3Dd5f72E0a?platforms=pancake")
    pancake_lps = r["result"]["PancakeSwap"]
    vault_stats = []
    lp_stats = pancake_lps["LPStaking"]
    vaults = lp_stats["vaults"]
    lp_usd_stats = lp_stats["totalUSDValues"]
    for v in vaults:
        vault_stats.append({
            "poolName": v["name"],
            "rewardToken": v["rewardToken"],
            "pendingRewards": v["pendingRewards"],
            "harvestedRewards": v["harvestedRewards"],
            "totalEarnedFromRewards": v["totalRewards"]*v["priceInUSDRewardToken"],
            "rewardToken": v["rewardToken"],
            "poolTransactions": v["LPInfo"]["compactSessions"],
            "token0": v["LPInfo"]["symbolToken0"],
            "token1": v["LPInfo"]["symbolToken1"],
            "token0price": v["LPInfo"]["priceInUSDToken0"],
            "token1price": v["LPInfo"]["priceInUSDToken1"],
            'currentToken0Count': v["LPInfo"]["currentToken0"],
            'currentToken1Count': v["LPInfo"]["currentToken1"],
            'depositToken0Count': v["LPInfo"]["depositToken0"],
            "depositToken1Count": v["LPInfo"]["depositToken1"],
            'changeToken0Count': v["LPInfo"]["changeToken0"],
            'changeToken1Count': v["LPInfo"]["changeToken1"],
            'actPrice': v["LPInfo"]["actPrice"],
            'depositPrice': v["LPInfo"]["depositPrice"],
            'faktorIL': v["LPInfo"]["faktorIL"],
            'ILInToken1': v["LPInfo"]["ILInToken1"],
            #'ILInPerc': v["LPInfo"]["ILInPerc"],
            #'LPEarningsInToken1': v["LPInfo"]['LPEarningsInToken1'],
            #'LPEarningsInPerc': v["LPInfo"]['LPEarningsInPerc'],
            #'feesEarnedInToken0': v["LPInfo"]["feesEarnedInToken0"],
            #'feesEarnedInToken1': v["LPInfo"]['feesEarnedInToken1'],
            #'feesEarnedInPerc': v["LPInfo"]['feesEarnedInPerc']
    })
    res = {
        "deposited_money": lp_usd_stats["deposit"],
        "yield_money": lp_usd_stats["yield"],
        "total_money": lp_usd_stats["total"],
        "vaultStats": vault_stats
    }
    return res

# %%
@api.route('/')
class Hello(Resource):
    def get(self): 
        return {"message":"Hello World!"}


@api.route("/binance_assets")
class GetBinanceAssets(Resource):
    def get(self):
        crypto_details = get_binance_assets()
        crypto_details.sort(key=lambda x: x["amount_in_usd"], reverse=True)
        return {"res": crypto_details}


@api.route("/eth_transactions")
class GetAllEthTransactions(Resource):
    def get(self):
        r = external_api_res_store.get("https://api.etherscan.io/api?module=account&action=txlist&address=0xbA431c3f9B6dFB27450616506B330E3Dd5f72E0a&startblock=12082330&endblock=99999999&sort=asc&apikey={APP_CONFIG.ETHERSCAN_API_KEY}")
        eth_transactions = r.json()["result"]
        return {"res": eth_transactions}


@api.route("/get_pancake_liquidity_pool")
class GetPancakeLiquidityPool(Resource):
    def get(self):
        res = get_pancake_lp_stats()
        return {"res": res}


@api.route("/get_total_assets")
class GetTotalAssets(Resource):
    def get(self):
        token_stats = {}

        bin_assets = get_binance_assets()
        for x in bin_assets:
            if x["asset"] not in token_stats.keys():
                token_stats[x["asset"]] = {}
            
            token_stats[x["asset"]]["count"] = float(x["free"])
            token_stats[x["asset"]]["current_price"] = float(x["current_price"])

        
        p_lp_stats = get_pancake_lp_stats()

        get_from_bin = lambda token, binance_stats: [x["current_price"] for x in binance_stats if x["asset"] == token]
        for v in p_lp_stats["vaultStats"]:
            for t, n in zip((v["token0"], v["token1"]), (0, 1)):
                t = v[f"token{n}"]
                t_count = float(v[f"currentToken{n}Count"])
                t_binstat = get_from_bin(t, bin_assets)
                t_price =  t_binstat[0] if len(t_binstat) > 0 else get_crypto_price(t)
                
                if t not in token_stats.keys():
                    token_stats[t] = {}
                    token_stats[t]["count"] = 0
                
                if token_stats[t]["count"] is not None and t_price is not None:
                    token_stats[t]["count"] += t_count
                    token_stats[t]["current_price"] = t_price
                    token_stats[t]["amount_in_usd"] = token_stats[t]["count"] * t_price
                else:
                    token_stats[t]["amount_in_usd"] = None
    
                logger.debug(token_stats)
        
        total_usd = 0
        for k, v in token_stats.items():
            total_usd += v["current_price"] * v["count"]

        return {"res": {"total_usd": total_usd, "token_stats": token_stats}}




def main():
    app.run(host=APP_CONFIG.BACKEND_API_IP, port=APP_CONFIG.BACKEND_API_PORT, debug=True)

if __name__ == "__main__":
    main()
# %%
# TODO: https://www.blockchaincenter.net/altcoin-season-index/
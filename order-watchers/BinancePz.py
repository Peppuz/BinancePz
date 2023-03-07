from locale import currency
from re import U
from tqdm import tqdm 
from binance.client import Client
from tabulate import tabulate
from tqdm import tqdm
from math import floor, isfinite
from os import close
from datetime import datetime, timedelta
import numpy as np
import requests
import json
import time

class BinancePz:
    """
        Methods list:
            - Executive
                * go_trade
                    - side (long/short)
                    - symbol
                    - percentage
                    - book type (limit/market)
                * transfer FIN to SPOT
                * transfer SPOT to FIN
            - Helpers
                * get_asset 
                * get_closest_bid_price
                * get_closest_ask_price
                * get_last_trades
                * get_order_fee
                * pretty
                * pretty_number
                * send_message
    """

    def __init__(self, db_path='pz.db', token="", bnb_key="", bnb_secret=""):
        self.conf       = [[],token, bnb_key, bnb_secret]
        # Telegram setup
        self.tgadmins   = self.conf[0]
        self.token      = self.conf[1]
        # Binance setup
        self.api_key    = self.conf[2]
        self.api_secret = self.conf[3]
        self.client     = Client(self.api_key, self.api_secret)
        self.wallet     = self.get_wallet()
        

    def pretty_number(self, num):
        # TODO : description of this function which i forgot why i did it
        return np.format_float_positional(num, trim='-')


    def send_message(self, msg):
        # Send telegram messages
        ids = [self.tgadmins]
        for id in ids:
            token = self.token
            url = 'https://api.telegram.org/bot'
            params = {'chat_id': id, 'text': msg}
            requests.get(url + token + '/sendMessage', params=params)


    def get_closest_bid_price(self, sym):
        return self.client.get_order_book(symbol=sym)['bids'][0][0]


    def get_closest_ask_price(self, sym):
        return float(self.client.get_klines(symbol=sym, interval=self.client.KLINE_INTERVAL_1MINUTE)[-1][4])


    def get_last_trades(self, symbol):
        return self.client.get_my_trades(symbol=symbol)


    def get_wallet(self):
        # Get tradable asset with stepSize precision set
        # get binance wallet
        bals = self.client.get_account()
        wallet = []
        for _balance in bals["balances"]:
            if float(_balance["free"]) != 0.0 or float(_balance["locked"]) != 0.0:
                ass = (_balance['asset'], float(_balance['free'])+float(_balance['locked']), float(_balance['free']))
                wallet.append(ass)
        return wallet


    def get_asset(self, symbol, take_percentage=1, asset_status='free'):
        if asset_status != 'free':
            b = list(filter(lambda x: x['asset']==symbol, self.client.get_account()['balances']))[0]
            q = float(b['free']) + float(b['locked'])
            return q

        b = list(filter(lambda x: x['asset']==symbol, self.client.get_account()['balances']))[0]['free']
        q = float(b)*take_percentage
        return self.pretty(symbol, q, typee='qty')


    def spot_balance(self):
        sum_usdt = 0.0
        balances = self.client.get_account()
        for _balance in balances["balances"]:
            asset = _balance["asset"]
            if float(_balance["free"]) != 0.0 or float(_balance["locked"]) != 0.0:
                # all non zeros assets
                try:
                    coin_quantity = float(_balance["free"]) + float(_balance["locked"])
                    if asset == "USDT":
                        sum_usdt += coin_quantity
                    else:
                        _price = self.client.get_symbol_ticker(symbol=asset + "USDT")
                        sum_usdt += coin_quantity * float(_price["price"])
                except:
                    pass

        return '{:.2f}'.format(sum_usdt)


    def current_btc_price(self):
        return float(self.client.get_symbol_ticker(symbol="BTCUSDT")["price"])


    def get_order_fee(self, order):
        fees = self.client.get_trade_fee(symbol=order['symbol'])
        if order['side'] == 'BUY':
            return float(fees[0]['makerCommission']) * float(order['cummulativeQuoteQty'])
        else:
            return float(fees[0]['takerCommission']) * float(order['cummulativeQuoteQty'])


    def pretty(self, symbol, num, typee="baseAssetPrecision"):
        # This function return the right rounded number rispectively to the symbol
        # default baseAssetPrecision
        # print(symbol)
        fil = list(filter(lambda x: x['symbol'] == symbol, self.client.get_exchange_info()['symbols']))[0]
        if typee == "quotePrice":
            # used to pretty format of Coi
            precision = fil['quotePrecision']

        elif typee == "exitPrice":
            precision = list(filter(
                lambda x: x['filterType'] == "PRICE_FILTER", fil['filters']))[0]['minPrice']
            if float(precision) < 1:
                b = str(precision).find('1') - 1
                return round((int(float(num) / float(precision)) * float(precision)), b)
            return floor(num)

        elif typee == "qty":
            # used to pretty format Quantity to sell
            precision = list(filter(lambda x: x['filterType'] == "LOT_SIZE", fil['filters']))[0]['stepSize']
            if float(precision) < 1:
                b = str(precision).find('1') - 1
                return round(((float(num) / float(precision)) * float(precision)), b)
            return int(float(num))

        else:
            precision = fil[typee]

        return round(float(num), precision)


    def log(self, data):
        logmsg = tabulate([
            ["Symbol", "Quantity", "Start Price", "Profit percentage", "Sell Price",  "MODE"],
            [ str(data[0]), str(data[1]), str(data[2]), str(data[3]), str(data[4]), "LONG" ]
        ])



    def transfer_dust(self, symbol='USDT', quantity=''):
        quantity =  float(self.client.get_asset_balance(asset=symbol)['free']) if quantity=='' else quantity
        self.client.make_universal_transfer(type="MAIN_FUNDING", asset=symbol, amount=quantity)
        return quantity 


    def funds_to_spot(self, symbol='BTC', quantity=1):
        self.client.make_universal_transfer(type="FUNDING_MAIN", asset=symbol, amount=quantity)
        return quantity 


    def report(self):
        snaps = self.client.get_account_snapshot(type='SPOT')
        for snap in snaps['snapshotVos']:
            timestamp = snap['updateTime']
            balances = snap['data']['balances']
            # che devo fare mo che ho i bilanci
            # voglio sapere quanto distano le date

        
        pass #self.client.


    def calculate_exit_price(symbol, percentage, start_price, long_short='long'):
        # formula : final_price = start_price + start_price / 100 percentage 
        if long_short=='long':
            close_prc =  float(start_price) + (float(start_price) / 100 * float(percentage))
        else:    
            close_prc =  float(start_price) - (float(start_price) / 100 * float(percentage))

        return str(self.pretty_number(self.pretty(symbol, close_prc, 'exitPrice')))
    



    def log_trade(self, trade):
        # print(trade)
        curr = self.db.cursor()
        orders = self.db.orders
        try:
            if trade['e'] == 'executionReport':
                orders.insert_one(trade)
            return True
        except:
            raise



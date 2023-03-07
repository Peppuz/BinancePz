################################################################
# This script is intended to open a:
# -> sell limit order right after the buy stop limit has triggered and triggered

import time, json
from binance.enums import *
from binance import ThreadedWebsocketManager
from BinancePz import BinancePz
from datetime import time

config = json.load(open('../credentials.json'))
pz = BinancePz('',
               token=config['token'], 
               bnb_key=config['bnb_key'],
               bnb_secret=config['bnb_secret'])
for coin in pz.get_wallet():
    print(coin)


def main():
    twm = ThreadedWebsocketManager(api_key=config['bnb_key'], api_secret=config['bnb_secret'])
    # start is required to initialise its internal loop
    twm.start()
    print(f"[INFO] Watcher started")


    def calculate_exit_price(symbol, percentage, start_price):
        """ formula : final_price = start_price + start_price / 100 * percentage """
        close_prc =  float(start_price) + (float(start_price) / 100 * float(percentage))
        return str(pz.pretty_number(pz.pretty(symbol, close_prc, 'exitPrice')))


    def calculate_stop_price(symbol, percentage, start_price):
        """ formula : final_price = start_price - start_price / 100 * percentage """
        stop_prc =  float(start_price) - (float(start_price) / 100 * float(percentage))
        limit_prc =  float(start_price) - (float(start_price) / 100 * float(percentage+0.2))
        
        return str(pz.pretty_number(pz.pretty(symbol, limit_prc, 'exitPrice'))), str(pz.pretty_number(pz.pretty(symbol, stop_prc, 'exitPrice')))


    def handle_user_message(msg):
        """ Order docs
        s = sybol
        e = msg type
        X = order status  
        p = order price
        reference = https://binance-docs.github.io/apidocs/spot/en/#payload-balance-update
        print(msg)
        """
        user_settings = json.load(open('user_settings.json'))

        # logging
        if msg['e'] in ("executionReport"):
            json.dump(msg, open('pz.log', 'a+'), indent=4)

        if msg['e'] == "executionReport" and msg['S'] != "SELL" and msg['X'] == "FILLED":
            print(f"msg status: {msg['X']}, price: {msg['p']}")

            # // limit order //
            exit_price = calculate_exit_price(msg['s'], user_settings['target_percentuale'], msg['p'])
            quantity = float(msg['q'])-float(msg['n']) 

            stopP, stopL = calculate_stop_price(msg['s'], user_settings,msg['p'])
            try: 
                # LIMIT ORDER - LONG
                pz.client.order_limit_sell(
                    symbol=msg['s'],
                    quantity= pz.pretty(msg['s'], quantity, 'qty'),
                    price=exit_price)
            
                percentage= float(input('Next percentage % : '))
            except Exception as e:
                pz.send_message(str(e))
                raise e            

    twm.start_user_socket(callback=handle_user_message)
    twm.join()


if __name__ == "__main__":
   main()
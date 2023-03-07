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

#print(pz.client.get_symbol_info("PERLUSDT"))

def main():
    twm = ThreadedWebsocketManager(api_key=config['bnb_key'], api_secret=config['bnb_secret'])
    # start is required to initialise its internal loop
    twm.start()
    print(f"[INFO] Watcher started")
    pz.send_message(f"[INFO] Watcher started")


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
        """ Order docs reference = https://binance-docs.github.io/apidocs/spot/en/#payload-balance-update"""
        user_settings = json.load(open('user_settings.json'))

        # logging
        if msg['e'] in ("executionReport"):
            json.dump(msg, open('pz.log', 'a+'), indent=4)

        if msg['e'] == "executionReport" and msg['S'] == "BUY" and msg['X'] == "FILLED":
            # // limit order //
            exit_price = calculate_exit_price(msg['s'], user_settings['target_percentuale'], msg['p'])
            # quantity = float(msg['q'])-float(msg['n']) 
            for coin in pz.get_wallet():
                if coin[0] == msg['s'][0:-4]:
                    quantity =  pz.pretty(msg['s'], coin[2], 'qty')

            print(f"[{msg['s']}] Quantity {quantity}")
            pz.send_message(f"[{msg['s']}] BUY order filled Quantity {quantity}")

            stopP, stopL = calculate_stop_price(msg['s'], user_settings['stop_percentuale'],msg['p'])
            
            # TODO: dobbiamo trovare i muri prima di mettere ordine, come? avevo una funzione
            print(pz.client.get_order_book(symbol=msg['s'])['bids'])

            
            try: 
                # OCO ORDER - LONG
                # pz.client.order_oco_sell(
                #     symbol=msg['s'], 
                #     quantity= quantity,
                #     price= exit_price,
                #     stopPrice=stopP
                #     )
                pz.client.create_order(
                    symbol=msg['s'],
                    side=SIDE_SELL,
                    type=ORDER_TYPE_STOP_LOSS_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity,
                    stopPrice=stopP,
                    price=stopL
                )
            except Exception as e:
                pz.send_message(str(e))
                raise e            

    twm.start_user_socket(callback=handle_user_message)
    twm.join()


if __name__ == "__main__":
   main()
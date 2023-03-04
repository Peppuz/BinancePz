################################################################
# This script is intended to open a:
# -> sell limit order right after the buy stop limit has triggered and triggered
percentage = 1   
import time, json
from binance import ThreadedWebsocketManager
from BinancePz import BinancePz

config = json.load(open('credentials.json'))
pz = BinancePz('',
               token=config['token'], 
               bnb_key=config['bnb_key'],
               bnb_secret=config['bnb_secret'])


def main():
    twm = ThreadedWebsocketManager(api_key=config['bnb_key'], api_secret=config['bnb_secret'])
    # start is required to initialise its internal loop
    twm.start()

    def calculate_exit_price(symbol, percentage, start_price):
        # formula : final_price = start_price + start_price / 100 percentage 
        close_prc =  float(start_price) + (float(start_price) / 100 * float(percentage))
        return str(pz.pretty_number(pz.pretty(symbol, close_prc, 'exitPrice')))

    def handle_user_message(msg):
        # s = sybol
        # e = msg type
        # X = order status  
        # p = order price
        # reference = https://binance-docs.github.io/apidocs/spot/en/#payload-balance-update
        # print(msg)
        if msg['e'] in ("executionReport"):
            json.dump(msg, open('pz.log', 'a+'), indent=4)

        if msg['e'] == "executionReport" and msg['S'] != "SELL" and msg['X'] == "FILLED":
            print(f"msg status: {msg['X']}, price: {msg['p']}")
            exit_price = calculate_exit_price(msg['s'], percentage, msg['p'])
            quantity = float(msg['q'])-float(msg['n']) 
            try: 
                pz.client.order_limit_sell(
                    symbol=msg['s'],
                    quantity= pz.pretty(msg['s'], quantity, 'qty'),
                    price=exit_price)
            except Exception as e:
                pz.send_message(str(e))            
    twm.start_user_socket(callback=handle_user_message)
    twm.join()


if __name__ == "__main__":
   main()


""" MSG example
{'e': 'executionReport', 
'E': 1677900602801, 
's': 'LQTYUSDT', 
'c': 'electron_5c10410c8e2243aabc7159550b5', 
'S': 'BUY', 
'o': 'LIMIT', 
'f': 'GTC', 
'q': '55.70000000', 
'p': '2.12200000', 
'P': '0.00000000', 
'F': '0.00000000', 
'g': -1, 
'C': '', 
'x': 'TRADE', 
'X': 'FILLED', 
'r': 'NONE', 
'i': 7289506, 
'l': '55.70000000', 
'z': '55.70000000', 
'L': '2.12200000', 
'n': '0.05570000', 
'N': 'LQTY', 
'T': 1677900602800, 
't': 1064284, 
'I': 15654760, 
'w': False, 
'm': True, 
'M': True, 
'O': 1677900600881, 
'Z': '118.19540000', 
'Y': '118.19540000', 
'Q': '0.00000000', 
'W': 1677900600881, 
'V': 'NONE'}

"""
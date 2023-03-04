from BinancePz import BinancePz
import json


""" 
With Riccardo we took all coins in order to spot the ones that have not USDT pairs and viceversa with BUSD. 
"""

config = json.load(open('credentials.json'))
pz = BinancePz('',
               token=config['token'], 
               bnb_key=config['bnb_key'],
               bnb_secret=config['bnb_secret'])

for coin in pz.get_wallet():
    print(coin)

usdt, busd = [], []
for coin in pz.client.get_all_tickers():
    cc = coin['symbol']
    if cc[-4:] in ('BUSD'):
        busd.append(coin['symbol'])
    if cc[-4:] in ('USDT'):
        usdt.append(coin['symbol'])

with open('listone.txt', 'w+') as targ:
    for b in busd:
        targ.write('{}\n'.format(b))
    
    targ.write("\n\n\n\n")
    
    for b in usdt:
        targ.write('{}\n'.format(b))
    



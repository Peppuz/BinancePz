# BinancePz

This class is a simple wrapper for the python-binance package.

## Installation
Assuming python is already installed.
```sh
git clone https://github.com/cyberpz/BinancePz.git
cd BinancePz
pip install -r requirements.txt
```
Ignore warnings, go for a ride.

---
#
# Usage

1. Rename the file `cretentials.template.json` into `credentials.json` and open it
2. Generate a telegram token for your notifier (from @botfather)
3. Generate Binance API key
4. Copy and paste all keys into `credentials.json` file
5. *(Optional, but highly suggested)* Enable IP filtering on the Binance API key, 
    so you know that only you are using the keys.

Ok now you can create a little file:
```python
from BinancePz import BinancePz
import json

config = json.load(open('credentials.json'))
pz = BinancePz('',
               token=config['token'], 
               bnb_key=config['bnb_key'],
               bnb_secret=config['bnb_secret'])

for coin in pz.get_wallet():
    print(coin)
```
and lunch it:
```sh
python file.py
```

Good bye!!!

## No Documentation, it's all up here, for [ITALIAN version clikc here!](https://tenor.com/it/view/zalone-scemi-stupidi-creduloni-finger-licking-gif-16460645)
---
#
## Methods

* get_wallet - Gathers all spot wallet
* get_asset - Gathers quantity of specified coin in spot wallet
* spot_balance - Returns total wallet value in USD
* current_btc_price - Returns current BTCUSDT value
* pretty - Return the right rounded number rispectively to the symbol (types: quotePrice, exitPrice, qty) 
* transfer_dust - Transfer coins from Spot to Fundings
* funds_to_spot - Transfer coins from Fundings to Spot
* get_closest_ask_price - Usefull shortcut for trading operation
* get_closest_bid_price - Usefull shortcut for trading operation
* send_message - Sends message to telegram admins

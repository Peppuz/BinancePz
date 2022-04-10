# BinancePz

This class is a simple wrapper for the python-binance package.

# Usage
Import the file in the prefered folder,
add to your script: 

```python 
from BinancePz import BinancePz
pz = BinancePz('', token='', bnb_key='', bnb_secret='')
```

inserting telegram's bot into `token` and binance credentials relatively to `bnb` parameters.


# Tested Methods

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

# wikifolio-trading-api
A Python Wrapper for the official Wikifolio Trading API

Wikifolio has realeased an official API for trading. This is a Python wrapper for this API. Instead of using https://github.com/henrydatei/wikifolio-api, you can use this wrapper to trade with your wikifolio if you have a client api key and a user api key. To get these keys, you have to
- register a wikifolio account
- write an email to office@wikifolio.com and ask for a client api key and a user api key
- they write back/phone you and ask for the purpose of using the api
- whatever you tell them, don't say you want to fully automatize your trading, they don't like that
- they send an agreement to you, which you have to sign and send back
- they send you the keys

Although this wrapper can automate your trading you should not officially do it. Wikifolio does not like it and they can block your account. So use it at your own risk. What is possible is that a user clicks a button and then the wrapper does the trading, i.e. rebalancing the wikifolio.

### TODOs
- implement all methods of the official API
- publish on PyPi

### Usage
If published on PyPi, you can install it with
```
pip install wikifolioTradingAPI // not yet published and unshure if this name is available
```
Then you can use it like this:
```python
from wikifolioTradingAPI import WikifolioTradingAPI

wf_api = WikifolioTradingAPI("my_client_api_key", "my_user_api_key")
print(wf_api.list_wikifolios())
print(wf_api.get_wikifolio('wf0spc2022'))
# print(wf_api.list_wikifolio_underlyings('wf0spc2022')) # Was not working when I tested it
print(wf_api.list_wikifolio_orders('wf0spc2022'))
```
import hashlib
import hmac
import httplib
import json
import urllib
from decimal import Decimal

import requests

from Interfaces.IExchange import IExchange


class BTCEExchange(IExchange):

    def __init__(self):
        self.name = "BTC-E"
        self.api_key = "4QI4ACIG-6A5PAVOQ-6CECH97S-3PA8BBX4-KTDQKI5B"
        self.username = "Fireblade8998"
        self.api_secret = "e740a78137d11056490b3e72a04bc6d35c035c351bde2dad8ddf419c9f848b4c"
        self.nonce = self.nonce_api_call()
        self.unconfirmedDeposits = False

    def getNonce(self):
        """
        Returns the nonce value needed for secure POST requests
        """
        return self.nonce + 1

    def getSignature(self, params):
        """
        Returns the encoded signature needed for the handshake with BTC-E API
        """
        return hmac.new(self.api_secret, params, digestmod=hashlib.sha512).hexdigest()

    def nonce_api_call(self):
        """
        On init, calls to the BTC-E server to get the expected nonce for this particular API key.
        """
        params = {}
        params['method'] = "getInfo"
        params['nonce'] = 1
        params = urllib.urlencode(params)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Key": self.api_key,
                   "Sign": self.getSignature(params)}
        conn = httplib.HTTPSConnection("btc-e.com")
        conn.request("POST", "/tapi", params, headers)
        response = conn.getresponse()
        data = json.load(response)
        res = str(data['error'])
        if str.__contains__(res, "you should send"):
            newNonce = res.split("you should send:", 1)[1]
            return int(newNonce)
        else:
            exit()

    def api_call(self, method, params={}):
        """
        Packages the request and sends / receives the answer.

        @param method: the string that corresponds with the API call
        @param params: any additional parameters that need to be passed to the API
        """
        params['method'] = method
        params['nonce'] = str(self.getNonce())
        params = urllib.urlencode(params)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Key": self.api_key,
                   "Sign": self.getSignature(params)}
        conn = httplib.HTTPSConnection("btc-e.com")
        conn.request("POST", "/tapi", params, headers)
        response = conn.getresponse()
        data = json.load(response)
        conn.close()
        self.nonce += 1
        return data

    def getInfo(self):
        return self.api_call('getInfo', {})

    # market buy - must be instant (market) buy
    # should return a JSON dictionary to be parsed including order ID and execution status
    def buy(self, amount):
        """
        Due to constraints in the BTC-E API, no instant (market) order is available.
        Creates a buy limit order set to the top of the ask table - should execute instantly. May need some work.

        @param amount: amount in BTC - ***MUST BE ROUNDED TO 3 PLACES BECAUSE BTC-E IS RETARDED***
        @return: {success (0 or 1), amount bought}
        """
        currentPrice = self.getCurrentBuyPrice()
        json = self.api_call("Trade", {'pair': "btc_usd", 'type': 'buy', 'amount': float("{0:.3f}".format(amount)),
                                       'rate': currentPrice})
        if json['success'] == 0:
            return {'success': 0, 'amount': 0}
        else:
            return {'success': json['success'], 'amount': json['received'], 'price': Decimal(currentPrice)}

    # market sell - must be instant (market) sell
    # should return a JSON dictionary to be parsed including order ID and execution status
    def sell(self, amount):
        """
        Due to constraints in the BTC-E API, no instant (market) order is available.
        Creates a sell limit order set to the top of the bid table - should execute instantly. May need some work.

        @param amount: amount in BTC - ***MUST BE ROUNDED TO 3 PLACES BECAUSE BTC-E IS RETARDED***
        """
        currentPrice = self.getCurrentSellPrice()
        return self.api_call("Trade", {'pair': "btc_usd", 'type': 'sell', 'amount': float("{0:.3f}".format(amount)),
                                       'rate': currentPrice})

    # should return a balance available in either BTC or USD
    def getAccountBalance(self, currency={}):
        """
        Returns a balance in USD or BTC

        @param currency: BTC or USD. Leave blank for both.
        """
        data = self.getInfo()

        if currency.__contains__("BTC"):
            return Decimal(data['return']['funds']['btc'])
        elif currency.__contains__("USD"):
            return Decimal(data['return']['funds']['usd'])
        else:
            return {'BTC': Decimal(data['return']['funds']['btc']), 'USD': Decimal(data['return']['funds']['usd'])}

    # should return a balance available in either BTC or USD
    def getTicker(self):
        """
        Returns the ticker JSON object with the following format:
        {'name:': ex.name, 'buy': json['ask'], 'sell': json['bid'], 'last': json['last'] 'fee': json['fee']}
        """

        #get ticker from public API v3
        ticker = requests.get("https://btc-e.com/api/3/ticker/btc_usd").json()['btc_usd']

        #get trade info from public API v3
        info = requests.get("https://btc-e.com/api/3/info").json()

        fee = info['pairs']['btc_usd']['fee']

        #package new ticker object and return
        ticker['name'] = self.name
        ticker['fee'] = Decimal(fee / 100)
        ticker['buy'] = Decimal(ticker['buy'])
        ticker['sell'] = Decimal(ticker['sell'])
        return ticker

    def getTickerNoFee(self):
        """
        Returns the ticker JSON object without the second call to get the fee. Saves overhead for subsequent calls.
        """
        # get ticker from public API v3
        return requests.get("https://btc-e.com/api/3/ticker/btc_usd").json()['btc_usd']


    # should return last buy price in USD
    def getCurrentBuyPrice(self):
        """
        Returns the last ask price in USD.
        """
        return self.getTickerNoFee()['buy']

    # should return last sell price in US
    def getCurrentSellPrice(self):
        """
        Returns the last bid price in USD.
        """
        return self.getTickerNoFee()['sell']

    # should cancel the order
    # param orderID: the orderID to cancel
    def cancelOrder(self, orderID):
        """
        Cancels the selected order.

        @param orderID: the order to cancel
        """
        return self.api_call("CancelOrder", {'order_id': orderID})

    # should return all orders that are currently open as JSON
    def getOpenOrders(self):
        """
        Returns all open orders.
        """
        return self.api_call("ActiveOrders", {})

    # should return all orders that are pending as JSON
    # param id_list: a list of IDs of pending orders
    def getActiveOrders(self, id_list={}):
        """
        Returns all active orders and their current status.

        @param id_list: provide order IDs to check their status.

        **NOTE**: This is not supported for BTC-E. Only open orders are accessible.
        """
        pass

    # should return all orders that are completed as JSON
    def getExecutedOrders(self):
        """
        Returns all completed orders and their current status.
        """
        return self.api_call("TradeHistory", {})

    # should return the buy/sell fee
    def getExchangeFee(self):
        """
        Returns the exchanges's buy/sell fee
        """
        # get trade info from public API v3
        info = requests.get("https://btc-e.com/api/3/info").json()

        fee = info['pairs']['btc_usd']['fee']

        return fee

    def getUnconfirmedDeposits(self):
        """
        Returns all pending "in transit" BTC deposits without at least 3 confirmations.

        ***NOTE***: This is not supported for BTC-E.
        """
        pass

    # should return a BTC address for the exchange
    # this needs to be verifiable with a static file somewhere, don't want to send BTC to a bad address
    def getBTCAddress(self):
        """
        Returns the BTC deposit address for BTC-E.

        ***NOTE***: This is not supported by BTC-E. This method MUST be updated manually.
        """
        return "1CggtUtpNrwtv1sHGSsXr4Mh3jQiL3R9u4"

    def withdrawToAddress(self, address, amount):
        """
        Withdraws to the address specified. Careful with this one.

        @param address: the BTC address to send the coins to
        @param amount: the amount to send from BTC-E's wallet
        """
        return self.api_call("WithdrawCoin", {'coinName': "BTC", 'address': address, 'amount': amount})

import hashlib
import hmac
import httplib
import json
import urllib

import requests

from Interfaces.IExchange import IExchange


class BTCEExchange(IExchange):

    def __init__(self):
        self.name = "BTC-E"
        self.api_key = "4QI4ACIG-6A5PAVOQ-6CECH97S-3PA8BBX4-KTDQKI5B"
        self.username = "Fireblade8998"
        self.api_secret = "e740a78137d11056490b3e72a04bc6d35c035c351bde2dad8ddf419c9f848b4c"
        self.nonce = self.nonce_api_call()

    @staticmethod
    def request(path, params):
        """
        Returns a JSON object from POST using API Key, Secret, User Key and an API path.

        @param path: the string at the end of the API string, "ticker" for example
        @param params: the encoded parameters and signature required to authenticate
        """
        url = "https://www.btc-e.com/api/" + path + "/"
        r = requests.post(url, params)
        return r.json()

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

        @param amount: amount in BTC
        """
        currentPrice = self.getCurrentBuyPrice()
        return self.api_call("buy", {'amount': amount, 'price': currentPrice})

    # market sell - must be instant (market) sell
    # should return a JSON dictionary to be parsed including order ID and execution status
    def sell(self, amount):
        """
        Due to constraints in the BTC-E API, no instant (market) order is available.
        Creates a sell limit order set to the top of the bid table - should execute instantly. May need some work.

        @param amount: amount in BTC
        """
        currentPrice = self.getCurrentSellPrice()
        return self.api_call("sell", {'amount': amount, 'price': currentPrice})

    # should return a balance available in either BTC or USD
    def getAccountBalance(self, currency="USD"):
        """
        Returns a balance in USD or BTC

        @param currency: BTC or USD. Leave blank for USD.
        """
        balance = self.api_call("balance", {})
        if str.__contains__(currency, "BTC"):
            return json.dumps(balance['btc_balance'])
        elif str.__contains__(currency, "USD"):
            return json.dumps(balance['usd_balance'])

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
        ticker['fee'] = fee

        return ticker


    # should return last buy price in USD
    def getCurrentBuyPrice(self):
        """
        Returns the last ask price in USD.
        """
        return self.api_call("ticker", {})['ask']

    # should return last sell price in US
    def getCurrentSellPrice(self):
        """
        Returns the last bid price in USD.
        """
        return self.api_call("ticker", {})['bid']

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
        return self.api_call("balance", {})['fee']

    def getUnconfirmedDeposits(self):
        """
        Returns all pending "in transit" BTC deposits without at least 3 confirmations.
        """
        return json.dumps(self.api_call("unconfirmed_btc", {}))

    # should return a BTC address for the exchange
    # this needs to be verifiable with a static file somewhere, don't want to send BTC to a bad address
    def getBTCAddress(self):
        """
        Returns the BTC deposit address for BTC-E.
        """
        return self.api_call("bitcoin_deposit_address", {})

    def withdrawToAddress(self, address, amount):
        """
        Withdraws to the address specified. Careful with this one.

        @param address: the BTC address to send the coins to
        @param amount: the amount to send from BTC-E's wallet
        """
        return self.api_call("WithdrawCoin", {'coinName': "BTC", 'address': address, 'amount': amount})

import hashlib
import hmac
import json
import sys
import time
from decimal import Decimal

import requests

from Interfaces.IExchange import IExchange


class BitstampExchange(IExchange):

    def __init__(self):
        self.name = "Bitstamp"
        self.api_key = "xlVE2zCKgeH8EiZ490QUmzmSzsKSzDIy"
        self.username = "743672"
        self.api_secret = "WIGmO0WRKXdqAXfasWvgdB25O88lobc6"
        self.__nonce_v = '{:.10f}'.format(time.time() * 1000).split('.')[0]

    @staticmethod
    def request(path, params):
        """
        Returns a JSON object from POST using API Key, Secret, User Key and an API path.

        @param path: the string at the end of the API string, "ticker" for example
        @param params: the encoded parameters and signature required to authenticate
        """
        url = "https://www.bitstamp.net/api/" + path + "/"
        r = requests.post(url, params)
        return r.json()

    def __nonce(self):
        """
        Returns the nonce value needed for secure POST requests
        """
        self.__nonce_v = '{:.10f}'.format(time.time() * 1000).split('.')[0]

    def __signature(self):
        """
        Returns the encoded signature needed for the handshake with Bitstamp API
        """
        self.__nonce()
        string = self.__nonce_v + self.username + self.api_key  # create string

        if sys.version_info.major == 2:
            signature = hmac.new(self.api_secret, msg=string, digestmod=hashlib.sha256).hexdigest().upper()
        else:
            signature = hmac.new(str.encode(self.api_secret), msg=str.encode(string), digestmod=hashlib.sha256)\
                .hexdigest().upper()

        return signature

    def api_call(self, method, params, private=0):
        """
        Packages the request and sends / receives the answer. Private should be set to 1 if a signature is required,
        usually for private API calls that need authentication.

        @param method: the string that corresponds with the API call
        @param params: any additional parameters that need to be passed to the API
        @param private: set to 0 for all public request, set to 1 when authentication is required
        """
        param = {}
        if private == 1:  # add auth-data if needed
            param['key'] = self.api_key
            self.__nonce()
            param['nonce'] = self.__nonce_v
            param['signature'] = self.__signature()
        for key, value in params.items():
            param[str(key)] = value
        answer = self.request(method, param)  # Post Request
        return answer  # generate dict and return

    #market buy - must be instant (market) buy
    #should return a JSON dictionary to be parsed including order ID and execution status
    def buy(self, amount):
        """
        Due to constraints in the Bitstamp API, no instant (market) order is available.
        Creates a buy limit order set to the top of the ask table - should execute instantly. May need some work.

        @param amount: amount in BTC
        """
        currentPrice = self.getCurrentBuyPrice()
        json = self.api_call("buy", {'amount': amount, 'price': currentPrice}, 1)
        if 'error' in json:
            return {'success': 0, 'amount': 0}
        else:
            # check on the order status after buy is sent
            if self.getOrderStatus(json['id'] != "Finished"):
                # order is not filled yet, return the order ID
                return {'success': 1, 'amount': json['amount'], 'price': Decimal(json['price']), 'order_id': json['id']}

            # if the order is filled, don't sent an order_id back
            else:
                return {'success': 1, 'amount': json['amount'], 'price': Decimal(json['price']), 'order_id': 0}

    #market sell - must be instant (market) sell
    #should return a JSON dictionary to be parsed including order ID and execution status
    def sell(self, amount):
        """
        Due to constraints in the Bitstamp API, no instant (market) order is available.
        Creates a sell limit order set to the top of the bid table - should execute instantly. May need some work.

        @param amount: amount in BTC
        """
        currentPrice = self.getCurrentSellPrice()
        json = self.api_call("sell", {'amount': amount, 'price': currentPrice}, 1)
        if 'error' in json:
            return {'success': 0, 'amount': 0}
        else:
            return {'success': 1, 'amount': json['amount'], 'price': Decimal(json['price'])}

    def getOrderStatus(self, ID):
        """
        Fetches the order status of a particular order ID. Useful for checking whether an order has finished
        being filled.

        @param ID: the order ID of the order in question
        """

        #json = self.api_call("order_status", {'id': ID}, 1)
        json={'status': "Finished", 'transactions': 4}
        if 'error' in json:
            return []
        else:
            return json['status']

    #should return a balance available in either BTC or USD
    def getAccountBalance(self, currency={}):
        """
        Returns a balance in USD or BTC

        @param currency: BTC or USD. Leave blank for both.
        """
        balance = self.api_call("balance", {}, 1)
        if currency.__contains__("BTC"):
            return json.dumps(balance['btc_balance'])
        elif currency.__contains__("USD"):
            return json.dumps(balance['usd_balance'])
        else:
            return {'BTC': Decimal(balance['btc_balance']), 'USD': Decimal(balance['usd_balance'])}


    #should return a balance available in either BTC or USD
    def getTicker(self):
        """
        Returns the ticker JSON object with the following format:
        {'name:': ex.name, 'buy': json['ask'], 'sell': json['bid'], 'last': json['last], 'fee': json['fee']}
        """
        res = self.api_call("ticker", {}, 0)
        res['buy'] = Decimal(res['ask'])
        res['sell'] = Decimal(res['bid'])
        res['fee'] = Decimal(self.getExchangeFee()) / 100
        return res

    #should return last buy price in USD
    def getCurrentBuyPrice(self):
        """
        Returns the last ask price in USD.
        """
        return self.api_call("ticker", {}, 0)['ask']

    #should return last sell price in US
    def getCurrentSellPrice(self):
        """
        Returns the last bid price in USD.
        """
        return self.api_call("ticker", {}, 0)['bid']

    #should cancel the order
    #param orderID: the orderID to cancel
    def cancelOrder(self, orderID):
        """
        Cancels the selected order.

        @param orderID: the order to cancel
        """
        return json.dumps(self.api_call("cancel_order", {"id": orderID}, 1))

    #should return all orders that are currently open as JSON
    def getOpenOrders(self):
        """
        Returns all open orders.
        """
        test = [{'id': 123123, 'datetime': '2016-12-25 12:12:23', 'type': 0, 'price': 570.67, 'amount': 2}, {'id': 123124, 'datetime': '2016-12-25 12:12:23', 'type': 0, 'price': 571.67, 'amount': 2}]

        #return self.api_call("open_orders", {}, 1)
        return test


    #should return all orders that are pending as JSON
    #param id_list: a list of IDs of pending orders
    def getActiveOrders(self, id_list={}):
        """
        Returns all active orders and their current status.

        @param id_list: provide order IDs to check their status.
        """
        activeOrders={}
        for i in id_list:
            order = json.dumps(self.api_call("order_status", {'id': i}, 1))
            activeOrders[str(i)] = order
        return str(activeOrders)

    #should return all orders that are completed as JSON
    def getExecutedOrders(self):
        """
        Returns all completed orders and their current status.
        """
        param = {'id': 1, 'order_id': 2, 'test': 3}
        return json.dumps(self.api_call("order_status", param, 1))

    #should return the buy/sell fee
    def getExchangeFee(self):
        """
        Returns the exchanges's buy/sell fee
        """
        return self.api_call("balance", {}, 1)['fee']

    def getUnconfirmedDeposits(self):
        """
        Returns all pending "in transit" BTC deposits without at least 3 confirmations.
        """
        return json.dumps(self.api_call("unconfirmed_btc", {}, 1))

    #should return a BTC address for the exchange
    #this needs to be verifiable with a static file somewhere, don't want to send BTC to a bad address
    def getBTCAddress(self):
        """
        Returns the BTC deposit address for Bitstamp.
        """
        return self.api_call("bitcoin_deposit_address", {}, 1)

    def withdrawToAddress(self, address, amount):
        """
        Withdraws to the address specified. Careful with this one.

        @param address: the BTC address to send the coins to
        @param amount: the amount to send from Bitstamp's wallet
        """
        return json.dumps(self.api_call("bitcoin_withdrawal", {'address': address, 'amount': amount}, 1))

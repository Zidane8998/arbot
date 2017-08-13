import hashlib
import hmac
import httplib
import json
import urllib
import time
import requests
import base64
import urlparse
from decimal import Decimal


from Interfaces.IExchange import IExchange


class KrakenExchange(IExchange):

    def __init__(self):
        self.name = "Kraken"
        self.api_key = "Sl5Kf492Z2SLEzkUzSHgCbuyiJXWyBY7O3zPREwz+BTiXwm92ZHdeb30"
        self.api_secret = "P/Agn2DKLRaiCvfL322ExOCQUJkM/gnGqBPtkcSdh95k0BS5tmN3VT8cupsgSOllgdguoeii4hnos0n+Qw0y4A=="
        self.api_address = "https://api.kraken.com"
        self.api_version = "0"
        self.nonce = 0
        self.readyForBuy = True

    def getNonce(self):
        """
        Returns the nonce value needed for secure POST requests
        """
        return int(1000 * time.time())

    def getSignature(self, params):
        """
        Returns the encoded signature needed for the handshake with Bitfinex API
        """
        return hmac.new(self.api_secret, params, digestmod=hashlib.sha384).hexdigest()

    def generate_query_string(self, filters):
        if filters:
            return '?' + urllib.urlencode(filters)
        else:
            return ''

    def make_message(self, verb, url, body, nonce, timestamp):
        # There should be no spaces after separators
        return json.dumps([verb, url, body, str(nonce), str(timestamp)], separators=(',', ':'))

    def sign_message(self, body):
        return hmac.new(base64.b64decode(self.api_secret), body, hashlib.sha512)

    def make_request(self, method, params={}):
        url = '/' + self.api_version + '/private/' + method
        params['nonce'] = int(1000*time.time())

        postdata = urllib.urlencode(params)
        body = url + hashlib.sha256(str(params['nonce']) + postdata).digest()

        signature = hmac.new(base64.b64decode(self.api_secret), body, hashlib.sha512)

        headers = {
            'API-Key': self.api_key,
            'API-Sign': base64.b64encode(signature.digest())
        }

        conn = httplib.HTTPSConnection('api.kraken.com', timeout=30)

        conn.request("POST", url, body, headers)
        response = conn.getresponse()

        return response.read()


    def getInfo(self, filters={}):
        filters['userId'] = self.user_id
        queryString = self.generate_query_string(filters)
        path = "/wallets%s" % (queryString)
        response = self.make_request("GET", path, {})
        return response

    def api_call(self, method, params={}):
        """
        Packages the request and sends / receives the answer.

        @param method: the string that corresponds with the API call
        @param params: any additional parameters that need to be passed to the API
        """

        payload = {
            "request": method,
            "nonce": self.getNonce()
        }

        for key, value in params.items():
            payload[str(key)] = value

        headers = self.package_call(payload)

        url = "https://api.bitfinex.com/" + method
        response = requests.get(url, data={}, headers=headers)
        data = response.json()
        return data


    # market buy - must be instant (market) buy
    # should return a JSON dictionary to be parsed including order ID and execution status
    def buy(self, amount):
        """
        1. Check if enough funds exist for the buy, if not mark exchange as "no buy"
        2. Due to constraints in the BTC-E API, no instant (market) order is available.
           Creates a buy limit order set to the top of the ask table - should execute instantly. May need some work.

        @param amount: amount in BTC - ***MUST BE ROUNDED TO 3 PLACES BECAUSE BTC-E IS RETARDED***
        @return: {success (0 or 1), amount bought, price, order_id (0 or order id)}
        """

        currentPrice = Decimal(self.getCurrentBuyPrice())
        data = self.getAccountBalance()
        usd = data['USD']

        # check that enough funds exist in the exchange, if not mark exchange as "no buy" and return
        if amount * currentPrice >= usd:
            print "Exchange " + self.name + " has run out of funds and is being marked as no buy."
            #self.readyForBuy = False
            return {'success': 0, 'amount': 0}

        json = self.api_call("Trade", {'pair': "btc_usd", 'type': 'buy', 'amount': float("{0:.3f}".format(amount)),
                                       'rate': currentPrice})
        if json['success'] == 0:
            return {'success': 0, 'amount': 0}
        else:
            return {'success': json['success'], 'amount': Decimal(json['return']['received']) + Decimal(json['return']['remains']), 'price': Decimal(currentPrice), 'order_id': json['return']['order_id']}

    # market sell - must be instant (market) sell
    # should return a JSON dictionary to be parsed including order ID and execution status
    def sell(self, amount):
        """
        Due to constraints in the BTC-E API, no instant (market) order is available.
        Creates a sell limit order set to the top of the bid table - should execute instantly. May need some work.

        @param amount: amount in BTC - ***MUST BE ROUNDED TO 3 PLACES BECAUSE BTC-E IS RETARDED***
        """
        currentPrice = self.getCurrentSellPrice()
        json = self.api_call("Trade", {'pair': "btc_usd", 'type': 'sell', 'amount': float("{0:.3f}".format(amount)),
                                       'rate': currentPrice})

        if json['success'] == 0:
            return {'success': 0, 'amount': 0}
        else:
            return {'success': json['success'], 'amount': json['received'], 'price': Decimal(currentPrice), 'id': json['order_id']}

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
        ticker = requests.get("https://api.itbit.com/v1/markets/BTCUSD/ticker").json()

        #get trade info from public API v3
        info = requests.get("https://api.itbit.com/v1/markets/BTCUSD/ticker").json()

        fee = info['pairs']['btc_usd']['fee']

        #package new ticker object and return
        ticker['name'] = self.name
        ticker['fee'] = Decimal(self.getExchangeFee() / 100) #Decimal(fee / 100)
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
        #data = self.api_call("ActiveOrders", {})
        data = {'success':1,'return':{'12446':{'pair':'btc_usd','type':'sell','amount':12.345,'rate':485,'timestamp_created':1342448420,'status':0}}}
        if data['success'] == 0:
            return {}
        # package the results to be similar to other exchange outputs
        else:
            newList = []
            list = data['return']
            for key, cur in list.iteritems():
                cur['id'] = key
                newList.append(cur)
            return newList

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
        #info = requests.get("https://btc-e.com/api/3/info").json()

        #fee = info['pairs']['btc_usd']['fee']

        return 0.2

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
        data = self.api_call("WithdrawCoin", {'coinName': "BTC", 'address': address, 'amount': amount})

        if "error" in data:
            return {'success': 0, 'error': data['error']}
        else:
            return {'success': 1, 'id': data['tID']}

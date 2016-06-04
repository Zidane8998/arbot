from abc import ABCMeta, abstractmethod


class IExchange():
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    #market buy - must be instant (market) buy
    #should return a JSON dictionary to be parsed including order ID and execution status
    @abstractmethod
    def buy(self, amount):
        pass

    #market sell - must be instant (market) sell
    #should return a JSON dictionary to be parsed including order ID and execution status
    @abstractmethod
    def sell(self, amount):
        pass

    #should return a balance available in USD
    @abstractmethod
    def getAccountBalance(self):
        pass

    #should return last buy price in USD
    @abstractmethod
    def getCurrentBuyPrice(self):
        pass

    #should return last sell price in USD
    @abstractmethod
    def getCurrentSellPrice(self):
        pass

    #should return ticker information for the exchange as a dict
    @abstractmethod
    def getTicker(self):
        pass

    #should cancel the order
    #param orderID: the orderID to cancel
    @abstractmethod
    def cancelOrder(self, orderID):
        pass

    #should return all orders that are currently open as JSON
    @abstractmethod
    def getOpenOrders(self):
        pass

    #should return all orders that are pending as JSON
    #param id_list: a list of IDs of pending orders
    @abstractmethod
    def getActiveOrders(self, id_list={}):
        pass

    #should return all orders that are completed as JSON
    @abstractmethod
    def getExecutedOrders(self):
        pass

    #should return a BTC address for the exchange
    #this needs to be verifiable with a static file somewhere, don't want to send BTC to a bad address
    @abstractmethod
    def getBTCAddress(self):
        pass

    #should return a BTC address for the exchange
    #this needs to be verifiable with a static file somewhere, don't want to send BTC to a bad address
    @abstractmethod
    def withdrawToAddress(self, address, amount):
        pass


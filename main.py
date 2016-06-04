from Database import Database
from Exchanges.BTC_E import BTCEExchange
from Exchanges.Bitstamp import BitstampExchange


def main():

    btce = BTCEExchange()
    print btce.getInfo()
    print btce.getActiveOrders()
    print btce.cancelOrder(1)
    print btce.getExecutedOrders()
    print btce.withdrawToAddress(1, 1)
    print btce.getTicker()
    print "Get buy price: " + str(btce.getCurrentBuyPrice())
    print "Get sell price: " + str(btce.getCurrentSellPrice())
    print "Get exchange fee: " + str(btce.getExchangeFee())
    print "Sell: " + str(btce.sell(1))
    print "Buy: " + str(btce.buy(1))

    db = Database.Database()

    db.createNewTransaction('PND', 10, 'Bitfinex', 'Bitstamp', 560)

    """
    db.printResults(db.getAllTransactions())
    db.printResults(db.getAllPendingTransactions())
    db.printResults(db.getAllActiveTransactions())
    db.printResults(db.getAllInTransitTransactions())
    db.printResults(db.getAllClosedTransactions())
    
    db.printResults(db.getAllTransactionsFromTargetExchange('Bitstamp'))
    db.printResults(db.getAllPendingTransactionsFromTargetExchange('Bitstamp'))
    db.printResults(db.getAllActiveTransactionsFromTargetExchange('Bitstamp'))
    db.printResults(db.getAllInTransitTransactionsFromTargetExchange('Bitstamp'))
    db.printResults(db.getAllClosedTransactionsFromTargetExchange('Bitstamp'))

    db.printResults(db.getAllTransactionsFromOriginExchange('Bitfinex'))
    db.printResults(db.getAllPendingTransactionsFromOriginExchange('Bitfinex'))
    db.printResults(db.getAllActiveTransactionsFromOriginExchange('Bitfinex'))
    db.printResults(db.getAllInTransitTransactionsFromOriginExchange('Bitfinex'))
    db.printResults(db.getAllClosedTransactionsFromOriginExchange('Bitfinex'))
    """

    defaultTradeSize = 0.25
    defaultProfitMargin = 0.50
    exchanges = []
    global_ticker = []
    bitstamp = BitstampExchange()
    exchanges.append(bitstamp)

    """
    Populate ticker information for all exchanges, returning JSON format of {Bitcoin exchange name: name, buy: buy price, sell: sell price}
    """

    """
    Main program loop: for all exchanges, get ticker information
    """
    for ex in exchanges:
        json = ex.getTicker() #this call MUST return a dict with these elements or it will blow up
        exTicker = {'name': ex.name, 'buy': json['ask'], 'sell': json['bid'], 'fee': json['fee']}
        global_ticker.append(exTicker)
        """
        Get all transactions with this exchange as a target (may replace later with individual
        database calls - slower but more accurate)
        """
        for cur in db.getAllTransactionsFromTargetExchange(ex.name):
            """
            Process all in transit transactions with exchange as target
            """
            if cur['STATUS'] == 'INT':
                print cur
            """
            Process all active transactions with exchange as target
            """
            if cur['STATUS'] == 'ACT':
                print cur
            """
            Process all pending transactions with exchange as target
            """
            if cur['STATUS'] == 'PND':
                print cur
        """
        Get all transactions with this exchange as an origin (may replace later with individual
        database calls - slower but more accurate)
        """
        for cur in db.getAllTransactionsFromOriginExchange(ex.name):
            """
            Process all pending transactions with exchange as origin
            """
            if cur['STATUS'] == 'PND':
                print cur

        """
        Find buy low / sell high pairing if it exists by comparing all exchange prices
        """
        for cur in global_ticker:
            if cur['name'] != ex.name:
                """
                If a profit can be made by selling on another exchange, set up a new transaction

                Profit formula: (sell price - sell fee)
                """
                if (cur['sell'] - cur['fee']) - ((exTicker['buy'] + exTicker['fee'] +
                         (exTicker['buy'] * defaultTradeSize * 0.000014)) + defaultProfitMargin):
                    pass

    print bitstamp.getAccountBalance("BTC")
    print bitstamp.getTicker()
    print "Sell price: " + bitstamp.getCurrentSellPrice()
    print "Buy price: " + bitstamp.getCurrentBuyPrice()
    print "BTC deposit address: " + bitstamp.getBTCAddress()
    print "Open orders: " + bitstamp.getOpenOrders()
    print "Active orders: " + bitstamp.getActiveOrders({1, 2, 3})
    print bitstamp.getExecutedOrders()
    print bitstamp.cancelOrder(1)
    print bitstamp.withdrawToAddress("test", 1)
    print bitstamp.buy(1)
    print bitstamp.sell(1)
    print bitstamp.getUnconfirmedDeposits()


if __name__ == "__main__":
    main()

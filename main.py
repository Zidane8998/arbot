from Database import Database
from Exchanges.Bitstamp import BitstampExchange


def main():

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

    exchanges = []
    global_ticker = {}
    bitstamp = BitstampExchange()
    exchanges.append(bitstamp)

    """
    Populate ticker information for all exchanges, returning JSON format of {Bitcoin exchange name: name, buy: buy price, sell: sell price}
    """

    """
    Main program loop: for all exchanges, get ticker information
    """
    for ex in exchanges:
        json = ex.getTicker() #this call MUST return a dict or it will blow up
        inner = {'buy': json['ask'], 'sell': json['bid']}
        global_ticker[ex.name] = inner
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
        Find buy low / sell high pairing if it exists
        """


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

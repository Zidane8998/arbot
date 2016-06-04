from Database import Database
from Exchanges.Bitstamp import BitstampExchange


def main():

    db = Database.Database()

    db.createNewTransaction('PND', 10, 'Bitfinex', 'Bitstamp', 560)
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

    bitstamp = BitstampExchange()
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

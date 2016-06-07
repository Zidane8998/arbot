from decimal import Decimal
from operator import itemgetter

from Database import Database
from Exchanges.BTC_E import BTCEExchange
from Exchanges.Bitstamp import BitstampExchange


def getExchangeByName(exchanges, name):
    for exchange in exchanges:
        if exchange.name == name:
            return exchange

def calculateProfit(sellPrice, buyPrice, sellerFee, buyerFee, defaultTradeSize=Decimal(0.25), transactionFeeAmt=Decimal(0.0001)):
    sellRevenue = (sellPrice * defaultTradeSize)
    sellFee = (sellPrice * defaultTradeSize * sellerFee)

    totalSellRevenue = sellRevenue - sellFee

    buyCost = (buyPrice * defaultTradeSize)
    buyFee = (buyPrice * defaultTradeSize * buyerFee)
    transactionFee = (buyPrice * defaultTradeSize * transactionFeeAmt)

    totalBuyCost = buyCost + buyFee + transactionFee
    totalFees = sellFee + buyFee + transactionFee

    profit = totalSellRevenue - totalBuyCost

    return profit, totalSellRevenue, totalBuyCost, totalFees

def calculateProfitNoTransactionFee(sellPrice, buyPrice, sellerFee, buyerFee, defaultTradeSize=Decimal(0.25)):
    sellRevenue = (sellPrice * defaultTradeSize)
    sellFee = (sellPrice * defaultTradeSize * sellerFee)

    totalSellRevenue = sellRevenue - sellFee

    buyCost = (buyPrice * defaultTradeSize)
    buyFee = (buyPrice * defaultTradeSize * buyerFee)

    totalBuyCost = buyCost + buyFee
    totalFees = sellFee + buyFee

    profit = totalSellRevenue - totalBuyCost

    return profit, totalSellRevenue, totalBuyCost, totalFees


def unconfirmedDepositsCheck(exchanges, db):
    for cur in exchanges:
        data = db.getAllInTransitTransactionsFromTargetExchange(cur.name)
        if data != []:
            cur.unconfirmedDeposits = True
        elif data == [] and cur.unconfirmedDeposits is True:
            cur.unconfirmedDeposits = False

def main():

    """
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
    print bitstamp.getAccountBalance("BTC")
    print bitstamp.buy(1)

    print btce.getAccountBalance("BTC")
    print btce.getAccountBalance("USD")
    print btce.getAccountBalance()

    print bitstamp.getAccountBalance("BTC")
    print bitstamp.getAccountBalance("USD")
    print bitstamp.getAccountBalance()
    """



    db = Database.Database()

    testID = db.createNewTransaction('INT', 0.25, 'Bitfinex', 'Bitstamp', 560.03)
    testID = db.createNewTransaction('INT', 0.25, 'Bitfinex', 'Bitstamp', 540.69)
    testID = db.createNewTransaction('PND', 0.25, 'Bitfinex', 'Bitstamp', 560.03)
    #testID = db.createNewTransaction('PND', 0.25, 'Bitfinex', 'Bitstamp', 560.03)
    #db.clearOutTargetExchange(testID)

    defaultTradeSize = Decimal(0.25)
    defaultProfitMargin = Decimal(0.50)
    transactionFeeAmt = Decimal(0.0001)

    bitstamp = BitstampExchange()
    btce = BTCEExchange()


    exchanges = []
    global_ticker = {}

    exchanges.append(bitstamp)
    exchanges.append(btce)

    unconfirmedDepositsCheck(exchanges, db)

    """
    Populate ticker information for all exchanges, returning JSON format of {Bitcoin exchange name: name, buy: buy price, sell: sell price}
    """
    for ex in exchanges:
        json = ex.getTicker()
        exTicker = {'name': ex.name, 'buy': json['buy'], 'sell': json['sell'], 'fee': json['fee']}
        global_ticker[ex.name] = exTicker

    """
    Main program loop: for all exchanges, get ticker information
    """
    while 1:
        # check for unconfirmed deposits - just in case unconfirmed deposits flag is not set
        unconfirmedDepositsCheck(exchanges, db)
        for ex in exchanges:
            json = ex.getTicker() #this call MUST return a dict with these elements or it WILL blow up
            exTicker = {'name': ex.name, 'buy': json['buy'], 'sell': json['sell'], 'fee': json['fee']}
            global_ticker[ex.name] = exTicker

            # get balance in BTC from exchange - need this to process In Transit transactions
            balanceInBTC = Decimal(0.75013415)
            """
            Process all transactions with this exchange as a target (may replace later with individual
            database calls - slower but more accurate)
            """

            """
            Process all IN TRANSIT transactions with exchange as target
            """
            inTransit = sorted(db.getAllInTransitTransactionsFromTargetExchange(ex.name), key=itemgetter('ORIGINAL_BUY_PRICE'), reverse=False)
            for cur in inTransit:
                """
                Calculate if BTC has arrived
                    If it has, calculate the exact amount received
                        If it has:
                            Mark as active
                        Else:
                            Mark as pending
                            Remove target exchange, set current exchange to origin
                """

                # calculate if BTC has arrived
                if balanceInBTC > 0:
                    allPending = db.getAllPendingTransactionsFromTargetExchange(ex.name)
                    allActive = db.getAllActiveTransactionsFromTargetExchange(ex.name)

                    # sum all pending transactions BTC amount
                    totalPendingAmount = 0
                    for pnd in allPending:
                        totalPendingAmount += Decimal(pnd['AMOUNT'])

                    # sum all active transactions BTC amount
                    totalActiveAmount = 0
                    for act in allActive:
                        totalActiveAmount += Decimal(act['AMOUNT'])

                    # if there's BTC not included in the total pending + active amount, BTC has arrived
                    if balanceInBTC - totalPendingAmount - totalActiveAmount >= 0.001:
                        allInTransit = db.getAllInTransitTransactionsFromTargetExchange(ex.name)

                        # add up all other In Transit transactions to approximate the actual amount received
                        inTransitAmountMinusCur = 0
                        for intrans in allInTransit:
                            if intrans['ID'] != cur['ID']:
                                inTransitAmountMinusCur += Decimal(intrans['AMOUNT'])

                        # if there's enough to complete the transaction, set it to Active to subtract it for the
                        # next values in the transaction list that are In Transit also
                        if balanceInBTC - totalPendingAmount - totalActiveAmount >= cur['AMOUNT'] - 0.001:
                            newAmount = balanceInBTC - totalPendingAmount - totalActiveAmount - inTransitAmountMinusCur
                            db.changeTransactionStatus(cur['ID'], 'ACT')
                            db.changeAmount(cur['ID'], Decimal(newAmount))


            """
            Process all ACTIVE transactions with exchange as target
            """
            actives = db.getAllActiveTransactionsFromTargetExchange(ex.name)
            for cur in actives:
                """
                Calculate whether a profit can still be made
                    If it can:
                        Sell the BTC
                        Mark object as closed, record real profit amount (somewhere??)
                    Else:
                        Mark object as pending
                        Clear out target exchange, set current exchange to origin
                """
                
                # calculate whether a profit can be made
                curSell = ex.getCurrentSellPrice()
                
                # enter 0 for buy fee - was factored into the original buy price
                profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(curSell, cur['ORIGINAL_BUY_PRICE'],
                                                                                                exTicker['fee'], 0)
                # if profit can be made, sell and mark object as closed
                if profit >= defaultProfitMargin:
                    print "Selling Active transaction " + str(cur['ID']) + " on " + ex.name + " exchange."
                    print "-expected sell revenue: $" + str('{0:.2f}'.format(totalSellRevenue))
                    print "-total buy cost: $" + str('{0:.2f}'.format(totalBuyCost))
                    print "-total fees: $" + str('{0:.2f}'.format(totalFees))
                    print "-EXPECTED PROFIT: $" + str('{0:.2f}'.format(profit))
                    
                    # sell the BTC on the current (target) exchange
                    
                

            """
            Process all PENDING transactions with exchange as target
            """
            pending = db.getAllPendingTransactionsFromTargetExchange(ex.name)
            for cur in pending:
                """
                If profit can be made by selling on this exchange:
                    Sell the BTC
                    Mark object as closed, record real profit amount (somewhere??)
                Else:
                    Remove target exchange, set current exchange to origin
                """

            """
            Get all transactions with this exchange as an origin (may replace later with individual
            database calls - slower but more accurate)
            """
            for cur in db.getAllTransactionsFromOriginExchange(ex.name):
                """
                Process all PENDING transactions with exchange as origin
                """
                if cur['STATUS'] == 'PND':
                    """
                    If profit can be made by selling on this exchange:
                        Sell the BTC
                        Mark object as closed, record real profit amount (somewhere??)
                    """

                    """
                    If profit can be made by selling on a remote exchange:
                       Mark object as IN TRANSIT, set target exchange as remote exchange
                       Withdraw to target exchange
                    """

            """
            Find buy low / sell high pairing if it exists by comparing all exchange price points
            """
            for key, cur in global_ticker.iteritems():
                if key != ex.name:
                    """
                    If a profit can be made by buying / selling on another exchange, set up a new transaction

                    Profit formula: (sell price - sell fee) - (buy price + buy fee + transaction fee) = profit
                    """
                    for key2, remote in global_ticker.iteritems():
                        if key2 != key:
                            """
                            If profit can be made via the following
                                BUY: Remote Exchange: KEY2
                                SELL: Current Exchange: KEY
                            BUY the BTC
                            Create a new transaction
                            Withdraw the coins [remote -> cur]
                            """

                            remoteExchange = getExchangeByName(exchanges, key2)
                            currentExchange = getExchangeByName(exchanges, key)

                            curSell = cur['sell']
                            remoteSell = remote['sell']
                            curBuy = cur['buy']
                            remoteBuy = remote['buy']
                            curFee = cur['fee']
                            remoteFee = remote['fee']

                            profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(curSell, remoteBuy,
                                                                                                curFee, remoteFee)

                            if profit >= defaultProfitMargin:
                                print "Profit opportunity: buying from " + key2 + " and selling on " + key
                                print "-total sell revenue: $" + str('{0:.2f}'.format(totalSellRevenue))
                                print "-total buy cost: $" + str('{0:.2f}'.format(totalBuyCost))
                                print "-total fees: $" + str('{0:.2f}'.format(totalFees))
                                print "-PROFIT: $" + str('{0:.2f}'.format(profit))

                                # make sure the buy went through before making a new transaction

                                print "Attempting to buy " + str(defaultTradeSize) + " from " + key2 + " exchange!"
                                json = remoteExchange.buy(defaultTradeSize)
                                if json['success'] != 0:
                                    # if buy is successful, make new transaction
                                    print "Buy successful, bought " + str(json['amount']) + "@ $" + str(json['price'])

                                    # if buy price is different than expected, record it in the transaction
                                    totalBuyCost = (json['price'] * defaultTradeSize) + (json['price'] * defaultTradeSize * remoteFee)
                                    id = db.createNewTransaction('NEW', defaultTradeSize, key2, key, totalBuyCost)

                                    # if profit margin still exists with locked in buy price:
                                    # withdraw and change transaction status
                                    curSell = currentExchange.getCurrentSellPrice()
                                    remoteBuy = json['price']

                                    # set buy fee to 0, it's already factored into totalBuyCost above
                                    profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(curSell,
                                                                                                        remoteBuy,
                                                                                                        curFee,
                                                                                                        0)

                                    if profit >= defaultProfitMargin:

                                        # withdraw to the current exchange
                                        remoteExchange.withdrawToAddress(currentExchange.getBTCAddress(), json['amount'])

                                        # set transaction status to In Transit
                                        db.changeTransactionStatus(id, 'INT')

                                    # else, check if a profit can be made on the remote exchange, change status
                                    # this is only possible with large price swings or transactions severely delayed
                                    else:
                                        # if profit can be made, sell and set as closed
                                        remoteSell = remoteExchange.getCurrentSellPrice()
                                        originalBuyPrice = db.getTransactionBuyPrice(id)

                                        # set buy fee to 0 for this calc, already factored into original buy price
                                        profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(remoteSell,
                                                                                        originalBuyPrice, remoteFee, 0)

                                        if profit >= defaultProfitMargin:
                                            # sell the coins on the remote exchange
                                            remoteExchange.sell(json['amount'])
                                            # set as closed
                                            db.changeTransactionStatus(id, 'CLD')
                                        # otherwise, set to pending and clear out target exchange
                                        else:
                                            # set as pending
                                            db.changeTransactionStatus(id, 'PND')
                                            # clear out target exchange
                                            db.clearOutTargetExchange(id)
                                else:
                                    print "Something went wrong while trying to buy. Transaction was not created."

                            """
                            If profit can be made via the following
                                BUY: Current Exchange: KEY
                                SELL: Remote Exchange: KEY2
                            BUY the BTC
                            Create a new transaction
                            Withdraw the coins [cur - > remote]
                            """

                            profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(remoteSell, curBuy,
                                                                                                remoteFee, curFee)

                            if profit >= defaultProfitMargin:
                                print "Profit opportunity: buying from " + key + " and selling on " + key2
                                print "-total sell revenue: $" + str('{0:.2f}'.format(totalSellRevenue))
                                print "-total buy cost: $" + str('{0:.2f}'.format(totalBuyCost))
                                print "-total fees: $" + str('{0:.2f}'.format(totalFees))
                                print "-PROFIT: $" + str('{0:.2f}'.format(profit))

                                # make sure the buy went through before making a new transaction

                                print "Attempting to buy " + str(defaultTradeSize) + " from " + key + " exchange!"
                                json = currentExchange.buy(defaultTradeSize)
                                if json['success'] != 0:
                                    # if buy is successful, make new transaction
                                    print "Buy successful, bought " + str(json['amount']) + "@ $" + str(json['price'])

                                    # if buy price is different than expected, record it in the transaction
                                    totalBuyCost = (json['price'] * defaultTradeSize) + (json['price'] * defaultTradeSize * curFee)
                                    id = db.createNewTransaction('NEW', defaultTradeSize, key2, key, totalBuyCost)

                                    # if profit margin still exists with locked in buy price:
                                    # withdraw and change transaction status
                                    remoteSell = remoteExchange.getCurrentSellPrice()
                                    curBuy = json['price']

                                    # set buy fee to 0, it's already factored into totalBuyCost above
                                    profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(curSell,
                                                                                                        remoteBuy,
                                                                                                        curFee,
                                                                                                        0)

                                    if profit >= defaultProfitMargin:

                                        # withdraw to the current exchange
                                        currentExchange.withdrawToAddress(remoteExchange.getBTCAddress(),
                                                                          json['amount'])

                                        # set transaction status to In Transit
                                        db.changeTransactionStatus(id, 'INT')

                                    # else, check if a profit can be made on the current exchange, change status
                                    # this is only possible with large price swings or transactions severely delayed
                                    else:
                                        # if profit can be made, sell and set as closed
                                        curSell = currentExchange.getCurrentSellPrice()
                                        originalBuyPrice = db.getTransactionBuyPrice(id)

                                        # set buy fee to 0 for this calc, already factored into original buy price
                                        profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(curSell,
                                                                                                            originalBuyPrice,
                                                                                                            curFee,
                                                                                                            0)

                                        if profit >= defaultProfitMargin:
                                            # sell the coins on the remote exchange
                                            currentExchange.sell(json['amount'])
                                            # set as closed
                                            db.changeTransactionStatus(id, 'CLD')
                                        # otherwise, set to pending and clear out target exchange
                                        else:
                                            # set as pending
                                            db.changeTransactionStatus(id, 'PND')
                                            # clear out target exchange
                                            db.clearOutTargetExchange(id)
                                else:
                                    print "Something went wrong while trying to buy. Transaction was not created."


if __name__ == "__main__":
    main()

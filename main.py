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


def processAllNewTransactions(db, exchanges):
    """
    Process all NEW transactions - buy orders that have not yet been filled.
    This must be done prior to other commands to make sure the buy orders can be processed in a timely fashion.
    """
    newTrans = sorted(db.getAllNewTransactions(), key=itemgetter('ORIGINAL_BUY_PRICE'), reverse=False)

    for trans in newTrans:
        # retrieve the origin exchange object
        exchange = getExchangeByName(exchanges, trans['ORIGIN_EXCHANGE'])

        withdraw = False
        remoteAddress = None
        amount = trans['AMOUNT']

        # if exchange is Bitstamp, use Order Status - change to In Transit and withdraw if complete
        if exchange.name == "Bitstamp":
            if exchange.getOrderStatus(trans['ORDER_ID']) == "Finished":
                remoteAddress = getExchangeByName(exchanges, trans['TARGET_EXCHANGE']).getBTCAddress()
                withdraw = True

        #  for all other exchanges: if the order no longer appears in the open orders list, withdraw and complete
        else:
            openList = exchange.getOpenOrders()
            for op in openList:
                if op['id'] == trans['ORDER_ID']:
                    remoteAddress = exchange.getBTCAddress()
                    withdraw = True

        if withdraw == True:
            exchange.withdrawToAddress(remoteAddress, trans['AMOUNT'])
            db.changeTransactionStatus(trans['ID'], 'INT')


def findExchangePairs(current, exchanges, curBuy=0, defaultProfitMargin=0.50):
    """
    Takes a particular exchange and finds any potential profit pairs, sorting by the highest profit.
    """
    pairs = []
    for remote in exchanges:
        if remote != current:

            # update both the current and remote exchange ticker values
            curTicker = current.getTicker()
            remoteTicker = remote.getTicker()

            curSell = curTicker['sell']
            remoteSell = remoteTicker['sell']
            if curBuy == 0:
                curBuy = curTicker['buy']
            remoteBuy = remoteTicker['buy']
            curFee = curTicker['fee']
            remoteFee = remoteTicker['fee']

            """
            If profit is available by buying on the current exchange and selling remotely, store in list
            """
            # BUY from current, SELL on remote
            profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(remoteSell, curBuy,
                                                                                remoteFee, curFee)

            if profit >= defaultProfitMargin:
                pairs.append({'profit': profit, 'sellExchange': remote, 'buyExchange': current})

            """
            If profit is available by buying on a remote exchange and selling on this exchange, store in list
            """
            # BUY from remote, SELL on current
            profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(curSell, remoteBuy,
                                                                                curFee, remoteFee)
            if profit >= defaultProfitMargin:
                pairs.append({'profit': profit, 'sellExchange': current, 'buyExchange': remote})

            """
            Sort the list by highest expected profit
            """
            sorted(pairs, key=itemgetter('profit'), reverse=False)

    return pairs



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

    testID = db.createNewTransactionWithOrderID('NEW', 0.25, 'BTC-E', 'Bitstamp', 560.03, 12446)
    testID = db.createNewTransactionWithOrderID('NEW', 0.25, 'Bitstamp', 'BTC-E', 540.69, 12447)
    testID = db.createNewTransaction('PND', 0.25, 'BTC-E', 'Bitstamp', 560.03)
    db.clearOutTargetExchange(testID)
    test = db.getAllTransactions()
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

    bitstamp.buy(2)
    btce.buy(2)
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

        for ex in exchanges:
            """
            Process all NEW transactions - buy orders that have not yet been filled.
            This must be done prior to other commands to make sure the buy orders can be processed in a timely fashion.
            """
            processAllNewTransactions(db, exchanges)

            json = ex.getTicker()  # this call MUST return a dict with these elements or it WILL blow up
            exTicker = {'name': ex.name, 'buy': json['buy'], 'sell': json['sell'], 'fee': json['fee']}
            global_ticker[ex.name] = exTicker
            """
            Process all transactions with this exchange as a target (may replace later with individual
            database calls - slower but more accurate)
            """

            """
            Process all IN TRANSIT transactions with exchange as target
            """
            inTransit = sorted(db.getAllInTransitTransactionsFromTargetExchange(ex.name), key=itemgetter('ORIGINAL_BUY_PRICE'), reverse=False)

            # get balance in BTC from exchange - need this to process In Transit transactions
            balanceInBTC = Decimal(0.7492341)
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

                # calculate if BTC has arrived, mark as active
                if balanceInBTC > 0:
                    totalPendingAmount = db.getSumOfAllPendingTransactionsByTargetExchange(ex.name)
                    totalActiveAmount = db.getSumOfAllActiveTransactionsByTargetExchange(ex.name)
                    totalIntransAmount = db.getSumOfAllInTransitTransactionsByTargetExchange(ex.name)

                    # sum up the total expected amount for this exchange to make sure there's no errors
                    totalExpectedAmount = totalPendingAmount + totalActiveAmount + totalIntransAmount

                    # discrepancy - tracks the total amount "missing" vs. the expected value lost via transaction fee
                    discrepancy = Decimal(abs(totalExpectedAmount - balanceInBTC))

                    # if rounding errors (or otherwise) exist, roll them into the amount to get the actual amount
                    if discrepancy > 0:
                        print "In Transit transaction discrepancy found on " + ex.name + ": " + str(discrepancy) + " BTC"
                        noOfTrans = Decimal(len(db.getAllInTransitTransactionsFromTargetExchange(ex.name)))
                        adjust = Decimal(cur['AMOUNT']) * discrepancy * noOfTrans
                        print "Modifying transaction " + str(cur['ID']) + ", adjusting amount down " + str(adjust)
                        cur['AMOUNT'] = Decimal(cur['AMOUNT']) - adjust

                        # persist changes at the database level
                        db.changeAmount(cur['ID'], Decimal(cur['AMOUNT']) - adjust)

                    # test = balanceInBTC - totalPendingAmount - totalActiveAmount

                    # if there's BTC not included in the total pending + active amount, some BTC has arrived
                    if balanceInBTC - totalPendingAmount - totalActiveAmount >= cur['AMOUNT']:
                        # get new value after database update
                        totalIntransAmount = db.getSumOfAllInTransitTransactionsByTargetExchange(ex.name)

                        # add up all other In Transit transactions to approximate the actual amount received
                        inTransitAmountMinusCur = totalIntransAmount - Decimal(cur['AMOUNT'])

                        # if there's enough to complete the transaction, set it to Active
                        # test = balanceInBTC - totalPendingAmount - totalActiveAmount - inTransitAmountMinusCur
                        if balanceInBTC - totalPendingAmount - totalActiveAmount - inTransitAmountMinusCur >= cur['AMOUNT']:
                            db.changeTransactionStatus(cur['ID'], 'ACT')

            """
            Process all PENDING transactions with exchange as target
            """
            pending = db.getAllPendingTransactionsFromTargetExchange(ex.name)
            for cur in pending:
                """
                If profit can be made by selling on this exchange:
                    Mark as active
                Else:
                    Remove target exchange, set current exchange to origin
                """
                curSell = Decimal(ex.getCurrentSellPrice())

                profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfitNoTransactionFee(curSell, Decimal(cur['ORIGINAL_BUY_PRICE']), exTicker['fee'], 0)

                # if coins can be sold for a profit on this exchange, mark as active
                if profit >= defaultProfitMargin:
                    db.changeTransactionStatus(cur['ID'], 'ACT')

                # else, remove target exchange if it exists and set the current exchange as the origin
                else:
                    db.clearOutTargetExchange(cur['ID'])
                    db.changeOriginExchange(cur['ID'], ex.name)

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
                curSell = Decimal(ex.getCurrentSellPrice())
                
                # enter 0 for buy fee - was factored into the original buy price
                profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfitNoTransactionFee(curSell, Decimal(cur['ORIGINAL_BUY_PRICE']),
                                                                                                exTicker['fee'], 0)
                # if profit can be made, sell and mark object as closed
                if profit >= defaultProfitMargin:
                    print "Selling Active transaction " + str(cur['ID']) + " on " + ex.name + " exchange."
                    print "-expected sell revenue: $" + str('{0:.2f}'.format(totalSellRevenue))
                    print "-total buy cost: $" + str('{0:.2f}'.format(totalBuyCost))
                    print "-total fees: $" + str('{0:.2f}'.format(totalFees))
                    print "-EXPECTED PROFIT: $" + str('{0:.2f}'.format(profit))
                    
                    # sell the BTC on the current (target) exchange
                    print "Attempting to sell " + str(cur['AMOUNT']) + " on " + ex.name + " exchange!"
                    data = ex.sell(cur['AMOUNT'])

                    if data['success'] == 1:
                        # if sell went through, update and close transaction
                        db.changeFinalSellAmount(cur['ID'], data['amount'])
                        db.changeTransactionStatus(cur['ID'], 'CLD')
                    else:
                        print "Something went wrong while trying to sell. Transaction was not closed."
                else:
                    # set transaction to pending status
                    db.changeTransactionStatus(cur['ID'], 'PND')
                    # clear out target exchange
                    db.clearOutTargetExchange(cur['ID'])

            """
            Get all PENDING transactions with this exchange as an ORIGIN (may replace later with individual
            database calls - slower but more accurate)
            """
            test = db.getAllTransactions()
            pending = db.getAllPendingTransactionsFromOriginExchange(ex.name)
            for cur in pending:
                """
                If profit can be made by selling on this exchange:
                Sell the BTC
                Mark object as closed, record real profit amount (somewhere??)
                """

                # calculate whether a profit can be made
                curSell = Decimal(ex.getCurrentSellPrice())

                # enter 0 for buy fee - was factored into the original buy price
                profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfitNoTransactionFee(curSell, Decimal(
                    cur['ORIGINAL_BUY_PRICE']), exTicker['fee'], 0)

                # if profit can be made, sell and mark object as closed
                if profit >= defaultProfitMargin:
                    print "Selling Pending transaction " + str(cur['ID']) + " on " + ex.name + " exchange."
                    print "-expected sell revenue: $" + str('{0:.2f}'.format(totalSellRevenue))
                    print "-total buy cost: $" + str('{0:.2f}'.format(totalBuyCost))
                    print "-total fees: $" + str('{0:.2f}'.format(totalFees))
                    print "-EXPECTED PROFIT: $" + str('{0:.2f}'.format(profit))

                    # sell the BTC on the current (target) exchange
                    print "Attempting to sell " + str(cur['AMOUNT']) + " on " + ex.name + " exchange!"
                    data = ex.sell(cur['AMOUNT'])

                    if data['success'] == 1:
                        # if sell went through, update and close transaction
                        db.changeFinalSellAmount(cur['ID'], data['amount'])
                        db.changeTransactionStatus(cur['ID'], 'CLD')
                    else:
                        print "Something went wrong while trying to sell. Transaction was not closed."

                else:
                    """
                    If profit can be made by selling on a remote exchange:
                    Mark object as IN TRANSIT, set target exchange as remote exchange
                    Withdraw to target exchange
                    """
                    # use exchange pairs method to find the highest profit margin pair
                    pairs = findExchangePairs(ex, exchanges, Decimal(cur['ORIGINAL_BUY_PRICE']))

                    # use the first one returned in the list and sell
                    for pair in pairs:
                        if pair['sellExchange'] != ex:
                            remote = pair['sellExchange']
                            ex.withdrawToAddress(remote.getBTCAddress(), cur['AMOUNT'])
                            db.changeTransactionStatus(cur['ID'], 'INT')

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

                            if profit >= defaultProfitMargin and remoteExchange.readyForBuy is True:
                                print "Profit opportunity: buying from " + key2 + " and selling on " + key
                                print "-total sell revenue: $" + str('{0:.2f}'.format(totalSellRevenue))
                                print "-total buy cost: $" + str('{0:.2f}'.format(totalBuyCost))
                                print "-total fees: $" + str('{0:.2f}'.format(totalFees))
                                print "-PROFIT: $" + str('{0:.2f}'.format(profit))

                                # make sure the buy went through before making a new transaction

                                print "Attempting to buy " + str(defaultTradeSize) + " from " + key2 + " exchange!"
                                data = remoteExchange.buy(defaultTradeSize)

                                if data['success'] != 0:
                                    # if buy price is different than expected, record it in the transaction
                                    totalBuyCost = (data['price'] * data['amount']) + (data['price'] * data['amount'] * remoteFee)

                                    # if order ID is returned, buy is still being filled, needs time to execute
                                    # create a new transaction to track the buy and continue on through the loop
                                    if data['order_id'] != 0:
                                        id = db.createNewTransactionWithOrderID('NEW', data['amount'], key2, key, totalBuyCost, data['order_id'])
                                        print "Buy order is not complete, leaving in NEW status."
                                        continue

                                    # if buy is successful, make new transaction
                                    print "Buy successful, bought " + str(data['amount']) + "@ $" + str(data['price'])

                                    id = db.createNewTransaction('NEW', data['amount'], key2, key, totalBuyCost)

                                    # if profit margin still exists with locked in buy price:
                                    # withdraw and change transaction status
                                    curSell = currentExchange.getCurrentSellPrice()
                                    remoteBuy = remoteExchange.getCurrentBuyPrice()

                                    # set buy fee to 0, it's already factored into totalBuyCost above
                                    profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(curSell,
                                                                                                        remoteBuy,
                                                                                                        curFee,
                                                                                                        0)

                                    if profit >= defaultProfitMargin:

                                        # withdraw to the current exchange
                                        remoteExchange.withdrawToAddress(currentExchange.getBTCAddress(), data['amount'])

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
                                            # attempt to sell the coins on the remote exchange
                                            data2 = remoteExchange.sell(data['amount'])

                                            if data2['success'] == 1:
                                                # set final sell price
                                                db.changeFinalSellAmount(id, data2['amount'])
                                                # set as closed
                                                db.changeTransactionStatus(id, 'CLD')
                                            else:
                                                print "Something went wrong while trying to sell. Transaction was not closed."
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

                            if profit >= defaultProfitMargin and currentExchange.readyForBuy is True:
                                print "Profit opportunity: buying from " + key + " and selling on " + key2
                                print "-total sell revenue: $" + str('{0:.2f}'.format(totalSellRevenue))
                                print "-total buy cost: $" + str('{0:.2f}'.format(totalBuyCost))
                                print "-total fees: $" + str('{0:.2f}'.format(totalFees))
                                print "-PROFIT: $" + str('{0:.2f}'.format(profit))

                                # make sure the buy went through before making a new transaction

                                print "Attempting to buy " + str(defaultTradeSize) + " from " + key + " exchange!"
                                data = currentExchange.buy(defaultTradeSize)

                                if data['success'] != 0:
                                    # if buy price is different than expected, record it in the transaction
                                    totalBuyCost = (data['price'] * data['amount']) + (data['price'] * data['amount'] * curFee)

                                    # if order ID is returned, buy is still being filled, needs time to execute
                                    # create a new transaction to track the buy and continue on through the loop
                                    if data['order_id'] != 0:
                                        id = db.createNewTransactionWithOrderID('NEW', data['amount'], key, key2,
                                                                                totalBuyCost, data['order_id'])
                                        print "Buy order is not complete, leaving in NEW status."
                                        continue

                                    # if buy is successful, make new transaction
                                    print "Buy successful, bought " + str(data['amount']) + "@ $" + str(data['price'])

                                    id = db.createNewTransaction('NEW', data['amount'], key, key2, totalBuyCost)

                                    # if profit margin still exists with locked in buy price:
                                    # withdraw and change transaction status
                                    remoteSell = remoteExchange.getCurrentSellPrice()
                                    curBuy = currentExchange.getCurrentBuyPrice()

                                    # set buy fee to 0, it's already factored into totalBuyCost above
                                    profit, totalSellRevenue, totalBuyCost, totalFees = calculateProfit(curSell,
                                                                                                        remoteBuy,
                                                                                                        curFee,
                                                                                                        0)

                                    if profit >= defaultProfitMargin:

                                        # withdraw to the current exchange
                                        currentExchange.withdrawToAddress(remoteExchange.getBTCAddress(),
                                                                          data['amount'])

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
                                            data2 = currentExchange.sell(data['amount'])

                                            if data2['success'] == 1:
                                                # set final sell price
                                                db.changeFinalSellAmount(id, data2['amount'])
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

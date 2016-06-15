import json
import sqlite3
from decimal import Decimal


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.conn.row_factory = self.dict_factory
        self.newInsert = "INSERT INTO BOT_TRANSACTION (STATUS,AMOUNT,ORIGIN_EXCHANGE,TARGET_EXCHANGE," \
                         "ORIGINAL_BUY_PRICE) VALUES"
        self.newInsertOrderID = "INSERT INTO BOT_TRANSACTION (STATUS,AMOUNT,ORIGIN_EXCHANGE,TARGET_EXCHANGE," \
                                "ORIGINAL_BUY_PRICE, ORDER_ID) VALUES"
        self.getByID = "SELECT * FROM BOT_TRANSACTION WHERE ID={id}"
        self.getAll = "SELECT * FROM BOT_TRANSACTION"
        self.getAllPending = "SELECT * FROM BOT_TRANSACTION WHERE STATUS='PND'"
        self.getAllActive = "SELECT * FROM BOT_TRANSACTION WHERE STATUS='ACT'"
        self.getAllInTransit = "SELECT * FROM BOT_TRANSACTION WHERE STATUS='INT'"
        self.getAllClosed = "SELECT * FROM BOT_TRANSACTION WHERE STATUS='CLD'"
        self.getAllNew = "SELECT * FROM BOT_TRANSACTION WHERE STATUS='NEW'"

        self.getAllFromTargetExchange = "SELECT * FROM BOT_TRANSACTION WHERE TARGET_EXCHANGE='{te}'"
        self.getAllPendingFromTargetExchange = "SELECT * FROM BOT_TRANSACTION WHERE TARGET_EXCHANGE='{te}' " \
                                               "AND STATUS='PND'"
        self.getAllActiveFromTargetExchange = "SELECT * FROM BOT_TRANSACTION WHERE TARGET_EXCHANGE='{te}' " \
                                              "AND STATUS='ACT'"
        self.getAllNewFromTargetExchange = "SELECT * FROM BOT_TRANSACTION WHERE TARGET_EXCHANGE='{te}' " \
                                            "AND STATUS='NEW'"
        self.getAllInTransitFromTargetExchange = "SELECT * FROM BOT_TRANSACTION WHERE TARGET_EXCHANGE='{te}' " \
                                                 "AND STATUS='INT'"
        self.getAllClosedFromTargetExchange = "SELECT * FROM BOT_TRANSACTION WHERE TARGET_EXCHANGE='{te}' " \
                                              "AND STATUS='CLD'"
        
        self.getAllFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE ORIGIN_EXCHANGE='{oe}'"
        self.getAllPendingFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE STATUS='PND' AND ORIGIN_EXCHANGE='{oe}';"
        self.getAllActiveFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE ORIGIN_EXCHANGE='{oe}' " \
                                              "AND STATUS='ACT'"
        self.getAllNewFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE ORIGIN_EXCHANGE='{oe}' " \
                                           "AND STATUS='NEW'"
        self.getAllInTransitFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE ORIGIN_EXCHANGE='{oe}' " \
                                                 "AND STATUS='INT'"
        self.getAllClosedFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE ORIGIN_EXCHANGE='{oe}' " \
                                              "AND STATUS='CLD'"

        self.getTransBuyPrice = "SELECT ORIGINAL_BUY_PRICE FROM BOT_TRANSACTION WHERE ID={id}"
        self.createTestTable()

    @staticmethod
    def dict_factory(cursor, row):
        """
        Method enables the database to return dictionaries instead of lists for easier item access
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def createNewTransaction(self, status, amount, origin_exchange, target_exchange, original_buy_price):
        #package the inner SQL string contents
        inner = self.newInsert + "('{st}', {am}, '{oe}', '{te}', {ob})".format(st=status, am=amount, oe=origin_exchange,
                                                                            te=target_exchange, ob=original_buy_price)
        #execute and return the ID of the new row
        self.conn.execute(inner)
        self.conn.commit()
        query = "select seq from sqlite_sequence where name='BOT_TRANSACTION'"
        seq = self.conn.execute(query).fetchone()
        return seq['seq']

    def createNewTransactionWithOrderID(self, status, amount, origin_exchange, target_exchange, original_buy_price, order_id):
        # package the inner SQL string contents
        inner = self.newInsertOrderID + "('{st}', {am}, '{oe}', '{te}', {ob}, {oi})".format(st=status, am=amount, oe=origin_exchange,
                                                                               te=target_exchange,
                                                                               ob=original_buy_price, oi=order_id)
        # execute and return the ID of the new row
        self.conn.execute(inner)
        self.conn.commit()
        query = "select seq from sqlite_sequence where name='BOT_TRANSACTION'"
        seq = self.conn.execute(query).fetchone()
        return seq['seq']

    """
    -----------------GET ALL TRANSACTIONS: RETURN EVERYTHING---------------------------
    """

    def getTransactionByID(self, ID):
        return self.conn.execute(self.getByID.format(id=ID))

    def getAllTransactions(self):
        return self.conn.execute(self.getAll).fetchall()

    def getAllPendingTransactions(self):
        return self.conn.execute(self.getAllPending).fetchall()

    def getAllActiveTransactions(self):
        return self.conn.execute(self.getAllActive).fetchall()

    def getAllInTransitTransactions(self):
        return self.conn.execute(self.getAllInTransit).fetchall()

    def getAllClosedTransactions(self):
        return self.conn.execute(self.getAllClosed).fetchall()

    def getAllNewTransactions(self):
        return self.conn.execute(self.getAllNew).fetchall()

    """
    ---------------------TARGET EXCHANGE GET TRANSACTIONS: RETURN ONLY FROM TARGET EXCHANGE---------------------------
    """

    def getAllTransactionsFromTargetExchange(self, target_exchange):
        query = self.getAllFromTargetExchange.format(te=target_exchange)
        return self.conn.execute(query).fetchall()


    def getAllPendingTransactionsFromTargetExchange(self, target_exchange):
        query = self.getAllPendingFromTargetExchange.format(te=target_exchange)
        return self.conn.execute(query).fetchall()

    def getAllActiveTransactionsFromTargetExchange(self, target_exchange):
        query = self.getAllActiveFromTargetExchange.format(te=target_exchange)
        return self.conn.execute(query).fetchall()

    def getAllInTransitTransactionsFromTargetExchange(self, target_exchange):
        query = self.getAllInTransitFromTargetExchange.format(te=target_exchange)
        return self.conn.execute(query).fetchall()

    def getAllClosedTransactionsFromTargetExchange(self, target_exchange):
        query = self.getAllClosedFromTargetExchange.format(te=target_exchange)
        return self.conn.execute(query).fetchall()

    def getAllNewTransactionsFromTargetExchange(self, target_exchange):
        query = self.getAllNewFromTargetExchange.format(te=target_exchange)
        return self.conn.execute(query).fetchall()

    """
    ---------------------ORIGIN EXCHANGE GET TRANSACTIONS: RETURN ONLY FROM ORIGIN EXCHANGE---------------------------
    """

    def getAllTransactionsFromOriginExchange(self, origin_exchange):
        query = self.getAllFromOriginExchange.format(oe=origin_exchange)
        return self.conn.execute(query).fetchall()

    def getAllPendingTransactionsFromOriginExchange(self, origin_exchange):
        query = self.getAllPendingFromOriginExchange.format(oe=origin_exchange)
        return self.conn.execute(query).fetchall()

    def getAllActiveTransactionsFromOriginExchange(self, origin_exchange):
        query = self.getAllActiveFromOriginExchange.format(oe=origin_exchange)
        return self.conn.execute(query).fetchall()

    def getAllInTransitTransactionsFromOriginExchange(self, origin_exchange):
        query = self.getAllInTransitFromOriginExchange.format(oe=origin_exchange)
        return self.conn.execute(query).fetchall()

    def getAllClosedTransactionsFromOriginExchange(self, origin_exchange):
        query = self.getAllClosedFromOriginExchange.format(oe=origin_exchange)
        return self.conn.execute(query).fetchall()

    def getAllNewTransactionsFromOriginExchange(self, origin_exchange):
        query = self.getAllNewFromOriginExchange.format(oe=origin_exchange)
        return self.conn.execute(query).fetchall()

    """
    --------------------------------------------GET TRANSACTIONS - Individual attributes--------------------------------
    """
    def getTransactionBuyPrice(self, ID):
        query = self.getTransBuyPrice.format(id=ID)
        return self.conn.execute(query).fetchall()

    def getSumOfAllPendingTransactionsByTargetExchange(self, exchange):
        query = "SELECT SUM(AMOUNT) as 'SUM' FROM BOT_TRANSACTION WHERE STATUS='PND' AND TARGET_EXCHANGE='{ex}';".format(ex=exchange)
        data = self.conn.execute(query).fetchone()

        if data['SUM'] != None:
            return Decimal(data['SUM'])
        else:
            return 0

    def getSumOfAllActiveTransactionsByTargetExchange(self, exchange):
        query = "SELECT SUM(AMOUNT) as 'SUM' FROM BOT_TRANSACTION WHERE STATUS='ACT' AND TARGET_EXCHANGE='{ex}';".format(ex=exchange)
        data = self.conn.execute(query).fetchone()

        if data['SUM'] != None:
            return Decimal(data['SUM'])
        else:
            return 0

    def getSumOfAllInTransitTransactionsByTargetExchange(self, exchange):
        query = "SELECT SUM(AMOUNT) as 'SUM' FROM BOT_TRANSACTION WHERE STATUS='INT' AND TARGET_EXCHANGE='{ex}';".format(ex=exchange)
        data = self.conn.execute(query).fetchone()

        if data != None:
            return Decimal(data['SUM'])

        return data

    """
     -------------------------------------------ALTER TRANSACTIONS------------------------------------------------------
    """
    def changeOriginExchange(self, ID, exchange):
        query = "UPDATE BOT_TRANSACTION SET ORIGIN_EXCHANGE='{oe}' WHERE ID={id}".format(oe=exchange, id=ID)
        self.conn.execute(query)
        self.conn.commit()




    def changeFinalSellAmount(self, ID, amount):
        query = "UPDATE BOT_TRANSACTION SET FINAL_SELL_PRICE='{am}' WHERE ID={id}".format(am=amount, id=ID)
        self.conn.execute(query)
        self.conn.commit()

    def changeTransactionStatus(self, ID, status):
        query = "UPDATE BOT_TRANSACTION SET STATUS='{st}' WHERE ID={id}".format(st=status, id=ID)
        self.conn.execute(query)
        self.conn.commit()

    def changeAmount(self, ID, amount):
        query = "UPDATE BOT_TRANSACTION SET AMOUNT='{am}' WHERE ID={id}".format(am=amount, id=ID)
        self.conn.execute(query)
        self.conn.commit()

    def clearOutTargetExchange(self, ID):
        query = "UPDATE BOT_TRANSACTION SET TARGET_EXCHANGE=NULL WHERE ID={id}".format(id=ID)
        self.conn.execute(query)
        self.conn.commit()

    def printResults(self, results):
        if results == []:
            print "NULL"
        else:
            for row in results:
                print json.dumps(row)

    def createTestTable(self):
        self.conn.execute('''CREATE TABLE BOT_TRANSACTION
            (ID                        INTEGER PRIMARY KEY     AUTOINCREMENT NOT NULL,
            CREATED                    DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            LAST_UPDATED               DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            STATUS                     CHAR(3)                 NOT NULL,
            AMOUNT                     REAL                    NOT NULL,
            ORIGIN_EXCHANGE            TEXT                    NOT NULL,
            TARGET_EXCHANGE            TEXT,
            ORDER_ID                   TEXT,
            ORIGINAL_BUY_PRICE         REAL                    NOT NULL,
            FINAL_SELL_PRICE           REAL

            );''')


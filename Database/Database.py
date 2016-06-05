import json
import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.conn.row_factory = self.dict_factory
        self.newInsert = "INSERT INTO BOT_TRANSACTION (STATUS,AMOUNT,ORIGIN_EXCHANGE,TARGET_EXCHANGE," \
                         "ORIGINAL_BUY_PRICE) VALUES"
        self.getByID = "SELECT * FROM BOT_TRANSACTION WHERE ID={id}"
        self.getAll = "SELECT * FROM BOT_TRANSACTION"
        self.getAllPending = "SELECT * FROM BOT_TRANSACTION WHERE STATUS='PND'"
        self.getAllActive = "SELECT * FROM BOT_TRANSACTION WHERE STATUS='ACT'"
        self.getAllInTransit = "SELECT * FROM BOT_TRANSACTION WHERE STATUS='INT'"
        self.getAllClosed = "SELECT * FROM BOT_TRANSACTION WHERE STATUS='CLD'"
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
        self.getAllPendingFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE ORIGIN_EXCHANGE='{oe}' " \
                                               "AND STATUS='PND'"
        self.getAllActiveFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE ORIGIN_EXCHANGE='{oe}' " \
                                              "AND STATUS='ACT'"
        self.getAllNewFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE ORIGIN_EXCHANGE='{oe}' " \
                                           "AND STATUS='NEW'"
        self.getAllInTransitFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE ORIGIN_EXCHANGE='{oe}' " \
                                                 "AND STATUS='INT'"
        self.getAllClosedFromOriginExchange = "SELECT * FROM BOT_TRANSACTION WHERE ORIGIN_EXCHANGE='{oe}' " \
                                              "AND STATUS='CLD'"
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
        if self.conn.execute(inner):
            self.conn.commit()
            return self.cursor.lastrowid()

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
     -------------------------------------------ALTER TRANSACTIONS-----------------------------------------------------
    """
    def changeTransactionStatus(self, ID, status):
        query = "UPDATE BOT_TRANSACTION SET STATUS='{st}' WHERE ID={id}".format(st=status, id=ID)
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
            ORIGINAL_BUY_PRICE         REAL                    NOT NULL,
            FINAL_SELL_PRICE           REAL

            );''')


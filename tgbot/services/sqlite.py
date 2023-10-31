import sqlite3


class Database:
    def __init__(self, path_to_db: str = "main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone: bool = False, fetchall: bool = False,
                commit: bool = False):
        if not parameters:
            parameters = ()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            verification_status TEXT,
            fiat_balance REAL,
            number_of_trades INTEGER,
            number_of_referrals INTEGER,
            earned_money REAL,
            currency TEXT,
            referral_status TEXT,
            date_of_registration TEXT
        );
        """
        self.execute(sql, commit=True)

    def create_table_crypto_balances(self):
        sql = """
        CREATE TABLE IF NOT EXISTS CryptoBalances (
            balance_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            usdt_balance REAL,
            eth_balance REAL,
            btc_balance REAL,
            FOREIGN KEY(user_id) REFERENCES Users(user_id)
        );
        """
        self.execute(sql, commit=True)

    # def create_table_referrals(self):
    #     sql = """
    #     CREATE TABLE IF NOT EXISTS Referrals (
    #         referral_id INTEGER PRIMARY KEY,
    #         user_id INTEGER,
    #         referred_user_id INTEGER,
    #         FOREIGN KEY(user_id) REFERENCES Users(user_id),
    #         FOREIGN KEY(referred_user_id) REFERENCES Users(user_id)
    #     );
    #     """
    #     self.execute(sql, commit=True)

    def create_table_crypto_offers(self):
        sql = """
        CREATE TABLE IF NOT EXISTS CryptoOffers (
            offer_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            offer_sum REAL,
            offer_type TEXT,
            is_active INTEGER,
            FOREIGN KEY(user_id) REFERENCES Users(user_id)
        );
        """
        self.execute(sql, commit=True)

    def create_table_blacklist(self):
        sql = """
        CREATE TABLE IF NOT EXISTS BlackList (
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES Users(user_id)
        );
        """
        self.execute(sql, commit=True)

    def create_extra_charge(self):
        sql = """
            CREATE TABLE IF NOT EXISTS ExtraCharge (
                extra_charge int,
                position int
            )
        """
        self.execute(sql, commit=True)

    @staticmethod
    def create_tables():
        Database().create_table_users()
        Database().create_table_crypto_balances()
        # Database().create_table_referrals()
        Database().create_table_crypto_offers()
        Database().create_table_blacklist()
        Database().create_extra_charge()

    @staticmethod
    def format_args(sql: str, parameters: dict) -> tuple:
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, user_id: int, name: str, username: str, referral_status: str, date_of_registration: str,
                 verification_status="False", fiat_balance=0.0, number_of_trades=0, number_of_referrals=0,
                 earned_money=0.0, currency="RUB"):
        sql = """INSERT INTO Users (user_id, name, username, verification_status, referral_status, date_of_registration, 
        fiat_balance, number_of_trades, number_of_referrals, earned_money, currency) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 
        ?, ?)"""
        parameters = (
            user_id, name, username, verification_status, referral_status, date_of_registration,
            fiat_balance, number_of_trades, number_of_referrals, earned_money, currency,)
        self.execute(sql, parameters, commit=True)

    def blacklist_user(self, user_id):
        sql = "INSERT INTO BlackList (user_id) VALUES (?)"
        parameters = (user_id,)
        self.execute(sql, parameters, commit=True)

    def add_crypto_balance(self, user_id: int, usdt_balance=0.0, eth_balance=0.0, btc_balance=0.0):
        sql = """
        INSERT INTO CryptoBalances (user_id, usdt_balance, eth_balance, btc_balance)
        VALUES (?, ?, ?, ?)
        """
        parameters = (user_id, usdt_balance, eth_balance, btc_balance,)
        self.execute(sql, parameters, commit=True)

    # def add_referral(self, user_id: int, referred_user_id: int):
    #     sql = """
    #     INSERT INTO Referrals (user_id, referred_user_id)
    #     VALUES (?, ?)
    #     """
    #     parameters = (user_id, referred_user_id,)
    #     self.execute(sql, parameters, commit=True)

    def add_crypto_offer(self, user_id: int, offer_sum: float, offer_type: str, is_active="True"):
        sql = """
        INSERT INTO CryptoOffers (user_id, offer_sum, offer_type, is_active)
        VALUES (?, ?, ?, ?)
        """
        parameters = (user_id, offer_sum, offer_type, is_active,)
        self.execute(sql, parameters, commit=True)

    def select_all_users(self) -> list:
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def select_all_referrals(self) -> list:
        sql = """
        SELECT * FROM Referrals
        """
        return self.execute(sql, fetchall=True)

    def select_all_blacklisted_users(self) -> list:
        sql = """
        SELECT user_id FROM BlackList
        """
        return self.execute(sql, fetchall=True)

    def select_referrals(self, **kwargs):
        sql = "SELECT * FROM Referrals WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def select_all_crypto_balances(self) -> list:
        sql = """
        SELECT * FROM CryptoBalances
        """
        return self.execute(sql, fetchall=True)

    def select_extra_charge(self) -> list:
        sql = """
        SELECT * FROM ExtraCharge
        """
        return self.execute(sql, fetchall=True)

    def select_crypto_balances(self, **kwargs):
        sql = "SELECT * FROM CryptoBalances WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def update_user_name(self, user_id: int, new_name: str):
        sql = "UPDATE Users SET name=? WHERE user_id=?"
        self.execute(sql, (new_name, user_id,), commit=True)

    def update_user_username(self, user_id: int, new_username: str):
        sql = "UPDATE Users SET username=? WHERE user_id=?"
        self.execute(sql, (new_username, user_id,), commit=True)

    def update_user_verification_status(self, user_id: int, new_verification_status: str):
        sql = "UPDATE Users SET verification_status=? WHERE user_id=?"
        self.execute(sql, (new_verification_status, user_id,), commit=True)

    def update_user_fiat_balance(self, user_id: int, new_fiat_balance: float):
        sql = "UPDATE Users SET fiat_balance=? WHERE user_id=?"
        self.execute(sql, (new_fiat_balance, user_id,), commit=True)

    def update_user_number_of_trades(self, user_id: int, new_number_of_trades: int):
        sql = "UPDATE Users SET number_of_trades=? WHERE user_id=?"
        self.execute(sql, (new_number_of_trades, user_id,), commit=True)

    def update_user_earned_money(self, user_id: int, new_earned_money: float):
        sql = "UPDATE Users SET earned_money=? WHERE user_id=?"
        self.execute(sql, (new_earned_money, user_id,), commit=True)

    def update_user_currency(self, user_id: int, new_currency: str):
        sql = "UPDATE Users SET currency=? WHERE user_id=?"
        self.execute(sql, (new_currency, user_id,), commit=True)

    def update_user_referral_status(self, user_id: int, new_referral_status: str):
        sql = "UPDATE Users SET referral_status=? WHERE user_id=?"
        self.execute(sql, (new_referral_status, user_id,), commit=True)

    def update_usdt_balance(self, user_id: int, new_usdt_balance: float):
        sql = "UPDATE CryptoBalances SET usdt_balance=? WHERE user_id=?"
        parameters = (new_usdt_balance, user_id,)
        self.execute(sql, parameters, commit=True)

    def update_eth_balance(self, user_id: int, new_eth_balance: float):
        sql = "UPDATE CryptoBalances SET eth_balance=? WHERE user_id=?"
        parameters = (new_eth_balance, user_id,)
        self.execute(sql, parameters, commit=True)

    def update_btc_balance(self, user_id: int, new_btc_balance: float):
        sql = "UPDATE CryptoBalances SET btc_balance=? WHERE user_id=?"
        parameters = (new_btc_balance, user_id,)
        self.execute(sql, parameters, commit=True)

    def update_extra_charge(self, new_extra_charge: int, position: int):
        sql = "UPDATE ExtraCharge SET extra_charge=? WHERE position=?"
        parameters = (new_extra_charge, position,)
        self.execute(sql, parameters, commit=True)

    def update_offer_sum(self, offer_id: int, new_offer_sum: float):
        sql = """
        UPDATE CryptoOffers SET offer_sum=?
        WHERE offer_id=?
        """
        parameters = (new_offer_sum, offer_id,)
        self.execute(sql, parameters, commit=True)

    def update_offer_type(self, offer_id: int, new_offer_type: str):
        sql = """
        UPDATE CryptoOffers SET offer_type=?
        WHERE offer_id=?
        """
        parameters = (new_offer_type, offer_id,)
        self.execute(sql, parameters, commit=True)

    def update_is_active(self, offer_id: int, new_is_active: int):
        sql = """
        UPDATE CryptoOffers SET is_active=?
        WHERE offer_id=?
        """
        parameters = (new_is_active, offer_id,)
        self.execute(sql, parameters, commit=True)

    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE", commit=True)

    def delete_crypto_offer(self, offer_id: int):
        sql = """
        DELETE FROM CryptoOffers
        WHERE offer_id=?
        """
        parameters = (offer_id,)
        self.execute(sql, parameters, commit=True)

    def unban(self, user_id: int):
        sql = """
        DELETE FROM BlackList
        WHERE user_id=?
        """
        parameters = (user_id,)
        self.execute(sql, parameters, commit=True)

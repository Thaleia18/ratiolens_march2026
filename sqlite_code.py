import sqlite3
import os


class RatioLensDatabase:
    def __init__(self, path, database_name):
        self.database_name = os.path.join(path, database_name)
        try:
          conn = sqlite3.connect(self.database_name)
          print("Database created: ",database_name)
        except:
          print("Database not formed.")
      
      
    def create_tables(self):
        sql_statements = [
            "DROP TABLE IF EXISTS tenk_concepts;",
            "DROP TABLE IF EXISTS accounting_ratios;",
            """
            CREATE TABLE IF NOT EXISTS tenk_concepts (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker                  TEXT NOT NULL,
                company                 TEXT NOT NULL,
                year                    TEXT NOT NULL,
                revenue                 REAL,
                gross_profit            REAL,
                net_income              REAL,
                current_assets_total    REAL,
                assets                  REAL,
                current_liabilities_total REAL,
                long_term_debt          REAL,
                all_equity_balance      REAL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS accounting_ratios (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker          TEXT NOT NULL,
                company         TEXT NOT NULL,
                year            TEXT NOT NULL,
                profit_margin   REAL,
                roe             REAL,
                current_ratio   REAL,
                debt_to_equity  REAL
            );
            """
        ] 

        try:
            with sqlite3.connect(self.database_name) as conn:
                cursor = conn.cursor()
                for stmt in sql_statements:
                    cursor.execute(stmt)
                conn.commit()
                print("Tables created successfully.")
        except sqlite3.OperationalError as e:
            print("Failed to create tables:", e)


def add_record(database_name, ticker, company, year, d):
    try:
        sqliteConnection = sqlite3.connect(database_name)
        sql = ''' INSERT INTO tenk_concepts(
                ticker, company, year, revenue, gross_profit, net_income, current_assets_total, assets,
                current_liabilities_total, long_term_debt, all_equity_balance)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?) '''      
        values = (
            ticker,
            company,
            year,
            d.get('revenue'),
            d.get('grossprofit'),
            d.get('netincome'),
            d.get('currentassetstotal'),
            d.get('assets'),
            d.get('currentliabilitiestotal'),
            d.get('longtermdebt'),
            d.get('allequitybalance')
        )
        cur = sqliteConnection.cursor()
        cur.execute(sql, values)
        sqliteConnection.commit()
        print(f'Created a record with the id {ticker, year}')
        sqliteConnection.close()
    except sqlite3.Error as error:
        print("Failed to connect with sqlite3 database", error)   

def record_exists(database_name, ticker, year):
    try:
        conn = sqlite3.connect(database_name)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM tenk_concepts WHERE ticker = ? AND year = ?", (ticker, year))
        exists = cur.fetchone() is not None
        conn.close()
        return exists
    except sqlite3.Error as error:
        print("Failed to query sqlite3 database", error)
        return False

def delete_record(database_name, ticker, year):
    try:
        sqliteConnection = sqlite3.connect(database_name)
        cur = sqliteConnection.cursor()
        sql = "DELETE FROM tenk_concepts WHERE ticker = ? and year=?"
        cur.execute(sql, (ticker,year))
        sqliteConnection.commit()
        print(f"Deleted record with name '{ticker, year}'")
        sqliteConnection.close()
    except sqlite3.Error as error:
        print("Failed to delete record from sqlite3 database", error)   
    
if __name__ == "__main__":
    mydb = RatioLensDatabase('data','RL_database.db')
    mydb.create_tables()
    #delete_record('RL_database.db', 'AAPL', '2020')
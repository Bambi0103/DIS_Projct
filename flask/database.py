import psycopg2
import csv
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self, user, password, dbname="guesstheplayerdb",  host="localhost", port="5432"):
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()
        self.basepath = Path(__file__).resolve(strict=True).parent

    def close(self): 
        self.cursor.close()
        self.connection.close()

    def query(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()
    
    # Creating a meethod that is able to only select the attribute 'full_name' from the players table
    def get_full_names(self, term: str, limit: int = 20000) -> list[str]:
        sql = """
            SELECT DISTINCT full_name FROM players
            WHERE full_name ILIKE %s
            LIMIT %s;
        """
        self.cursor.execute(sql, (f"%{term}%", limit))
        return [row[0] for row in self.cursor.fetchall()]

 
import psycopg2
import csv
from datetime import datetime
from pathlib import Path
import re


def convert_value(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return val
    
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{3,20}$") # 3-20 characters, letters/digits/underscore/dash only
PASSWORD_REGEX = re.compile(r"^(?=.*[^a-zA-Z0-9]).{5,}$") # at least 5 characters, at least one special character

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
    
  
    def get_all_player_names(self) -> list[str]:
        query = "SELECT full_name FROM players;"  
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [row[0] for row in results]
    
    def get_all_player_ids(self) -> list[dict]:
        query = "SELECT id FROM players;"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [{"id": row[0]} for row in results]
    
    def get_random_player(self) -> dict:
        query = "SELECT * FROM players ORDER BY RANDOM() LIMIT 1;"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result:
            columns = [desc[0] for desc in self.cursor.description]
            return dict(zip(columns, result))
        return {}

    
    def get_players_by_name(self, name: str) -> list[dict]:
        print("Searching for players with name:", name)
        self.cursor.execute(
            "SELECT * FROM players WHERE full_name ILIKE %(n)s",
            {"n": name},
        )
        results = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]

        return [
            {col: convert_value(val) for col, val in zip(columns, row)}
            for row in results
        ]
    
    def get_player_by_id(self, player_id: int) -> dict:
        print("Searching for player with ID:", player_id)
        query = "SELECT * FROM players WHERE id = %s;"
        self.cursor.execute(query, (player_id,))
        result = self.cursor.fetchone()
        if result:
            columns = [desc[0] for desc in self.cursor.description]
            result = {col: convert_value(val) for col, val in zip(columns, result)}
            return result
        return {}
    
    def user_exists(self, username: str) -> bool:
        self.cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        return self.cursor.fetchone() is not None 
    
    def add_user(self, username: str, password: str) -> None:
        """Password saved as plaintext - not secure, obviously"""
        if not USERNAME_REGEX.fullmatch(username):
            raise ValueError("Username 3-20 chars, letters/digits/underscore/dash only.")
        if not PASSWORD_REGEX.fullmatch(password):
            raise ValueError("Password must be at least 5 chars, with at least one special char.")
        self.cursor.execute("""
                            INSERT INTO users (username, password)
                            VALUES (%s, %s)
                            ON CONFLICT (username) DO NOTHING""",
                            (username, password)
                            )
        self.connection.commit()

    def get_user(self, username: str) -> dict | None:
        """Return user if exists, else return None"""
        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,)) # Comma to make one-element tuple :/
        row = self.cursor.fetchone()
        if row is not None:
            descriptions = self.cursor.description
            return {desc[0]: row[i] for i, desc in enumerate(descriptions)}
        return None
        
        

    def init_db(self):
        # Convert birth_date in CSV from mm/dd/yyyy to yyyy-mm-dd
        source_file = self.basepath / "../data/fifa_players.csv"
        source_file = source_file.resolve()
        output_file = self.basepath / "../data/players_converted.csv"
        output_file = output_file.resolve()

        self.cursor.execute("DROP TABLE IF EXISTS users;")

        with open(source_file, 'r', newline='', encoding='utf-8') as infile, \
            open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
               if row["birth_date"]:
                  try:
                     dt = datetime.strptime(row["birth_date"], "%m/%d/%Y")
                     row["birth_date"] = dt.strftime("%Y-%m-%d")
                  except ValueError:
                     pass  # Keep original if format is unexpected
               writer.writerow(row)

        input_file = output_file  

        # Drop existing table if exists and create a new one
        with open(self.basepath / "sql/init/init_players.sql", "r", encoding="utf-8") as f:
            create_table_query = f.read()
            self.cursor.execute(create_table_query)
            self.connection.commit()
            print("Old table dropped and new table created successfully.")

        # Load data from CSV file
        with open(input_file, 'r', encoding='utf-8') as file:
            self.cursor.copy_expert("""
            COPY players (
                name, full_name, birth_date, age, height_cm, weight_kgs,
                positions, nationality, overall_rating, potential, value_euro, wage_euro,
                preferred_foot, international_reputation, weak_foot, skill_moves, body_type,
                release_clause_euro, national_team, national_rating, national_team_position,
                national_jersey_number, crossing, finishing, heading_accuracy, short_passing,
                volleys, dribbling, curve, freekick_accuracy, long_passing, ball_control,
                acceleration, sprint_speed, agility, reactions, balance, shot_power,
                jumping, stamina, strength, long_shots, aggression, interceptions,
                positioning, vision, penalties, composure, marking, standing_tackle, sliding_tackle
            )
            FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
            """, file)

        self.connection.commit()
        print("Database initialized and data loaded successfully.")

        # Removes unnecessary properties
        with open(self.basepath / "sql/init/clean_data.sql", "r", encoding="utf-8") as f:
            clean_data_query = f.read()
            self.cursor.execute(clean_data_query)
            self.connection.commit()
            print("Unnecessary properties removed successfully.")


        with open(self.basepath / "sql/init/init_users.sql", "r", encoding="utf-8") as f:
            init_users_query = f.read()
            self.cursor.execute(init_users_query)
            self.connection.commit()
            print("Users table initialized successfully.")

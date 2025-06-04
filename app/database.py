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
    
    # Creating a method that is able to only select the attribute 'full_name' from the players table
    def get_all_player_names(self) -> list[str]:
        query = "SELECT full_name FROM players;"  # or whatever your table/column is
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
        self.cursor.execute(
            "SELECT * FROM players WHERE full_name ILIKE %(n)s",
            {"n": name},
        )
        results = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in results]
    
    def get_player_by_id(self, player_id: int) -> dict:
        query = "SELECT * FROM players WHERE id = %s;"
        self.cursor.execute(query, (player_id,))
        result = self.cursor.fetchone()
        if result:
            columns = [desc[0] for desc in self.cursor.description]
            return dict(zip(columns, result))
        return {}

    def init_db(self):
        # Convert birth_date in CSV from mm/dd/yyyy to yyyy-mm-dd
        source_file = self.basepath / "../data/fifa_players.csv"
        source_file = source_file.resolve()
        output_file = self.basepath / "../data/players_converted.csv"
        output_file = output_file.resolve()

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

        input_file = output_file  # Use the converted file for loading

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

        # Remove unnecessary properties
        with open(self.basepath / "sql/init/clean_data.sql", "r", encoding="utf-8") as f:
            clean_data_query = f.read()
            self.cursor.execute(clean_data_query)
            self.connection.commit()
            print("Unnecessary properties removed successfully.")

        with open(self.basepath / "sql/init/init_teams_table.sql", "r", encoding="utf-8") as f:
            init_teams_query = f.read()
            self.cursor.execute(init_teams_query)
            self.connection.commit()
            print("Teams table initialized successfully.")
            print("Foreign key constraints added successfully.")

        with open(self.basepath / "sql/init/init_users.sql", "r", encoding="utf-8") as f:
            init_users_query = f.read()
            self.cursor.execute(init_users_query)
            self.connection.commit()
            print("Users table initialized successfully.")

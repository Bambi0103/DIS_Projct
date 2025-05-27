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

    def init_db(self):
        drop_table_query = """
            DROP TABLE IF EXISTS players, teams;
            """
        self.cursor.execute(drop_table_query)
        self.connection.commit()
        print("Existing table dropped.")

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

        # Create a new table
        create_table_query = """
            CREATE TABLE players (
                id SERIAL PRIMARY KEY,
                name TEXT,
                full_name TEXT,
                birth_date DATE,
                age INTEGER,
                height_cm NUMERIC,
                weight_kgs NUMERIC,
                positions TEXT,
                nationality TEXT,
                overall_rating INTEGER,
                potential INTEGER,
                value_euro NUMERIC,
                wage_euro NUMERIC,
                preferred_foot TEXT,
                international_reputation INTEGER CHECK (international_reputation BETWEEN 1 AND 5),
                weak_foot INTEGER CHECK (weak_foot BETWEEN 1 AND 5),
                skill_moves INTEGER CHECK (skill_moves BETWEEN 1 AND 5),
                body_type TEXT,
                release_clause_euro NUMERIC,
                national_team TEXT,
                national_rating INTEGER,
                national_team_position TEXT,
                national_jersey_number INTEGER,
                crossing INTEGER,
                finishing INTEGER,
                heading_accuracy INTEGER,
                short_passing INTEGER,
                volleys INTEGER,
                dribbling INTEGER,
                curve INTEGER,
                freekick_accuracy INTEGER,
                long_passing INTEGER,
                ball_control INTEGER,
                acceleration INTEGER,
                sprint_speed INTEGER,
                agility INTEGER,
                reactions INTEGER,
                balance INTEGER,
                shot_power INTEGER,
                jumping INTEGER,
                stamina INTEGER,
                strength INTEGER,
                long_shots INTEGER,
                aggression INTEGER,
                interceptions INTEGER,
                positioning INTEGER,
                vision INTEGER,
                penalties INTEGER,
                composure INTEGER,
                marking INTEGER,
                standing_tackle INTEGER,
                sliding_tackle INTEGER
            );
        """

        self.cursor.execute(create_table_query)
        self.connection.commit()
        print("Table created successfully.")

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
        query = """
            ALTER TABLE players
            DROP COLUMN IF EXISTS weak_foot,
            DROP COLUMN IF EXISTS potential,
            DROP COLUMN IF EXISTS national_rating,
            DROP COLUMN IF EXISTS overall_rating,
            DROP COLUMN IF EXISTS body_type,
            DROP COLUMN IF EXISTS release_clause_euro,
            DROP COLUMN IF EXISTS finishing, 
            DROP COLUMN IF EXISTS crossing,
            DROP COLUMN IF EXISTS ball_control,
            DROP COLUMN IF EXISTS balance,
            DROP COLUMN IF EXISTS heading_accuracy,
            DROP COLUMN IF EXISTS short_passing,
            DROP COLUMN IF EXISTS volleys,
            DROP COLUMN IF EXISTS dribbling,
            DROP COLUMN IF EXISTS curve,
            DROP COLUMN IF EXISTS interceptions,
            DROP COLUMN IF EXISTS long_passing,
            DROP COLUMN IF EXISTS composure,
            DROP COLUMN IF EXISTS vision,
            DROP COLUMN IF EXISTS marking,
            DROP COLUMN IF EXISTS standing_tackle,
            DROP COLUMN IF EXISTS sliding_tackle,
            DROP COLUMN IF EXISTS skill_moves,
            DROP COLUMN IF EXISTS sprint_speed,
            DROP COLUMN IF EXISTS agility,
            DROP COLUMN IF EXISTS reactions,
            DROP COLUMN IF EXISTS shot_power,
            DROP COLUMN IF EXISTS jumping,
            DROP COLUMN IF EXISTS stamina,
            DROP COLUMN IF EXISTS strength,
            DROP COLUMN IF EXISTS long_shots,
            DROP COLUMN IF EXISTS aggression,
            DROP COLUMN IF EXISTS interceptions,
            DROP COLUMN IF EXISTS acceleration,
            DROP COLUMN IF EXISTS positioning;    
        """
        self.cursor.execute(query)
        self.connection.commit()

        query = """
            DELETE FROM players
            WHERE national_team IS NULL
            """
        self.cursor.execute(query)
        self.connection.commit()
        print("NULL fields removed successfully.")

        # Create table teams
        create_teams_query = """""""""
            CREATE TABLE teams (
                team_name TEXT PRIMARY KEY
            );"""
        
        self.cursor.execute(create_teams_query)
        self.connection.commit()
        print("Teams table created successfully.")


        # Insert unique national_team values into teams table
        self.cursor.execute("""
            INSERT INTO teams (team_name)
            SELECT DISTINCT national_team
            FROM players
        """)
        self.connection.commit()
        print("Teams table populated with unique team names.")

        # Create foreign key relationship with teams table
        query = """
            ALTER TABLE players
            ADD CONSTRAINT fk_national_team
            FOREIGN KEY (national_team) REFERENCES teams(team_name);
            """
        
        self.cursor.execute(query)
        self.connection.commit()
        print("Foreign key relationship created successfully.")
        
        
        

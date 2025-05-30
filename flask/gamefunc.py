from database import Database


db= Database(user="bruger", password="password")

#Guess button functionality


#helper function to feetch a single row from the database
def fetch_single_row(full_name: str) -> dict:
    sql = """
        SELECT * FROM players WHERE full_name = %s;
    """
    return db.query(sql, (full_name,))
# print(fetch_single_row("Cristiano Ronaldo dos Santos Aveiro"))


# Making it choose a random full_name for the game
def choose_random_fullname():
    sql = """
        SELECT full_name FROM players
        ORDER BY RANDOM() LIMIT 1;
    """
    return db.query(sql)
# print(choose_random_fullname()

# looking if the users answer is equal to the random full_name
def check_answer(guess: str, sql) -> bool:
    if guess != choose_random_fullname(sql):
        




# print(check_answer("Cristiano Ronaldo dos Santos Aveiro", "Cristiano Ronaldo dos Santos Aveiro"))
            



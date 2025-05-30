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
# def check_answer(guess: str) -> bool:
#     random_fullname = choose_random_fullname()
#     if random_fullname and 'full_name' in random_fullname[0]:
#         return guess == random_fullname[0]['full_name']
#     else:

#         guessed_player = fetch_single_row(guess)
#         random_player = choose_random_fullname()

#         guessed_player = guessed_player[0]
#         random_player = random_player[0]


#         comparison_results = {key: guessed_player[key] == random_player[key] for key in guessed_player if key in random_player}


#         print("Comparison:")
#         for attribute, is_same in comparison_results.items():
#             print(f"{attribute}: {is_same}")

#         return any(comparison_results.values())
    
# test_guess = "Cristiano Ronaldo dos Santos Aveiro"
# result = check_answer(test_guess)
# print(f"Result of the guess '{test_guess}': {result}")
    # Test the check_answer function


    




# fra chat:
# Check if guess is correct or compare attributes
# def check_answer(guess: str) -> bool:

#     random_player = choose_random_fullname()
#     if guess == random_player:
#         return True

#     # Fetch full player info for both players
#     guessed_player = fetch_single_row(guess)
#     target_player = fetch_single_row(random_player[0]['full_name'])
#     print(f"Guessed player: {guessed_player}")
#     if not guessed_player or not target_player:
#         return False

#     # Compare attribute-by-attribute
#     differences = {
#         attr: (guessed_player[0][attr], target_player[0][attr])
#         for attr in guessed_player[0]
#         if guessed_player[0][attr] != target_player[0].get(attr)
#     }

#     print(f"Your guess: {guess}")
#     print(f"The correct player was: {random_name}")
#     print("Differences:")
#     for attr, (val1, val2) in differences.items():
#         print(f" - {attr}: {val1} ≠ {val2}")

#     return False
# print(check_answer("Cristiano Ronaldo dos Santos Aveiro"))  
# chat slut^



# print(check_answer("Cristiano Ronaldo dos Santos Aveiro", "Cristiano Ronaldo dos Santos Aveiro"))
            



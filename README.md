# DIS_Project

## Initial Setup
Below works as of 05/06/2025 with (but not exclusively) Python version 3.12 
- Initialise a Python virtual environment (recommended) by running `python -m venv venv` (Windows) or `python3 -m venv venv` on Unix-based systems.
- Activate the virtual environment by running `venv\Scripts\activate.bat` in Windows, and `source /Scripts/activate` on Unix-based systems
- Install required packages by running `pip install -r requirements.txt`. This might break in the future, as we have not specified which versions of the packages (nor Python) are required. 
- Ensure that PostgreSQL is installed by running `psql --version`. Refer to [this website](https://www.postgresql.org/) for Windows and Linux, and to [this website](https://postgresapp.com/) on MacOS
- Create the required database by running `psql -c "CREATE DATABASE guesstheplayerdb"`
- If all above was successful, run the app with `python[3] run.py --usr \<db-username\> \[--pwd \<db-password\>\]
- You should now be presented with a localhost ip-address (127......) which should present you with the application login screen.
- The login accepts
    - Username: mixed-case letters (see shortcomings), numbers, dashes, and underscores of length 3-20 characters
    - Password: minimum length of 5 characters, must contain at least one special character

## Gameplay
The gameplay is very similar to that of Worlde or Loldle, only here, the one tries to guess a specific football player. When a guess is made, a table/list of attributes is presented where each attribute is marked true or false. If the attribute contains a numerical value, a difference is presented (e.g. -30 would represent that your guess was 30 too low). 

## Features
- User login with registration (incl. passwords \[unhashed, unsalted, not particularly secure\])
- Game mode - User can guess on the players
- Player attributes comparison by color coded boxes
- Flask backend with PostgreSQL database
- Uses CSS to define and design the frontend of the application

## Shortcomings
- The player dataset is outdated by 6 years, so the latest transfers and new players are not included and some stats may be outdated. 
- When creating a username, Danish characters such as "æ", "ø", and "å" are not allowed, as they are not supported by the login system. Only letters a thorugh z in both uppercase and lowercase-, underscores, and dashes are accepted.
- Whenever a guess is made, the previous guess results are overwritten (unlike wordle/loldle), so only the latest guess results are visible. 


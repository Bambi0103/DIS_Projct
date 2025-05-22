import argparse
import os
from setup import Database

CREDENTIALS_FILE = "cache/credentials.txt"

def save_credentials(user, password):
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
    with open(CREDENTIALS_FILE, "w") as f:
        f.write(f"{user}\n{password}\n")

def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        return None, None
    with open(CREDENTIALS_FILE, "r") as f:
        lines = f.read().splitlines()
        if len(lines) >= 2:
            return lines[0], lines[1]
    return None, None

parser = argparse.ArgumentParser(description="Database connection")
parser.add_argument("--user", help="Database username")
parser.add_argument("--password", help="Database password")
args = parser.parse_args()

if args.user and args.password:
    save_credentials(args.user, args.password)
    user, password = args.user, args.password
else:
    user, password = load_credentials()
    if not user or not password:
        raise RuntimeError("No credentials provided and no cached credentials found.")

db = Database(user=user, password=password)
db.init_db()
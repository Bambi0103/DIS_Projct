import argparse
import os
from setup import Database

CREDENTIALS_FILE = "cache/credentials.txt"

def save_credentials(user, password=None):
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
    with open(CREDENTIALS_FILE, "w") as f:
        f.write(f"{user}\n")
        if password is not None:
            f.write(f"{password}\n")

def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        return None, None
    with open(CREDENTIALS_FILE, "r") as f:
        lines = f.read().splitlines()
        user = lines[0] if len(lines) >= 1 else None
        password = lines[1] if len(lines) >= 2 else None
        return user, password

parser = argparse.ArgumentParser(description="Database connection")
parser.add_argument("--user", required=True, help="Database username")
parser.add_argument("--password", help="Database password (optional)")
args = parser.parse_args()

if args.user:
    save_credentials(args.user, args.password)
    user, password = args.user, args.password
else:
    user, password = load_credentials()
    if not user:
        raise RuntimeError("No username provided and no cached username found.")

db = Database(user=user, password=password)
db.init_db()
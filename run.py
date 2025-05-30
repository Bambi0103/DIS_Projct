# run.py
import argparse
from app import create_app

def main():
    parser = argparse.ArgumentParser(description="Run the 'Guess the Player' Flask app.")
    parser.add_argument("--usr", required=True, help="Database username")
    parser.add_argument("--pwd", required=True, help="Database password")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run on")
    parser.add_argument("--port", type=int, default=5000, help="Port to run on")

    args = parser.parse_args()

    app = create_app(db_user=args.usr, db_pass=args.pwd)
    app.run(debug=True, host=args.host, port=args.port)

if __name__ == "__main__":
    main()

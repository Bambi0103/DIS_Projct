CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    right_guesses INTEGER DEFAULT 0,
    wrong_guesses INTEGER DEFAULT 0
);
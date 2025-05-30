from flask import Flask
from .blueprints.auth import auth_bp
from .blueprints.search import search_bp
from .database import Database  # Your existing DB wrapper

def create_app(db_user: str, db_pass: str, config_object: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="change-me",
        SESSION_COOKIE_NAME="guess_uid",
    )
    if config_object:
        app.config.from_object(config_object)

    db = Database(db_user, db_pass)
    app.db = db

    # Cache player names once during startup
    player_names = db.get_all_player_names()
    app.config["PLAYER_NAME_LIST"] = player_names

    app.register_blueprint(auth_bp)
    app.register_blueprint(search_bp)

    @app.route("/ping")
    def _ping():
        return {"status": "ok"}

    return app


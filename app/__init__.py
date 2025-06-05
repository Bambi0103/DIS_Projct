from flask import Flask, session, redirect, url_for
from .blueprints.auth import auth_bp
from .blueprints.search import search_bp
from .database import Database  

def create_app(db_user: str, 
               db_pass: str, 
               config_object: str | None = None, 
               init_db: bool = False,
               debug_level: int = False) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="change-me",
        SESSION_COOKIE_NAME="guess_uid",
        DEBUG_LEVEL=debug_level
    )
    if config_object:
        app.config.from_object(config_object)

    db = Database(db_user, db_pass)
    app.db = db

    # Save debug flag so it is globally accessible
    @app.before_request
    def _set_debug():
        session.setdefault("DEBUG_LEVEL", app.config["DEBUG_LEVEL"])

    if init_db and not _in_reloader_child():
        app.db.init_db()

    # Cache player names once during startup
    player_names = db.get_all_player_names()
    app.config["PLAYER_NAME_LIST"] = player_names

    app.register_blueprint(auth_bp)
    app.register_blueprint(search_bp)

    @app.route("/ping")
    def _ping():
        return {"status": "ok"}
    
    @app.route("/")
    def index():
        if "username" in session:
            print(f"User {session['username']} is authenticated.")
            return redirect(url_for("search.guess"))
        return redirect(url_for("auth.login"))

    return app


    
def _in_reloader_child() -> bool:
    """
    # Flask shenanigans - keep Flask from running initialisation of db twice
    """
    import os
    return os.environ.get("WERKZEUG_RUN_MAIN") == "true"

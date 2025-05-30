from flask import (
    Blueprint, current_app, render_template,
    request, session, abort
)
from markupsafe import escape
from difflib import get_close_matches
import random


search_bp = Blueprint(
    "search", __name__,
    template_folder="../../templates"
)

# ---------------- helpers ---------------- #
def _login_required():
    if "username" not in session:
        abort(401)   # htmx will follow redirect; plain browsers get 401


# ---------------- routes ----------------- #
@search_bp.route("/")
def guess():
    _login_required()

    # Choose random player
    players = current_app.db.get_all_player_ids()
    target = random.choice(players)
    session["target_player_id"] = target["id"]

    return render_template("guess.html")


@search_bp.get("/api/search")
def player_search():
    # _login_required()

    term = request.args.get("full_name", "").strip().lower()
    if not term or len(term) < 2:
        return "<datalist id='playerList'></datalist>"

    # Use the preloaded player name list
    all_names = current_app.config.get("PLAYER_NAME_LIST", [])
    matches = [name for name in all_names if term in name.lower()]
    matches = matches[:15]  # throttle

    options = "\n".join(f"<option value='{escape(name)}'>" for name in matches)
    return f"<datalist id='playerList'>{options}</datalist>"



from flask import (
    Blueprint, current_app, render_template,
    request, session, jsonify, current_app, redirect, url_for
)
from markupsafe import escape
import random
from flask import redirect, url_for


search_bp = Blueprint(
    "search", __name__,
    template_folder="../../templates"
)

# Helper functions:
@search_bp.before_app_request
def init_session():
    """Load random target player into session."""
    if "target_player_id" not in session:
        target = current_app.db.get_random_player()  # type: ignore[attr-defined]
        session["target_player_id"] = target["id"]
        session["attempts"] = 0
    else:
        # If already set, we assume the game is ongoing
        session.setdefault("attempts", 0)
    

def _login_required():
    if "username" not in session:
        return redirect(url_for("auth.login"))


def _evaluate_guess(answer: dict, guess: dict) -> dict:
    """Compare guess against answer and return results and diffs"""
    result = {}
    for key in answer:
        if key.lower() == "id":
            continue
        if key not in guess:
            continue
        val_answer = answer[key]
        val_guess = guess[key]
        if isinstance(val_answer, (int, float)) and isinstance(val_guess, (int, float)):
            result[key] = {
                "match": val_answer == val_guess,
                "diff": val_guess - val_answer
            }
        else:
            result[key] = {
                "match": val_answer == val_guess
            }
    return {
        "guess": guess,
        "answer": answer,
        "results": result
    }

def is_guess_correct(guess: dict, target: dict) -> bool:
    return guess == target


# Route handlers: 
@search_bp.route("/game")
def guess():
    logincheck = _login_required()
    if logincheck:
        return logincheck

    # Choose random 
    print("Getting players")
    players = current_app.db.get_all_player_ids()
    target = random.choice(players)
    session["target_player_id"] = target["id"]

    return render_template("guess.html")


@search_bp.get("/api/search")
def player_search():
    logincheck = _login_required()
    if logincheck:
        return logincheck

    term = request.args.get("full_name", "").strip().lower()
    if not term or len(term) < 1:
        return "<datalist id='playerList'></datalist>"

    # Use the preloaded player name list
    all_names = current_app.config.get("PLAYER_NAME_LIST", [])
    matches = [name for name in all_names if term in name.lower()]
    matches = matches[:15]  # throttle

    options = "\n".join(f"<option value='{escape(name)}'>" for name in matches)
    return f"<datalist id='playerList'>{options}</datalist>"


@search_bp.post("/api/guess")
def make_guess():
    """
    Called when the user submits a guess (HTMX POST). See guess.html and look for "post" 

    Look up requested player from db
    Compare against target player
    Return JSON with results (true false) and numeric difference if applicable
    """
    logincheck = _login_required()
    if logincheck:
        return logincheck

    player_name = request.form.get("full_name", "").strip()
    if not player_name:
        return jsonify({"error": "Empty guess"}), 400

    guess_rows = current_app.db.get_players_by_name(player_name)
    if not guess_rows:
        return jsonify({"error": "Player not found"}), 404

    guess_row = guess_rows[0] 
    target_id = session.get("target_player_id")
    if not target_id:
        return jsonify({"error": "No target player set"}), 400

    target_row = current_app.db.get_player_by_id(target_id)  # type: ignore[attr-defined]
    if not target_row:
        return jsonify({"error": "Target player not found"}), 404

    session["attempts"] += 1

    result = _evaluate_guess(target_row, guess_row)
    result["correct"] = is_guess_correct(guess_row, target_row)
    if result["correct"]:
        new_target = current_app.db.get_random_player()
        session["target_player_id"] = new_target["id"]
        result["attempts"] = 0
        return render_template("won.html", target_player=new_target, attempts=session["attempts"])
    




    return jsonify(result)
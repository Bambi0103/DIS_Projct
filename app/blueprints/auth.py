from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, current_app
)

auth_bp = Blueprint("auth", __name__, template_folder="../../templates")


"""User has choice between login and register after typing username + pass"""

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        action = request.form.get("action", "login")
        if not username or not password:
            flash("Please enter a username and password", category="error")
            return render_template("login.html")
        
    
        db = current_app.db
        # Register
        if action == "register":
            if db.user_exists(username):
                flash("User already exists", category="error")
                return render_template("login.html")
            db.add_user(username, password)
            session["username"] = username
            return redirect(url_for("search.guess"))

        # Login
        user = db.get_user(username)
        if user is None or user["password"] != password:
            flash("Incorrect login credentials", category="error") # Don't tell the user what is missing, since brute forcing is easy in our app
            return render_template("login.html")
        
        session["username"] = username
        return redirect(url_for("search.guess"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out!", category="info")
    return redirect(url_for("auth.login"))

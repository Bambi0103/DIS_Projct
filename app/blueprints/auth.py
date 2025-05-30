from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)

auth_bp = Blueprint("auth", __name__, template_folder="../../templates")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Very bare-bones login: user types *only* a username.
    We consider any non-empty string a valid user and
    rely on your db layer if you later want to check existence.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username:
            flash("Please enter a username", category="error")
            return redirect(url_for("auth.login"))

        # If you have a DB check, do it here, e.g.:
        # if not current_app.db.user_exists(username): ...

        session["username"] = username
        return redirect(url_for("search.guess"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out!", category="info")
    return redirect(url_for("auth.login"))

from flask import Flask 
from flask import render_template
from flask import Blueprint, request, jsonify
from database import Database
import psycopg2
import psycopg2.pool


bp = Blueprint('api', __name__, url_prefix='/api')
db = Database(user="bruger", password="password")
app = Flask(__name__)

@bp.route('/search')
def people():
    term = request.args.get("q", "").strip()
    results = db.get_full_names(term)
    return "".join(f'<option value="{name}">' for name in results)

@app.route('/')
def index():
    return render_template('base.html')

app.register_blueprint(bp)





if __name__ == "__main__":
    app.run(debug=True, port=5231)



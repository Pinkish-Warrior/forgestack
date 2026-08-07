import os
import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def create_app():
    app = Flask(__name__)

    # FIX: secret key comes from the environment and the app refuses to
    # start without it, instead of falling back to a value baked into
    # source control.
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable must be set")
    app.config["SECRET_KEY"] = secret_key

    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(DB_PATH)
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with app.app_context():
        db = get_db()
        db.executescript((BASE_DIR / "schema.sql").read_text())
        db.commit()

    @app.post("/register")
    def register():
        data = request.get_json(silent=True) or {}
        username = data.get("username", "")
        password = data.get("password", "")
        if not username or not password:
            return jsonify({"error": "username and password required"}), 400

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return jsonify({"error": "username already exists"}), 409

        return jsonify({"message": "registered"}), 201

    @app.post("/login")
    def login():
        data = request.get_json(silent=True) or {}
        username = data.get("username", "")
        password = data.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            return jsonify({"error": "invalid credentials"}), 401

        session["user_id"] = user["id"]
        return jsonify({"message": "logged in"})

    @app.post("/logout")
    def logout():
        session.clear()
        return jsonify({"message": "logged out"})

    def current_user_id():
        return session.get("user_id")

    @app.post("/upload")
    def upload():
        if not current_user_id():
            return jsonify({"error": "authentication required"}), 401

        if "file" not in request.files:
            return jsonify({"error": "file required"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "empty filename"}), 400

        filename = secure_filename(file.filename)
        file.save(UPLOAD_DIR / filename)
        return jsonify({"message": "uploaded", "filename": filename}), 201

    @app.get("/notes")
    def list_notes():
        user_id = current_user_id()
        if not user_id:
            return jsonify({"error": "authentication required"}), 401

        db = get_db()
        rows = db.execute(
            "SELECT id, title, body FROM notes WHERE user_id = ?", (user_id,)
        ).fetchall()
        return jsonify([dict(row) for row in rows])

    # FIX: `q` is bound as a parameter instead of being spliced into the
    # SQL string, so it can't change the shape of the query.
    @app.get("/notes/search")
    def search_notes():
        user_id = current_user_id()
        if not user_id:
            return jsonify({"error": "authentication required"}), 401

        query_term = request.args.get("q", "")
        db = get_db()
        rows = db.execute(
            "SELECT id, title, body FROM notes WHERE user_id = ? AND title LIKE ?",
            (user_id, f"%{query_term}%"),
        ).fetchall()
        return jsonify([dict(row) for row in rows])

    @app.post("/notes")
    def create_note():
        user_id = current_user_id()
        if not user_id:
            return jsonify({"error": "authentication required"}), 401

        data = request.get_json(silent=True) or {}
        title = data.get("title", "")
        body = data.get("body", "")
        if not title or not body:
            return jsonify({"error": "title and body required"}), 400

        db = get_db()
        db.execute(
            "INSERT INTO notes (user_id, title, body) VALUES (?, ?, ?)",
            (user_id, title, body),
        )
        db.commit()
        return jsonify({"message": "note created"}), 201

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

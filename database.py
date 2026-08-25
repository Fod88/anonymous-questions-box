import sqlite3
from flask import g
from werkzeug.security import generate_password_hash
from config import Config


def get_db():
    """Return a SQLite connection stored on the Flask application context."""
    if "db" not in g:
        g.db = sqlite3.connect(Config.DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create tables (if they do not exist) and seed the default admin account."""
    with app.app_context():
        db = get_db()

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL DEFAULT 'Anonymous',
                message TEXT NOT NULL,
                is_read INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            """
        )

        db.commit()

        # Seed the default admin account only if no admin exists yet.
        existing_admin = db.execute(
            "SELECT id FROM admins WHERE username = ?", (Config.ADMIN_USERNAME,)
        ).fetchone()

        if existing_admin is None:
            db.execute(
                "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                (Config.ADMIN_USERNAME, generate_password_hash(Config.ADMIN_PASSWORD)),
            )
            db.commit()

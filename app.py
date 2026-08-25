from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash

from config import Config
from database import get_db, close_db, init_db

app = Flask(__name__)
app.config.from_object(Config)
app.teardown_appcontext(close_db)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def login_required(view_func):
    """Protect a route so only an authenticated admin can access it."""

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_id"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def message_to_dict(row):
    return {
        "id": row["id"],
        "username": row["username"],
        "message": row["message"],
        "is_read": bool(row["is_read"]),
        "created_at": row["created_at"],
    }


# ---------------------------------------------------------------------------
# Public routes (user side)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Landing page: choose a username or continue anonymously."""
    return render_template("index.html")


@app.route("/messages")
def messages_page():
    """Page where the user writes and sends messages."""
    username = session.get("display_username", "Anonymous")
    return render_template("messages.html", username=username)


@app.route("/set-username", methods=["POST"])
def set_username():
    """Store the chosen display name (or Anonymous) in the session, then continue."""
    username = request.form.get("username", "").strip()
    session["display_username"] = username if username else "Anonymous"
    return redirect(url_for("messages_page"))


# ---------------------------------------------------------------------------
# Public API (send a message)
# ---------------------------------------------------------------------------

@app.route("/api/messages", methods=["POST"])
def create_message():
    """Create a new anonymous/named message. No authentication required."""
    data = request.get_json(silent=True) or request.form

    message_text = (data.get("message") or "").strip()
    username = (data.get("username") or session.get("display_username") or "Anonymous").strip()

    if not username:
        username = "Anonymous"

    if not message_text:
        return jsonify({"error": "Message text is required"}), 400

    if len(message_text) > 2000:
        return jsonify({"error": "Message is too long (max 2000 characters)"}), 400

    if len(username) > 50:
        return jsonify({"error": "Username is too long (max 50 characters)"}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO messages (username, message) VALUES (?, ?)",
        (username, message_text),
    )
    db.commit()

    new_row = db.execute(
        "SELECT * FROM messages WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()

    return jsonify({"message": "Message sent successfully", "data": message_to_dict(new_row)}), 201


# ---------------------------------------------------------------------------
# Admin authentication
# ---------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        if session.get("admin_id"):
            return redirect(url_for("admin_dashboard"))
        return render_template("admin/login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    error = None
    if not username or not password:
        error = "Username and password are required."
    else:
        db = get_db()
        admin = db.execute(
            "SELECT * FROM admins WHERE username = ?", (username,)
        ).fetchone()

        if admin is None or not check_password_hash(admin["password_hash"], password):
            error = "Invalid username or password."

    if error:
        return render_template("admin/login.html", error=error), 401

    session.clear()
    session["admin_id"] = admin["id"]
    session["admin_username"] = admin["username"]
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    return render_template("admin/dashboard.html", admin_username=session.get("admin_username"))


# ---------------------------------------------------------------------------
# Admin API (protected)
# ---------------------------------------------------------------------------

@app.route("/api/messages", methods=["GET"])
@login_required
def get_messages():
    """Return all messages, newest first. Admin only."""
    db = get_db()
    rows = db.execute("SELECT * FROM messages ORDER BY created_at DESC").fetchall()

    messages = [message_to_dict(row) for row in rows]
    total_count = len(messages)
    unread_count = sum(1 for m in messages if not m["is_read"])

    return jsonify({
        "messages": messages,
        "total_count": total_count,
        "unread_count": unread_count,
    }), 200


@app.route("/api/messages/<int:message_id>/read", methods=["PATCH"])
@login_required
def mark_message_read(message_id):
    """Mark a single message as read. Admin only."""
    db = get_db()
    row = db.execute("SELECT id FROM messages WHERE id = ?", (message_id,)).fetchone()

    if row is None:
        return jsonify({"error": "Message not found"}), 404

    db.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (message_id,))
    db.commit()

    return jsonify({"message": "Message marked as read"}), 200


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
@login_required
def delete_message(message_id):
    """Delete a message. Admin only."""
    db = get_db()
    row = db.execute("SELECT id FROM messages WHERE id = ?", (message_id,)).fetchone()

    if row is None:
        return jsonify({"error": "Message not found"}), 404

    db.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    db.commit()

    return jsonify({"message": "Message deleted successfully"}), 200


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return "Internal server error", 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db(app)
    app.run(debug=True, host="0.0.0.0", port=5000)

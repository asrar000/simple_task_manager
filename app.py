from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_PATH = "data/tasks.db"


# ---------- DB ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'todo',
            created_at TEXT,
            due_date TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------- API ----------
@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    status = data.get("status", "todo")
    if status not in ["todo", "in_progress", "done"]:
        return jsonify({"error": "invalid status"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks (title, description, status, created_at, due_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["title"],
        data.get("description"),
        status,
        datetime.utcnow().isoformat(),
        data.get("due_date")
    ))
    conn.commit()

    task_id = cur.lastrowid
    conn.close()

    return jsonify({"id": task_id}), 201


@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    status = request.args.get("status")
    q = request.args.get("q")

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if status:
        query += " AND status=?"
        params.append(status)

    if q:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])

    conn = get_db()
    tasks = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(task) for task in tasks])


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    cur = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "task not found"}), 404

    return jsonify({"message": "deleted"})


# ---------- FRONTEND ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tasks")
def tasks_page():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return render_template("tasks.html", tasks=tasks)


@app.route("/tasks/done/<int:task_id>")
def mark_done(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("tasks_page"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

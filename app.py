from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_PATH = "data/tasks.db"
VALID_STATUS = ["todo", "in_progress", "done"]


# ---------- UTIL ----------
def log(msg):
    print(f"[LOG] {msg}")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    log("Initializing database")
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT,
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
    log("POST /api/tasks")

    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    status = data.get("status", "todo")
    if status not in VALID_STATUS:
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
    conn.close()

    return jsonify({"message": "task created"}), 201


@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    log("GET /api/tasks")
    status = request.args.get("status")
    q = request.args.get("q")
    sort = request.args.get("sort")

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if status:
        query += " AND status=?"
        params.append(status)

    if q:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])

    if sort in ["due_date", "created_at"]:
        query += f" ORDER BY {sort}"

    conn = get_db()
    tasks = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(t) for t in tasks]), 200


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    log(f"GET /api/tasks/{task_id}")
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()

    if not task:
        return jsonify({"error": "task not found"}), 404

    return jsonify(dict(task)), 200


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    log(f"PUT /api/tasks/{task_id}")
    data = request.get_json()

    if not data:
        return jsonify({"error": "no data provided"}), 400

    if "status" in data and data["status"] not in VALID_STATUS:
        return jsonify({"error": "invalid status"}), 400

    fields, values = [], []
    for k in ["title", "description", "status", "due_date"]:
        if k in data:
            fields.append(f"{k}=?")
            values.append(data[k])

    if not fields:
        return jsonify({"error": "nothing to update"}), 400

    values.append(task_id)

    conn = get_db()
    cur = conn.execute(
        f"UPDATE tasks SET {', '.join(fields)} WHERE id=?",
        values
    )
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "task not found"}), 404

    return jsonify({"message": "task updated"}), 200




@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    log(f"DELETE /api/tasks/{task_id}")
    conn = get_db()
    cur = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "task not found"}), 404

    return jsonify({"message": "task deleted"}), 200


# ---------- FRONTEND ----------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/tasks")
def tasks_page():
    status = request.args.get("status")
    query = "SELECT * FROM tasks"
    params = []

    if status:
        query += " WHERE status=?"
        params.append(status)

    conn = get_db()
    tasks = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("tasks.html", tasks=tasks)


@app.route("/tasks/done/<int:task_id>")
def mark_done(task_id):
    log(f"Marking task {task_id} done")
    conn = get_db()
    conn.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("tasks_page"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

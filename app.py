from flask import Flask, jsonify, request, send_from_directory
import sqlite3, uuid
from datetime import datetime

app = Flask(__name__, static_folder="static")
DB = "todo_notes.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS todos (
        id TEXT PRIMARY KEY, text TEXT NOT NULL, done INTEGER DEFAULT 0,
        due_at TEXT, alarm_fired INTEGER DEFAULT 0, created_at TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY, content TEXT NOT NULL, pinned INTEGER DEFAULT 0,
        created_at TEXT NOT NULL)""")
    conn.commit(); conn.close()

@app.route("/todos", methods=["GET"])
def get_todos():
    conn = get_db()
    rows = conn.execute("SELECT * FROM todos ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json()
    todo = {"id": str(uuid.uuid4()), "text": data["text"], "done": 0,
            "due_at": data.get("due_at"), "alarm_fired": 0,
            "created_at": datetime.utcnow().isoformat()}
    conn = get_db()
    conn.execute("INSERT INTO todos VALUES (?,?,?,?,?,?)",
        (todo["id"], todo["text"], todo["done"], todo["due_at"], todo["alarm_fired"], todo["created_at"]))
    conn.commit(); conn.close()
    return jsonify(todo), 201

@app.route("/todos/<todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json()
    conn = get_db()
    todo = conn.execute("SELECT * FROM todos WHERE id=?", (todo_id,)).fetchone()
    if not todo:
        conn.close(); return jsonify({"error": "not found"}), 404
    text = data.get("text", todo["text"]); due_at = data.get("due_at", todo["due_at"])
    conn.execute("UPDATE todos SET text=?, due_at=? WHERE id=?", (text, due_at, todo_id))
    conn.commit(); conn.close()
    return jsonify({"id": todo_id, "text": text, "due_at": due_at})

@app.route("/todos/<todo_id>/done", methods=["PUT"])
def toggle_done(todo_id):
    conn = get_db()
    todo = conn.execute("SELECT * FROM todos WHERE id=?", (todo_id,)).fetchone()
    if not todo:
        conn.close(); return jsonify({"error": "not found"}), 404
    new_val = 0 if todo["done"] else 1
    conn.execute("UPDATE todos SET done=? WHERE id=?", (new_val, todo_id))
    conn.commit(); conn.close()
    return jsonify({"id": todo_id, "done": bool(new_val)})

@app.route("/todos/<todo_id>/alarm-fired", methods=["PUT"])
def mark_alarm_fired(todo_id):
    conn = get_db()
    conn.execute("UPDATE todos SET alarm_fired=1 WHERE id=?", (todo_id,))
    conn.commit(); conn.close()
    return jsonify({"id": todo_id, "alarm_fired": True})

@app.route("/todos/<todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    conn = get_db()
    conn.execute("DELETE FROM todos WHERE id=?", (todo_id,))
    conn.commit(); conn.close()
    return "", 204

@app.route("/notes", methods=["GET"])
def get_notes():
    conn = get_db()
    rows = conn.execute("SELECT * FROM notes ORDER BY pinned DESC, created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    note = {"id": str(uuid.uuid4()), "content": data["content"], "pinned": 0,
            "created_at": datetime.utcnow().isoformat()}
    conn = get_db()
    conn.execute("INSERT INTO notes VALUES (?,?,?,?)",
        (note["id"], note["content"], note["pinned"], note["created_at"]))
    conn.commit(); conn.close()
    return jsonify(note), 201

@app.route("/notes/<note_id>/pin", methods=["PUT"])
def toggle_pin(note_id):
    conn = get_db()
    note = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
    if not note:
        conn.close(); return jsonify({"error": "not found"}), 404
    new_val = 0 if note["pinned"] else 1
    conn.execute("UPDATE notes SET pinned=? WHERE id=?", (new_val, note_id))
    conn.commit(); conn.close()
    return jsonify({"id": note_id, "pinned": bool(new_val)})

@app.route("/notes/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    conn = get_db()
    conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit(); conn.close()
    return "", 204

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", debug=True)
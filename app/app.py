from flask import Flask, request, jsonify, render_template_string
import psycopg2
import os
import time

app = Flask(__name__)

def get_db():
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "db"),
                port=os.environ.get("DB_PORT", 5432),
                database=os.environ.get("DB_NAME", "tododb"),
                user=os.environ.get("DB_USER", "todouser"),
                password=os.environ.get("DB_PASS", "todopass")
            )
            return conn
        except Exception:
            retries -= 1
            time.sleep(2)
    raise Exception("No se pudo conectar a la base de datos")

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lista de Tareas</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', sans-serif; background: #f0f4f8; min-height: 100vh; padding: 40px 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; color: #2d3748; margin-bottom: 30px; font-size: 2rem; }
        .add-form { display: flex; gap: 10px; margin-bottom: 24px; }
        .add-form input { flex: 1; padding: 12px 16px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem; outline: none; transition: border-color 0.2s; }
        .add-form input:focus { border-color: #667eea; }
        .add-form button { padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; transition: background 0.2s; }
        .add-form button:hover { background: #5a67d8; }
        .task-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
        .task { display: flex; align-items: center; gap: 12px; background: white; padding: 14px 16px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .task.done span { text-decoration: line-through; color: #a0aec0; }
        .task span { flex: 1; font-size: 1rem; color: #2d3748; }
        .task input[type=checkbox] { width: 18px; height: 18px; cursor: pointer; accent-color: #667eea; }
        .task button { padding: 6px 12px; background: #fc8181; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem; transition: background 0.2s; }
        .task button:hover { background: #e53e3e; }
        .empty { text-align: center; color: #a0aec0; padding: 40px; font-size: 1.1rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 Lista de Tareas</h1>
        <div class="add-form">
            <input type="text" id="taskInput" placeholder="Nueva tarea..." onkeydown="if(event.key==='Enter') addTask()">
            <button onclick="addTask()">Añadir</button>
        </div>
        <ul class="task-list" id="taskList">
            <li class="empty">Cargando tareas...</li>
        </ul>
    </div>
    <script>
        async function loadTasks() {
            const res = await fetch('/api/tasks');
            const tasks = await res.json();
            const list = document.getElementById('taskList');
            if (tasks.length === 0) {
                list.innerHTML = '<li class="empty">No hay tareas. ¡Añade una!</li>';
                return;
            }
            list.innerHTML = tasks.map(t => `
                <li class="task ${t.done ? 'done' : ''}">
                    <input type="checkbox" ${t.done ? 'checked' : ''} onchange="toggleTask(${t.id})">
                    <span>${t.title}</span>
                    <button onclick="deleteTask(${t.id})">Eliminar</button>
                </li>
            `).join('');
        }
        async function addTask() {
            const input = document.getElementById('taskInput');
            const title = input.value.trim();
            if (!title) return;
            await fetch('/api/tasks', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({title}) });
            input.value = '';
            loadTasks();
        }
        async function toggleTask(id) {
            await fetch(`/api/tasks/${id}/toggle`, { method: 'PUT' });
            loadTasks();
        }
        async function deleteTask(id) {
            await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
            loadTasks();
        }
        loadTasks();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, done FROM tasks ORDER BY created_at DESC")
    tasks = [{"id": r[0], "title": r[1], "done": r[2]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({"error": "El título es obligatorio"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id", (title,))
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": task_id, "title": title, "done": False}), 201

@app.route('/api/tasks/<int:task_id>/toggle', methods=['PUT'])
def toggle_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done = NOT done WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)

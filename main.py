import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
app.json.ensure_ascii = False;
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE,
                       password
                       TEXT,
                       role
                       TEXT
                   )
                   """)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES ('admin', 'SuperSecretAdminP@ss123!', 'admin')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('alice', 'alice123', 'user')")
        conn.commit()
    conn.close()


os.makedirs("reports", exist_ok=True)
with open("reports/financial_2024.txt", "w", encoding="utf-8") as f:
    f.write("Отчет за 2024 год: Все показатели в норме. Конфиденциально.")

@app.route('/')
def index():
    html = """
    <h2>Уязвимый веб-сервис</h2>
    <ul>
        <li><b>SQL Injection:</b> POST-запрос на <code>/login</code> (параметры <code>username</code>, <code>password</code>)</li>
        <li><b>Path Traversal:</b> GET-запрос на <code>/view?file=financial_2024.txt</code></li>
    </ul>
    """
    return html

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = f"SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password}'"

    try:
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({
                "status": "success",
                "message": f"Добро пожаловать, {user[1]}!",
                "user_id": user[0],
                "role": user[2]
            }), 200
        else:
            return jsonify({"status": "error", "message": "Incorrect login or password"}), 401
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"status": "error", "sql_error": str(e)}), 500

@app.route('/view', methods=['GET'])
def view_file():
    filename = request.args.get('file', '')
    if not filename:
        return jsonify({"status": "error", "message": "The file parameter is required."}), 400

    file_path = os.path.join("reports", filename)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"status": "success", "filename": filename, "content": content}), 200
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Файл не найден"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
import os

application = Flask(__name__)

ENV = os.environ.get('FLASK_ENV', 'developerskie')


# Inicjalizacja bazy danych
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        completed INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()


# Wywołanie inicjalizacji bazy danych
init_db()


# Główny widok HTML (dla wszystkich stron)
BASE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>CRUD App</title>
</head>
<body>
    <h1>Hello, Big Data z Pythonem!</h1>
    <p>Środowisko: <strong>{{ env }}</strong></p>
    <h2>Dodaj zadanie</h2>
    <form action="/add" method="post">
        <input type="text" name="title" placeholder="Tytuł zadania" required>
        <button type="submit">Dodaj</button>
    </form>
    <h2>Zadania</h2>
    <ul>
        {% for task in tasks %}
        <li>
            {% if task[2] == 1 %}
            <s>{{ task[1] }}</s>
            {% else %}
            {{ task[1] }}
            {% endif %}
            <a href="/complete/{{ task[0] }}">[Zakończ]</a>
            <a href="/delete/{{ task[0] }}">[Usuń]</a>
        </li>
        {% endfor %}
    </ul>
</body>
</html>
'''


@application.route('/')
def index():
    # Pobranie wszystkich zadań
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT id, title, completed FROM tasks")
    tasks = c.fetchall()
    conn.close()
    return render_template_string(BASE_HTML, tasks=tasks, env=ENV)


@application.route('/add', methods=['POST'])
def add():
    # Dodanie nowego zadania
    title = request.form.get('title')
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@application.route('/complete/<int:task_id>')
def complete(task_id):
    # Oznaczenie zadania jako zakończone
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@application.route('/delete/<int:task_id>')
def delete(task_id):
    # Usunięcie zadania
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


app = application


if __name__ == '__main__':
    application.run(debug=True)

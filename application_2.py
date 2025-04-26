from flask import Flask, request, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os

application = Flask(__name__)

# Konfiguracja środowiska
ENV = os.environ.get('FLASK_ENV', 'dev')

# Konfiguracja bazy danych w zależności od środowiska
if ENV == 'prod':
    # MySQL dla produkcji
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
    DB_NAME = os.environ.get('DB_NAME', 'tasks_db')
    application.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    DB_TYPE = "MySQL"
else:
    # SQLite dla rozwoju
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    DB_TYPE = "SQLite"

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicjalizacja SQLAlchemy
db = SQLAlchemy(application)

# Model zadania
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)

# Utworzenie tabel
with application.app_context():
    db.create_all()

# Główny widok HTML
BASE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>CRUD App</title>
</head>
<body>
    <h1>Witaj, BigData z Pythonem!</h1>
    <p>Środowisko: <strong>{{ ENV }}</strong></p>
    <p>Baza danych: <strong>{{ db_type }}</strong></p>
    <h2>Dodaj zadanie</h2>
    <form action="/add" method="post">
        <input type="text" name="title" placeholder="Tytuł zadania" required>
        <button type="submit">Dodaj</button>
    </form>
    <h2>Zadania</h2>
    <ul>
        {% for task in tasks %}
        <li>
            {% if task.completed %}
            <s>{{ task.title }}</s>
            {% else %}
            {{ task.title }}
            {% endif %}
            <a href="/complete/{{ task.id }}">[Zakończ]</a>
            <a href="/delete/{{ task.id }}">[Usuń]</a>
        </li>
        {% endfor %}
    </ul>
</body>
</html>
'''

@application.route('/')
def index():
    tasks = Task.query.all()
    return render_template_string(BASE_HTML, tasks=tasks, ENV=ENV, db_type=DB_TYPE)

@application.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    task = Task(title=title)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))

@application.route('/complete/<int:task_id>')
def complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('index'))

@application.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    application.run(debug=True)
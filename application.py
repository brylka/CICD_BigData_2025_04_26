import os

from flask import Flask

application = Flask(__name__)


ENV = os.environ.get('FLASK_ENV', 'developerskie')

# Konfiguracja zależna od środowiska
if ENV == 'produkcja':
    # Ustawienia dla wersji produkcyjnej
    # np. połączenie z bazą danych
    pass
else:
    # Ustawienia dla wersji developerskiej
    # np. użycie bazy sqlite
    pass

@application.route('/')
def hello_world():
    return(f'<h1>Hello, BigData z Pythonem!</h1><p>Przykład CI/CD - automatyczne wdrażanie!</p>'
           f'<p>Środowisko: <b>{ENV}</b></p>'
           f'<p>Wykonał: Bartosz Bryniarski')


if __name__ == '__main__':
    application.run(debug=True)
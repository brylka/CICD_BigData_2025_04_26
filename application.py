from flask import Flask

application = Flask(__name__)


@application.route('/')
def hello_world():
    return('<h1>Hello, BigData z Pythonem!</h1><p>Przykład CI/CD - automatyczne wdrażanie!</p>'
           '<p>Wykonał: Bartosz Bryniarski')


if __name__ == '__main__':
    application.run(debug=True)
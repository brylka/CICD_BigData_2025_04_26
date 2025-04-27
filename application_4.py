from flask import Flask, render_template_string
import requests
import anthropic
import os
from datetime import datetime

app = Flask(__name__)


def get_weather_data():
    """Pobiera dane pogodowe dla Wrocławia z OpenWeatherMap API"""
    # Pobranie klucza API z zmiennych środowiskowych
    api_key = os.environ.get('OPENWEATHER_API_KEY')

    if not api_key:
        return None, "Brak klucza API OpenWeatherMap w zmiennych środowiskowych"

    # Współrzędne geograficzne Wrocławia
    lat = 51.1079
    lon = 17.0385

    # Adres URL API z parametrami
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=pl"

    try:
        # Wykonanie zapytania HTTP
        response = requests.get(url)

        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Błąd OpenWeatherMap API: {response.status_code}"
    except Exception as e:
        return None, f"Błąd podczas pobierania danych pogodowych: {str(e)}"


def analyze_weather_with_claude(weather_data):
    """Wysyła dane pogodowe do Claude API i otrzymuje analizę"""
    # Pobranie klucza API z zmiennych środowiskowych
    claude_api_key = os.environ.get('CLAUDE_API_KEY')

    if not claude_api_key:
        return "Brak klucza API Claude w zmiennych środowiskowych"

    try:
        client = anthropic.Anthropic(api_key=claude_api_key)

        # Formatowanie danych pogodowych
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        wind_speed = weather_data['wind']['speed']
        description = weather_data['weather'][0]['description']
        city_name = weather_data['name']

        # Konwersja timestamp na czytelną datę
        timestamp = weather_data['dt']
        date_time = datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y, godz. %H:%M')

        # Przygotowanie zapytania do Claude
        prompt = f"""
        Przeanalizuj te dane pogodowe dla {city_name} z {date_time}:
        - Temperatura: {temp}°C (odczuwalna: {feels_like}°C)
        - Wilgotność: {humidity}%
        - Ciśnienie: {pressure} hPa
        - Prędkość wiatru: {wind_speed} m/s
        - Opis: {description}

        Przygotuj krótką, praktyczną analizę pogody w formacie markdown, która będzie użyteczna dla przeciętnego użytkownika.
        Zacznij od tytułu "# Analiza pogody dla {city_name} - {date_time}".
        Uwzględnij, jak obecna pogoda może wpływać na codzienne aktywności, co warto ze sobą zabrać wychodząc z domu,
        i czy są jakieś szczególne zagrożenia lub korzystne warunki. 
        Użyj przyjaznego tonu i podaj maksymalnie 3-4 praktyczne wskazówki z odpowiednimi emoji na początku każdej wskazówki.
        """

        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        # Ekstrahuj tylko tekstową zawartość
        try:
            # Próba uzyskania samego tekstu z odpowiedzi
            if hasattr(message.content[0], 'text'):
                return message.content[0].text
            elif isinstance(message.content, list) and len(message.content) > 0:
                # Dla starszych wersji API
                if hasattr(message.content[0], 'value'):
                    return message.content[0].value
                else:
                    # Próba uzyskania wartości jako słownika
                    return message.content[0].get('text', str(message.content))
            else:
                return str(message.content)
        except Exception as e:
            return f"Błąd podczas przetwarzania odpowiedzi Claude: {str(e)}"

    except Exception as e:
        return f"Błąd podczas komunikacji z Claude API: {str(e)}"


# HTML template z obsługą Markdown
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pogoda dla Wrocławia</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/showdown/2.1.0/showdown.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #2c3e50;
            margin-top: 0;
        }
        h2 {
            color: #3498db;
            margin-top: 25px;
        }
        strong {
            color: #2c3e50;
        }
        .weather-icon {
            font-size: 24px;
            margin-right: 10px;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #7f8c8d;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
            padding: 20px;
            background-color: #fadbd8;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div id="weather-content">{{ error_message|safe }}</div>
    </div>
    <div class="footer">
        Dane pogodowe: OpenWeatherMap | Analiza: Claude AI
    </div>

    <script>
        // Konwersja Markdown na HTML tylko gdy nie ma komunikatu o błędzie
        const errorMessage = "{{ error_message|safe }}";
        if (!errorMessage) {
            const converter = new showdown.Converter();
            converter.setOption('tables', true);
            converter.setOption('emoji', true);

            const markdownContent = `{{ weather_analysis|safe }}`;
            document.getElementById('weather-content').innerHTML = converter.makeHtml(markdownContent);
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    # Pobierz dane pogodowe
    weather_data, error = get_weather_data()

    if error:
        return render_template_string(HTML_TEMPLATE,
                                      error_message=f'<div class="error">{error}</div>',
                                      weather_analysis="")

    if weather_data:
        # Analiza pogody przez Claude
        weather_analysis = analyze_weather_with_claude(weather_data)

        # Sprawdź, czy analiza nie zawiera komunikatu o błędzie
        if weather_analysis.startswith('Błąd'):
            return render_template_string(HTML_TEMPLATE,
                                          error_message=f'<div class="error">{weather_analysis}</div>',
                                          weather_analysis="")

        # Renderowanie szablonu z analizą pogody
        return render_template_string(HTML_TEMPLATE, weather_analysis=weather_analysis, error_message="")
    else:
        return render_template_string(HTML_TEMPLATE,
                                      error_message='<div class="error">Nie udało się pobrać danych pogodowych. Spróbuj ponownie później.</div>',
                                      weather_analysis="")


application = app

if __name__ == '__main__':
    app.run(debug=True)
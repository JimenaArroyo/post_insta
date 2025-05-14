from flask import Flask

from instagrapi import Client
import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests
import jsonify
app = Flask(__name__)

# Configuración para la cuenta de Instagram
INSTAGRAM_USER = "la_prieta_linda_pyn"
INSTAGRAM_PASS = "BrunoBowser2"


def obtener_temperatura():
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
	"latitude": 19.702778,
	"longitude": -101.183333,
	"hourly": "temperature_2m"
}
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
	    start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	    end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	    freq = pd.Timedelta(seconds = hourly.Interval()),
	    inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    temperatura_actual = hourly_dataframe.iloc[0]  
    print(f"Temperatura actual (aproximada): {temperatura_actual['temperature_2m']} °C")
    data = str(temperatura_actual.temperature_2m)
    return data

def subir_historia():
    cl = Client()
    cl.login(INSTAGRAM_USER, INSTAGRAM_PASS)


    imagen = "historia.png"
    texto = "¡Hace calor en Morelia! Ven por tu nieve ❄"

    cl.photo_upload_to_story(imagen, texto)

@app.route("/verificar_y_publicar", methods=["GET"])
def verificar_y_publicar():
    temp = float(obtener_temperatura())
    if temp > 26:
        subir_historia()
        return f"Temperatura: {temp}°C. Historia publicada en Instagram."
    else:
        return f"Temperatura: {temp}°C. No se publica nada."


@app.route('/')
def index():
    return verificar_y_publicar()

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template
from instagrapi import Client
import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests
import firebase_admin
from firebase_admin import credentials, firestore
import os
import requests
import tempfile
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-auth.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

INSTAGRAM_USER = os.getenv("INSTAGRAM_USER")
INSTAGRAM_PASS = os.getenv("INSTAGRAM_PASS")

def obtener_temperatura():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 19.702778,
        "longitude": -101.183333,
        "hourly": "temperature_2m"
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    temperature = hourly.Variables(0).ValuesAsNumpy()
    return float(temperature[0])

def subir_historia_desde_firestore():
    historias_ref = db.collection("historias").where("estatus", "==", False).limit(1)
    docs = list(historias_ref.stream())

    if not docs:
        return "No hay historias nuevas."

    historia = docs[0]
    data = historia.to_dict()
    imagen_url = data.get("img_url")
    texto = data.get("titulo")

    if not imagen_url:
        return "Historia sin imagen."

    response = requests.get(imagen_url)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp_file.write(response.content)
    tmp_file.close()

    cl = Client()
    cl.login(INSTAGRAM_USER, INSTAGRAM_PASS)
    cl.photo_upload_to_story(tmp_file.name, texto)

    historia.reference.update({"estatus": True})
    return f"Historia subida: {texto}"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    subidas_ref = db.collection("historias").where("estatus", "==", True)
    no_subidas_ref = db.collection("historias").where("estatus", "==", False)
    subidas = [doc.to_dict() for doc in subidas_ref.stream()]
    no_subidas = [doc.to_dict() for doc in no_subidas_ref.stream()]
    return render_template("dashboard.html", historias_subidas=subidas, historias_no_subidas=no_subidas)

@app.route('/verificar_y_publicar')
def verificar_y_publicar():
    temp = obtener_temperatura()
    if temp > 30:
        resultado = subir_historia_desde_firestore()
        return f"Temperatura: {temp}°C. {resultado}"
    return f"Temperatura: {temp}°C. No se publica nada."

if __name__ == "__main__":
    app.run(debug=True)

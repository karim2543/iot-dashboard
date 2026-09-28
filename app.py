from flask import Flask, render_template, jsonify, request, redirect
import firebase_admin # type: ignore
from firebase_admin import credentials, db # type: ignore
import random
import threading
import time
from datetime import datetime
from pathlib import Path
import mysql.connector as mysql # type: ignore

# =========================================================
# INITIALISATION FLASK
# =========================================================
app = Flask(__name__)

# =========================================================
# CONFIGURATION MYSQL (XAMPP)
# =========================================================
db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "enetcom_db"
}

# =========================================================
# CONFIGURATION FIREBASE
# =========================================================
BASE_DIR = Path(__file__).resolve().parent

JSON_KEY = "firebase-key.json"

CRED_PATH = BASE_DIR / JSON_KEY

firebase_available = False

try:

    if CRED_PATH.exists():

        cred = credentials.Certificate(str(CRED_PATH))

        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL":
                "https://iot5-80edb-default-rtdb.firebaseio.com"
            }
        )

        firebase_available = True

        print("Firebase connecté avec succès")

    else:

        print("firebase-key.json introuvable")

except Exception as e:

    print(f"Erreur Firebase : {e}")

# =========================================================
# DONNÉES ACTUELLES
# =========================================================
current_state = {

    "temp_ext": 24,

    "temp_int": 30,

    "aqi": 45,

    "wind": 2.4,

    "pressure": 1011,

    "humidity": 33,

    "time_full": "",

    "sun_time": "07:21:39"
}

# =========================================================
# HISTORIQUE ANALYTICS
# =========================================================
analytics_history = {

    "labels": [
        "08h",
        "10h",
        "12h",
        "14h",
        "16h",
        "18h",
        "20h"
    ],

    "temp_ext_log": [
        22,
        23,
        25,
        24,
        26,
        25,
        24
    ],

    "temp_int_log": [
        28,
        29,
        31,
        30,
        31,
        30,
        29
    ],

    "humidity_log": [
        40,
        38,
        35,
        33,
        34,
        36,
        37
    ],

    "pressure_log": [
        1010,
        1011,
        1012,
        1011,
        1009,
        1010,
        1011
    ],

    "wind_log": [
        3.1,
        4.2,
        5.0,
        3.8,
        2.4,
        3.1,
        3.6
    ],

    "radar_aqi": [
        45,
        32,
        55,
        20,
        15
    ]
}

# =========================================================
# HARDWARE NODES
# =========================================================
hardware_nodes = [

    {
        "id": "NODE-01",
        "room": "Labo Principal",
        "battery": "100%",
        "status": "En ligne",
        "color": "#34d399"
    },

    {
        "id": "NODE-02",
        "room": "Zone Extérieure",
        "battery": "74%",
        "status": "En ligne",
        "color": "#34d399"
    },

    {
        "id": "NODE-03",
        "room": "Serveur IoT",
        "battery": "Alimenté",
        "status": "En ligne",
        "color": "#34d399"
    },

    {
        "id": "NODE-04",
        "room": "Chambre Stérile",
        "battery": "12%",
        "status": "Batterie Faible",
        "color": "#fbbf24"
    }
]

# =========================================================
# LOGS SYSTEME
# =========================================================
system_logs = [

    {
        "time": "10:14:22",
        "type": "Alerte",
        "msg": "Seuil critique humidité (>35%)",
        "badge": "#ef4444"
    },

    {
        "time": "09:45:10",
        "type": "Info",
        "msg": "Synchronisation Firebase réussie",
        "badge": "#3b82f6"
    },

    {
        "time": "06:00",
        "type": "Cycle",
        "msg": "Réinitialisation des buffers horaires",
        "badge": "#10b981"
    }
]

# =========================================================
# MYSQL AUTO INSERT
# =========================================================
def insert_mysql_data():

    connection = None
    cursor = None

    try:

        connection = mysql.connect(**db_config)

        cursor = connection.cursor()

        query = """
        INSERT INTO sensor_data
        (
            temperature,
            humidity,
            timestamp
        )
        VALUES (%s,%s,%s)
        """

        values = (

            current_state["temp_ext"],

            current_state["humidity"],

            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        cursor.execute(query, values)

        connection.commit()

        print("Données insérées dans MySQL")

    except mysql.Error as e:

        print(f"Erreur MySQL : {e}")

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

# =========================================================
# SIMULATEUR IOT
# =========================================================
def data_simulator():

    while True:

        now = datetime.now()

        current_state["time_full"] = now.strftime(
            "%d %B %Y - %H:%M:%S"
        )

        # ======================================
        # RANDOM VALUES
        # ======================================
        current_state["temp_ext"] = random.randint(22, 26)

        current_state["temp_int"] = random.randint(28, 32)

        current_state["humidity"] = random.randint(30, 45)

        current_state["pressure"] = random.randint(1008, 1015)

        current_state["wind"] = round(
            random.uniform(1.5, 5.5),
            1
        )

        current_state["aqi"] = random.randint(20, 80)

        # ======================================
        # FIREBASE UPDATE
        # ======================================
        if firebase_available:

            try:

                db.reference(
                    "capteurs/exterieur"
                ).set(current_state["temp_ext"])

                db.reference(
                    "capteurs/interieur"
                ).set(current_state["temp_int"])

                db.reference(
                    "capteurs/humidite"
                ).set(current_state["humidity"])

                db.reference(
                    "capteurs/pression"
                ).set(current_state["pressure"])

                db.reference(
                    "capteurs/vent"
                ).set(current_state["wind"])

                db.reference(
                    "capteurs/aqi"
                ).set(current_state["aqi"])

            except Exception as e:

                print(f"Erreur Firebase : {e}")

        # ======================================
        # MYSQL SAVE
        # ======================================
        insert_mysql_data()

        # ======================================
        # ANALYTICS HISTORY
        # ======================================
        analytics_history["temp_ext_log"].append(
            current_state["temp_ext"]
        )

        analytics_history["temp_ext_log"].pop(0)

        analytics_history["temp_int_log"].append(
            current_state["temp_int"]
        )

        analytics_history["temp_int_log"].pop(0)

        analytics_history["humidity_log"].append(
            current_state["humidity"]
        )

        analytics_history["humidity_log"].pop(0)

        analytics_history["pressure_log"].append(
            current_state["pressure"]
        )

        analytics_history["pressure_log"].pop(0)

        analytics_history["wind_log"].append(
            current_state["wind"]
        )

        analytics_history["wind_log"].pop(0)

        analytics_history["radar_aqi"] = [

            random.randint(30, 60),

            random.randint(20, 50),

            random.randint(40, 70),

            random.randint(10, 30),

            random.randint(5, 25)
        ]

        analytics_history["labels"].append(
            now.strftime("%H:%M")
        )

        analytics_history["labels"].pop(0)

        time.sleep(10)

# =========================================================
# THREAD BACKGROUND
# =========================================================
threading.Thread(
    target=data_simulator,
    daemon=True
).start()

# =========================================================
# HOME PAGE
# =========================================================
@app.route('/')
def index():

    return render_template(

        'index.html',

        nodes=hardware_nodes,

        logs=system_logs,

        **current_state
    )

# =========================================================
# ANALYTICS API
# =========================================================
@app.route('/api/analytics')
def get_analytics():

    return jsonify(analytics_history)

# =========================================================
# CONTROL PAGE
# =========================================================
@app.route('/control')
def control():

    connection = None
    cursor = None

    try:

        connection = mysql.connect(**db_config)

        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT *
        FROM sensor_data
        ORDER BY id DESC
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        return render_template(
            'control.html',
            rows=rows
        )

    except mysql.Error as e:

        return render_template(
            'control.html',
            rows=[],
            error=str(e)
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

# =========================================================
# INSERT DATA MANUALLY
# =========================================================
@app.route('/insert', methods=['POST'])
def insert():

    connection = None
    cursor = None

    try:

        temperature = request.form['temperature']

        humidity = request.form['humidity']

        timestamp = request.form['timestamp']

        connection = mysql.connect(**db_config)

        cursor = connection.cursor()

        query = """
        INSERT INTO sensor_data
        (
            temperature,
            humidity,
            timestamp
        )
        VALUES (%s,%s,%s)
        """

        values = (
            temperature,
            humidity,
            timestamp
        )

        cursor.execute(query, values)

        connection.commit()

    except mysql.Error as e:

        print(e)

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

    return redirect('/control')

# =========================================================
# LIVE API
# =========================================================
@app.route('/api/live')
def live_data():

    return jsonify(current_state)

# =========================================================
# MAIN
# =========================================================
if __name__ == '__main__':

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash
import logging
import os
from MySQLdb.cursors import DictCursor

import paho.mqtt.client as mqtt
import ssl

# MQTT configuration
MQTT_BROKER = os.environ["DOMINIO"]
MQTT_PORT = int(os.environ["PUERTO_MQTTS"])
MQTT_USER = os.environ["MQTT_USER"]
MQTT_PASS = os.environ["MQTT_PASS"]

app = Flask(__name__)
# app.config['APPLICATION_ROOT'] = '/mqttfront'
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


# MySQL connection
app.config["MYSQL_USER"] = os.environ["MYSQL_USER"]
app.config["MYSQL_PASSWORD"] = os.environ["MYSQL_PASSWORD"]
app.config["MYSQL_DB"] = os.environ["MYSQL_DB"]
app.config["MYSQL_HOST"] = os.environ["MYSQL_HOST"]

app.config["SENSORES_DB"] = os.environ["SENSORES_DB"]

app.config["PERMANENT_SESSION_LIFETIME"] = 180

app.secret_key = os.environ["FLASK_SECRET_KEY"]

mysql = MySQL(app)

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def send_mqtt(topic, payload):
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.publish(topic, payload)
    client.disconnect()

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        if not request.form.get("usuario"):
            return "el campo usuario es oblicatorio"
        elif not request.form.get("password"):
            return "el campo contraseña es oblicatorio"

        passhash = generate_password_hash(
            request.form.get("password"), method="scrypt", salt_length=16
        )
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO usuarios (usuario, hash) VALUES (%s,%s)",
            (request.form.get("usuario"), passhash[17:]),
        )
        if mysql.connection.affected_rows():
            flash("Se agregó un usuario")
            logging.info("se agregó un usuario")
        mysql.connection.commit()
        return redirect(url_for("index"))

    return render_template("registrar.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form.get("usuario"):
            return "el campo usuario es oblicatorio"
        elif not request.form.get("password"):
            return "el campo contraseña es oblicatorio"

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM usuarios WHERE usuario LIKE %s",
            (request.form.get("usuario"),),
        )
        rows = cur.fetchone()
        if rows:
            if check_password_hash(
                "scrypt:32768:8:1$" + rows[2], request.form.get("password")
            ):
                session.permanent = True
                session["user_id"] = request.form.get("usuario")
                logging.info("se autenticó correctamente")
                return redirect(url_for("index"))
            else:
                flash("usuario o contraseña incorrecto")
                return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/")
@require_login
def index():
    cur = mysql.connection.cursor(DictCursor)
    try:
        # Cambiar a la base de datos de sensores
        cur.execute("USE sensores_remotos")
        # Obtener todos los id de los sensores
        cur.execute("SELECT sensor_id FROM mediciones")
        sensores_id = cur.fetchall()
        return render_template("index.html", sensores_id=sensores_id)
    except Exception as e:
        logging.error(f"Error al obtener los datos de los sensores: {e}")
        flash("Error al obtener los datos de los sensores")
        return render_template("index.html", sensores_id=[])
    finally:
        cur.close()


@app.route("/change_theme/<theme>")
@require_login
def change_theme(theme):
    session["theme"] = theme
    return redirect(request.referrer)

@app.route("/comando", methods=["POST"])
@require_login
def comando():
    sensor_id = request.form.get("sensor_id")
    accion = request.form.get("accion")
    setpoint = request.form.get("setpoint")

    # Armar los tópicos MQTT con el sensor_id y los nombres de los sub-tópicos
    topico_setpoint = f"{sensor_id}/{os.environ['TOPICO_SETPOINT']}"
    topico_destello = f"{sensor_id}/{os.environ['TOPICO_DESTELLO']}"

    if accion == "destello":
        payload = '{"destello": 1}'
        send_mqtt(topico_destello, payload)
        flash(f"Comando destello enviado a {sensor_id}")
    elif accion == "setpoint" and setpoint:
        try:
            valor = float(setpoint)
            payload = f'{{"setpoint": {valor}}}'
            send_mqtt(topico_setpoint, payload)
            flash(f"Setpoint {valor} enviado a {sensor_id}")
        except ValueError:
            flash("Setpoint inválido")
    else:
        flash("Acción inválida")

    return redirect(url_for("index"))

@app.route("/logout")
@require_login
def logout():
    session.clear()
    logging.info("el usuario {} cerró su sesión".format(session.get("user_id")))
    return redirect(url_for("index"))

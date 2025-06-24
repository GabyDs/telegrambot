from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
import logging
import os
from MySQLdb.cursors import DictCursor


app = Flask(__name__)

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


@app.route("/logout")
@require_login
def logout():
    session.clear()
    logging.info("el usuario {} cerró su sesión".format(session.get("user_id")))
    return redirect(url_for("index"))

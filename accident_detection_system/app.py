from flask import Flask, request, jsonify, render_template
import math
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "resqai"

mysql = MySQL(app)

stations = [
    {
        "name": "City Hospital",
        "lat": 10.8505,
        "lon": 76.2711,
        "phone": "+911111111111"
    },
    {
        "name": "General Hospital",
        "lat": 10.8600,
        "lon": 76.2800,
        "phone": "+922222222222"
    }
]

def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2-lat1)**2 + (lon2-lon1)**2)

@app.route("/")
def home():
    return render_template("index.html", stations=stations)

@app.route("/alert", methods=["POST"])
def alert():
    data = request.json
    lat = float(data["lat"])
    lon = float(data["lon"])
    severity = data["severity"]

    nearest = min(
        stations,
        key=lambda s: calculate_distance(lat, lon, s["lat"], s["lon"])
    )

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO accidents (lat, lon, severity, station) VALUES (%s, %s, %s, %s)",
        (lat, lon, severity, nearest["name"])
    )
    mysql.connection.commit()
    cursor.close()

    return jsonify({
        "station": nearest["name"],
        "phone": nearest["phone"]
    })


@app.route("/dashboard")
def dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM accidents ORDER BY id DESC")
    data = cursor.fetchall()
    cursor.close()

    return render_template("dashboard.html", accidents=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

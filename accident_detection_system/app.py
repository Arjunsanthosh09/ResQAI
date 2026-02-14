from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import osmnx as ox
import networkx as nx
import os
import time
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2

# ------------------ APP INIT ------------------

app = Flask(__name__)
app.secret_key = "resqai_secret_key"

# ------------------ DATABASE CONFIG ------------------

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "resqai"

mysql = MySQL(app)

# ------------------ LOAD AI MODELS ------------------

severity_model = joblib.load("severity_model.pkl")
traffic_model = joblib.load("traffic_model.pkl")

# ------------------ LOAD MAP GRAPH ------------------

GRAPH_FILE = "thrikkodithanam.graphml"

if os.path.exists(GRAPH_FILE):
    G = ox.load_graphml(GRAPH_FILE)
else:
    G = ox.graph_from_point((9.4350, 76.5650), dist=4000, network_type="drive")
    ox.save_graphml(G, GRAPH_FILE)

def get_hospitals():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, lat, lon, road_type FROM hospitals")
    result = cursor.fetchall()
    cursor.close()

    hospital_list = []

    for row in result:
        hospital_list.append({
            "id": row[0],
            "name": row[1],
            "lat": float(row[2]),
            "lon": float(row[3])
        })

    return hospital_list
def smart_hospital_selection(lat, lon, severity):

    current_hour = datetime.datetime.now().hour
    hospitals = get_hospitals()

    best_hospital = None
    best_score = float("inf")

    for hospital in hospitals:

        # 1️⃣ Calculate distance
        distance = calculate_distance(
            lat,
            lon,
            hospital["lat"],
            hospital["lon"]
        )

        # 2️⃣ Get road_type from database
        road_type = hospital["road_type"]

        # 3️⃣ Predict traffic delay using AI model
        delay_factor = traffic_model.predict(
            [[current_hour, road_type]]
        )[0]

        # 4️⃣ Adjusted travel time
        adjusted_time = distance * delay_factor

        # 5️⃣ Decision Logic
        if severity == 2:
            # High severity → choose nearest hospital (fastest physical distance)
            if distance < best_score:
                best_score = distance
                best_hospital = hospital
        else:
            # Low/Moderate → consider traffic delay
            if adjusted_time < best_score:
                best_score = adjusted_time
                best_hospital = hospital

    # 6️⃣ Safety check
    if best_hospital is None:
        return "No Hospital Available"

    return best_hospital["name"]

# ------------------ HELPER FUNCTIONS ------------------

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# ------------------ HOME ------------------

@app.route("/")
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT name, lat, lon, phone FROM hospitals")
    stations = cursor.fetchall()
    cursor.close()
    return render_template("index.html", stations=stations)

# ------------------ AI ACCIDENT ALERT ------------------

@app.route("/alert", methods=["POST"])
def alert():

    data = request.json
    lat = float(data["lat"])
    lon = float(data["lon"])
    speed = float(data["speed"])
    weather = int(data["weather"])  # 0 clear,1 rain,2 fog
    hour = datetime.now().hour

    # -------- AI Severity Prediction --------
    severity_input = pd.DataFrame(
        [[speed, weather, hour]],
        columns=["speed", "weather", "hour"]
    )

    severity_code = int(severity_model.predict(severity_input)[0])
    confidence = float(severity_model.predict_proba(severity_input).max())
    severity_map = {
        0: "Low",
        1: "Moderate",
        2: "High"
    }
    severity_label = severity_map.get(severity_code, "Low")

    # -------- Find Nearest Hospital --------
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM hospitals")
    hospitals = cursor.fetchall()

    nearest = min(
        hospitals,
        key=lambda h: haversine(lat, lon, h["lat"], h["lon"])
    )

    cursor.execute(
    "INSERT INTO accidents (lat, lon, severity, station) VALUES (%s,%s,%s,%s)",
    (lat, lon, severity_label, nearest["name"])
)
    mysql.connection.commit()
    cursor.close()

    return jsonify({
    "station": nearest["name"],
    "severity": severity_label,
    "confidence": round(confidence * 100, 2)
})


# ------------------ LOGIN ------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM hospitals WHERE username=%s AND password=%s",
            (username, password)
        )
        hospital = cursor.fetchone()
        cursor.close()

        if hospital:
            session["hospital"] = hospital["name"]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Credentials"

    return render_template("login.html")

# ------------------ DASHBOARD ------------------

@app.route("/dashboard")
def dashboard():
    if "hospital" not in session:
        return redirect(url_for("login"))

    hospital_name = session["hospital"]

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM accidents WHERE station=%s ORDER BY id DESC",
        (hospital_name,)
    )
    data = cursor.fetchall()
    cursor.close()

    return render_template("dashboard.html", accidents=data, hospital=hospital_name)
# ============================================================
# 🚑 AI ROUTE OPTIMIZATION (REAL AI REROUTING)
# ============================================================

@app.route("/optimize/<int:accident_id>")
def optimize_route(accident_id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # -------- GET ACCIDENT --------
    cursor.execute("SELECT * FROM accidents WHERE id=%s", (accident_id,))
    accident = cursor.fetchone()

    if not accident:
        cursor.close()
        return "Accident not found"

    accident_lat = float(accident["lat"])
    accident_lon = float(accident["lon"])

    # -------- GET HOSPITAL --------
    cursor.execute(
        "SELECT lat, lon FROM hospitals WHERE name=%s",
        (accident["station"],)
    )
    hospital = cursor.fetchone()
    cursor.close()

    hospital_lat = float(hospital["lat"])
    hospital_lon = float(hospital["lon"])

    # -------- NEAREST GRAPH NODES --------
    orig_node = ox.distance.nearest_nodes(G, accident_lon, accident_lat)
    dest_node = ox.distance.nearest_nodes(G, hospital_lon, hospital_lat)

    # =====================================================
    # 1️⃣ ORIGINAL ROUTE (NORMAL CONDITIONS)
    # =====================================================

    route1 = nx.astar_path(G, orig_node, dest_node, weight="length")
    cost1 = nx.path_weight(G, route1, weight="length")

    # =====================================================
    # 2️⃣ SIMULATE AI TRAFFIC CONDITIONS
    # =====================================================

    G_congested = G.copy()
    current_hour = datetime.now().hour
    congested_edges = []

    for u, v, key, data in G_congested.edges(keys=True, data=True):

        road_type = 1
        if "highway" in data:
            if isinstance(data["highway"], list):
                road_type = 2
            else:
                road_type = 3

        # AI Traffic Prediction
        traffic_input = pd.DataFrame(
            [[current_hour, road_type]],
            columns=["hour", "road_type"]
        )

        delay_factor = float(traffic_model.predict(traffic_input)[0])

        # Random additional congestion (20%)
        if np.random.rand() < 0.20:
            delay_factor *= 2.5
            congested_edges.append((u, v))

        data["length"] *= delay_factor

    # =====================================================
    # 3️⃣ NEW ROUTE AFTER TRAFFIC
    # =====================================================

    route2 = nx.astar_path(G_congested, orig_node, dest_node, weight="length")
    cost2 = nx.path_weight(G_congested, route2, weight="length")

    # =====================================================
    # 4️⃣ ETA CALCULATION
    # =====================================================

    avg_speed_mps = 11.11  # 40 km/h

    eta1 = round(cost1 / avg_speed_mps / 60, 2)
    eta2 = round(cost2 / avg_speed_mps / 60, 2)

    # =====================================================
    # 5️⃣ SMART DECISION LOGIC
    # =====================================================

    if cost2 < cost1:
        print("🚧 Better route found → AI Rerouting Enabled")
    else:
        print("✅ Original route still optimal")
        route2 = route1
        eta2 = eta1

    # =====================================================
    # 6️⃣ CONVERT TO COORDINATES
    # =====================================================

    original_route = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route1]
    new_route = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route2]

    # OPTIONAL: Send congested road segments
    congested_coords = []
    for u, v in congested_edges:
        lat1 = G.nodes[u]["y"]
        lon1 = G.nodes[u]["x"]
        lat2 = G.nodes[v]["y"]
        lon2 = G.nodes[v]["x"]
        congested_coords.append([[lat1, lon1], [lat2, lon2]])

    # =====================================================
    # 7️⃣ RENDER TEMPLATE
    # =====================================================

    return render_template(
        "route_animation.html",
        original_route=original_route,
        new_route=new_route,
        accident_lat=accident_lat,
        accident_lon=accident_lon,
        hospital_lat=hospital_lat,
        hospital_lon=hospital_lon,
        eta_original=eta1,
        eta_new=eta2,
        congested_edges=congested_coords
    )



# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import osmnx as ox
import networkx as nx
import random
import copy
import os

app = Flask(__name__)
app.secret_key = "resqai_secret_key"

# ------------------ DATABASE CONFIG ------------------

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "resqai"

mysql = MySQL(app)

# ------------------ LOAD / DOWNLOAD ROAD NETWORK ------------------

GRAPH_FILE = "thrikkodithanam.graphml"

if os.path.exists(GRAPH_FILE):
    print("Loading saved map...")
    G = ox.load_graphml(GRAPH_FILE)
else:
    print("Downloading road network from OpenStreetMap...")
    G = ox.graph_from_point(
        (9.4350, 76.5650),  # Center of your area
        dist=4000,
        network_type="drive"
    )
    ox.save_graphml(G, GRAPH_FILE)

# ------------------ HOME ------------------

@app.route("/")
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT name, lat, lon, phone FROM hospitals")
    stations = cursor.fetchall()
    cursor.close()
    return render_template("index.html", stations=stations)

# ------------------ ACCIDENT ALERT ------------------

@app.route("/alert", methods=["POST"])
def alert():
    data = request.json
    lat = float(data["lat"])
    lon = float(data["lon"])
    severity = data["severity"]

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM hospitals")
    hospitals = cursor.fetchall()

    # Find nearest hospital
    nearest = min(
        hospitals,
        key=lambda h: ((lat - h["lat"])**2 + (lon - h["lon"])**2)
    )

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

# ------------------ ROUTE OPTIMIZATION (REAL MAP) ------------------

@app.route("/optimize/<int:accident_id>")
def optimize_route(accident_id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM accidents WHERE id=%s", (accident_id,))
    accident = cursor.fetchone()
    cursor.close()

    if not accident:
        return "Accident not found"

    accident_lat = float(accident["lat"])
    accident_lon = float(accident["lon"])

    # Get hospital location
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT lat, lon FROM hospitals WHERE name=%s", (accident["station"],))
    hospital = cursor.fetchone()
    cursor.close()

    hospital_lat = float(hospital["lat"])
    hospital_lon = float(hospital["lon"])

    # Find nearest graph nodes
    orig_node = ox.distance.nearest_nodes(G, accident_lon, accident_lat)
    dest_node = ox.distance.nearest_nodes(G, hospital_lon, hospital_lat)

    # Copy graph for congestion simulation
    G_copy = copy.deepcopy(G)

    # 1️⃣ Normal shortest route
    original_route = nx.shortest_path(G_copy, orig_node, dest_node, weight="length")

    # 2️⃣ Inject congestion on first edge of shortest route
    if len(original_route) >= 2:
        u = original_route[0]
        v = original_route[1]

        if G_copy.has_edge(u, v):
            for key in G_copy[u][v]:
                G_copy[u][v][key]["length"] *= 5  # Increase weight

    # 3️⃣ Recalculate route
    new_route = nx.shortest_path(G_copy, orig_node, dest_node, weight="length")

    # Convert node ids to lat/lon coordinates
    original_coords = [
        (G.nodes[node]["y"], G.nodes[node]["x"])
        for node in original_route
    ]

    new_coords = [
        (G.nodes[node]["y"], G.nodes[node]["x"])
        for node in new_route
    ]

    return render_template(
        "route_animation.html",
        original_route=original_coords,
        new_route=new_coords,
        accident_lat=accident_lat,
        accident_lon=accident_lon,
        hospital_lat=hospital_lat,
        hospital_lon=hospital_lon
    )

# ------------------ LOGOUT ------------------

@app.route("/logout")
def logout():
    session.pop("hospital", None)
    return redirect(url_for("login"))

# ------------------
@app.route('/recalculate', methods=['POST'])
def recalculate():

    data = request.get_json()
    current_lat = data['lat']
    current_lon = data['lon']

    # Find nearest node from CURRENT position
    orig_node = ox.distance.nearest_nodes(G, current_lon, current_lat)

    # Destination node (accident)
    dest_node = ox.distance.nearest_nodes(G, accident_lon, accident_lat)

    # Recalculate shortest path
    route = nx.shortest_path(G, orig_node, dest_node, weight='length')

    # Convert nodes to lat/lon list
    route_coords = []
    for node in route:
        route_coords.append([
            G.nodes[node]['y'],
            G.nodes[node]['x']
        ])

    return jsonify(route_coords)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

<div align="center">

<img src="https://img.shields.io/badge/ResQAI-Emergency%20Response%20System-red?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyek0xMyAxN2gtMnYtNmgydjZ6bTAtOGgtMlY3aDJ2MnoiLz48L3N2Zz4=" alt="ResQAI Banner"/>

# 🚑 ResQAI

### Smart Emergency Response & Route Optimization System

*AI-powered accident detection • Intelligent hospital matching • Dynamic routing*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://mysql.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-Academic-green?style=flat-square)](LICENSE)

</div>

---

## 📖 Overview

**ResQAI** is an AI-powered emergency response system designed to minimize critical response time during road accidents. It combines machine learning-based severity prediction, intelligent hospital selection, and real-time route optimization to dispatch ambulances faster and smarter.

> ⚡ Every second counts in an emergency. ResQAI bridges the gap between accident detection and hospital arrival using smart automation.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🚨 **Severity Prediction** | ML model classifies accident severity in real-time |
| 🏥 **Smart Hospital Selection** | Selects the nearest suitable hospital based on distance & traffic |
| 🗺️ **A\* Route Optimization** | Finds the fastest path using graph-based routing |
| 🔁 **Dynamic Rerouting** | Automatically adapts routes on congestion detection |
| 📊 **Hospital Dashboard** | Live monitoring interface for hospital staff |
| 💾 **MySQL Integration** | Persistent storage for accidents and hospital records |

---

## 🧠 Tech Stack

<div align="center">

| Layer | Technology |
|---|---|
| **Backend** | Flask (Python) |
| **Database** | MySQL |
| **Machine Learning** | Scikit-learn, Joblib |
| **Routing Engine** | OSMnx, NetworkX |
| **Frontend** | HTML5, CSS3, JavaScript |

</div>

---

## 📁 Project Structure

```
ResQAI/
├── app.py                      # Main Flask application
├── severity_model.pkl          # Trained accident severity ML model
├── traffic_model.pkl           # Trained traffic prediction ML model
├── thrikkodithanam.graphml     # OSM road network graph
├── templates/
│   ├── index.html              # Landing / accident input page
│   ├── login.html              # Hospital staff login
│   ├── dashboard.html          # Hospital monitoring dashboard
│   └── route_animation.html    # Live route visualization
├── static/                     # CSS, JS, and assets
└── README.md
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/Arjunsanthosh09/resqai.git
cd resqai
```

### 2. Create a Virtual Environment

```bash
# Create
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install flask flask-mysqldb osmnx networkx numpy pandas joblib scikit-learn
```

### 4. Configure the Database

Connect to your MySQL server and run the following:

```sql
CREATE DATABASE resqai;
USE resqai;

CREATE TABLE hospitals (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100),
    lat         DOUBLE,
    lon         DOUBLE,
    phone       VARCHAR(20),
    username    VARCHAR(50),
    password    VARCHAR(50),
    road_type   INT
);

CREATE TABLE accidents (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    lat         DOUBLE,
    lon         DOUBLE,
    severity    VARCHAR(20),
    station     VARCHAR(100),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Run the Application

```bash
python app.py
```

Open your browser and navigate to: **http://localhost:5000**

---

## 📡 API Reference

### `POST /alert`

Accepts accident coordinates and metadata; returns predicted severity and the recommended hospital.

```json
// Request
{
  "lat": 9.7120,
  "lon": 76.5560
}

// Response
{
  "severity": "High",
  "hospital": "General Hospital, Kottayam",
  "distance_km": 3.2
}
```

---

### `POST /dynamic_reroute`

Returns an updated optimal route when congestion is detected along the current path.

```json
// Request
{
  "origin_lat": 9.7120,
  "origin_lon": 76.5560,
  "hospital_id": 3
}

// Response
{
  "route": [[9.712, 76.556], [9.718, 76.561], ...],
  "eta_minutes": 7
}
```

---

## 🔮 Roadmap

- [ ] Live traffic integration (Google Maps / HERE API)
- [ ] Mobile application (Android & iOS)
- [ ] Real-time ambulance GPS tracking
- [ ] Push notification system for hospitals
- [ ] Multi-city road network support
- [ ] Admin analytics dashboard

---

## 👤 Author

**Arjun Santhosh**

[![GitHub](https://img.shields.io/badge/GitHub-Arjunsanthosh09-181717?style=flat-square&logo=github)](https://github.com/Arjunsanthosh09)

---

## 📜 License

This project is intended for **academic and educational use only**.  
Unauthorized commercial use is not permitted.

---

<div align="center">

Made with ❤️ to save lives

*If this project helped you, consider giving it a ⭐*

</div>

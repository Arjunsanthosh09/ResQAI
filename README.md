# 🚑 ResQAI – Smart Emergency Response & Route Optimization System

ResQAI is an AI-powered emergency response system that detects accident severity, identifies the nearest suitable hospital, and dynamically optimizes ambulance routes using traffic intelligence.

---

## 👤 Author
**Arjun Santhosh**  
GitHub: https://github.com/Arjunsanthosh09

---

## 📌 Features

- 🚨 Accident Severity Prediction using Machine Learning
- 🏥 Smart Hospital Selection based on distance & traffic
- 🗺️ Route Optimization using A* Algorithm
- 🔁 Dynamic Rerouting with simulated congestion
- 📊 Hospital Dashboard for monitoring alerts
- 💾 MySQL Database integration

---

## 🧠 Tech Stack

- Backend: Flask (Python)
- Database: MySQL
- ML Models: Scikit-learn (Joblib)
- Routing: OSMnx + NetworkX
- Frontend: HTML, CSS, JavaScript

---

## 📁 Project Structure

ResQAI/
│── app.py
│── severity_model.pkl
│── traffic_model.pkl
│── thrikkodithanam.graphml
│── templates/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── route_animation.html
│── static/
│── README.md

---

## ⚙️ Installation

### 1. Clone Repository
git clone https://github.com/Arjunsanthosh09/resqai.git
cd resqai

### 2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate   (Windows)
source venv/bin/activate (Linux/Mac)

### 3. Install Dependencies
pip install flask flask-mysqldb osmnx networkx numpy pandas joblib

### 4. Setup Database
CREATE DATABASE resqai;

CREATE TABLE hospitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    lat DOUBLE,
    lon DOUBLE,
    phone VARCHAR(20),
    username VARCHAR(50),
    password VARCHAR(50),
    road_type INT
);

CREATE TABLE accidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lat DOUBLE,
    lon DOUBLE,
    severity VARCHAR(20),
    station VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

### 5. Run Application
python app.py

Open: http://localhost:5000

---

## 📡 API

### POST /alert
Send accident data and receive severity + hospital

### POST /dynamic_reroute
Get updated route based on congestion

---

## 🚀 Future Improvements

- Live traffic integration (Google Maps API)
- Mobile app version
- Real-time ambulance tracking
- Notification system

---

## 📜 License
For academic and educational use only.

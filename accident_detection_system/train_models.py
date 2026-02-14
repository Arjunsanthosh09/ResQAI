# train_models.py

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib

# -----------------------------
# 1️⃣ Accident Severity Model
# -----------------------------

# Fake training dataset (replace later with real data)
np.random.seed(42)

data = pd.DataFrame({
    "speed": np.random.randint(20, 120, 500),
    "weather": np.random.randint(0, 3, 500),  # 0=clear,1=rain,2=fog
    "hour": np.random.randint(0, 24, 500),
})

# Severity: 0=Low,1=Medium,2=High
data["severity"] = (
    (data["speed"] > 80).astype(int)
    + (data["weather"] == 1).astype(int)
)

X = data[["speed", "weather", "hour"]]
y = data["severity"]

severity_model = RandomForestClassifier()
severity_model.fit(X, y)

joblib.dump(severity_model, "severity_model.pkl")


# -----------------------------
# 2️⃣ Traffic Congestion Model
# -----------------------------

traffic_data = pd.DataFrame({
    "hour": np.random.randint(0, 24, 500),
    "road_type": np.random.randint(1, 4, 500),
})

traffic_data["delay_factor"] = (
    1 + (traffic_data["hour"].between(8,10) |
         traffic_data["hour"].between(17,19)).astype(int) * 2
)

X2 = traffic_data[["hour", "road_type"]]
y2 = traffic_data["delay_factor"]

traffic_model = RandomForestRegressor()
traffic_model.fit(X2, y2)

joblib.dump(traffic_model, "traffic_model.pkl")

print("AI Models Trained Successfully.")

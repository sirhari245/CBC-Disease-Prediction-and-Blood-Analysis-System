# ==========================================
# CBC Disease Prediction System
# Machine Learning Project
# ==========================================

from flask import Flask, render_template_string, request
import pandas as pd
import numpy as np
import sqlite3
import os
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# ==========================================
# DATABASE SETUP
# ==========================================

conn = sqlite3.connect('database.db', check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS reports(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hemoglobin REAL,
    wbc REAL,
    rbc REAL,
    platelets REAL,
    prediction TEXT
)
""")

conn.commit()

# ==========================================
# CREATE DATASET
# ==========================================

if not os.path.exists("cbc_dataset.csv"):

    dataset = pd.DataFrame({

        'hemoglobin': [
            8, 13, 11, 9, 14,
            10, 15, 7, 16, 12
        ],

        'wbc': [
            14000, 7000, 12000, 15000, 8000,
            13000, 6000, 16000, 7500, 9000
        ],

        'rbc': [
            4.0, 5.0, 4.2, 4.1, 5.2,
            4.3, 5.5, 3.9, 5.1, 4.8
        ],

        'platelets': [
            100000, 250000, 140000, 90000, 300000,
            120000, 280000, 80000, 270000, 220000
        ],

        'disease': [
            'Anemia',
            'Normal',
            'Infection',
            'Platelet Disorder',
            'Normal',
            'Anemia',
            'Normal',
            'Platelet Disorder',
            'Normal',
            'Normal'
        ]

    })

    dataset.to_csv("cbc_dataset.csv", index=False)

# ==========================================
# TRAIN MACHINE LEARNING MODEL
# ==========================================

if not os.path.exists("model.pkl"):

    data = pd.read_csv("cbc_dataset.csv")

    X = data[['hemoglobin', 'wbc', 'rbc', 'platelets']]

    Y = data['disease']

    encoder = LabelEncoder()

    Y_encoded = encoder.fit_transform(Y)

    model = RandomForestClassifier()

    model.fit(X, Y_encoded)

    joblib.dump(model, "model.pkl")

    joblib.dump(encoder, "encoder.pkl")

# ==========================================
# LOAD MODEL
# ==========================================

model = joblib.load("model.pkl")

encoder = joblib.load("encoder.pkl")

# ==========================================
# HTML PAGE
# ==========================================

home_page = """

<!DOCTYPE html>
<html>

<head>

<title>AI CBC Disease Prediction</title>

<style>

body{
    background:#f5f5f5;
    font-family:Arial;
}

.container{
    width:700px;
    margin:40px auto;
    background:white;
    padding:30px;
    border-radius:10px;
    box-shadow:0px 0px 10px gray;
}

h1{
    text-align:center;
    color:darkred;
}

input{
    width:100%;
    padding:12px;
    margin-top:15px;
}

button{
    width:100%;
    padding:12px;
    margin-top:20px;
    background:darkred;
    color:white;
    border:none;
    font-size:16px;
    cursor:pointer;
}

button:hover{
    background:red;
}

.btn{
    display:block;
    margin-top:20px;
    background:darkred;
    color:white;
    text-align:center;
    padding:12px;
    text-decoration:none;
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:20px;
}

table, th, td{
    border:1px solid gray;
}

th, td{
    padding:10px;
    text-align:center;
}

</style>

</head>

<body>

<div class="container">

<h1>AI-Based CBC Disease Prediction</h1>

<form action="/predict" method="POST">

<input type="number"
       step="0.1"
       name="hb"
       placeholder="Enter Hemoglobin"
       required>

<input type="number"
       name="wbc"
       placeholder="Enter WBC Count"
       required>

<input type="number"
       step="0.1"
       name="rbc"
       placeholder="Enter RBC Count"
       required>

<input type="number"
       name="platelets"
       placeholder="Enter Platelet Count"
       required>

<button type="submit">
Predict Disease
</button>

</form>

<a href="/history" class="btn">
View Prediction History
</a>

</div>

</body>
</html>

"""

# ==========================================
# HOME ROUTE
# ==========================================

@app.route('/')
def home():

    return render_template_string(home_page)

# ==========================================
# PREDICTION ROUTE
# ==========================================

@app.route('/predict', methods=['POST'])
def predict():

    hb = float(request.form['hb'])
    wbc = float(request.form['wbc'])
    rbc = float(request.form['rbc'])
    platelets = float(request.form['platelets'])

    values = np.array([[hb, wbc, rbc, platelets]])

    prediction = model.predict(values)

    result = encoder.inverse_transform(prediction)

    final_result = result[0]

    # SAVE REPORT
    cur.execute("""

    INSERT INTO reports(
        hemoglobin,
        wbc,
        rbc,
        platelets,
        prediction
    )

    VALUES(?,?,?,?,?)

    """, (hb, wbc, rbc, platelets, final_result))

    conn.commit()

    result_page = """

    <!DOCTYPE html>
    <html>

    <head>

    <title>Prediction Result</title>

    <style>

    body{
        background:#f5f5f5;
        font-family:Arial;
    }

    .container{
        width:700px;
        margin:40px auto;
        background:white;
        padding:30px;
        border-radius:10px;
        box-shadow:0px 0px 10px gray;
    }

    h1{
        text-align:center;
        color:darkred;
    }

    h2{
        text-align:center;
        color:green;
        margin-top:30px;
    }

    .btn{
        display:block;
        margin-top:20px;
        background:darkred;
        color:white;
        text-align:center;
        padding:12px;
        text-decoration:none;
    }

    </style>

    </head>

    <body>

    <div class="container">

    <h1>Prediction Result</h1>

    <h2>{{ prediction }}</h2>

    <a href="/" class="btn">
    Predict Another Report
    </a>

    </div>

    </body>
    </html>

    """

    return render_template_string(
        result_page,
        prediction=final_result
    )

# ==========================================
# HISTORY ROUTE
# ==========================================

@app.route('/history')
def history():

    cur.execute("SELECT * FROM reports")

    reports = cur.fetchall()

    history_page = """

    <!DOCTYPE html>
    <html>

    <head>

    <title>Prediction History</title>

    <style>

    body{
        background:#f5f5f5;
        font-family:Arial;
    }

    .container{
        width:900px;
        margin:40px auto;
        background:white;
        padding:30px;
        border-radius:10px;
        box-shadow:0px 0px 10px gray;
    }

    h1{
        text-align:center;
        color:darkred;
    }

    table{
        width:100%;
        border-collapse:collapse;
        margin-top:20px;
    }

    table, th, td{
        border:1px solid gray;
    }

    th, td{
        padding:10px;
        text-align:center;
    }

    .btn{
        display:block;
        margin-top:20px;
        background:darkred;
        color:white;
        text-align:center;
        padding:12px;
        text-decoration:none;
    }

    </style>

    </head>

    <body>

    <div class="container">

    <h1>Prediction History</h1>

    <table>

    <tr>

        <th>ID</th>
        <th>HB</th>
        <th>WBC</th>
        <th>RBC</th>
        <th>Platelets</th>
        <th>Prediction</th>

    </tr>

    {% for report in reports %}

    <tr>

        <td>{{ report[0] }}</td>
        <td>{{ report[1] }}</td>
        <td>{{ report[2] }}</td>
        <td>{{ report[3] }}</td>
        <td>{{ report[4] }}</td>
        <td>{{ report[5] }}</td>

    </tr>

    {% endfor %}

    </table>

    <a href="/" class="btn">
    Back
    </a>

    </div>

    </body>
    </html>

    """

    return render_template_string(
        history_page,
        reports=reports
    )

# ==========================================
# RUN APP
# ==========================================

if __name__ == '__main__':

    app.run(debug=True)
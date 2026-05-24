# app.py

from flask import Flask, render_template_string, request
import sqlite3

app = Flask(__name__)

# ================= DATABASE =================

conn = sqlite3.connect('database.db', check_same_thread=False)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS reports(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hemoglobin REAL,
    wbc REAL,
    rbc REAL,
    platelets REAL,
    result TEXT
)
''')

conn.commit()

# ================= HTML + CSS =================

index_page = '''

<!DOCTYPE html>
<html>

<head>

    <title>CBC Report Analyzer</title>

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

        ul{
            line-height:2;
            font-size:18px;
        }

    </style>

</head>

<body>

<div class="container">

    <h1>CBC Report Analyzer</h1>

    <form action="/analyze" method="POST">

        <input type="number"
               step="0.1"
               name="hb"
               placeholder="Hemoglobin"
               required>

        <input type="number"
               name="wbc"
               placeholder="WBC Count"
               required>

        <input type="number"
               step="0.1"
               name="rbc"
               placeholder="RBC Count"
               required>

        <input type="number"
               name="platelets"
               placeholder="Platelet Count"
               required>

        <button type="submit">
            Analyze Report
        </button>

    </form>

    <a href="/history" class="btn">
        View History
    </a>

</div>

</body>
</html>

'''

# ================= HOME PAGE =================

@app.route('/')
def home():

    return render_template_string(index_page)

# ================= ANALYZE =================

@app.route('/analyze', methods=['POST'])
def analyze():

    hb = float(request.form['hb'])
    wbc = float(request.form['wbc'])
    rbc = float(request.form['rbc'])
    platelets = float(request.form['platelets'])

    results = []

    # Hemoglobin
    if hb < 12:
        results.append("Low Hemoglobin - Possible Anemia")
    elif hb > 17:
        results.append("High Hemoglobin")
    else:
        results.append("Hemoglobin Normal")

    # WBC
    if wbc > 11000:
        results.append("High WBC - Possible Infection")
    elif wbc < 4000:
        results.append("Low WBC Count")
    else:
        results.append("WBC Normal")

    # RBC
    if rbc < 4.5:
        results.append("Low RBC Count")
    else:
        results.append("RBC Normal")

    # Platelets
    if platelets < 150000:
        results.append("Low Platelets")
    elif platelets > 450000:
        results.append("High Platelets")
    else:
        results.append("Platelets Normal")

    result_text = ", ".join(results)

    # Save to Database
    cur.execute('''
    INSERT INTO reports(
        hemoglobin,
        wbc,
        rbc,
        platelets,
        result
    )
    VALUES(?,?,?,?,?)
    ''', (hb, wbc, rbc, platelets, result_text))

    conn.commit()

    result_page = '''

    <!DOCTYPE html>
    <html>

    <head>

        <title>Result</title>

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

            ul{
                line-height:2;
                font-size:18px;
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

        <h1>Analysis Result</h1>

        <ul>

            {% for result in results %}
                <li>{{ result }}</li>
            {% endfor %}

        </ul>

        <a href="/" class="btn">
            Analyze Another Report
        </a>

    </div>

    </body>
    </html>

    '''

    return render_template_string(
        result_page,
        results=results
    )

# ================= HISTORY =================

@app.route('/history')
def history():

    cur.execute("SELECT * FROM reports")

    data = cur.fetchall()

    history_page = '''

    <!DOCTYPE html>
    <html>

    <head>

        <title>History</title>

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

        <h1>Saved Reports</h1>

        <table>

            <tr>

                <th>ID</th>
                <th>HB</th>
                <th>WBC</th>
                <th>RBC</th>
                <th>Platelets</th>
                <th>Result</th>

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

    '''

    return render_template_string(
        history_page,
        reports=data
    )

# ================= RUN =================

if __name__ == '__main__':

    app.run(debug=True)
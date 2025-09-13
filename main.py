from flask import Flask,render_template
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv() 

DATA_DIR = os.getenv("DATA_DIR")

app = Flask(__name__)

stations_path = os.path.join(DATA_DIR, "stations.txt")
stations = pd.read_csv(stations_path, skiprows=17)

@app.route("/")
def home():
    return render_template("home.html",data=stations.to_html())

@app.route("/api/v1/<station>/<date>")
def data(station,date):
    path = os.path.join(DATA_DIR, f"TG_STAID{int(station):06d}.txt")

    df = pd.read_csv(path,skiprows=20, parse_dates=["    DATE"])
    df =  df.loc[df['   TG'] != -9999]
    target = df.loc[df["    DATE"] == date]['   TG']
    
    if target.empty:
        temperature = None
    else:
        temperature = target.squeeze() / 10
    

    return {"station" : station,
            "date" : date,
             "temperature": temperature }

if __name__ == "__main__":
    app.run(debug=True) 
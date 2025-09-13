from flask import Flask,render_template
import pandas as pd

app = Flask(__name__)

stations = pd.read_csv("E:\Code\Python\weather-api\ \
                       data-small\stations.txt",skiprows=17)
stations = stations[["STAID","STANAME                                 "]]

@app.route("/")
def home():
    return render_template("home.html",data=stations.to_html())

@app.route("/api/v1/<station>/<date>")
def data(station,date):
    path = "E:\Code\Python\weather-api\data-small\TG_STAID" + str(station).zfill(6) + ".txt"
    df = pd.read_csv(path,skiprows=20, parse_dates=["    DATE"])
    temperature = df.loc[df["    DATE"] == date]['   TG'].squeeze() / 10
    
    return {"station" : station,
            "date" : date,
             "temperature": temperature }

if __name__ == "__main__":
    app.run(debug=True) 
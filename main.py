"""
Weather Data API with Flask
This application provides a web interface and API for accessing historical weather station data.
"""

from flask import Flask, render_template
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

# Get the data directory path from environment variables
DATA_DIR = os.getenv("DATA_DIR")

# Initialize Flask application
app = Flask(__name__)

# Path to the stations data file
stations_path = os.path.join(DATA_DIR, "stations.txt")

# Read stations data from CSV file, skipping the first 17 rows (metadata/header)
stations = pd.read_csv(stations_path, skiprows=17)

@app.route("/")
def home():
    """
    Homepage route that displays all available weather stations.
    
    Returns:
        Rendered HTML template with stations data formatted as an HTML table
    """
    return render_template("home.html", data=stations.to_html())

@app.route("/api/v1/<station>/<date>")
def data(station, date):
    """
    API endpoint to retrieve temperature data for a specific station and date.
    
    Args:
        station (str): Station ID number (without leading zeros)
        date (str): Date in the format used in the data files (likely YYYY-MM-DD)
    
    Returns:
        JSON object containing station ID, date, and temperature in Celsius
        Returns temperature as None if no data is found for the given date
    """
    # Construct the file path for the specific station's data
    # Format station ID as a 6-digit number with leading zeros
    path = os.path.join(DATA_DIR, f"TG_STAID{int(station):06d}.txt")

    # Read the station's temperature data, skipping metadata rows
    # Parse the DATE column as datetime objects for easier comparison
    df = pd.read_csv(path, skiprows=20, parse_dates=["    DATE"])
    
    # Filter out missing temperature values (represented by -9999)
    df = df.loc[df['   TG'] != -9999]
    
    # Find temperature data for the specific date
    target = df.loc[df["    DATE"] == date]['   TG']
    
    # Check if data exists for the requested date
    if target.empty:
        temperature = None
    else:
        # Extract the temperature value and convert to Celsius (divided by 10)
        temperature = target.squeeze() / 10
    
    # Return the result as a JSON response
    return {
        "station": station,
        "date": date,
        "temperature": temperature
    }

if __name__ == "__main__":
    # Run the Flask application in debug mode
    app.run(debug=True)
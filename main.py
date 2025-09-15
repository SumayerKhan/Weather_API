"""
Weather Data API with Flask
---------------------------
This application serves a small web UI and several JSON API endpoints to access
historical weather station data (daily mean temperatures). Data files come from
an external source and include multi-line headers plus some quirks such as:

- Column names with leading spaces (e.g., "    DATE", "   TG", " Q_TG", " SOUID").
- Missing temperature values encoded as the sentinel -9999 (must be filtered out).
- Station files named as TG_STAIDXXXXXX.txt where XXXXXX is a 6-digit STAID.

Key Endpoints
-------------
- GET /                      : Simple homepage showing the list of stations.
- GET /api/v1/<station>/<date>
                             : Temperature (°C) for one station on one date.
- GET /api/v1/<station>      : All cleaned rows for one station (JSON array).
- GET /api/v1/annual/<station>/<year>
                             : All rows for a given year (string match on DATE).

Notes
-----
- When we need date equality comparisons, we parse dates to datetime at read time.
- When we need "starts with year" filtering, we coerce DATE to string then use
  vectorized string operations (Series.str.*).
"""

from flask import Flask, render_template
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables (expects DATA_DIR to be set in a .env file)
# e.g., DATA_DIR=/absolute/path/to/data
load_dotenv()

# Absolute/relative path to the folder containing stations.txt and TG_STAID*.txt
DATA_DIR = os.getenv("DATA_DIR")

# Initialize Flask application instance
app = Flask(__name__)

# Path to the stations listing file (has a 17-line textual header before CSV content)
stations_path = os.path.join(DATA_DIR, "stations.txt")

# Read the stations list, skipping textual header lines that precede the actual table.
# NOTE: Adjust 'skiprows' if the upstream file format changes.
stations = pd.read_csv(stations_path, skiprows=17)


@app.route("/")
def home():
    """
    Render the homepage that displays all available weather stations in a table.

    Returns:
        str: Rendered HTML from 'home.html' with an HTML table of station rows.
    """
    # Convert the stations DataFrame to an HTML table for quick visualization.
    # In a production app you would usually render columns explicitly in the template.
    return render_template("home.html", data=stations.to_html())


@app.route("/api/v1/<station>/<date>")
def data(station: str, date: str):
    """
    Retrieve temperature data for a specific station on a specific date.

    Args:
        station (str): Station numeric ID (may be provided without leading zeros).
        date (str): Date string matching the file's DATE format.
                    Because we parse the DATE column as datetime, this will
                    be compared as a pandas-compatible date (exact match).

    Returns:
        dict: JSON-serializable dictionary with:
              - station (str)
              - date (str)
              - temperature (float | None)  # °C; None if not found
    """
    # Build file path for the requested station:
    # int() ensures valid integer; :06d pads to 6 digits (e.g., 23 -> "000023").
    path = os.path.join(DATA_DIR, f"TG_STAID{int(station):06d}.txt")

    # Read station data:
    # - skiprows=20 to ignore long textual header.
    # - parse_dates=["    DATE"] so we can do exact datetime comparisons.
    #   NOTE: The DATE column name has leading spaces in the source file.
    df = pd.read_csv(path, skiprows=20, parse_dates=["    DATE"])

    # Remove rows where temperature is missing:
    # The file encodes "no data" as -9999 (tenths of °C), so filter them out.
    df = df.loc[df["   TG"] != -9999]

    # Select the temperature entries exactly matching the requested date.
    # Because DATE is parsed as datetime and 'date' is a string, pandas will
    # attempt to align/compare appropriately. If needed, you could also do:
    # df["    DATE"].dt.strftime("%Y-%m-%d") == date
    target = df.loc[df["    DATE"] == date]["   TG"]

    # If no row matches the date, return temperature=None
    if target.empty:
        temperature = None
    else:
        # Values are tenths of a degree Celsius; divide by 10 to get °C.
        # squeeze() extracts a scalar if there's exactly one value.
        temperature = target.squeeze() / 10

    # Flask will jsonify dicts automatically if returned from a route function.
    return {
        "station": station,
        "date": date,
        "temperature": temperature,
    }


@app.route("/api/v1/<station>")
def all_data(station: str):
    """
    Return all valid rows (with temperature present) for a specific station.

    Args:
        station (str): Station numeric ID.

    Returns:
        list[dict]: List of row dictionaries (JSON array), one per observation.
    """
    path = os.path.join(DATA_DIR, f"TG_STAID{int(station):06d}.txt")

    # Parse DATE as datetime here since we often want to treat it as a real date.
    df = pd.read_csv(path, skiprows=20, parse_dates=["    DATE"])

    # Filter out sentinel -9999 values (unknown/missing measurements).
    df = df.loc[df["   TG"] != -9999]

    # Convert the entire cleaned DataFrame to a list of dicts for JSON responses.
    # orient="records" => [{"col1": v11, "col2": v12, ...}, {"col1": v21, ...}, ...]
    result = df.to_dict(orient="records")
    return result


@app.route("/api/v1/annual/<station>/<year>")
def yearly(station: str, year: str):
    """
    Return all rows for a given station in a given calendar year.

    This endpoint uses a string-based year filter. We:
      1) read the CSV (DATE not parsed here),
      2) coerce the DATE column to string,
      3) select rows where DATE starts with the requested 'year' (e.g., "2020").

    Args:
        station (str): Station numeric ID.
        year (str): 4-digit year string (e.g., "2020").

    Returns:
        list[dict]: List of row dictionaries for that year.
    """
    path = os.path.join(DATA_DIR, f"TG_STAID{int(station):06d}.txt")
    df = pd.read_csv(path, skiprows=20)

    # The source file's DATE header has leading spaces. We keep the original name.
    # Convert to string so we can use vectorized string operations on the Series.
    df["    DATE"] = df["    DATE"].astype(str)

    # Vectorized "starts with" on the DATE column to select the target year.
    # We wrap 'year' with str() to be safe if it were passed as an int-like string.
    mask = df["    DATE"].str.startswith(str(year))

    # Build final JSON-friendly structure. (Not filtering -9999 here on purpose,
    # to keep behavior identical to your original code. Consider filtering like
    # df = df.loc[df["   TG"] != -9999] if you only want valid temperatures.)
    result = df.loc[mask].to_dict(orient="records")
    return result


if __name__ == "__main__":
    # Debug mode enables auto-reload and better error pages during development.
    # Do not use debug=True in production.
    app.run(debug=True)

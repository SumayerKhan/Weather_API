# Weather Data API

A Flask-based web application that serves historical weather station data through REST API endpoints and a simple web interface. The application processes daily mean temperature data from weather stations with built-in data cleaning and validation.

## Features

- **Web Interface**: Simple homepage displaying all available weather stations
- **REST API**: Multiple endpoints for accessing temperature data
- **Data Cleaning**: Automatic filtering of missing/invalid temperature readings
- **Flexible Date Handling**: Support for both exact date matching and year-based filtering
- **Station Management**: Automatic station file discovery and processing

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Homepage with station list table |
| `GET` | `/api/v1/<station>/<date>` | Temperature for specific station and date |
| `GET` | `/api/v1/<station>` | All valid records for a station |
| `GET` | `/api/v1/annual/<station>/<year>` | All records for a station in a given year |

### Endpoint Details

#### Get Single Temperature Reading
```
GET /api/v1/<station>/<date>
```
- **station**: Station ID (numeric, leading zeros optional)
- **date**: Date in YYYY-MM-DD format
- **Returns**: JSON object with station, date, and temperature (°C)

**Example Response:**
```json
{
  "station": "10",
  "date": "1998-10-15",
  "temperature": 12.5
}
```

#### Get All Station Data
```
GET /api/v1/<station>
```
- **station**: Station ID (numeric)
- **Returns**: JSON array of all valid temperature records

#### Get Annual Data
```
GET /api/v1/annual/<station>/<year>
```
- **station**: Station ID (numeric)
- **year**: 4-digit year (e.g., "2020")
- **Returns**: JSON array of all records for the specified year

## Installation & Setup

### Prerequisites
- Python 3.7+
- pip package manager

### Dependencies
```bash
pip install flask pandas python-dotenv
```

### Environment Configuration
Create a `.env` file in the project root:
```env
DATA_DIR=/path/to/your/weather/data/directory
```

### Data Directory Structure
Your data directory should contain:
```
data/
├── stations.txt          # Station metadata (17-line header + CSV)
└── TG_STAID000001.txt    # Individual station files
└── TG_STAID000002.txt
└── ...
```

### Station Data File Format
- **Filename**: `TG_STAID{6-digit-station-id}.txt`
- **Header**: 20 lines of metadata (automatically skipped)
- **Columns**: 
  - `    DATE`: Date with leading spaces
  - `   TG`: Temperature in tenths of °C
  - ` Q_TG`: Quality indicator
  - ` SOUID`: Source identifier
- **Missing Data**: Encoded as `-9999` (automatically filtered)

## Running the Application

### Development Mode
```bash
python app.py
```
The application will start on `http://127.0.0.1:5000` with debug mode enabled.

### Production Deployment
For production, disable debug mode and use a proper WSGI server:
```python
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
```

## Data Processing Notes

### Temperature Conversion
- Raw data is stored in tenths of degrees Celsius
- API responses automatically convert to degrees Celsius (divide by 10)

### Data Cleaning
- Missing/invalid temperatures (`-9999`) are automatically filtered out
- Only valid temperature readings are returned in API responses

### Date Handling
- **Exact matching** (`/api/v1/<station>/<date>`): Uses datetime parsing for precise comparisons
- **Year filtering** (`/api/v1/annual/<station>/<year>`): Uses string matching for performance

## Usage Examples

### cURL Examples
```bash
# Get temperature for station 123 on January 15, 2020
curl http://localhost:5000/api/v1/123/2020-01-15

# Get all data for station 456
curl http://localhost:5000/api/v1/456

# Get 2020 data for station 789
curl http://localhost:5000/api/v1/annual/789/2020
```

### Python Examples
```python
import requests

base_url = "http://localhost:5000"

# Single temperature reading
response = requests.get(f"{base_url}/api/v1/123/2020-01-15")
data = response.json()
print(f"Temperature: {data['temperature']}°C")

# All station data
response = requests.get(f"{base_url}/api/v1/123")
all_data = response.json()
print(f"Total records: {len(all_data)}")

# Annual data
response = requests.get(f"{base_url}/api/v1/annual/123/2020")
yearly_data = response.json()
print(f"Records in 2020: {len(yearly_data)}")
```

## Error Handling

- **Missing station files**: Will result in file not found errors
- **Invalid station IDs**: Non-numeric IDs will cause value errors
- **Missing dates**: Returns `temperature: null` in JSON response
- **Invalid data directory**: Check your `DATA_DIR` environment variable

## Development Notes

### File Structure
```
project/
├── app.py              # Main Flask application
├── .env                # Environment variables
├── templates/
│   └── home.html       # Homepage template
└── requirements.txt    # Python dependencies
```

### Template Requirements
Create a basic `templates/home.html` file:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Weather Stations</title>
</head>
<body>
    <h1>Available Weather Stations</h1>
    {{ data|safe }}
</body>
</html>
```

## Contributing

1. Ensure all data files follow the expected format
2. Test API endpoints with various station IDs and date ranges
3. Validate temperature conversions and data cleaning logic
4. Consider adding input validation and error handling for production use

## License

This project is designed for processing weather station data in a standardized format. Ensure you have appropriate rights to use the weather data files.
import os
import requests

RAW_DIR = "data/raw"


def fetch_traffic():
    """Download all Calgary traffic incidents as one CSV."""
    url = "https://data.calgary.ca/resource/35ra-9556.csv?$limit=500000"
    r = requests.get(url)
    r.raise_for_status()
    with open(f"{RAW_DIR}/traffic_incidents.csv", "wb") as f:
        f.write(r.content)
    print("Saved traffic_incidents.csv")


def fetch_weather(start_year=2017, end_year=2026, station_id=50430):
    """Download daily weather for Calgary Intl, one CSV per year."""
    for year in range(start_year, end_year + 1):
        url = (
            "https://climate.weather.gc.ca/climate_data/bulk_data_e.html"
            f"?format=csv&stationID={station_id}&Year={year}&Month=1&Day=1&timeframe=2"
        )
        r = requests.get(url)
        r.raise_for_status()
        with open(f"{RAW_DIR}/weather_{year}.csv", "wb") as f:
            f.write(r.content)
        print(f"Saved weather_{year}.csv")


if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    fetch_traffic()
    fetch_weather()
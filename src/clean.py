import pandas as pd
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

SUMMER_MONTHS = [5, 6, 7, 8, 9]

def clean_traffic():
  ## Tracffic incidents csv cleaning
  traffic = pd.read_csv(RAW_DIR / "traffic_incidents.csv")

  # keep only the columns we need
  traffic = traffic[["id", "incident_info", "description",
                    "start_dt_utc", "quadrant", "latitude", "longitude"]].copy()

  # drop duplicate incidents
  traffic = traffic.drop_duplicates(subset="id")

  # parse as UTC, convert to Calgary time, then drop the timezone label
  traffic["start_dt"] = (
      pd.to_datetime(traffic["start_dt_utc"], errors="coerce", utc=True)
        .dt.tz_convert("America/Edmonton")
        .dt.tz_localize(None)
  )
  traffic = traffic.drop(columns="start_dt_utc")
  traffic = traffic.dropna(subset=["start_dt"])

  # keep winter season only (drop May–September)
  traffic = traffic[~traffic["start_dt"].dt.month.isin(SUMMER_MONTHS)]

  # date and hour in Calgary time
  traffic["date"] = traffic["start_dt"].dt.date
  traffic["hour"] = traffic["start_dt"].dt.hour

  # clean up quadrants
  traffic["quadrant"] = traffic["quadrant"].str.strip().str.upper()
  traffic = traffic[traffic["quadrant"].isin(["NE", "NW", "SE", "SW"])]

  return traffic



def clean_weather():
    files = sorted(glob.glob(str(RAW_DIR / "weather_*.csv")))
    weather = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
 
    # rename columns to shorter names and keep only the ones we need
    weather = weather.rename(columns={
        "Date/Time": "date",
        "Max Temp (°C)": "max_temp",
        "Min Temp (°C)": "min_temp",
        "Mean Temp (°C)": "mean_temp",
        "Total Snow (cm)": "total_snow",
        "Total Snow Flag": "snow_flag",
        "Total Precip (mm)": "total_precip",
        "Snow on Grnd (cm)": "snow_on_ground",
    })
    weather = weather[["date", "max_temp", "min_temp", "mean_temp",
                       "total_snow", "snow_flag", "total_precip", "snow_on_ground"]].copy()
 
    # fix data types
    weather["date"] = pd.to_datetime(weather["date"])
    num_cols = ["max_temp", "min_temp", "mean_temp",
                "total_snow", "total_precip", "snow_on_ground"]
    weather[num_cols] = weather[num_cols].apply(pd.to_numeric, errors="coerce")
 
    # drop future dates (rows with no measurements at all)
    weather = weather.dropna(subset=num_cols, how="all")
 
    # trace snowfall ("T") counts as 0 cm
    weather.loc[weather["snow_flag"] == "T", "total_snow"] = 0
    weather = weather.drop(columns="snow_flag")
 
    weather["total_snow"] = weather["total_snow"].fillna(0)
 
    # keep winter season only (drop May–September)`
    weather = weather[~weather["date"].dt.month.isin(SUMMER_MONTHS)]
 
    # one row per day, in order, with a plain date to match the traffic table
    weather = weather.drop_duplicates(subset="date").sort_values("date")
    weather["date"] = weather["date"].dt.date
 
    return weather
 
 
if __name__ == "__main__":
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    traffic = clean_traffic()
    traffic.to_csv(f"{PROCESSED_DIR}/incidents.csv", index=False)
    print(f"incidents: {len(traffic)} rows, {traffic['date'].min()} to {traffic['date'].max()}")
 
    weather = clean_weather()
    weather.to_csv(f"{PROCESSED_DIR}/weather_daily.csv", index=False)
    print(f"weather_daily: {len(weather)} rows, {weather['date'].min()} to {weather['date'].max()}")
 
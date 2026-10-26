import pandas as pd


## Tracffic incidents csv cleaning
traffic = pd.read_csv("../data/raw/traffic_incidents.csv")

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
traffic = traffic[~traffic["start_dt"].dt.month.isin([5, 6, 7, 8, 9])]

# date and hour in Calgary time
traffic["date"] = traffic["start_dt"].dt.date
traffic["hour"] = traffic["start_dt"].dt.hour

# clean up quadrants
traffic["quadrant"] = traffic["quadrant"].str.strip().str.upper()
traffic = traffic[traffic["quadrant"].isin(["NE", "NW", "SE", "SW"])]

print(traffic.shape)
traffic.groupby("date").size().describe()




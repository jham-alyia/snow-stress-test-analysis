# Snow Season Stress Test

**How long does Calgary stay dangerous after a snowfall, and which parts of the city take longest to recover?**
 
## About the project
 
When snow hits Calgary, collision risk doesn't spike and disappear the same day. It lingers while snow stays on the roads. This project combines Calgary traffic incident data with Environment Canada weather data to measure **how long** elevated incident levels last after a snowfall and **where** in the city they last longest.
 
The goal is to show where and when Calgary's winter road response may be falling behind. That's useful for drivers deciding when roads are safe again and for planners deciding where to plow and sand first.
 
## Questions
 
- How much higher are traffic incidents on days with heavy snowfall than on dry days?
- After a big snowfall, how many days do incidents stay above normal levels?
- Which quadrants of the city take longest to recover?
- Does the same snowfall cause more incidents in colder temperatures?
## Data
 
| Source | Key fields |
|---|---|
| [City of Calgary – Traffic Incidents](https://data.calgary.ca/Transportation-Transit/Traffic-Incidents/35ra-9556/about_data) | Incident Info, Description, Start time, Quadrant |
| [Environment Canada – Calgary Intl daily weather](https://climate.weather.gc.ca/) | Max/Min/Mean Temp, Total Snow, Total Precip, Snow on Grnd |
 
## Tools
 
Python (pandas), SQL (DuckDB), Streamlit

## Author

**Jham Alyia Manalaysay** · Mathematics, Concentration in Applied and Computational Mathematics (Minor in Computer Science)
University of Calgary
# Flight Data Pipeline

End-to-end project that ingests live (current flight states and flight information) and historical flight data (arrivals and departures).
Stores in AWS S3, queries the data with Athena, and displayed in a Streamlit Dashboard.
---

## Architecture

```
OpenSky API -> Python Ingestion Scripts -> AWS S3 (raw JSON) -> AWS Athena (SQL queries) -> Streamlit Dashboard
```

**Ingestion scripts:**
- `all_flights_ingest.py` — fetches live airborne flights every 2 hours over a rolling window
- `arrivals_departures.py` — fetches yesterday's arrivals and departures daily for 8 airports
- `states_ingest.py` — fetches real time state vectors (latitude/longitude, altitude, speed) every 15 minutes

**Storage:** Raw JSON written to S3 with the following folder structure (`raw/all_flights/`, `raw/arrivals/`, `raw/departures/`, `raw/states/`)

**Query layer:** AWS Athena reads directly from S3

**Dashboard:** Streamlit app with KPI cards, bar charts, route analysis, heatmap, and a live flight map

## Stack

| Layer | Tool |
|---|---|
| Ingestion | Python, urllib, OpenSky Network API |
| Storage | AWS S3 |
| Query | AWS Athena |
| Visualization | Streamlit, Plotly |
---
## Tradeoffs & Design Decisions

**urllib over requests**
Initially I used the `requests` library since I was more familiar with it. When I tried to deploy on AWS Lambda, packaging `requests` for a Linux runtime from a Windows machine was difficult. Switched to `urllib` from the Python standard library.

**Local scheduling over AWS Lambda**
Designed the pipeline for AWS Lambda triggered by Eventbridge. Initially I had only read the endpoints section of the OpenSky API docs.  When my ingestion scripts in lambda were not working, I found that the OpenSky Network  blocks cloud provider IP ranges to prevent automated abuse. Currently the scripts are run locally using Windows Task Scheduler.

**Overwrite vs. append for live flights**
Initially I was creating new timestamped json files each time the all_flight_ingest.py file was run.  Changed so that
`all_flights` and `states` use a fixed S3 key (`latest_flights.json`) so files are overwritten on each run rather than accumulated. Historical arrivals and departures are dated (`YYYY-MM-DD.json`) to preserve daily records if the project is expanded for daily analysis.

**Athena over a traditional database**
Chose Athena since it is serverless and directly queries the JSON files in S3; no need for a database to provision and manage.

Tradeoff: query latency is higher than a traditional DB.

**Newline-delimited JSON**
OpenSky returns arrays of flight objects. Initially wrote raw arrays to S3, which caused Athena parsing errors. Switched to newline-delimited JSON (one object per line), which is the format Athena's JSON SerDe expects.
---



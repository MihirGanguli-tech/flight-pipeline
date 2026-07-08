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

**Storage:** Raw JSON written to S3 with a partitioned folder structure (`raw/all_flights/`, `raw/arrivals/`, `raw/departures/`, `raw/states/`)

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


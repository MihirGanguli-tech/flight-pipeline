import time
import urllib.request
import urllib.parse
import json
import boto3
import os
from ingestion.opensky_client import TokenManager
from ingestion.all_flights_ingest import fetch,tokens,airports
from datetime import datetime, timedelta


def lambda_handler(event, context):
    yesterday = datetime.now() - timedelta(days=1)
    day_start = int(datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0).timestamp())
    day_end = int(datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59).timestamp())

    end = int(time.time())
    begin = end - 7200


    arrivals = []
    departures = []

    for airport in airports:
        arrivals.append(fetch(
            "https://opensky-network.org/api/flights/arrival",
            tokens.headers(),
            {"airport": airport, "begin": day_start, "end": day_end}
        ))
        departures.append(fetch(
            "https://opensky-network.org/api/flights/departure",
            tokens.headers(),
            {"airport": airport, "begin": day_start, "end": day_end}
        ))

    print("arrivals:", len(arrivals))
    print("departures:", len(departures))

    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket="mihir-opensky-bucket",
        Key=f"raw/arrivals/{yesterday.strftime('%Y-%m-%d')}.json",
        Body='\n'.join(json.dumps(flight) for airport in arrivals for flight in airport)
    )

    s3_client.put_object(
        Bucket="mihir-opensky-bucket",
        Key=f"raw/departures/{yesterday.strftime('%Y-%m-%d')}.json",
        Body='\n'.join(json.dumps(flight) for airport in departures for flight in airport)
    )

    s3_client.put_object(
    Bucket="mihir-opensky-bucket",
    Key="raw/last_updated_arrivals_departures.json",
    Body=json.dumps({"last_updated_arrivals_departures": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    )

if __name__ == "__main__":
    lambda_handler(None, None)
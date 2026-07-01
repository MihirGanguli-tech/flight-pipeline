import time
import urllib.request
import urllib.parse
import json
import boto3
import os
from opensky_client import TokenManager
from datetime import datetime, timedelta

tokens = TokenManager()

airports = ["KDEN", "KLAX", "KJFK", "KIAD", "KDFW", "KORD", "KATL", "KMIA"]

def fetch(url, headers, params):
    full_url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full_url, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def lambda_handler(event, context):
    yesterday = datetime.now() - timedelta(days=1)
    day_start = int(datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0).timestamp())
    day_end = int(datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59).timestamp())

    end = int(time.time())
    begin = end - 7200

    all_flights = fetch(
        "https://opensky-network.org/api/flights/all",
        tokens.headers(),
        {"begin": begin, "end": end}
    )

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

    print("live flights:", len(all_flights))
    print("arrivals:", len(arrivals))
    print("departures:", len(departures))

    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket="mihir-opensky-bucket",
        Key=f"raw/all_flights/{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json",
        Body='\n'.join(json.dumps(flight) for flight in all_flights)
    )

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

if __name__ == "__main__":
    lambda_handler(None, None)
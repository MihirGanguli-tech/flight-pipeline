import time
import urllib.request
import urllib.parse
import json
import boto3
import os
from ingestion.opensky_client import TokenManager
from datetime import datetime, timedelta

tokens = TokenManager()

# 8 most busy US airports
airports = ["KDEN", "KLAX", "KJFK", "KIAD", "KDFW", "KORD", "KATL", "KMIA"]

def fetch(url, headers, params):
    full_url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full_url, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

#Entry point for AWS lambda
def lambda_handler(event, context):
    yesterday = datetime.now() - timedelta(days=1)
    day_start = int(datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0).timestamp())
    day_end = int(datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59).timestamp())

    #current time 
    end = int(time.time())
    #2 hrs previous timestamp
    begin = end - 7200

    all_flights = fetch(
        "https://opensky-network.org/api/flights/all",
        tokens.headers(),
        {"begin": begin, "end": end}
    )

    

    print("live flights:", len(all_flights))
 

    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket="mihir-opensky-bucket",
        Key=f"raw/all_flights/latest_flights.json",
        Body='\n'.join(json.dumps(flight) for flight in all_flights) # new line for each live flight 
    )
    #All flights last updated timestamp; will be displayed in dashboard
    s3_client.put_object(
    Bucket="mihir-opensky-bucket",
    Key="raw/last_updated_flights.json",
    Body=json.dumps({"last_updated_flights": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    )


if __name__ == "__main__":
    lambda_handler(None, None)
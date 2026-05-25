import time
import requests
from ingestion.opensky_client import TokenManager
from datetime import datetime, timedelta
import boto3
import json

tokens = TokenManager()


#ICAO codes for busy US airports
airports = ["KDEN", "KLAX", "KJFK", "KIAD", "KDFW", "KORD", "KATL", "KMIA"]




def lambda_handler(event, context):

    # only able to get departures for the day before the current day, not real time

    yesterday = datetime.now() - timedelta(days=1)
    day_start = int(datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0).timestamp())
    day_end = int(datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59).timestamp())

    #fetch flights on 2 hour rolling window, 7200 seconds
    end = int(time.time())
    begin = end -7200

    all_flights = requests.get(
        "https://opensky-network.org/api/flights/all",
        headers = tokens.headers(),
        params = {
            "begin": begin,
            "end": end
        }).json()

    arrivals = []
    departures = []

    for airport in airports:
        #get arrivals and departures for each airport in the list, append to arrival and departure list for all airports

        all_arrivals = requests.get(
            "https://opensky-network.org/api/flights/arrival",
            headers = tokens.headers(),
            params = {
                "airport": airport,
                "begin": day_start,
                "end": day_end
            })
        all_departures = requests.get(
            "https://opensky-network.org/api/flights/departure",
            headers = tokens.headers(),
            params = {
                "airport": airport,
                "begin": day_start,
                "end": day_end
            })
        arrivals.append(all_arrivals.json())
        departures.append(all_departures.json())
    
    print("live flights:", len(all_flights))
    print("arrivals:", len(arrivals))
    print("departures:", len(departures)) 

    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket="mihir-opensky-bucket",
        Key=f"raw/all_flights/{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json",
        Body=json.dumps(all_flights)
    )

    s3_client.put_object(
        Bucket="mihir-opensky-bucket",
        Key=f"raw/arrivals/{yesterday.strftime('%Y-%m-%d')}.json",
        Body=json.dumps(arrivals)
    )

    s3_client.put_object(
        Bucket="mihir-opensky-bucket",
        Key=f"raw/departures/{yesterday.strftime('%Y-%m-%d')}.json",
        Body=json.dumps(departures)
        )
    

 
        
if __name__ == "__main__":
    lambda_handler(None, None)
    
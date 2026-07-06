import time
import urllib.request
import urllib.parse
import json
import boto3
import os
from ingestion.opensky_client import TokenManager
from ingestion.all_flights_ingest import fetch,tokens,airports
from datetime import datetime, timedelta

#Entry point for AWS lambda
def lambda_handler(event, context):
    yesterday = datetime.now() - timedelta(days=1)
    day_start = int(datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0).timestamp())
    day_end = int(datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59).timestamp())

    #current time
    end = int(time.time())

    #15 minutes before, update states vectors every 15 mins
    begin = end - 900

    response = fetch(
    "https://opensky-network.org/api/states/all",
    tokens.headers(),

        #bounding state vectors to only fetch for flights in the US airspace
        {
        "lamin": 24.5,
        "lamax": 49.5,
        "lomin": -125,
        "lomax": -66
        }
    )
    all_states = response["states"]
    timestamp = response["time"]



    print(f"state vectors fetched for {len(all_states)} flights")

    #AWS Athena not able to create table from arrays, need to convert to dict, and map each value of the array to the corresponding keys
    state_vector_keys = [
        "icao24", "callsign", "origin_country", "time_position", 
        "last_contact", "longitude", "latitude", 
        "baro_altitude", "on_ground", "velocity", "true_track",
        "vertical_rate", "sensors", "geo_altitude", "squawk", "spi", 
        "position_source", "category"
        ]
    state_vector_dict = dict.fromkeys(state_vector_keys)

    states_as_dicts = []
    for state in all_states:
        state_dict = {}

        for i in range(len(state_vector_keys)):

            if i < len(state):
                state_dict[state_vector_keys[i]] = state[i]
            else: 
                None
        states_as_dicts.append(state_dict)






    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket="mihir-opensky-bucket",
        Key=f"raw/states/latest_flight_states.json",
        Body='\n'.join(json.dumps(flight) for flight in states_as_dicts) #new line for each state vector
    )
    #All flights last updated timestamp; will be displayed in dashboard
    s3_client.put_object(
    Bucket="mihir-opensky-bucket",
    Key="raw/last_updated_states.json",
    Body=json.dumps({"last_updated_states": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    )


if __name__ == "__main__":
    lambda_handler(None, None)
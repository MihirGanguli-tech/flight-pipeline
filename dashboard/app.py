from constants import AIRPORTS
import streamlit as st
import pandas as pd
import awswrangler as wr
import plotly.express as px



def run_query(sql):
    return wr.athena.read_sql_query(
        sql=sql,
        database="flights",
        s3_output="s3://mihir-opensky-bucket/athena-results/"
    )



#title
st.set_page_config(page_title="Flight Dashboard", layout="wide")
st.title("US Flight Dashboard")



st.sidebar.header("Filters")
selected_airport = st.sidebar.selectbox("Select Airport", list(AIRPORTS.keys()))

df_routes = run_query("""
        SELECT CONCAT(estarrivalairport, '->', estdepartureairport) as route,  COUNT(*) as numFlights
        FROM arrivals
        WHERE estdepartureairport IS NOT NULL
        AND estarrivalairport IS NOT NULL
        AND estarrivalairport != estdepartureairport
        GROUP BY estdepartureairport, estarrivalairport
        ORDER BY numFlights DESC
        LIMIT 10;                             
""")

df_all_flights = run_query("""             
            SELECT COUNT(*) as total_flights FROM all_flights;
""")

df_busiest_airports = run_query("""
   Select estarrivalairport,Count(estarrivalairport) as arrivals 
FROM arrivals 
GROUP BY estarrivalairport 
ORDER BY arrivals DESC;                              
                                
                                
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Live Flights", df_all_flights["total_flights"][0])

with col2:
    st.metric("Busiest Airport", df_busiest_airports["estarrivalairport"][0])

with col3:
    st.metric("Most Popular Route", df_routes["route"][0])

#most common destination airports


st.write(df_busiest_airports)

#bar chart of most busy airports by arrivals
fig = px.bar(df_busiest_airports, x="estarrivalairport", y="arrivals", title="Busiest Airports", )
st.plotly_chart(fig)


df_routes = run_query("""
        SELECT CONCAT(estarrivalairport, '->', estdepartureairport) as route,  COUNT(*) as numFlights
        FROM arrivals
        WHERE estdepartureairport IS NOT NULL
        AND estarrivalairport IS NOT NULL
        AND estarrivalairport != estdepartureairport
        GROUP BY estdepartureairport, estarrivalairport
        ORDER BY numFlights DESC
        LIMIT 10;                             
""")
st.write(df_routes)
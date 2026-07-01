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

#most common destination airports
df_airports = run_query("""
    SELECT estarrivalairport, COUNT(*) as arrivals
    FROM arrivals
    GROUP BY estarrivalairport
    ORDER BY arrivals DESC
""")

st.write(df_airports)

#bar chart of most busy airports by arrivals
fig = px.bar(df_airports, x="estarrivalairport", y="arrivals", title="Busiest Airports", )
st.plotly_chart(fig)


df_routes = run_query("""
        SELECT CONCAT(estarrivalairport, '->', estdepartureairport) as route,  COUNT(*) as numFlights
        FROM arrivals
        WHERE estdepartureairport IS NOT NULL
        AND estarrivalairport IS NOT NULL
        GROUP BY estdepartureairport, estarrivalairport
        ORDER BY numFlights DESC
        LIMIT 10;                             
""")
st.write(df_routes)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from datetime import date

st.set_page_config(page_title="ClimCalamity — Climate Risk Prediction Dashboard", layout="wide")

st.title("🌍 ClimCalamity — AI-Powered Climate Risk Predictor")
st.markdown("Predict droughts, wildfires, and other natural calamities using satellite-derived indicators and AI models.")

# --- Sidebar controls ---
st.sidebar.header("Control Panel")
start_date = st.sidebar.date_input("Start Date", date(2024, 1, 1))
end_date = st.sidebar.date_input("End Date", date.today())
model_choice = st.sidebar.selectbox("Select AI Model", ["XGBoost", "Random Forest", "LSTM (time-series)"])
region = st.sidebar.selectbox("Region", ["Global", "India", "USA", "Africa", "Australia"])

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Predictions"):
    st.session_state['fetch'] = True

# --- Placeholder for backend data ---
if 'fetch' in st.session_state:
    st.info(f"Fetching predictions for {region} using {model_choice} model...")
    try:
        # Fetch real satellite-derived climate data from NASA POWER API
try:
    lat, lon = 20.0, 78.0  # Center of India; you can later link to map clicks
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters=T2M,PRECTOT,RH2M&community=AG"
        f"&longitude={lon}&latitude={lat}"
        f"&start={start_date.strftime('%Y%m%d')}&end={end_date.strftime('%Y%m%d')}&format=JSON"
    )
    resp = requests.get(url)
    data_json = resp.json()['properties']['parameter']

    df = pd.DataFrame({
        'date': pd.date_range(start=start_date, end=end_date),
        'temperature': list(data_json['T2M'].values()),
        'precipitation': list(data_json['PRECTOT'].values()),
        'humidity': list(data_json['RH2M'].values())
    })

    # Simple mock “risk” calculations (replace with ML model later)
    df['drought_risk'] = 1 - (df['precipitation'] / df['precipitation'].max())
    df['fire_risk'] = (df['temperature'] / df['temperature'].max()) * (1 - df['humidity'] / 100)

    # Add location info for map plotting
    df['lat'] = lat + np.random.uniform(-1, 1, len(df))
    df['lon'] = lon + np.random.uniform(-1, 1, len(df))

    st.session_state['predictions'] = df

except Exception as e:
    st.error(f\"Error fetching real data: {e}\")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

# --- Map and Charts ---
if 'predictions' in st.session_state:
    data = st.session_state['predictions']

    st.subheader("🗺️ Climate Risk Map")
    fig = px.scatter_mapbox(
        data,
        lat='lat', lon='lon',
        color='drought_risk', size='fire_risk',
        color_continuous_scale='YlOrRd', size_max=20, zoom=2,
        hover_data=['date', 'drought_risk', 'fire_risk']
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Time-Series Indicators (Sample)")
    # Simulated time-series for a random coordinate
    sample = data.iloc[0]
    ts = pd.DataFrame({
        'date': pd.date_range(start=start_date, end=end_date, periods=30),
        'ndvi': np.random.rand(30),
        'soil_moisture': np.random.rand(30),
        'precipitation': np.random.rand(30)
    })
    fig2 = px.line(ts, x='date', y=['ndvi', 'soil_moisture', 'precipitation'], title=f"Time-Series at Lat {sample.lat:.2f}, Lon {sample.lon:.2f}")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("💾 Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download Predictions CSV"):
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button("Click to Download", csv, "climate_predictions.csv", "text/csv")
    with col2:
        if st.button("Save to Database"):
            st.success("✅ Data saved (simulation — connect to backend later)")

else:
    st.info("Use the sidebar to set parameters and click **Refresh Predictions** to start.")

st.markdown("---")
st.caption("Backend expectations: endpoints `/api/predictions` and `/api/timeseries` should return risk scores and satellite features.")

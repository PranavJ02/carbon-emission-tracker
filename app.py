"""
app.py - Streamlit Carbon Footprint Dashboard (optional)
"""

import streamlit as st
import pandas as pd
import datetime as dt
import os
import plotly.express as px

CSV_FILE = "data.csv"

EMISSION_FACTORS = {
    "car": 0.21, "bike": 0.08, "bus": 0.10,
    "electricity": 0.85, "meat_meal": 5.0, "veg_meal": 1.5
}

def ensure_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "Date", "Car_km", "Bike_km", "Bus_km", "Electricity_kwh", "Meat_meals", "Veg_meals",
            "Car_emission", "Bike_emission", "Bus_emission", "Electricity_emission", "Food_emission", "Total_emission"
        ])
        df.to_csv(CSV_FILE, index=False)

def calculate_emissions(car_km, bike_km, bus_km, elec_kwh, meat_meals, veg_meals):
    car_em = car_km * EMISSION_FACTORS["car"]
    bike_em = bike_km * EMISSION_FACTORS["bike"]
    bus_em = bus_km * EMISSION_FACTORS["bus"]
    elec_em = elec_kwh * EMISSION_FACTORS["electricity"]
    food_em = meat_meals * EMISSION_FACTORS["meat_meal"] + veg_meals * EMISSION_FACTORS["veg_meal"]
    total = car_em + bike_em + bus_em + elec_em + food_em
    return round(car_em,3), round(bike_em,3), round(bus_em,3), round(elec_em,3), round(food_em,3), round(total,3)

def append_row(date, car_km, bike_km, bus_km, elec_kwh, meat_meals, veg_meals, car_em, bike_em, bus_em, elec_em, food_em, total):
    ensure_csv()
    df = pd.read_csv(CSV_FILE)
    new = {
        "Date": date.isoformat(),
        "Car_km": car_km, "Bike_km": bike_km, "Bus_km": bus_km, "Electricity_kwh": elec_kwh,
        "Meat_meals": meat_meals, "Veg_meals": veg_meals,
        "Car_emission": car_em, "Bike_emission": bike_em, "Bus_emission": bus_em,
        "Electricity_emission": elec_em, "Food_emission": food_em, "Total_emission": total
    }
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

st.set_page_config(page_title="Carbon Footprint Tracker", layout="wide")
st.title("🌱 Carbon Footprint Calculator & Tracker")

# Sidebar inputs
st.sidebar.header("Log today's data")
date = st.sidebar.date_input("Date", dt.date.today())
car_km = st.sidebar.number_input("Car km", min_value=0.0, value=0.0, step=0.1)
bike_km = st.sidebar.number_input("Bike km", min_value=0.0, value=0.0, step=0.1)
bus_km = st.sidebar.number_input("Bus km", min_value=0.0, value=0.0, step=0.1)
elec_kwh = st.sidebar.number_input("Electricity (kWh)", min_value=0.0, value=0.0, step=0.1)
meat_meals = st.sidebar.number_input("Non-veg meals", min_value=0, value=0, step=1)
veg_meals = st.sidebar.number_input("Veg meals", min_value=0, value=0, step=1)

if st.sidebar.button("Log Entry"):
    car_em, bike_em, bus_em, elec_em, food_em, total = calculate_emissions(
        car_km, bike_km, bus_km, elec_kwh, meat_meals, veg_meals
    )
    append_row(date, car_km, bike_km, bus_km, elec_kwh, meat_meals, veg_meals,
               car_em, bike_em, bus_em, elec_em, food_em, total)
    st.sidebar.success(f"Logged — total {total} kg CO2")
    st.rerun()

st.subheader("Estimate (preview)")
car_em, bike_em, bus_em, elec_em, food_em, total = calculate_emissions(car_km, bike_km, bus_km, elec_kwh, meat_meals, veg_meals)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Travel (kg CO2)", f"{round(car_em + bike_em + bus_em,3)}")
c2.metric("Electricity (kg CO2)", f"{elec_em}")
c3.metric("Food (kg CO2)", f"{food_em}")
c4.metric("Total (kg CO2)", f"{total}")

# Load existing data
ensure_csv()
df = pd.read_csv(CSV_FILE)
if df.empty:
    st.info("No entries yet. Use sidebar to log today's data.")
else:
    df["Date"] = pd.to_datetime(df["Date"])
    st.subheader("Trend (last 30 days)")
    recent = df[df["Date"] >= (pd.to_datetime(dt.date.today()) - pd.Timedelta(days=29))]
    agg = recent.groupby(recent["Date"].dt.date)["Total_emission"].sum().reset_index()
    fig = px.line(agg, x="Date", y="Total_emission", markers=True, title="Daily total CO2")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Breakdown (last 7 days)")
    last7 = df[df["Date"] >= (pd.to_datetime(dt.date.today()) - pd.Timedelta(days=6))]
    sums = {
        "Travel": last7[["Car_emission", "Bike_emission", "Bus_emission"]].sum().sum(),
        "Electricity": last7["Electricity_emission"].sum(),
        "Food": last7["Food_emission"].sum()
    }
    breakdown = pd.DataFrame(list(sums.items()), columns=["Category", "kg CO2"])
    st.table(breakdown)

    st.subheader("All logged entries")
    st.dataframe(df.sort_values("Date", ascending=False))

    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "data.csv", "text/csv")


import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Pharma Digital Twin - What-If Analysis", layout="wide")
st.title("💊 Pharma Formulation Unit Digital Twin – What-If Scenario Analysis")

# Emission factors (editable in sidebar)
st.sidebar.header("Emission Factors (kgCO2e/unit)")
ef_energy = st.sidebar.number_input("Energy (per kWh)", value=0.9)
ef_steam = st.sidebar.number_input("Steam (per kg)", value=0.07)
ef_lactose = st.sidebar.number_input("Lactose (per kg)", value=1.5)
ef_ethanol = st.sidebar.number_input("Ethanol (per kg)", value=3.0)
ef_gelatin = st.sidebar.number_input("Gelatin (per kg)", value=2.0)
ef_api = st.sidebar.number_input("API (per kg)", value=5.0)
ef_solvent = st.sidebar.number_input("Solvent (per kg)", value=4.0)
ef_packaging = st.sidebar.number_input("Packaging (per kg)", value=2.0)
ef_filter_media = st.sidebar.number_input("Filter Media (per kg)", value=1.8)
ef_cleaning_agent = st.sidebar.number_input("Cleaning Agent (per kg)", value=2.5)
ef_hvac = st.sidebar.number_input("HVAC (per kWh)", value=0.7)
ef_wastewater = st.sidebar.number_input("Wastewater (per kg)", value=0.2)
ef_compressed_air = st.sidebar.number_input("Compressed Air (per kWh)", value=0.95)

emission_factors = {
    "energy": ef_energy,
    "steam": ef_steam,
    "lactose": ef_lactose,
    "ethanol": ef_ethanol,
    "gelatin": ef_gelatin,
    "api": ef_api,
    "solvent": ef_solvent,
    "packaging": ef_packaging,
    "filter_media": ef_filter_media,
    "cleaning_agent": ef_cleaning_agent,
    "hvac": ef_hvac,
    "wastewater": ef_wastewater,
    "compressed_air": ef_compressed_air,
}

# What-if controls – Process Parameters
st.sidebar.header("Process Parameters (What-If)")
n_batches = st.sidebar.slider("Number of Batches", 10, 200, 100)
batch_size = st.sidebar.slider("Batch Size (kg)", 50, 300, 100)
energy_efficiency = st.sidebar.slider("Energy Efficiency Improvement (%)", 50, 110, 100) / 100
steam_efficiency = st.sidebar.slider("Steam Efficiency Improvement (%)", 50, 110, 100) / 100
hvac_efficiency = st.sidebar.slider("HVAC Efficiency (%)", 50, 110, 100) / 100

# What-if controls – Material Use
lactose_mult = st.sidebar.slider("Lactose Usage Multiplier", 0.8, 1.2, 1.0)
ethanol_mult = st.sidebar.slider("Ethanol Usage Multiplier", 0.8, 1.2, 1.0)
gelatin_mult = st.sidebar.slider("Gelatin Usage Multiplier", 0.8, 1.2, 1.0)
api_mult = st.sidebar.slider("API Usage Multiplier", 0.8, 1.2, 1.0)
solvent_mult = st.sidebar.slider("Solvent Usage Multiplier", 0.8, 1.2, 1.0)

# What-if controls – Product Mix
st.sidebar.header("Product Mix")
pct_tablet = st.sidebar.slider("Tablets (%)", 0, 100, 50)
pct_inhaler = st.sidebar.slider("Inhalers (%)", 0, 100 - pct_tablet, 30)
pct_other = 100 - pct_tablet - pct_inhaler
product_mix = {"tablet": pct_tablet, "inhaler": pct_inhaler, "other": pct_other}

# What-if controls – Scheduling & Cleaning
st.sidebar.header("Scheduling & Cleaning")
cleaning_freq = st.sidebar.slider("Cleaning Frequency (per batch)", 0.2, 1.0, 0.5)
changeover_penalty = st.sidebar.slider("Changeover Penalty (extra cleaning energy multiplier)", 1.0, 2.0, 1.2)

# What-if controls – Regulatory/Cost
st.sidebar.header("Regulatory & Cost")
carbon_price = st.sidebar.slider("Carbon Price ($/ton CO2e)", 0, 200, 50)

# Generate synthetic batch data based on current what-if parameters
np.random.seed(42)
data = []
for i in range(n_batches):
    # Simulate product mix
    r = np.random.rand() * 100
    if r < product_mix["tablet"]:
        product = "tablet"
        lactose_kg = np.random.normal(80, 8) * lactose_mult
        ethanol_kg = np.random.normal(10, 2) * ethanol_mult
        gelatin_kg = np.random.normal(10, 2) * gelatin_mult
        api_kg = np.random.normal(7, 1.5) * api_mult
        solvent_kg = np.random.normal(2, 0.5) * solvent_mult
        packaging_kg = np.random.normal(5, 0.7)
    elif r < product_mix["tablet"] + product_mix["inhaler"]:
        product = "inhaler"
        lactose_kg = np.random.normal(30, 5) * lactose_mult
        ethanol_kg = np.random.normal(25, 4) * ethanol_mult
        gelatin_kg = np.random.normal(7, 1) * gelatin_mult
        api_kg = np.random.normal(4, 1) * api_mult
        solvent_kg = np.random.normal(15, 2) * solvent_mult
        packaging_kg = np.random.normal(8, 1.5)
    else:
        product = "other"
        lactose_kg = np.random.normal(60, 10) * lactose_mult
        ethanol_kg = np.random.normal(15, 3) * ethanol_mult
        gelatin_kg = np.random.normal(10, 2) * gelatin_mult
        api_kg = np.random.normal(3, 1) * api_mult
        solvent_kg = np.random.normal(5, 1) * solvent_mult
        packaging_kg = np.random.normal(6, 0.8)

    batch_energy = np.random.normal(1200, 100) * energy_efficiency
    batch_steam = np.random.normal(280, 40) * steam_efficiency
    batch_hvac = np.random.normal(130, 15) * hvac_efficiency
    filter_media_kg = np.random.normal(3, 0.3)
    cleaning_agent_kg = np.random.normal(6, 0.8) * cleaning_freq
    wastewater_kg = np.random.normal(20, 2) * cleaning_freq
    compressed_air_kWh = np.random.normal(8, 1)
    cleaning_energy = np.random.normal(40, 5) * cleaning_freq * changeover_penalty

    data.append({
        "Batch_ID": i + 1,
        "Product": product,
        "Energy_kWh": batch_energy,
        "Steam_kg": batch_steam,
        "HVAC_kWh": batch_hvac,
        "Lactose_kg": lactose_kg,
        "Ethanol_kg": ethanol_kg,
        "Gelatin_kg": gelatin_kg,
        "API_kg": api_kg,
        "Solvent_kg": solvent_kg,
        "Packaging_kg": packaging_kg,
        "Filter_Media_kg": filter_media_kg,
        "Cleaning_Agent_kg": cleaning_agent_kg,
        "Wastewater_kg": wastewater_kg,
        "Compressed_Air_kWh": compressed_air_kWh,
        "Cleaning_Energy_kWh": cleaning_energy,
    })

df = pd.DataFrame(data)

# GHG Emissions Calculation
def calculate_ghg(row):
    ef = emission_factors
    ghg = (
        row["Energy_kWh"] * ef["energy"] +
        row["Steam_kg"] * ef["steam"] +
        row["HVAC_kWh"] * ef["hvac"] +
        row["Lactose_kg"] * ef["lactose"] +
        row["Ethanol_kg"] * ef["ethanol"] +
        row["Gelatin_kg"] * ef["gelatin"] +
        row["API_kg"] * ef["api"] +
        row["Solvent_kg"] * ef["solvent"] +
        row["Packaging_kg"] * ef["packaging"] +
        row["Filter_Media_kg"] * ef["filter_media"] +
        row["Cleaning_Agent_kg"] * ef["cleaning_agent"] +
        row["Wastewater_kg"] * ef["wastewater"] +
        row["Compressed_Air_kWh"] * ef["compressed_air"] +
        row["Cleaning_Energy_kWh"] * ef["energy"]
    )
    return ghg

df["GHG_kgCO2e"] = df.apply(calculate_ghg, axis=1)
df["Carbon_Cost_$"] = df["GHG_kgCO2e"] / 1000 * carbon_price

# Dashboard Outputs
st.metric("Average GHG Emissions (kgCO2e/batch)", f"{df['GHG_kgCO2e'].mean():.2f}")
st.metric("Total GHG Emissions (ton CO2e)", f"{df['GHG_kgCO2e'].sum()/1000:.2f}")
st.metric("Total Carbon Cost ($)", f"{df['Carbon_Cost_$'].sum():.2f}")

st.subheader("GHG Emissions by Batch")
st.line_chart(df.set_index("Batch_ID")["GHG_kgCO2e"])

st.subheader("Breakdown by Product")
st.bar_chart(df.groupby("Product")["GHG_kgCO2e"].mean())

st.subheader("Batch Data (first 20 rows)")
st.dataframe(df.head(20).round(2))

st.markdown("""
**What-if analysis you can perform:**
- Change process parameters (energy, steam, batch size, cleaning frequency)
- Test material substitutions and usage levels
- Adjust product mix (tablets/inhalers/other)
- Test scheduling and cleaning strategies
- Simulate regulatory changes (carbon price)
- See impact on GHG emissions and cost
""")

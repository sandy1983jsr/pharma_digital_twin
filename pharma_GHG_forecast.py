import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Pharma Digital Twin", layout="wide")

# Title
st.title("💊 Pharma Digital Twin: GHG Optimization & Scenario Planning")

# Sidebar - Emission Factors
st.sidebar.header("⚙️ Emission Factors")
ef_energy = st.sidebar.number_input("Energy (kgCO2e/kWh)", value=0.9)
ef_steam = st.sidebar.number_input("Steam (kgCO2e/kg)", value=0.07)
ef_materials = {
    "Lactose": st.sidebar.number_input("Lactose (kgCO2e/kg)", value=1.5),
    "Ethanol": st.sidebar.number_input("Ethanol (kgCO2e/kg)", value=3.0),
    "Gelatin": st.sidebar.number_input("Gelatin (kgCO2e/kg)", value=2.0)
}

# Generate synthetic batch data
np.random.seed(42)
n_batches = 100
df = pd.DataFrame({
    "Batch_ID": range(1, n_batches + 1),
    "Energy_kWh": np.random.normal(1200, 100, n_batches),
    "Steam_kg_per_batch": np.random.normal(300, 40, n_batches),
    "Lactose_kg": np.random.normal(100, 10, n_batches),
    "Ethanol_kg": np.random.normal(20, 5, n_batches),
    "Gelatin_kg": np.random.normal(15, 3, n_batches),
})

# GHG calculation function
def calculate_ghg(df, ef_energy, ef_steam, ef_materials):
    df = df.copy()
    df["GHG_Energy"] = df["Energy_kWh"] * ef_energy
    df["GHG_Steam"] = df["Steam_kg_per_batch"] * ef_steam
    df["GHG_Lactose"] = df["Lactose_kg"] * ef_materials["Lactose"]
    df["GHG_Ethanol"] = df["Ethanol_kg"] * ef_materials["Ethanol"]
    df["GHG_Gelatin"] = df["Gelatin_kg"] * ef_materials["Gelatin"]
    df["GHG_Materials"] = df[["GHG_Lactose", "GHG_Ethanol", "GHG_Gelatin"]].sum(axis=1)
    df["GHG_Total"] = df["GHG_Energy"] + df["GHG_Steam"] + df["GHG_Materials"]
    return df

# Scenario multipliers
scenario_options = {
    "Baseline": (1.0, 1.0, 1.0, 1.0, 1.0),
    "Energy Efficient": (0.9, 1.0, 1.0, 1.0, 1.0),
    "Low Steam": (1.0, 0.8, 1.0, 1.0, 1.0),
    "Green Materials": (1.0, 1.0, 0.95, 0.9, 0.9),
    "Custom": None
}

# Sidebar - Scenario Selector
st.sidebar.header("🧪 Scenario")
scenario = st.sidebar.selectbox("Choose a scenario", list(scenario_options.keys()))

if scenario == "Custom":
    e_mult = st.sidebar.slider("Energy Multiplier", 0.5, 1.5, 1.0)
    s_mult = st.sidebar.slider("Steam Multiplier", 0.5, 1.5, 1.0)
    lac_mult = st.sidebar.slider("Lactose Multiplier", 0.5, 1.5, 1.0)
    eth_mult = st.sidebar.slider("Ethanol Multiplier", 0.5, 1.5, 1.0)
    gel_mult = st.sidebar.slider("Gelatin Multiplier", 0.5, 1.5, 1.0)
else:
    e_mult, s_mult, lac_mult, eth_mult, gel_mult = scenario_options[scenario]

# Apply scenario
df_scenario = df.copy()
df_scenario["Energy_kWh"] *= e_mult
df_scenario["Steam_kg_per_batch"] *= s_mult
df_scenario["Lactose_kg"] *= lac_mult
df_scenario["Ethanol_kg"] *= eth_mult
df_scenario["Gelatin_kg"] *= gel_mult

# Calculate GHG
df_baseline = calculate_ghg(df, ef_energy, ef_steam, ef_materials)
df_scenario = calculate_ghg(df_scenario, ef_energy, ef_steam, ef_materials)

# Display Metrics
col1, col2 = st.columns(2)
col1.metric("📊 Avg GHG Baseline (kgCO2e)", f"{df_baseline['GHG_Total'].mean():.2f}")
col2.metric(f"🔁 Avg GHG ({scenario})", f"{df_scenario['GHG_Total'].mean():.2f}")

# GHG Comparison Chart
st.subheader("📈 GHG Emissions by Batch")
ghg_compare = pd.DataFrame({
    "Batch": df["Batch_ID"],
    "Baseline": df_baseline["GHG_Total"],
    f"{scenario}": df_scenario["GHG_Total"]
}).set_index("Batch")
st.line_chart(ghg_compare)

# Show Data
st.subheader("📋 Scenario Data")
st.dataframe(df_scenario.round(2))

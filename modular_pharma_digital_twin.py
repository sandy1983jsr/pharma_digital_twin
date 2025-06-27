import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Pharma Digital Twin – SCADA, Sequencing, What-If & Optimization", layout="wide")
st.title("Company ABC - Pharma Formulation Unit Digital Twin – SCADA Data, Sequencing, What-If & Optimization")

# --- Emission Factors (editable)
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

# --- Data Source Selection
st.sidebar.header("Data Source")
data_mode = st.sidebar.radio("Choose Data Source", ["Sample Data", "Upload SCADA CSV"])
uploaded_file = st.sidebar.file_uploader("Upload SCADA CSV", type=["csv"]) if data_mode == "Upload SCADA CSV" else None

# --- What-if & Optimization Controls
st.sidebar.header("What-If/Optimization Controls")
n_batches = st.sidebar.slider("Number of Batches (sample data only)", 10, 200, 100)
batch_size = st.sidebar.slider("Batch Size (kg, sample data only)", 50, 300, 100)
energy_efficiency = st.sidebar.slider("Energy Efficiency (%)", 50, 110, 100) / 100
steam_efficiency = st.sidebar.slider("Steam Efficiency (%)", 50, 110, 100) / 100
hvac_efficiency = st.sidebar.slider("HVAC Efficiency (%)", 50, 110, 100) / 100
lactose_mult = st.sidebar.slider("Lactose Usage Multiplier", 0.8, 1.2, 1.0)
ethanol_mult = st.sidebar.slider("Ethanol Usage Multiplier", 0.8, 1.2, 1.0)
gelatin_mult = st.sidebar.slider("Gelatin Usage Multiplier", 0.8, 1.2, 1.0)
api_mult = st.sidebar.slider("API Usage Multiplier", 0.8, 1.2, 1.0)
solvent_mult = st.sidebar.slider("Solvent Usage Multiplier", 0.8, 1.2, 1.0)
pct_tablet = st.sidebar.slider("Tablets (%)", 0, 100, 50)
pct_inhaler = st.sidebar.slider("Inhalers (%)", 0, 100 - pct_tablet, 30)
pct_other = 100 - pct_tablet - pct_inhaler
product_mix = {"tablet": pct_tablet, "inhaler": pct_inhaler, "other": pct_other}
cleaning_freq = st.sidebar.slider("Cleaning Frequency (per batch)", 0.2, 1.0, 0.5)
changeover_penalty = st.sidebar.slider("Changeover Cleaning Penalty", 1.0, 2.0, 1.2)
carbon_price = st.sidebar.slider("Carbon Price ($/ton CO2e)", 0, 200, 50)
optimize_sequence = st.sidebar.checkbox("Optimize Batch Sequence (minimize changeovers)")

# --- Data Load
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("SCADA data loaded!")
    # Expect columns: Batch_ID, Product, Energy_kWh, Steam_kg, Lactose_kg, Ethanol_kg, etc.
    if "Batch_ID" not in df.columns or "Product" not in df.columns:
        st.error("CSV must include 'Batch_ID' and 'Product' columns!")
else:
    np.random.seed(42)
    product_types = ["tablet", "inhaler", "other"]
    batches = []
    for i in range(n_batches):
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
        batches.append({
            "Batch_ID": i + 1,
            "Product": product,
            "Energy_kWh": np.random.normal(1200, 100) * energy_efficiency,
            "Steam_kg": np.random.normal(280, 40) * steam_efficiency,
            "HVAC_kWh": np.random.normal(130, 15) * hvac_efficiency,
            "Lactose_kg": lactose_kg,
            "Ethanol_kg": ethanol_kg,
            "Gelatin_kg": gelatin_kg,
            "API_kg": api_kg,
            "Solvent_kg": solvent_kg,
            "Packaging_kg": packaging_kg,
            "Filter_Media_kg": np.random.normal(3, 0.3),
            "Cleaning_Agent_kg": np.random.normal(6, 0.8) * cleaning_freq,
            "Wastewater_kg": np.random.normal(20, 2) * cleaning_freq,
            "Compressed_Air_kWh": np.random.normal(8, 1),
            "Cleaning_Energy_kWh": np.random.normal(40, 5) * cleaning_freq,
        })
    df = pd.DataFrame(batches)

# --- Sequencing & Changeover logic
df["Prev_Product"] = df["Product"].shift(1, fill_value=df["Product"].iloc[0])
df["Changeover"] = (df["Product"] != df["Prev_Product"]).astype(int)
df["Cleaning_Agent_kg"] *= (1 + (changeover_penalty - 1) * df["Changeover"])

# --- Optimization: Minimize changeovers
if optimize_sequence:
    # Simple optimization: group by product type (can use more advanced algos for real use)
    df = df.sort_values("Product").reset_index(drop=True)
    df["Batch_ID"] = range(1, len(df) + 1)
    # Recalculate sequencing columns
    df["Prev_Product"] = df["Product"].shift(1, fill_value=df["Product"].iloc[0])
    df["Changeover"] = (df["Product"] != df["Prev_Product"]).astype(int)
    df["Cleaning_Agent_kg"] = df["Cleaning_Agent_kg"].values * (1 + (changeover_penalty - 1) * df["Changeover"])
    st.success("Batch sequence optimized to minimize changeovers!")

# --- GHG Emissions Calculation
def calculate_ghg(row):
    ef = emission_factors
    ghg = (
        row.get("Energy_kWh",0) * ef["energy"] +
        row.get("Steam_kg",0) * ef["steam"] +
        row.get("HVAC_kWh",0) * ef["hvac"] +
        row.get("Lactose_kg",0) * ef["lactose"] +
        row.get("Ethanol_kg",0) * ef["ethanol"] +
        row.get("Gelatin_kg",0) * ef["gelatin"] +
        row.get("API_kg",0) * ef["api"] +
        row.get("Solvent_kg",0) * ef["solvent"] +
        row.get("Packaging_kg",0) * ef["packaging"] +
        row.get("Filter_Media_kg",0) * ef["filter_media"] +
        row.get("Cleaning_Agent_kg",0) * ef["cleaning_agent"] +
        row.get("Wastewater_kg",0) * ef["wastewater"] +
        row.get("Compressed_Air_kWh",0) * ef["compressed_air"] +
        row.get("Cleaning_Energy_kWh",0) * ef["energy"]
    )
    return ghg

df["GHG_kgCO2e"] = df.apply(calculate_ghg, axis=1)
df["Carbon_Cost_$"] = df["GHG_kgCO2e"] / 1000 * carbon_price

# --- Dashboard Outputs
col1, col2, col3 = st.columns(3)
col1.metric("Average GHG Emissions (kgCO2e/batch)", f"{df['GHG_kgCO2e'].mean():.2f}")
col2.metric("Total GHG Emissions (ton CO2e)", f"{df['GHG_kgCO2e'].sum()/1000:.2f}")
col3.metric("Total Carbon Cost ($)", f"{df['Carbon_Cost_$'].sum():.2f}")

st.subheader("GHG Emissions by Batch")
st.line_chart(df.set_index("Batch_ID")["GHG_kgCO2e"])

st.subheader("Breakdown by Product")
st.bar_chart(df.groupby("Product")["GHG_kgCO2e"].mean())

st.subheader("Batch Data (first 20 rows)")
st.dataframe(df.head(20).round(2))

st.subheader("Changeover Analysis")
st.write(f"Total changeovers: {df['Changeover'].sum()} (sequence impacts cleaning and emissions)")

st.markdown("""
- **Upload SCADA/process CSVs or use sample data**
- **Model impact of batch/product sequencing on GHG/resource use**
- **Visualize and optimize batch scheduling for cost and emissions**
- **Use sidebar controls for what-if scenario analysis**
- **All calculations update live with your choices and data**
- ** Created by Sandeep Kumar Mohanty
""")

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit page setup
st.set_page_config(layout="wide")
st.title("🧪 Pharma Digital Twin - Anomaly Detection Dashboard")

# Sidebar: Load data
st.sidebar.header("Step 1: Load Data")
sample_data = st.sidebar.checkbox("Use Sample Pharma Batch Data")

if sample_data:
    # Generate sample data
    np.random.seed(42)
    data = pd.DataFrame({
        "Batch_ID": range(1, 101),
        "Energy_kWh": np.random.normal(1200, 100, 100),
        "GHG_kgCO2": np.random.normal(150, 20, 100),
        "Material_Yield_%": np.random.normal(92, 3, 100),
        "Steam_kg_per_batch": np.random.normal(300, 40, 100),
        "Downtime_Minutes_By_Cause": np.random.normal(20, 10, 100),
        "Batch_Cycle_Time_Minutes": np.random.normal(250, 20, 100)
    })

    # Inject anomalies
    data.loc[10, "Steam_kg_per_batch"] += 200
    data.loc[25, "Downtime_Minutes_By_Cause"] += 80
    data.loc[70, "Batch_Cycle_Time_Minutes"] += 100
    data.loc[33, "Energy_kWh"] += 400
    data.loc[67, "Material_Yield_%"] -= 15
else:
    uploaded = st.sidebar.file_uploader("Upload CSV File", type=["csv"])
    if uploaded:
        data = pd.read_csv(uploaded)

# If data is loaded, proceed
if 'data' in locals():
    # Show dataset
    st.subheader("📊 Batch Resource KPI Data")
    st.dataframe(data)

    # Anomaly detection using Isolation Forest
    st.subheader("⚠️ Anomaly Detection")

    features = [
        "Energy_kWh", "GHG_kgCO2", "Material_Yield_%",
        "Steam_kg_per_batch", "Downtime_Minutes_By_Cause", "Batch_Cycle_Time_Minutes"
    ]

    model = IsolationForest(contamination=0.05, random_state=42)
    preds = model.fit_predict(data[features])
    data["Anomaly"] = preds
    data["Anomaly_Flag"] = data["Anomaly"].map({1: "Normal", -1: "Anomalous"})

    # Show detected anomalies
    st.markdown("### 🔬 Detected Anomalies")
    st.dataframe(data[data["Anomaly_Flag"] == "Anomalous"])

    # Visual analytics
    st.markdown("### 📈 Anomaly Visualization")
    fig, ax = plt.subplots(2, 3, figsize=(20, 10))
    for i, f in enumerate(features):
        sns.boxplot(x="Anomaly_Flag", y=f, data=data, ax=ax[i // 3][i % 3])
        ax[i // 3][i % 3].set_title(f"{f} Distribution")
    st.pyplot(fig)

    st.info("📌 Tip: Anomalies may indicate inefficient equipment, excessive cleaning, poor scheduling, or formulation issues.")
else:
    st.warning("Upload or use sample data to continue.")

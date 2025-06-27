import streamlit as st
import pandas as pd
import numpy as np

# -- Expanded emission factors --
EMISSION_FACTORS = {
    "energy": 0.9,           # kgCO2e/kWh
    "steam": 0.07,           # kgCO2e/kg
    "234a": 1430.0,          # kgCO2e/kg
    "lactose": 1.5,          # kgCO2e/kg
    "ethanol": 3.0,          # kgCO2e/kg
    "gelatin": 2.0,          # kgCO2e/kg
    "api": 5.0,              # kgCO2e/kg
    "solvent": 4.0,          # kgCO2e/kg
    "hvac": 0.7,             # kgCO2e/kWh
    "wastewater": 0.2,       # kgCO2e/kg
    "packaging": 2.0,        # kgCO2e/kg
    "filter_media": 1.8,     # kgCO2e/kg
    "cleaning_agent": 2.5,   # kgCO2e/kg
    "compressed_air": 0.95,  # kgCO2e/kWh
}

# -- Unit operation base class --
class UnitOperation:
    def __init__(self, name):
        self.name = name
    def calculate_emissions(self, params):
        return 0

class Mixing(UnitOperation):
    def calculate_emissions(self, params):
        energy = params.get("energy_kWh", 0)
        material = params.get("material_kg", 0)
        mat_type = params.get("material_type", "lactose")
        return (energy * EMISSION_FACTORS["energy"] +
                material * EMISSION_FACTORS.get(mat_type, 1.0))

class Filtration(UnitOperation):
    def calculate_emissions(self, params):
        energy = params.get("energy_kWh", 0)
        filter_media = params.get("filter_media_kg", 0)
        return (energy * EMISSION_FACTORS["energy"] +
                filter_media * EMISSION_FACTORS["filter_media"])

class Drying(UnitOperation):
    def calculate_emissions(self, params):
        energy = params.get("energy_kWh", 0)
        steam = params.get("steam_kg", 0)
        return (energy * EMISSION_FACTORS["energy"] +
                steam * EMISSION_FACTORS["steam"])

class Packaging(UnitOperation):
    def calculate_emissions(self, params):
        packaging_mat = params.get("packaging_mat_kg", 0)
        compressed_air = params.get("compressed_air_kWh", 0)
        return (packaging_mat * EMISSION_FACTORS["packaging"] +
                compressed_air * EMISSION_FACTORS["compressed_air"])

class Cleaning(UnitOperation):
    def calculate_emissions(self, params):
        cleaning_agent = params.get("cleaning_agent_kg", 0)
        wastewater = params.get("wastewater_kg", 0)
        energy = params.get("energy_kWh", 0)
        return (cleaning_agent * EMISSION_FACTORS["cleaning_agent"] +
                wastewater * EMISSION_FACTORS["wastewater"] +
                energy * EMISSION_FACTORS["energy"])

class HVAC(UnitOperation):
    def calculate_emissions(self, params):
        hvac_energy = params.get("hvac_kWh", 0)
        return hvac_energy * EMISSION_FACTORS["hvac"]

class StreamGeneration(UnitOperation):
    def calculate_emissions(self, params):
        steam = params.get("steam_kg", 0)
        return steam * EMISSION_FACTORS["steam"]

# -- Advanced process control logic --
def process_control(setpoints, actuals):
    """Simple PID-like control for each parameter."""
    adjustments = {}
    Kp = 0.15
    Ki = 0.02
    Kd = 0.04
    prev_errors = getattr(process_control, "prev_errors", {})
    integrals = getattr(process_control, "integrals", {})
    for key in setpoints:
        error = setpoints[key] - actuals.get(key, setpoints[key])
        prev_error = prev_errors.get(key, 0)
        integrals[key] = integrals.get(key, 0) + error
        derivative = error - prev_error
        adjustments[key] = Kp * error + Ki * integrals[key] + Kd * derivative
        prev_errors[key] = error
    process_control.prev_errors = prev_errors
    process_control.integrals = integrals
    return adjustments

# -- Scheduling logic (simple round-robin assignment) --
def schedule_batches(n_batches, ops):
    schedule = []
    for i in range(n_batches):
        schedule.append({op.name: i % len(ops) for op in ops})
    return schedule

# -- Streamlit UI for scenario simulation --
st.title("🧪 Modular Pharma Digital Twin – Advanced Unit Operations & Emission Sources")

unit_ops = [
    Mixing("Mixing"),
    Filtration("Filtration"),
    Drying("Drying"),
    Packaging("Packaging"),
    Cleaning("Cleaning"),
    HVAC("HVAC"),
    StreamGeneration("StreamGeneration"),
]

n_batches = st.sidebar.number_input("Number of Batches", 1, 200, 25)
np.random.seed(42)
batch_data = []
for i in range(int(n_batches)):
    # Simulated process parameters for each unit operation
    mixing_energy = np.random.normal(200, 20)
    mixing_material = np.random.normal(100, 10)
    filtration_energy = np.random.normal(40, 5)
    filter_media_kg = np.random.normal(3, 0.3)
    drying_energy = np.random.normal(180, 15)
    drying_steam = np.random.normal(120, 12)
    packaging_mat_kg = np.random.normal(12, 1.2)
    compressed_air_kWh = np.random.normal(8, 0.9)
    cleaning_agent_kg = np.random.normal(6, 0.7)
    wastewater_kg = np.random.normal(20, 2)
    cleaning_energy = np.random.normal(30, 3)
    hvac_kWh = np.random.normal(150, 20)
    steam_kg = np.random.normal(300, 30)

    # Actuals and setpoints for process control (simulate some drift)
    setpoints = {"mixing_energy": 200, "drying_energy": 180}
    actuals = {"mixing_energy": mixing_energy, "drying_energy": drying_energy}
    adjustments = process_control(setpoints, actuals)
    mixing_energy += adjustments["mixing_energy"]
    drying_energy += adjustments["drying_energy"]

    batch = {
        "Mixing": {"energy_kWh": mixing_energy, "material_kg": mixing_material, "material_type": "lactose"},
        "Filtration": {"energy_kWh": filtration_energy, "filter_media_kg": filter_media_kg},
        "Drying": {"energy_kWh": drying_energy, "steam_kg": drying_steam},
        "Packaging": {"packaging_mat_kg": packaging_mat_kg, "compressed_air_kWh": compressed_air_kWh},
        "Cleaning": {"cleaning_agent_kg": cleaning_agent_kg, "wastewater_kg": wastewater_kg, "energy_kWh": cleaning_energy},
        "HVAC": {"hvac_kWh": hvac_kWh},
        "StreamGeneration": {"steam_kg": steam_kg},
    }
    batch["Total_Emissions"] = sum(
        op.calculate_emissions(batch[op.name]) for op in unit_ops
    )
    batch_data.append(batch)

df = pd.DataFrame([{
    "Batch": i + 1,
    "Total_Emissions": batch["Total_Emissions"],
    **{op.name + "_Emissions": op.calculate_emissions(batch[op.name]) for op in unit_ops}
} for i, batch in enumerate(batch_data)])

st.dataframe(df.round(2))
st.line_chart(df.set_index("Batch")["Total_Emissions"])

st.markdown("""
**Extend further:**  
- Add more emission factors in `EMISSION_FACTORS`.
- Add or refine process control logic for each unit.
- Replace random data with real process or scheduling data.
- Use advanced scheduling (e.g., priority queues, constraints) as needed.
""")

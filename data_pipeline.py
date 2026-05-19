"""
data_pipeline.py
----------------
Mock data generation pipeline and emission factor engine.
Simulates 52 weekly readings per facility across 2025 with
industry-specific consumption baselines and seasonal multipliers.
"""

import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

from config import (
    EMISSION_FACTORS, SCOPE_MAP, FACILITIES,
    INDUSTRY_CONSUMPTION, INDUSTRY_ENERGY_MIX,
)


@st.cache_data(show_spinner=False)
def generate_mock_data(seed: int = 42) -> pd.DataFrame:
    """
    Generate realistic 2025 weekly energy consumption records for
    20 Indian industrial facilities.

    Design decisions:
    - 52 weekly readings per facility = 1,040 total records
    - Seasonal multiplier peaks in Apr-Jun (summer cooling load)
    - Energy source sampled from industry-specific probability weights
    - Consumption floored at 500 kWh to avoid negative values
    """
    rng = np.random.default_rng(seed)
    records = []

    for fac_id, fac in FACILITIES.items():
        industry = fac["industry"]
        base_mean, base_std = INDUSTRY_CONSUMPTION.get(
            industry, INDUSTRY_CONSUMPTION["default"]
        )
        mix     = INDUSTRY_ENERGY_MIX.get(industry, INDUSTRY_ENERGY_MIX["default"])
        sources = list(mix.keys())
        weights = list(mix.values())

        for week in range(52):
            ts    = datetime(2025, 1, 1) + timedelta(
                weeks=week, hours=int(rng.integers(0, 168))
            )
            # Seasonal load: peaks in summer (month 5), troughs in winter (month 11)
            seasonal    = 1.0 + 0.15 * np.sin((ts.month - 3) * np.pi / 6)
            source      = rng.choice(sources, p=weights)
            consumption = max(500.0, rng.normal(base_mean * seasonal, base_std))

            records.append({
                "Timestamp":         ts,
                "Facility_ID":       fac_id,
                "Facility_Location": fac["city"],
                "State":             fac["state"],
                "Industry":          industry,
                "lat":               fac["lat"],
                "lon":               fac["lon"],
                "Energy_Source":     source,
                "Consumption_kWh":   round(consumption, 2),
                "Scope_Category":    SCOPE_MAP[source],
            })

    df = pd.DataFrame(records)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df


def calculate_emissions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply CEA / GHG Protocol emission factors to raw consumption data.

    Formula:
        CO2e_kg = Consumption_kWh x EF (kg CO2e / kWh)
        MTCO2e  = CO2e_kg / 1000
    """
    df = df.copy()
    df["EF_kg_per_kWh"] = df["Energy_Source"].map(EMISSION_FACTORS)
    df["CO2e_kg"]       = df["Consumption_kWh"] * df["EF_kg_per_kWh"]
    df["MTCO2e"]        = df["CO2e_kg"] / 1_000
    return df

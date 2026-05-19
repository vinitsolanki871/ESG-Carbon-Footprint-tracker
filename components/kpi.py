"""
components/kpi.py
-----------------
Renders the 6-card KPI row:
  Total Emissions · Scope 1 · Scope 2 · MoM Change · Renewable Share · Total GWh
"""

import streamlit as st
import pandas as pd


def render_kpis(df: pd.DataFrame) -> dict:
    """
    Compute and display KPI metrics.

    Returns a dict of computed values so downstream sections
    (insights, simulator) can reuse them without recalculating.
    """
    df = df.copy()
    df["YearMonth"] = df["Timestamp"].dt.to_period("M")

    total_mtco2e  = df["MTCO2e"].sum()
    scope1_total  = df[df["Scope_Category"] == "Scope 1"]["MTCO2e"].sum()
    scope2_total  = df[df["Scope_Category"] == "Scope 2"]["MTCO2e"].sum()
    total_kwh     = df["Consumption_kWh"].sum()
    renewable_kwh = df[df["Energy_Source"].isin(["Solar", "Wind"])]["Consumption_kWh"].sum()
    renewable_pct = (renewable_kwh / total_kwh * 100) if total_kwh > 0 else 0.0

    monthly = df.groupby("YearMonth")["MTCO2e"].sum().sort_index()
    if len(monthly) >= 2:
        mom_change      = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2]) * 100
        mom_label       = f"{mom_change:+.1f}%"
        mom_delta_color = "inverse"
    else:
        mom_label, mom_delta_color = "N/A", "off"

    st.subheader("📊 Key Performance Indicators")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Emissions",    f"{total_mtco2e:,.1f} MTCO2e")
    c2.metric("Scope 1 (Direct)",   f"{scope1_total:,.1f} MTCO2e",  help="Natural Gas + Diesel + Biomass")
    c3.metric("Scope 2 (Indirect)", f"{scope2_total:,.1f} MTCO2e",  help="Grid + Solar + Wind")
    c4.metric("MoM Change",         mom_label, delta=mom_label, delta_color=mom_delta_color)
    c5.metric("Renewable Share",    f"{renewable_pct:.1f}%",         help="Solar + Wind % of total kWh")
    c6.metric("Total Consumption",  f"{total_kwh/1e6:.2f} GWh")

    return dict(
        total_mtco2e=total_mtco2e,
        scope1_total=scope1_total,
        scope2_total=scope2_total,
        total_kwh=total_kwh,
        renewable_pct=renewable_pct,
    )

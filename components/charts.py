"""
components/charts.py
--------------------
All non-map chart sections:
  - Monthly Emissions Trend (bar)
  - Emissions by Industry (bar)
  - Carbon Intensity Benchmarking (horizontal bar)
  - Energy Mix Donut
  - Consumption vs Emissions Scatter
"""

import streamlit as st
import pandas as pd
import altair as alt

from config import CHART_PALETTE


def render_trend_and_industry(df: pd.DataFrame) -> None:
    """Monthly trend (Scope split) + Emissions by Industry side by side."""
    df = df.copy()
    df["YearMonth"] = df["Timestamp"].dt.to_period("M")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 Monthly Emissions Trend")
        monthly_scope = (
            df.groupby(["YearMonth", "Scope_Category"])["MTCO2e"]
            .sum().reset_index()
        )
        monthly_scope["Month"] = monthly_scope["YearMonth"].dt.strftime("%b %Y")
        pivot = monthly_scope.pivot(
            index="Month", columns="Scope_Category", values="MTCO2e"
        ).fillna(0)
        palette = ["#FF6B6B", "#4ECDC4", "#FFE66D"]
        st.bar_chart(pivot, color=palette[:max(1, pivot.shape[1])])

    with col_right:
        st.subheader("🏭 Emissions by Industry")
        ind_em = (
            df.groupby("Industry")["MTCO2e"]
            .sum().sort_values(ascending=False)
            .reset_index().set_index("Industry")
        )
        st.bar_chart(ind_em, color="#00C896")


def render_intensity_benchmark(df: pd.DataFrame) -> None:
    """Horizontal bar chart: carbon intensity per facility (MTCO2e / 1,000 kWh)."""
    st.subheader("⚡ Carbon Intensity Benchmarking")
    st.caption("MTCO2e per 1,000 kWh consumed — lower is better")

    intensity_df = (
        df.groupby(["Facility_Location", "Industry"])
        .agg(Total_MTCO2e=("MTCO2e", "sum"), Total_kWh=("Consumption_kWh", "sum"))
        .reset_index()
    )
    intensity_df["Intensity"] = (
        intensity_df["Total_MTCO2e"] / intensity_df["Total_kWh"]
    ) * 1_000
    intensity_df = intensity_df.sort_values("Intensity", ascending=False)

    chart = (
        alt.Chart(intensity_df)
        .mark_bar()
        .encode(
            x=alt.X("Intensity:Q", title="MTCO2e per 1,000 kWh"),
            y=alt.Y("Facility_Location:N", sort="-x", title=""),
            color=alt.Color(
                "Intensity:Q",
                scale=alt.Scale(scheme="redyellowgreen", reverse=True),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Facility_Location:N", title="City"),
                alt.Tooltip("Industry:N",           title="Industry"),
                alt.Tooltip("Intensity:Q",          title="Intensity",    format=".4f"),
                alt.Tooltip("Total_MTCO2e:Q",       title="Total MTCO2e", format=",.1f"),
                alt.Tooltip("Total_kWh:Q",          title="Total kWh",    format=",.0f"),
            ],
        )
        .properties(height=420)
    )
    st.altair_chart(chart, use_container_width=True)


def render_energy_mix_and_scatter(df: pd.DataFrame) -> None:
    """Energy source donut chart + Consumption vs Emissions scatter."""
    st.subheader("🔋 Energy Mix & Consumption Analysis")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Energy Source Share (by kWh)**")
        mix_df = (
            df.groupby("Energy_Source")["Consumption_kWh"]
            .sum().reset_index()
            .rename(columns={"Consumption_kWh": "Total_kWh"})
        )
        donut = (
            alt.Chart(mix_df)
            .mark_arc(innerRadius=60)
            .encode(
                theta=alt.Theta("Total_kWh:Q"),
                color=alt.Color(
                    "Energy_Source:N",
                    scale=alt.Scale(range=CHART_PALETTE[:len(mix_df)]),
                ),
                tooltip=[
                    alt.Tooltip("Energy_Source:N", title="Source"),
                    alt.Tooltip("Total_kWh:Q",     title="kWh", format=",.0f"),
                ],
            )
            .properties(height=280)
        )
        st.altair_chart(donut, use_container_width=True)

    with col_b:
        st.markdown("**Consumption vs Emissions by Facility**")
        scatter_df = (
            df.groupby(["Facility_Location", "Industry"])
            .agg(Total_kWh=("Consumption_kWh", "sum"), Total_MTCO2e=("MTCO2e", "sum"))
            .reset_index()
        )
        scatter = (
            alt.Chart(scatter_df)
            .mark_circle(size=130)
            .encode(
                x=alt.X("Total_kWh:Q",    title="Total Consumption (kWh)"),
                y=alt.Y("Total_MTCO2e:Q", title="Total Emissions (MTCO2e)"),
                color=alt.Color("Industry:N", legend=alt.Legend(title="Industry")),
                tooltip=[
                    alt.Tooltip("Facility_Location:N", title="City"),
                    alt.Tooltip("Industry:N",           title="Industry"),
                    alt.Tooltip("Total_kWh:Q",          title="kWh",    format=",.0f"),
                    alt.Tooltip("Total_MTCO2e:Q",       title="MTCO2e", format=",.1f"),
                ],
            )
            .properties(height=280)
        )
        st.altair_chart(scatter, use_container_width=True)

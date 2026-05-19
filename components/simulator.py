"""
components/simulator.py
-----------------------
Interactive Net Zero Trajectory Simulator.
Models compound annual emission reductions against the SBTi 1.5°C linear path
from the current filtered baseline to a user-selected target year.
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date


def render_simulator(total_mtco2e: float, start_dt: date, end_dt: date) -> None:
    st.subheader("🎯 Net Zero Trajectory Simulator (2025 → Target Year)")
    st.caption("Adjust the annual reduction rate and target year to model your decarbonisation path vs. SBTi 1.5°C.")

    ctrl_col, chart_col = st.columns([1, 3])

    with ctrl_col:
        annual_pct   = st.slider("Annual Reduction Rate (%)", 1, 30, 10, 1)
        target_year  = st.selectbox("Net Zero Target Year", [2030, 2035, 2040, 2045, 2050])

    # Annualise baseline from filtered date range
    days_active    = max((end_dt - start_dt).days, 1)
    annual_base    = total_mtco2e / (days_active / 365.25)

    years          = list(range(2025, target_year + 1))
    span           = target_year - 2025
    modelled       = [annual_base * ((1 - annual_pct / 100) ** i) for i in range(len(years))]
    sbti_linear    = [annual_base * (1 - i / span) for i in range(len(years))]

    traj_df = pd.DataFrame({
        "Year":     years * 2,
        "MTCO2e":   modelled + sbti_linear,
        "Scenario": ["Your Plan"] * len(years) + ["SBTi 1.5°C Path"] * len(years),
    })

    with chart_col:
        chart = (
            alt.Chart(traj_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("Year:O", title="Year"),
                y=alt.Y("MTCO2e:Q", title="Annual Emissions (MTCO2e)"),
                color=alt.Color(
                    "Scenario:N",
                    scale=alt.Scale(
                        domain=["Your Plan", "SBTi 1.5°C Path"],
                        range=["#00C896", "#FF6B6B"],
                    ),
                ),
                strokeDash=alt.condition(
                    alt.datum.Scenario == "SBTi 1.5°C Path",
                    alt.value([6, 3]),
                    alt.value([0]),
                ),
                tooltip=[
                    alt.Tooltip("Year:O"),
                    alt.Tooltip("MTCO2e:Q",   format=",.1f"),
                    alt.Tooltip("Scenario:N"),
                ],
            )
            .properties(height=320)
        )
        st.altair_chart(chart, use_container_width=True)

        gap = modelled[-1] - sbti_linear[-1]
        if gap > 0.5:
            st.warning(
                f"⚠️ At **{annual_pct}%/yr** you'll have **{gap:,.1f} MTCO2e** "
                f"remaining by {target_year}. Increase the rate or procure carbon offsets."
            )
        else:
            st.success(
                f"✅ At **{annual_pct}%/yr** you are on track to reach net zero by **{target_year}**."
            )

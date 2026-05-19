"""
components/insights.py
----------------------
Dynamic insights panel:
  - Flags the highest-emitting facility
  - Calculates 10% mitigation tonnage
  - Renders a 5-point India-specific mitigation strategy
  - Shows a full drill-down breakdown table in an expander
"""

import streamlit as st
import pandas as pd


def render_insights(df: pd.DataFrame, map_df: pd.DataFrame, total_mtco2e: float) -> None:
    st.subheader("💡 Insights & Recommendations")

    top_row       = map_df.loc[map_df["MTCO2e"].idxmax()]
    top_name      = top_row["Facility_Location"]
    top_mt        = top_row["MTCO2e"]
    top_share     = (top_mt / total_mtco2e * 100) if total_mtco2e > 0 else 0
    mitigation_10 = top_mt * 0.10
    top_source    = df.groupby("Energy_Source")["MTCO2e"].sum().idxmax()
    top_industry  = df.groupby("Industry")["MTCO2e"].sum().idxmax()

    col1, col2 = st.columns(2)

    with col1:
        st.error(f"**🚨 Highest-Emitting Facility: {top_name}**")
        st.markdown(f"""
- Responsible for **{top_mt:,.1f} MTCO2e** ({top_share:.1f}% of total fleet)
- Dominant energy source: **{top_source}**
- Highest-emitting industry sector: **{top_industry}**
- A **10% reduction** at {top_name} = **{mitigation_10:,.1f} MTCO2e** avoided annually
""")

    with col2:
        st.info("**📋 India-Specific 10% Mitigation Framework**")
        st.markdown(f"""
1. **BEE Energy Audit** — Commission a Bureau of Energy Efficiency (BEE) Star Label audit at {top_name} for HVAC, motors, and lighting retrofits.
2. **RPO Compliance** — Meet Renewable Purchase Obligation targets by procuring solar/wind RECs under India's REC mechanism.
3. **PM-KUSUM Solar** — Install rooftop solar under the PM-KUSUM scheme to offset grid electricity (Scope 2) at {top_name}.
4. **CNG/EV Fleet Switch** — Replace diesel logistics vehicles with CNG or EVs aligned with FAME-II incentives.
5. **PAT Scheme Monitoring** — Enrol in the Perform Achieve Trade (PAT) cycle to benchmark and trade energy savings certificates (ESCerts).
""")

    with st.expander("📄 Full Facility Emissions Breakdown"):
        breakdown = (
            df.groupby(["Facility_Location", "State", "Industry", "Scope_Category", "Energy_Source"])
            ["MTCO2e"].sum().reset_index()
            .sort_values("MTCO2e", ascending=False)
            .rename(columns={"MTCO2e": "MTCO2e (MT)"})
        )
        breakdown["MTCO2e (MT)"] = breakdown["MTCO2e (MT)"].round(2)
        st.dataframe(breakdown, use_container_width=True, hide_index=True)

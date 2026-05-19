"""
components/sidebar.py
---------------------
Renders all sidebar filter widgets and returns the active filter state
as a plain dict so app.py can apply them to the dataframe.
"""

import io
import streamlit as st
import pandas as pd


def render_sidebar(df_full: pd.DataFrame) -> dict:
    """
    Render sidebar branding, all filter widgets, and export button.

    Returns
    -------
    dict with keys:
        start_dt, end_dt        — date.date objects
        selected_states         — list[str]
        selected_industries     — list[str]
        selected_locations      — list[str]
        selected_sources        — list[str]
        selected_scopes         — list[str]
        map_layer_mode          — str
        show_arcs               — bool
        export_trigger          — bool
    """
    with st.sidebar:
        # ── Branding ──────────────────────────────
        st.markdown("""
        <div style='text-align:center; padding:12px 0 4px 0;'>
            <span style='font-size:2rem;'>🌿</span><br/>
            <span style='color:#00C896; font-weight:700; font-size:1rem;'>ESG TRACKER</span><br/>
            <span style='color:#4a5568; font-size:0.72rem;'>India · FY 2024</span>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        # ── Data Filters ──────────────────────────
        st.markdown("##### 🔍 Data Filters")

        min_date = df_full["Timestamp"].min().date()
        max_date = df_full["Timestamp"].max().date()
        date_sel = st.date_input(
            "Date Range", value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
        )
        start_dt, end_dt = (date_sel[0], date_sel[1]) if len(date_sel) == 2 else (min_date, max_date)

        selected_states = st.multiselect(
            "State", options=sorted(df_full["State"].unique()),
            default=sorted(df_full["State"].unique()),
        )
        selected_industries = st.multiselect(
            "Industry", options=sorted(df_full["Industry"].unique()),
            default=sorted(df_full["Industry"].unique()),
        )
        selected_locations = st.multiselect(
            "City", options=sorted(df_full["Facility_Location"].unique()),
            default=sorted(df_full["Facility_Location"].unique()),
        )
        selected_sources = st.multiselect(
            "Energy Source", options=sorted(df_full["Energy_Source"].unique()),
            default=sorted(df_full["Energy_Source"].unique()),
        )
        selected_scopes = st.multiselect(
            "Scope Category", options=sorted(df_full["Scope_Category"].unique()),
            default=sorted(df_full["Scope_Category"].unique()),
        )

        # ── Map Options ───────────────────────────
        st.divider()
        st.markdown("##### 🗺️ Map Options")
        map_layer_mode = st.radio(
            "Layer Style",
            ["Bubble + Labels", "3D Column", "Heatmap"],
            index=0,
        )
        show_arcs = st.checkbox("Show Arc Connections", value=True)

        # ── Export ────────────────────────────────
        st.divider()
        st.markdown("**📥 Export**")
        export_trigger = st.button("Prepare CSV Download", use_container_width=True)

    return dict(
        start_dt=start_dt, end_dt=end_dt,
        selected_states=selected_states,
        selected_industries=selected_industries,
        selected_locations=selected_locations,
        selected_sources=selected_sources,
        selected_scopes=selected_scopes,
        map_layer_mode=map_layer_mode,
        show_arcs=show_arcs,
        export_trigger=export_trigger,
    )


def apply_filters(df_full: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply the filter state dict to df_full and return the filtered copy."""
    df = df_full[
        (df_full["Timestamp"].dt.date >= filters["start_dt"]) &
        (df_full["Timestamp"].dt.date <= filters["end_dt"]) &
        (df_full["State"].isin(filters["selected_states"])) &
        (df_full["Industry"].isin(filters["selected_industries"])) &
        (df_full["Facility_Location"].isin(filters["selected_locations"])) &
        (df_full["Energy_Source"].isin(filters["selected_sources"])) &
        (df_full["Scope_Category"].isin(filters["selected_scopes"]))
    ].copy()
    return df


def render_export(df: pd.DataFrame, filters: dict) -> None:
    """Render the CSV download button in the sidebar if export was triggered."""
    if not filters["export_trigger"]:
        return
    export_cols = [
        "Timestamp", "Facility_ID", "Facility_Location", "State", "Industry",
        "Energy_Source", "Scope_Category", "Consumption_kWh",
        "EF_kg_per_kWh", "CO2e_kg", "MTCO2e",
    ]
    buf = io.StringIO()
    df[export_cols].to_csv(buf, index=False)
    st.sidebar.download_button(
        label="⬇️ Download Filtered Data (.csv)",
        data=buf.getvalue(),
        file_name=f"esg_india_{filters['start_dt']}_{filters['end_dt']}.csv",
        mime="text/csv",
        use_container_width=True,
    )

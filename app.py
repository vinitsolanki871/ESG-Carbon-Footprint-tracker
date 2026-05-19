"""
app.py
------
Entry point — orchestrates all components.
Run with:  streamlit run app.py

Project structure:
    app.py                  ← this file (entry point)
    config.py               ← emission factors, facilities, constants
    data_pipeline.py        ← data generation + emission calculation
    components/
        theme.py            ← CSS + header banner
        sidebar.py          ← filters, returns filter state dict
        kpi.py              ← 6-metric KPI row
        charts.py           ← trend, industry, intensity, donut, scatter
        map_view.py         ← PyDeck multi-layer map + risk cards
        insights.py         ← dynamic insights + mitigation framework
        simulator.py        ← net zero trajectory simulator
"""

import warnings
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

import streamlit as st

# ── Page config (must be first Streamlit call) ──
st.set_page_config(
    page_title="ESG Carbon Footprint Tracker",
    page_icon="🌿",
    layout="wide",
)

# ── Internal imports ────────────────────────────
from data_pipeline import generate_mock_data, calculate_emissions
from components.theme     import inject_theme, render_header
from components.sidebar   import render_sidebar, apply_filters, render_export
from components.kpi       import render_kpis
from components.charts    import (
    render_trend_and_industry,
    render_intensity_benchmark,
    render_energy_mix_and_scatter,
)
from components.map_view  import render_map
from components.insights  import render_insights
from components.simulator import render_simulator

# ── 1. Theme & Header ───────────────────────────
inject_theme()
render_header()

# ── 2. Load & process data ──────────────────────
df_full = calculate_emissions(generate_mock_data())

# ── 3. Sidebar filters ──────────────────────────
filters = render_sidebar(df_full)
df      = apply_filters(df_full, filters)

if df.empty:
    st.warning("No data matches the selected filters. Please adjust your selections.")
    st.stop()

# ── 4. KPI Row ──────────────────────────────────
kpis = render_kpis(df)
st.divider()

# ── 5. Trend + Industry Charts ──────────────────
render_trend_and_industry(df)
st.divider()

# ── 6. Map ──────────────────────────────────────
map_df = render_map(df, filters["map_layer_mode"], filters["show_arcs"])
st.divider()

# ── 7. Insights & Recommendations ───────────────
render_insights(df, map_df, kpis["total_mtco2e"])
st.divider()

# ── 8. Carbon Intensity Benchmarking ────────────
render_intensity_benchmark(df)
st.divider()

# ── 9. Energy Mix & Scatter ─────────────────────
render_energy_mix_and_scatter(df)
st.divider()

# ── 10. Net Zero Simulator ──────────────────────
render_simulator(kpis["total_mtco2e"], filters["start_dt"], filters["end_dt"])
st.divider()

# ── 11. CSV Export ──────────────────────────────
render_export(df, filters)

st.caption(
    "Data modelled on CEA 2025 grid EF (0.82 kg CO2e/kWh) · MoPNG fuel factors · "
    "20 Indian industrial cities · SBTi 1.5°C pathway"
)

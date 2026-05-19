"""
components/map_view.py
----------------------
Rich PyDeck map with three switchable layer modes:
  - Bubble + Labels  (ScatterplotLayer + TextLayer)
  - 3D Column        (ColumnLayer extruded)
  - Heatmap          (HeatmapLayer with jittered weighted points)
Plus an optional ArcLayer connecting all facilities to the top emitter.
Facility risk summary cards are rendered beside the map.
"""

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st


def _build_map_df(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-facility stats and compute risk tiers + visual encodings."""
    map_df = (
        df.groupby(["Facility_ID", "Facility_Location", "State", "Industry", "lat", "lon"])
        .agg(
            MTCO2e=("MTCO2e", "sum"),
            Total_kWh=("Consumption_kWh", "sum"),
            Records=("MTCO2e", "count"),
        )
        .reset_index()
    )

    map_df["Intensity"] = (map_df["MTCO2e"] / map_df["Total_kWh"]) * 1_000
    map_df["Share_pct"] = (map_df["MTCO2e"] / map_df["MTCO2e"].sum() * 100).round(1)

    map_max          = max(map_df["MTCO2e"].max(), 1)
    map_df["radius"] = (map_df["MTCO2e"] / map_max) * 90_000
    map_df["elev"]   = (map_df["MTCO2e"] / map_max) * 300_000

    thresh_high = map_df["MTCO2e"].quantile(0.67)
    thresh_mid  = map_df["MTCO2e"].quantile(0.33)

    def _color(v):
        if v >= thresh_high: return [220, 53,  69,  200]
        if v >= thresh_mid:  return [255, 193, 7,   200]
        return                      [0,   200, 150, 200]

    map_df["color"]     = map_df["MTCO2e"].apply(_color)
    map_df["Risk_Tier"] = map_df["MTCO2e"].apply(
        lambda v: "HIGH" if v >= thresh_high else ("MEDIUM" if v >= thresh_mid else "LOW")
    )
    map_df["label"] = (
        map_df["Facility_ID"] + "\n" +
        map_df["MTCO2e"].apply(lambda x: f"{x:,.0f} MT")
    )
    return map_df


def _build_layers(map_df: pd.DataFrame, mode: str, show_arcs: bool) -> list:
    """Construct PyDeck layer list based on selected mode."""
    layers = []
    top_fac  = map_df.loc[map_df["MTCO2e"].idxmax()]
    arc_data = map_df[map_df["Facility_ID"] != top_fac["Facility_ID"]].copy()
    arc_data["target_lat"] = top_fac["lat"]
    arc_data["target_lon"] = top_fac["lon"]

    if mode == "Bubble + Labels":
        layers.append(pdk.Layer(
            "ScatterplotLayer", data=map_df,
            get_position="[lon, lat]", get_radius="radius",
            get_fill_color="color", get_line_color=[255, 255, 255, 60],
            stroked=True, line_width_min_pixels=1,
            pickable=True, auto_highlight=True,
        ))
        layers.append(pdk.Layer(
            "TextLayer", data=map_df,
            get_position="[lon, lat]", get_text="label",
            get_size=13, get_color=[230, 237, 243, 220],
            get_alignment_baseline="'bottom'", get_anchor="'middle'",
        ))

    elif mode == "3D Column":
        layers.append(pdk.Layer(
            "ColumnLayer", data=map_df,
            get_position="[lon, lat]", get_elevation="elev",
            elevation_scale=1, radius=55_000,
            get_fill_color="color",
            pickable=True, auto_highlight=True, extruded=True,
        ))

    elif mode == "Heatmap":
        heat_rows = []
        for _, row in map_df.iterrows():
            for _ in range(int(row["Records"])):
                heat_rows.append({
                    "lat":    row["lat"] + np.random.normal(0, 0.15),
                    "lon":    row["lon"] + np.random.normal(0, 0.15),
                    "weight": row["MTCO2e"] / row["Records"],
                })
        layers.append(pdk.Layer(
            "HeatmapLayer", data=pd.DataFrame(heat_rows),
            get_position="[lon, lat]", get_weight="weight",
            radiusPixels=80, intensity=1, threshold=0.05,
        ))

    if show_arcs and mode != "Heatmap":
        layers.append(pdk.Layer(
            "ArcLayer", data=arc_data,
            get_source_position="[lon, lat]",
            get_target_position="[target_lon, target_lat]",
            get_source_color=[0, 200, 150, 160],
            get_target_color=[220, 53, 69, 160],
            get_width=2,
        ))

    return layers


TOOLTIP = {
    "html": """
    <div style='font-family:Inter,sans-serif; min-width:210px;'>
        <div style='font-size:14px; font-weight:700; color:#00C896; margin-bottom:6px;'>
            {Facility_ID} &mdash; {Facility_Location}, {State}
        </div>
        <table style='font-size:12px; color:#E6EDF3; border-collapse:collapse; width:100%;'>
            <tr><td style='color:#8B9EA8; padding:2px 8px 2px 0;'>Industry</td>
                <td style='font-weight:600;'>{Industry}</td></tr>
            <tr><td style='color:#8B9EA8; padding:2px 8px 2px 0;'>Total Emissions</td>
                <td style='font-weight:600;'>{MTCO2e:.1f} MTCO2e</td></tr>
            <tr><td style='color:#8B9EA8; padding:2px 8px 2px 0;'>Fleet Share</td>
                <td style='font-weight:600;'>{Share_pct}%</td></tr>
            <tr><td style='color:#8B9EA8; padding:2px 8px 2px 0;'>Consumption</td>
                <td style='font-weight:600;'>{Total_kWh:.0f} kWh</td></tr>
            <tr><td style='color:#8B9EA8; padding:2px 8px 2px 0;'>Intensity</td>
                <td style='font-weight:600;'>{Intensity:.4f} MT/MWh</td></tr>
            <tr><td style='color:#8B9EA8; padding:2px 8px 2px 0;'>Risk Tier</td>
                <td style='font-weight:700; color:#FF6B6B;'>{Risk_Tier}</td></tr>
        </table>
    </div>""",
    "style": {
        "backgroundColor": "#0f1f18",
        "border": "1px solid #00C89650",
        "borderRadius": "10px",
        "padding": "12px 16px",
    },
}


def render_map(df: pd.DataFrame, mode: str, show_arcs: bool) -> pd.DataFrame:
    """
    Render the full map section including the risk summary sidebar panel.
    Returns map_df so insights.py can reuse it.
    """
    st.subheader("🗺️ Emissions Hotspot Map")
    st.caption("Bubble size = MTCO2e · Colour = risk tier · Arcs connect to highest emitter")

    map_df  = _build_map_df(df)
    layers  = _build_layers(map_df, mode, show_arcs)
    pitch   = 45 if mode == "3D Column" else 30
    view    = pdk.ViewState(latitude=21.0, longitude=78.0, zoom=4.5, pitch=pitch)

    map_col, stats_col = st.columns([3, 1])

    with map_col:
        st.pydeck_chart(pdk.Deck(
            layers=layers, initial_view_state=view, tooltip=TOOLTIP,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        ), height=520)

    with stats_col:
        st.markdown("**📍 Facility Risk Summary**")
        tier_colors = {"HIGH": "#DC3545", "MEDIUM": "#FFC107", "LOW": "#00C896"}
        for _, row in map_df.sort_values("MTCO2e", ascending=False).iterrows():
            tc = tier_colors[row["Risk_Tier"]]
            st.markdown(f"""
            <div style='background:#161B22; border:1px solid #00C89625;
                        border-left:3px solid {tc}; border-radius:8px;
                        padding:9px 12px; margin-bottom:7px;'>
                <div style='font-size:0.75rem; font-weight:700; color:{tc};'>{row["Risk_Tier"]} RISK</div>
                <div style='font-size:0.83rem; font-weight:600; color:#E6EDF3;'>{row["Facility_ID"]}</div>
                <div style='font-size:0.73rem; color:#8B9EA8;'>{row["Facility_Location"]}, {row["State"]}</div>
                <div style='font-size:0.73rem; color:#4a5568;'>{row["Industry"]}</div>
                <div style='font-size:0.82rem; color:#00C896; font-weight:700; margin-top:3px;'>
                    {row["MTCO2e"]:,.1f} MTCO2e
                    <span style='color:#8B9EA8; font-weight:400;'>({row["Share_pct"]}%)</span>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style='font-size:0.73rem; color:#8B9EA8; margin-top:8px;'>
            <b style='color:#E6EDF3;'>Legend</b><br/>
            <span style='color:#DC3545;'>&#9632;</span> High &nbsp;
            <span style='color:#FFC107;'>&#9632;</span> Medium &nbsp;
            <span style='color:#00C896;'>&#9632;</span> Low
        </div>""", unsafe_allow_html=True)

    return map_df

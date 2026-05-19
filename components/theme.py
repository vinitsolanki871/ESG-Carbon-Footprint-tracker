"""
components/theme.py
-------------------
Injects the global dark ESG theme CSS and renders the top header banner.
Call inject_theme() once at the top of app.py before any other st.* calls.
"""

import streamlit as st


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(160deg, #0D1117 0%, #0f1f18 50%, #0D1117 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1f18 0%, #161B22 100%) !important;
    border-right: 1px solid #00C89630;
}
.esg-header {
    background: linear-gradient(135deg, #0f2d1f 0%, #0a3d2b 50%, #0f2d1f 100%);
    border: 1px solid #00C89640;
    border-radius: 16px;
    padding: 24px 36px;
    margin-bottom: 16px;
    box-shadow: 0 4px 32px #00C89620;
}
.esg-header h1 { font-size:2rem; font-weight:700; color:#00C896; margin:0 0 4px 0; }
.esg-header p  { color:#8B9EA8; font-size:0.88rem; margin:0; letter-spacing:0.5px; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #161B22, #1a2535);
    border: 1px solid #00C89630;
    border-radius: 14px;
    padding: 18px 20px !important;
    box-shadow: 0 2px 16px #00000040;
}
[data-testid="stMetric"]:hover { box-shadow: 0 4px 24px #00C89630; border-color:#00C89660; }
[data-testid="stMetricLabel"]  { font-size:0.75rem !important; font-weight:600 !important;
                                  letter-spacing:0.8px !important; text-transform:uppercase !important;
                                  color:#8B9EA8 !important; }
[data-testid="stMetricValue"]  { font-size:1.6rem !important; font-weight:700 !important; color:#00C896 !important; }

h2, h3 { color:#E6EDF3 !important; font-weight:600 !important; }
hr     { border-color:#00C89620 !important; margin:20px 0 !important; }

[data-testid="stExpander"]  { background:#161B22; border:1px solid #00C89625; border-radius:12px; }
[data-testid="stDataFrame"] { border:1px solid #00C89625; border-radius:10px; overflow:hidden; }

.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, #00C896, #00a07a) !important;
    color:#0D1117 !important; font-weight:700 !important;
    border:none !important; border-radius:8px !important;
}
[data-baseweb="tag"] {
    background-color:#00C89625 !important; border:1px solid #00C89650 !important;
    color:#00C896 !important; border-radius:6px !important;
}
.stCaption, [data-testid="stCaptionContainer"] { color:#4a5568 !important; font-size:0.78rem !important; }
</style>
"""


def inject_theme() -> None:
    """Inject global CSS — must be called before any other st.* render calls."""
    st.markdown(CSS, unsafe_allow_html=True)


def render_header() -> None:
    """Render the top green gradient header banner."""
    st.markdown("""
    <div class="esg-header">
        <h1>🌿 Corporate Sustainability &amp; Carbon Footprint Tracker</h1>
        <p>CEA Grid EF 2025 &nbsp;·&nbsp; Scope 1 &amp; 2 Emissions &nbsp;·&nbsp;
           FY 2025 &nbsp;·&nbsp; 20 Indian Industrial Facilities</p>
    </div>
    """, unsafe_allow_html=True)

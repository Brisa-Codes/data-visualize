import streamlit as st
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from viral_viz.data.fetcher import DataFetcher, get_categories, get_datasets_in_category, get_dataset_description
from viral_viz.data.preprocessor import DataPreprocessor
from viral_viz.export.packager import DualPackager
from viral_viz.viz.bar_race import BarChartRace
from viral_viz.viz.line_race import LineRaceChart
from viral_viz.export.renderer import VideoRenderer
import time

st.set_page_config(page_title="ViralViz — Generator", page_icon="🎬", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    * { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; }
    .block-container { padding-top: 3.5rem; max-width: 1100px; }

    /* ── Navbar ────────────────────────────────────── */
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.7rem 2rem;
        background: rgba(10, 10, 18, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid #1a1a2a;
    }
    .nav-logo {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        text-decoration: none !important;
        color: #f0f0f0 !important;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: -0.3px;
    }
    .nav-logo-icon {
        width: 22px;
        height: 22px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 3px;
    }
    .nav-logo-icon .bar {
        background: #FF6B35;
        width: 4px;
        border-radius: 2px 2px 0 0;
    }
    .nav-logo-icon .bar:nth-child(1) { height: 11px; }
    .nav-logo-icon .bar:nth-child(2) { height: 18px; }
    .nav-logo-icon .bar:nth-child(3) { height: 14px; }
    .nav-right {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    .nav-right a {
        color: #888 !important;
        text-decoration: none !important;
        font-size: 0.82rem;
        font-weight: 500;
        padding: 0.35rem 0.7rem;
        border-radius: 6px;
        transition: color 0.2s;
    }
    .nav-right a:hover { color: #f0f0f0 !important; }
    .nav-active {
        background: rgba(255, 107, 53, 0.1) !important;
        color: #FF6B35 !important;
    }

    /* Hide Streamlit chrome */
    [data-testid="stToolbar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* Generate button */
    .stButton > button[kind="primary"] {
        background: #FF6B35 !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.5rem !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #e55a28 !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: #1a1a2a !important;
        color: #ddd !important;
        border: 1px solid #2a2a3a !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: border-color 0.2s;
    }
    .stDownloadButton > button:hover {
        border-color: #FF6B35 !important;
        color: #FF6B35 !important;
    }

    /* Progress bar */
    [data-testid="stProgressBar"] { position: relative; margin-top: 1rem; }
    [data-testid="stProgressBar"] > div:first-child {
        position: absolute; width: 100%; text-align: center;
        z-index: 2; font-size: 0.78rem; font-weight: 600;
        line-height: 1.6; color: #fff;
        text-shadow: 0 1px 3px rgba(0,0,0,0.5);
    }

    hr { border-color: #1a1a2a !important; }

    /* Header */
    .gen-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 0 1.5rem 0;
        border-bottom: 1px solid #1a1a2a;
        margin-bottom: 2rem;
    }
    .workspace-title {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    .workspace-icon {
        width: 36px;
        height: 36px;
        background: rgba(255, 107, 53, 0.1);
        color: #FF6B35;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    .workspace-title h2 {
        font-size: 1.4rem;
        color: #f0f0f0;
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .gen-header .tag {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #aaa;
        padding: 0.35rem 0.8rem;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Video cards */
    .vid-container {
        background: #0f0f16;
        border: 1px solid #1a1a2a;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    .vid-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .vid-label::before {
        content: '';
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #FF6B35;
    }

    /* Empty State Dashboard */
    .empty-state {
        background: #0b0b10;
        border: 1px dashed #2a2a3a;
        border-radius: 16px;
        padding: 5rem 2rem;
        text-align: center;
        margin-top: 1rem;
    }
    .empty-state-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        opacity: 0.6;
        filter: grayscale(100%);
    }
    .empty-state h3 {
        color: #e0e0e0;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .empty-state p {
        color: #666;
        max-width: 420px;
        margin: 0 auto 2.5rem auto;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .status-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
    }
    .status-badge {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.8rem;
        color: #888;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .status-badge.active {
        background: rgba(255, 107, 53, 0.08);
        border-color: rgba(255, 107, 53, 0.2);
        color: #FF6B35;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #444;
    }
    .status-dot.green { background: #00E676; box-shadow: 0 0 8px rgba(0,230,118,0.4); }

    /* Expander styling */
    .stExpander {
        background: #0f0f16 !important;
        border: 1px solid #1a1a2a !important;
        border-radius: 10px !important;
        margin-bottom: 0.8rem !important;
    }
    .stExpander summary { color: #ccc !important; font-weight: 600 !important; }
    .stExpander [data-testid="stExpanderContent"] { padding: 0.5rem 0.8rem !important; }

    /* Hide sidebar on mobile */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; padding-top: 3rem !important; }
        .navbar { padding: 0.5rem 0.8rem; }
        .nav-logo { font-size: 0.95rem; }
        .nav-logo-icon { width: 18px; height: 18px; gap: 2px; }
        .nav-logo-icon .bar { width: 3px; }
        .nav-right a { font-size: 0.72rem; padding: 0.3rem 0.5rem; }
        .gen-header { padding: 0.3rem 0 1rem 0; margin-bottom: 1rem; }
        .workspace-title h2 { font-size: 1.1rem; }
        .workspace-icon { width: 30px; height: 30px; font-size: 1rem; }
        .tag { font-size: 0.6rem !important; padding: 0.25rem 0.5rem !important; }
        .empty-state { padding: 3rem 1.2rem; }
        .empty-state h3 { font-size: 1.2rem; }
        .empty-state p { font-size: 0.85rem; }
        .status-badges { flex-direction: column; align-items: center; gap: 0.5rem; }
    }

</style>
""", unsafe_allow_html=True)

# ── Navbar ───────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <a class="nav-logo" href="/" target="_self">
        <div class="nav-logo-icon">
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
        </div>
        ViralViz
    </a>
    <div class="nav-right">
        <a href="/" target="_self">Home</a>
        <a class="nav-active" href="#">Generator</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────
st.markdown("""
<div class="gen-header">
    <div class="workspace-title">
        <div class="workspace-icon">🎬</div>
        <h2>Studio Workspace</h2>
    </div>
    <span class="tag">Engine Online</span>
</div>
""", unsafe_allow_html=True)

os.makedirs("renders", exist_ok=True)

# ── Input Controls (main area — works on mobile + desktop) ───────────
input_csv = None
topic = None
years = None
catalog_category = None
catalog_dataset = None

# 1. Visualization Mode
chart_type_label = st.radio("Step 1: Choose Visualization Type", ["Bar Race", "Line Race"],
                            horizontal=True, help="Bar Race = horizontal bars. Line Race = ranked curve chart.")
chart_type = "bar" if chart_type_label == "Bar Race" else "line"

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📂 Step 2: Data Source", expanded=True):
    data_source = st.radio("Source", ["Built-in Catalog", "CSV Upload", "World Bank API", "Kaggle API"],
                           label_visibility="collapsed", horizontal=True)

    if data_source == "Built-in Catalog":
        c1, c2 = st.columns(2)
        with c1:
            catalog_category = st.selectbox("Category", get_categories())
        with c2:
            datasets = get_datasets_in_category(catalog_category)
            catalog_dataset = st.selectbox("Dataset", datasets)
        st.caption(f"ℹ️ {get_dataset_description(catalog_category, catalog_dataset)}")
    elif data_source == "CSV Upload":
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        input_csv = uploaded_file
    elif data_source == "World Bank API":
        topic = st.text_input("Indicator Code", value="NY.GDP.MKTP.CD")
        years = st.slider("Year Range", 1960, 2023, (2000, 2023))
    else:
        st.info("Search Kaggle for datasets. No API keys required.")
        search_query = st.text_input("Search Kaggle (e.g. population, gdp, climate)")
        
        if 'kaggle_results' not in st.session_state:
            st.session_state.kaggle_results = []
            
        if st.button("Search Kaggle", key="search_btn"):
            if search_query:
                with st.spinner("Searching..."):
                    st.session_state.kaggle_results = DataFetcher.search_kaggle(search_query)
        
        kaggle_dataset = ""
        if st.session_state.kaggle_results:
            options = {f"{r['title']} ({r['ref']})": r['ref'] for r in st.session_state.kaggle_results}
            selected_option = st.selectbox("Select a Dataset", list(options.keys()))
            kaggle_dataset = options[selected_option]

with st.expander("🎨 Step 3: Aesthetics"):
    default_title = catalog_dataset if catalog_dataset else "My Visualization"
    title = st.text_input("Chart Title", value=default_title)

    col1, col2, col3 = st.columns(3)
    with col1:
        theme = st.selectbox("Theme", ["dark", "light"])
    with col2:
        speed = st.selectbox("Speed", ["normal", "fast", "slow"])
    with col3:
        fmt = st.selectbox("Format", ["landscape", "portrait"])

# ── Session state ────────────────────────────────────────────────────
if "rendered_outputs" not in st.session_state:
    st.session_state.rendered_outputs = []

# ── Generate ─────────────────────────────────────────────────────────
if st.button("Generate Video →", type="primary", use_container_width=True):
    if data_source == "CSV Upload" and input_csv is None:
        st.error("Please upload a CSV file.")
    else:
        progress = st.progress(0, text="Loading data...")
        status_text = st.empty()
        try:
            if data_source == "Built-in Catalog":
                df = DataFetcher.from_catalog(catalog_category, catalog_dataset)
            elif data_source == "CSV Upload":
                df = pd.read_csv(input_csv, index_col=0)
                df.index = pd.to_numeric(df.index, errors='ignore')
            elif data_source == "World Bank API":
                df = DataFetcher.from_world_bank(topic, years[0], years[1])
            else:
                if not kaggle_dataset:
                    raise ValueError("Please search and select a Kaggle dataset.")
                
                progress.progress(5, text="Fetching data from Kaggle...")
                df = DataFetcher.from_kaggle(
                    dataset_ref=kaggle_dataset
                )
            progress.progress(10, text="Interpolating frames...")

            fps = 30
            if speed == 'fast': seconds_per_period = 0.8
            elif speed == 'slow': seconds_per_period = 2.0
            else: seconds_per_period = 1.5

            df_clean = DataPreprocessor.clean_data(df)
            df_interpolated = DataPreprocessor.interpolate_frames(
                df_clean, fps=fps, seconds_per_period=seconds_per_period
            )
            total_frames = len(df_interpolated)

            format_idx = {'landscape': 0, 'portrait': 1}

            def update_progress(fmt_name, cur, tot):
                offset = format_idx.get(fmt_name, 0)
                base = 15 + (offset * 40)
                pct = base + int((cur / tot) * 40)
                pct = min(pct, 95)
                text_pct = min(100, int(cur/tot*100))
                progress.progress(pct, text=f"Rendering {fmt_name}... {text_pct}%")

            base_name = f"viz_{int(time.time())}"
            if fmt == 'both':
                outputs = DualPackager.export_both(
                    df_interpolated, top_n=10, theme=theme, fps=fps,
                    output_dir="renders", base_name=base_name, title=title,
                    chart_type=chart_type,
                    on_progress=update_progress
                )
            else:
                def single_progress(cur, tot):
                    pct = 15 + int((cur / tot) * 80)
                    pct = min(pct, 95)
                    text_pct = min(100, int(cur/tot*100))
                    progress.progress(pct, text=f"Rendering {fmt}... {text_pct}%")

                ChartClass = LineRaceChart if chart_type == "line" else BarChartRace
                chart = ChartClass(df_interpolated, top_n=10, theme=theme, fmt=fmt, title=title)
                out_path = os.path.join("renders", f"{base_name}_{fmt}.mp4")
                VideoRenderer.render_generator(
                    chart.generate_frames(), fps, out_path, audio_clip=None,
                    total_frames=total_frames, on_progress=single_progress
                )
                outputs = [out_path]

            progress.progress(100, text="✅ Done!")
            time.sleep(0.5)
            progress.empty()
            status_text.empty()

            rendered = []
            for path in outputs:
                with open(path, "rb") as f:
                    rendered.append({
                        "path": path,
                        "filename": os.path.basename(path),
                        "bytes": f.read(),
                    })
            st.session_state.rendered_outputs = rendered

        except Exception as e:
            progress.empty()
            status_text.empty()
            st.error(f"Error: {str(e)}")

# ── Results ──────────────────────────────────────────────────────────
if not st.session_state.rendered_outputs:
    # Empty State Dashboard
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">📊</div>
        <h3>Workspace Ready</h3>
        <p>Configure your dataset, title, and formatting options in the sidebar to generate your first cinematic video.</p>
        <div class="status-badges">
            <div class="status-badge active"><div class="status-dot green"></div> Pillow Renderer</div>
            <div class="status-badge"><div class="status-dot"></div> Awaiting Input</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.success("Render complete. Your videos are ready.")

    for i, item in enumerate(st.session_state.rendered_outputs):
        is_portrait = "portrait" in item["filename"]

        if is_portrait:
            label = "Mobile · 9:16"
            pad_l, vid_col, pad_r = st.columns([1.5, 2, 1.5])
        else:
            label = "Widescreen · 16:9"
            pad_l, vid_col, pad_r = st.columns([1, 3, 1])

        with vid_col:
            st.markdown(f'<div class="vid-container"><div class="vid-label">{label}</div>', unsafe_allow_html=True)
            st.video(item["bytes"])
            st.download_button(
                label="↓ Download HD MP4",
                data=item["bytes"],
                file_name=item["filename"],
                mime="video/mp4",
                key=f"dl_{i}",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

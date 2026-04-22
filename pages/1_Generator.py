import streamlit as st
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from viral_viz.data.fetcher import DataFetcher, get_categories, get_datasets_in_category, get_dataset_description
from viral_viz.data.preprocessor import DataPreprocessor
from viral_viz.export.packager import DualPackager
from viral_viz.viz.bar_race import BarChartRace
from viral_viz.export.renderer import VideoRenderer
import time

st.set_page_config(page_title="ViralViz — Generator", page_icon="🎬", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    * { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; }
    .block-container { padding-top: 1.5rem; max-width: 1100px; }

    /* Hide Streamlit chrome */
    [data-testid="stToolbar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0c0c14;
        border-right: 1px solid #1a1a2a;
    }
    [data-testid="stSidebar"] * { color: #ccc !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stRadio label {
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #888 !important;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.85rem !important;
        color: #aaa !important;
        letter-spacing: 1px;
    }

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

    /* Success alert */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
        background: rgba(0, 230, 118, 0.1) !important;
        border: 1px solid rgba(0, 230, 118, 0.2) !important;
        color: #00E676 !important;
    }
</style>
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

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 DATA SOURCE")
    data_source = st.radio("Source", ["Built-in Catalog", "CSV Upload", "World Bank API"],
                           label_visibility="collapsed")

    input_csv = None
    topic = None
    years = None
    catalog_category = None
    catalog_dataset = None

    if data_source == "Built-in Catalog":
        catalog_category = st.selectbox("Category", get_categories())
        datasets = get_datasets_in_category(catalog_category)
        catalog_dataset = st.selectbox("Dataset", datasets)
        st.caption(f"ℹ️ {get_dataset_description(catalog_category, catalog_dataset)}")
    elif data_source == "CSV Upload":
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        input_csv = uploaded_file
    else:
        topic = st.text_input("Indicator Code", value="NY.GDP.MKTP.CD")
        years = st.slider("Year Range", 1960, 2023, (2000, 2023))

    st.markdown("---")
    st.markdown("### 🎨 AESTHETICS")
    default_title = catalog_dataset if catalog_dataset else "My Visualization"
    title = st.text_input("Chart Title", value=default_title)

    col1, col2 = st.columns(2)
    with col1:
        theme = st.selectbox("Theme", ["dark", "light"])
    with col2:
        speed = st.selectbox("Speed", ["normal", "fast", "slow"])

    fmt = st.selectbox("Format", ["landscape", "portrait", "both"])

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
            else:
                df = DataFetcher.from_world_bank(topic, years[0], years[1])
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
                progress.progress(pct, text=f"Rendering {fmt_name}... {int(cur/tot*100)}%")

            base_name = f"viz_{int(time.time())}"
            if fmt == 'both':
                outputs = DualPackager.export_both(
                    df_interpolated, top_n=10, theme=theme, fps=fps,
                    output_dir="renders", base_name=base_name, title=title,
                    on_progress=update_progress
                )
            else:
                def single_progress(cur, tot):
                    pct = 15 + int((cur / tot) * 80)
                    pct = min(pct, 95)
                    progress.progress(pct, text=f"Rendering {fmt}... {int(cur/tot*100)}%")

                race = BarChartRace(df_interpolated, top_n=10, theme=theme, fmt=fmt, title=title)
                out_path = os.path.join("renders", f"{base_name}_{fmt}.mp4")
                VideoRenderer.render_generator(
                    race.generate_frames(), fps, out_path, audio_clip=None,
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

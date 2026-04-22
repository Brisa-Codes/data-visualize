import streamlit as st

st.set_page_config(page_title="ViralViz Engine", page_icon="📈", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    .block-container { padding-top: 0; max-width: 1100px; }

    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    [data-testid="stToolbar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    * { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; }

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
        padding: 0.8rem 2.5rem;
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
        font-size: 1.2rem;
        letter-spacing: -0.3px;
    }
    .nav-logo-icon {
        width: 24px;
        height: 24px;
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
    .nav-logo-icon .bar:nth-child(1) { height: 12px; }
    .nav-logo-icon .bar:nth-child(2) { height: 20px; }
    .nav-logo-icon .bar:nth-child(3) { height: 16px; }
    .nav-links {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    .nav-links a {
        color: #999;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        transition: color 0.2s;
    }
    .nav-links a:hover { color: #f0f0f0; }
    .nav-sep {
        color: #333;
        font-size: 0.9rem;
        margin: 0 0.1rem;
    }
    .nav-cta {
        background: #FF6B35 !important;
        color: white !important;
        padding: 0.45rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        margin-left: 0.5rem;
    }
    .nav-cta:hover { background: #e55a28 !important; }

    /* ── Hero ─────────────────────────────────────── */
    .hero {
        text-align: center;
        padding: 8rem 1rem 2rem 1rem;
    }
    .hero-tag {
        display: inline-block;
        border: 1px solid #333;
        color: #aaa;
        padding: 0.35rem 0.9rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }
    .hero h1 {
        font-size: 3.8rem;
        font-weight: 700;
        line-height: 1.05;
        color: #f5f5f5;
        margin-bottom: 1.2rem;
        letter-spacing: -1.5px;
    }
    .hero .accent { color: #FF6B35; }
    .hero p {
        color: #777;
        font-size: 1.1rem;
        max-width: 520px;
        margin: 0 auto;
        line-height: 1.7;
    }

    /* ── Stats ─────────────────────────────────────── */
    .stats {
        display: flex;
        justify-content: center;
        gap: 4rem;
        margin: 4rem 0;
        flex-wrap: wrap;
    }
    .stat { text-align: center; }
    .stat-val {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #f0f0f0;
    }
    .stat-lbl {
        color: #555;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 0.3rem;
    }

    /* ── Divider ───────────────────────────────────── */
    .divider {
        width: 60px;
        height: 3px;
        background: #FF6B35;
        margin: 0 auto 3rem auto;
        border-radius: 2px;
    }

    /* ── Features ──────────────────────────────────── */
    .features {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.2rem;
        margin: 0 auto 5rem auto;
        max-width: 960px;
    }
    /* ── Mobile Responsive ─────────────────────────── */
    @media (max-width: 768px) {
        /* Navbar */
        .navbar { padding: 0.6rem 1rem; }
        .nav-logo { font-size: 1rem; gap: 0.4rem; }
        .nav-logo-icon { width: 20px; height: 20px; gap: 2px; }
        .nav-logo-icon .bar { width: 3px; }
        .nav-logo-icon .bar:nth-child(1) { height: 9px; }
        .nav-logo-icon .bar:nth-child(2) { height: 16px; }
        .nav-logo-icon .bar:nth-child(3) { height: 12px; }
        .nav-links a { font-size: 0.72rem; padding: 0.3rem 0.4rem; }
        .nav-sep { display: none; }
        .nav-cta { padding: 0.4rem 0.7rem !important; font-size: 0.72rem !important; margin-left: 0.2rem; }

        /* Hero */
        .hero { padding: 5.5rem 1rem 1.5rem 1rem; }
        .hero h1 { font-size: 2.2rem; letter-spacing: -0.8px; }
        .hero p { font-size: 0.9rem; max-width: 100%; }
        .hero-tag { font-size: 0.65rem; padding: 0.25rem 0.6rem; margin-bottom: 1.2rem; }

        /* CTA button */
        .cta-btn { font-size: 0.9rem; padding: 0.7rem 1.8rem; width: 100%; text-align: center; box-sizing: border-box; }

        /* Stats */
        .stats { gap: 1.5rem; margin: 2.5rem 0; }
        .stat-val { font-size: 1.8rem; }
        .stat-lbl { font-size: 0.65rem; }

        /* Features grid */
        .features { grid-template-columns: 1fr; gap: 1rem; margin-bottom: 3rem; }
        .feat { padding: 1.5rem 1.2rem; }

        /* Steps grid */
        .steps { grid-template-columns: 1fr; gap: 1.2rem; margin-bottom: 3rem; }

        /* Section heads */
        .section-head { font-size: 1.2rem; }
        .section-sub { font-size: 0.78rem; }

        /* Footer */
        .footer { padding: 2rem 1rem 1.5rem; }
        .footer-grid { grid-template-columns: 1fr; gap: 1.5rem; }
        .footer-brand p { font-size: 0.75rem; }
        .footer-copy { margin-top: 1.5rem; padding-top: 1rem; }

        /* Streamlit overrides */
        .block-container { padding-left: 0.5rem; padding-right: 0.5rem; }
    }

    /* Extra small (< 400px) */
    @media (max-width: 400px) {
        .hero h1 { font-size: 1.8rem; }
        .hero p { font-size: 0.82rem; }
        .stat-val { font-size: 1.5rem; }
        .stats { flex-direction: column; gap: 1rem; }
        .navbar { padding: 0.5rem 0.7rem; }
        .nav-links a:not(.nav-cta) { display: none; }
    }
    .feat {
        background: #111119;
        border: 1px solid #1e1e2e;
        border-radius: 12px;
        padding: 2rem 1.5rem;
    }
    .feat:hover { border-color: #2a2a3a; }
    .feat-icon {
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    .feat h3 {
        color: #e0e0e0;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .feat p {
        color: #666;
        font-size: 0.82rem;
        line-height: 1.6;
    }

    /* ── Steps ─────────────────────────────────────── */
    .section-head {
        text-align: center;
        color: #e0e0e0;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
        letter-spacing: -0.5px;
    }
    .section-sub {
        text-align: center;
        color: #555;
        font-size: 0.85rem;
        margin-bottom: 3rem;
    }
    .steps {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        max-width: 860px;
        margin: 0 auto 5rem auto;
    }
    .step { text-align: center; padding: 0.5rem; }
    .step-n {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: #FF6B35;
        color: white;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    .step h4 {
        color: #ddd;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .step p { color: #666; font-size: 0.8rem; line-height: 1.6; }

    /* ── Footer ────────────────────────────────────── */
    .footer {
        border-top: 1px solid #1a1a2a;
        padding: 3rem 2rem 2rem;
        margin-top: 3rem;
    }
    .footer-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 2rem;
        max-width: 1000px;
        margin: 0 auto;
    }
    .footer-brand p {
        color: #555;
        font-size: 0.78rem;
        line-height: 1.6;
        margin-top: 0.8rem;
    }
    .footer-brand .f-logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #ddd !important;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        text-decoration: none !important;
    }
    .footer-col h4 {
        color: #aaa;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.8rem;
    }
    .footer-col a {
        display: block;
        color: #666 !important;
        text-decoration: none !important;
        font-size: 0.8rem;
        padding: 0.2rem 0;
        transition: color 0.2s;
    }
    .footer-col a:hover { color: #FF6B35 !important; }
    .footer-copy {
        text-align: center;
        color: #333;
        font-size: 0.7rem;
        margin-top: 2.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #141420;
    }

    /* ── CTA ───────────────────────────────────────── */
    .cta-btn {
        display: inline-block;
        background: #FF6B35;
        color: white !important;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.8rem 2.2rem;
        border-radius: 10px;
        text-decoration: none !important;
        margin-top: 1.5rem;
        transition: background 0.2s;
    }
    .cta-btn:hover {
        background: #e55a28;
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
    <div class="nav-links">
        <a href="#features">Features</a>
        <span class="nav-sep">|</span>
        <a href="#how-it-works">How it Works</a>
        <span class="nav-sep">|</span>
        <a class="nav-cta" href="Generator" target="_self">Get Started</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">Data → Video Engine</div>
    <h1>Data stories that<br><span class="accent">move.</span></h1>
    <p>
        Generate cinematic bar chart race videos for
        YouTube, TikTok & Reels. Pick a dataset, hit render, download.
    </p>
    <a class="cta-btn" href="Generator" target="_self">Get Started →</a>
</div>
""", unsafe_allow_html=True)

# ── Stats ────────────────────────────────────────────────────────────
st.markdown("""
<div class="stats">
    <div class="stat">
        <div class="stat-val">10+</div>
        <div class="stat-lbl">Datasets</div>
    </div>
    <div class="stat">
        <div class="stat-val">720p</div>
        <div class="stat-lbl">HD Output</div>
    </div>
    <div class="stat">
        <div class="stat-val">~10s</div>
        <div class="stat-lbl">Render Time</div>
    </div>
    <div class="stat">
        <div class="stat-val">2</div>
        <div class="stat-lbl">Formats</div>
    </div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── Features ─────────────────────────────────────────────────────────
st.markdown("""
<div class="features">
    <div class="feat">
        <div class="feat-icon">◐</div>
        <h3>Smooth Motion</h3>
        <p>Bars glide with exponential easing. Rank changes feel cinematic, not jumpy.</p>
    </div>
    <div class="feat">
        <div class="feat-icon">▯</div>
        <h3>Multi-Format</h3>
        <p>Export 16:9 for YouTube or 9:16 for TikTok & Reels — both in one click.</p>
    </div>
    <div class="feat">
        <div class="feat-icon">⟐</div>
        <h3>Fast Pipeline</h3>
        <p>Custom Pillow renderer at 170+ fps. Full videos in seconds, not minutes.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── How It Works ─────────────────────────────────────────────────────
st.markdown("""
<h2 class="section-head">How it works</h2>
<p class="section-sub">Three steps. No editing software needed.</p>

<div class="steps">
    <div class="step">
        <div class="step-n">1</div>
        <h4>Pick a dataset</h4>
        <p>Choose from built-in datasets or upload your own CSV with time-series data.</p>
    </div>
    <div class="step">
        <div class="step-n">2</div>
        <h4>Configure</h4>
        <p>Set title, theme, speed, and output format. Preview settings before rendering.</p>
    </div>
    <div class="step">
        <div class="step-n">3</div>
        <h4>Download</h4>
        <p>Hit generate, watch the progress, and download your MP4 — ready for upload.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-grid">
        <div class="footer-brand">
            <div class="f-logo">
                <div class="nav-logo-icon" style="transform: scale(0.85); transform-origin: left center;">
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                </div>
                ViralViz
            </div>
            <p>Turn time-series data into cinematic bar chart race videos optimized for social media platforms.</p>
        </div>
        <div class="footer-col">
            <h4>Product</h4>
            <a href="Generator" target="_self">Generator</a>
            <a href="#features">Features</a>
            <a href="#how-it-works">How it Works</a>
        </div>
        <div class="footer-col">
            <h4>Formats</h4>
            <a href="#">YouTube (16:9)</a>
            <a href="#">TikTok (9:16)</a>
            <a href="#">Instagram Reels</a>
        </div>
        <div class="footer-col">
            <h4>Resources</h4>
            <a href="#">Documentation</a>
            <a href="#">CSV Template</a>
            <a href="#">GitHub</a>
        </div>
    </div>
    <div class="footer-copy">© 2026 ViralViz Engine. All rights reserved.</div>
</div>
""", unsafe_allow_html=True)

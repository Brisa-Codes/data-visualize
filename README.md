# ViralViz Engine

Turn time-series data into cinematic bar chart race videos.

## Features

- **Built-in Dataset Catalog** — GDP, population, CO₂ emissions, sports stats & more
- **World Bank API** — Pull any indicator from the World Bank's open data
- **CSV Upload** — Bring your own data
- **Dual Format Export** — Landscape (16:9) and Portrait (9:16) in a single render
- **Pillow-Powered** — ~170 FPS rendering, full 30s videos in under 15 seconds
- **Cinematic Design** — Cubic-eased transitions, smart label placement, progress bars

## Quick Start

```bash
# Clone
git clone https://github.com/Brisa-Codes/data-visualize.git
cd data-visualize

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Project Structure

```
├── app.py                   # Landing page
├── pages/
│   └── 1_Generator.py       # Video generator workspace
├── viral_viz/
│   ├── data/
│   │   ├── fetcher.py        # Data sources (catalog, CSV, World Bank)
│   │   ├── preprocessor.py   # Interpolation & frame generation
│   │   └── suggester.py      # Trending topic suggestions
│   ├── viz/
│   │   ├── bar_race.py       # Pillow-based bar chart renderer
│   │   ├── themes.py         # Dark & light color palettes
│   │   └── layout.py         # 16:9 / 9:16 safe zone management
│   ├── export/
│   │   ├── renderer.py       # Frame-to-MP4 pipeline (imageio/ffmpeg)
│   │   └── packager.py       # Dual-format batch export
│   └── audio/
│       ├── mixer.py          # Background music & SFX mixing
│       └── sync.py           # Audio synchronization
├── renders/                  # Output directory (gitignored)
└── requirements.txt
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit 1.50 |
| Rendering | Pillow (PIL) |
| Video Encoding | imageio + ffmpeg |
| Data | pandas, World Bank API |
| Audio | moviepy |

## Requirements

- Python 3.9+
- ffmpeg (installed automatically via `imageio-ffmpeg`)

## License

MIT

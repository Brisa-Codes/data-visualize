import os
from .renderer import VideoRenderer
from ..viz.bar_race import BarChartRace
from ..viz.line_race import LineRaceChart
import pandas as pd
from typing import Callable, Optional


class DualPackager:
    """Handles dual-format export for YouTube and Shorts."""

    @staticmethod
    def export_both(df: pd.DataFrame, top_n: int, theme: str, fps: int,
                    output_dir: str, base_name: str, audio_clip=None,
                    title: str = "",
                    chart_type: str = "bar",
                    on_progress: Optional[Callable[[str, int, int], None]] = None):
        """Generates both landscape and portrait versions with progress."""
        formats = ['landscape', 'portrait']
        outputs = []
        total_frames = len(df)

        ChartClass = LineRaceChart if chart_type == "line" else BarChartRace

        for fmt in formats:
            chart = ChartClass(df, top_n=top_n, theme=theme, fmt=fmt, title=title)
            frame_gen = chart.generate_frames()
            output_path = os.path.join(output_dir, f"{base_name}_{fmt}.mp4")

            def _progress(cur, tot, _fmt=fmt):
                if on_progress:
                    on_progress(_fmt, cur, tot)

            VideoRenderer.render_generator(frame_gen, fps, output_path, audio_clip,
                                           total_frames=total_frames,
                                           on_progress=_progress)
            outputs.append(output_path)

        return outputs

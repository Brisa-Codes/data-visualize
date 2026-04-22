from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pandas as pd
from typing import Generator

from .themes import Themes
from .layout import LayoutManager
from .emojis import ENTITY_EMOJIS
from pilmoji import Pilmoji


class LineRaceChart:
    """
    Animated ranked line chart renderer using Pillow.
    Shows top-N entities as points on a curve, sorted by value,
    with smooth transitions between time periods.
    """

    def __init__(self, df: pd.DataFrame, top_n: int = 10, theme: str = 'dark',
                 fmt: str = 'landscape', title: str = "",
                 smoothing: float = 0.025):
        self.df = df
        self.top_n = top_n
        self.theme = theme
        self.fmt = fmt
        self.title = title
        self.smoothing = smoothing

        categories = df.columns
        bar_colors = Themes.PALETTES.get(theme, Themes.PALETTES['dark'])['bars']
        self.colors = {cat: bar_colors[i % len(bar_colors)] for i, cat in enumerate(categories)}

        # Pre-load fonts
        try:
            self.font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
            self.font_value = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
            self.font_year  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
            self.font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 38)
            self.font_axis  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
            self.font_rank  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
        except (OSError, IOError):
            try:
                self.font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
                self.font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                self.font_year  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
                self.font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
                self.font_axis  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                self.font_rank  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
            except (OSError, IOError):
                self.font_label = ImageFont.load_default()
                self.font_value = ImageFont.load_default()
                self.font_year  = ImageFont.load_default()
                self.font_title = ImageFont.load_default()
                self.font_axis  = ImageFont.load_default()
                self.font_rank  = ImageFont.load_default()

    @staticmethod
    def _catmull_rom(p0, p1, p2, p3, num_points=20):
        """Generate smooth curve points between p1 and p2 using Catmull-Rom spline."""
        points = []
        for i in range(num_points):
            t = i / num_points
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * ((2 * p1[0]) +
                        (-p0[0] + p2[0]) * t +
                        (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                        (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) +
                        (-p0[1] + p2[1]) * t +
                        (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                        (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
            points.append((x, y))
        return points

    def _smooth_curve(self, points):
        """Generate a smooth curve through a list of (x, y) points."""
        if len(points) < 2: return points
        if len(points) == 2: return points
        padded = [points[0]] + list(points) + [points[-1]]
        curve = []
        for i in range(1, len(padded) - 2):
            segment = self._catmull_rom(padded[i-1], padded[i], padded[i+1], padded[i+2], num_points=16)
            curve.extend(segment)
        curve.append(points[-1])
        return curve

    def _format_value(self, val):
        """Format large numbers with B/M/K suffixes."""
        if val >= 1e9: return f"${val/1e9:,.1f}B"
        elif val >= 1e6: return f"${val/1e6:,.1f}M"
        elif val >= 1e3: return f"${val/1e3:,.0f}K"
        else: return f"{val:,.0f}"

    def _draw_title(self, draw, W, H, zones, text_color):
        if not self.title: return
        words = self.title.split()
        lines, current_line = [], []
        max_w = W * 0.9
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=self.font_title)
            if bbox[2] - bbox[0] <= max_w: current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        line_h = 44
        ty = int(H * (1 - zones['title_y']))
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=self.font_title)
            tx = (W - (bbox[2] - bbox[0])) // 2
            draw.text((tx, ty + i * line_h), line, fill=text_color, font=self.font_title)

    def generate_frames(self) -> Generator[np.ndarray, None, None]:
        """Generator yielding RGB numpy arrays."""
        specs = LayoutManager.FORMATS[self.fmt]
        W, H = specs['width'], specs['height']
        zones = LayoutManager.get_safe_zones(self.fmt)
        palette = Themes.PALETTES.get(self.theme, Themes.PALETTES['dark'])

        chart_left   = int(W * zones['chart_left']) + 30
        chart_right  = int(W * zones['chart_right']) - 10
        chart_top    = int(H * (1 - zones['chart_top'])) + 20
        chart_bottom = int(H * (1 - zones['chart_bottom'])) - 30
        chart_w, chart_h = chart_right - chart_left, chart_bottom - chart_top

        # Add hold frames
        indices = list(self.df.index)
        indices += [indices[-1]] * 60
        total_frames = len(indices)

        bg_color, text_color, text_dim = palette['bg'], palette['text'], palette['text_dim']
        grid_color, line_color = palette['grid'], '#00E676'

        # Year color
        bg_rgb = tuple(int(palette['bg'][i:i+2], 16) for i in (1, 3, 5))
        bg_luma = (bg_rgb[0] * 299 + bg_rgb[1] * 587 + bg_rgb[2] * 114) / 1000
        wm_rgb = (255, 255, 255) if bg_luma < 128 else (0, 0, 0)
        year_color = tuple(int(bg_rgb[i] + (wm_rgb[i] - bg_rgb[i]) * 0.1) for i in range(3))

        smooth_vals, smooth_ranks = {}, {}
        reveal_frames = 60

        dummy_img = Image.new('RGB', (1, 1))
        shared_pilmoji = Pilmoji(dummy_img)

        try:
            for frame_num, time_idx in enumerate(indices):
                reveal_pct = min(frame_num / reveal_frames, 1.0)
                img = Image.new('RGB', (W, H), bg_color)
                draw = ImageDraw.Draw(img)

                shared_pilmoji.image = img
                shared_pilmoji.draw = draw
                pilmoji = shared_pilmoji

                row = self.df.loc[time_idx].dropna()
                top_entities = row.sort_values(ascending=False).head(self.top_n).sort_values(ascending=True)
                if len(top_entities) == 0:
                    yield np.asarray(img)
                    continue
    
                max_val = max(top_entities.max(), 1)
                min_val = 0
                
                target_ranks = {ent: i for i, ent in enumerate(top_entities.index)}
                for entity in top_entities.index:
                    # Value smoothing
                    target_val = top_entities[entity]
                    if entity not in smooth_vals:
                        # Start from 0 for a grow-in effect if it's the first time seeing this entity
                        smooth_vals[entity] = 0.0 
                    
                    smooth_vals[entity] += self.smoothing * (target_val - smooth_vals[entity])
                    
                    # Rank smoothing (X-axis) — extra soft for "soft take overs"
                    target_rank = target_ranks[entity]
                    if entity not in smooth_ranks:
                        smooth_ranks[entity] = float(target_rank)
                    else:
                        smooth_ranks[entity] += 0.015 * (target_rank - smooth_ranks[entity])
    
                # Grid
                for i in range(6):
                    gy = chart_bottom - int(chart_h * i / 5)
                    draw.line([(chart_left, gy), (chart_right, gy)], fill=grid_color, width=1)
                    gv = min_val + (max_val - min_val) * i / 5
                    draw.text((chart_left - 5, gy - 6), self._format_value(gv), fill=text_dim, font=self.font_axis, anchor="ra")
    
                # Dots
                dot_positions = []
                reveal_x_limit = chart_left + int(reveal_pct * chart_w)
                for ent in top_entities.index:
                    x = chart_left + int((smooth_ranks[ent] / max(self.top_n - 1, 1)) * chart_w)
                    y = chart_bottom - int(((smooth_vals[ent] - min_val) / (max_val - min_val)) * chart_h)
                    if x <= reveal_x_limit: dot_positions.append((x, y, ent, smooth_vals[ent]))
                dot_positions.sort(key=lambda d: d[0])
    
                # Curve & Fill
                if len(dot_positions) >= 2:
                    pts = [(dp[0], dp[1]) for dp in dot_positions]
                    curve = self._smooth_curve(pts)
                    fill_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                    ImageDraw.Draw(fill_layer).polygon([(chart_left, chart_bottom)] + curve + [(curve[-1][0], chart_bottom)], fill=(0, 230, 118, 30))
                    img.paste(fill_layer, (0, 0), fill_layer)
                    for i in range(len(curve)-1):
                        draw.line([curve[i], curve[i+1]], fill=line_color, width=2)
    
                # Labels
                for x, y, ent, val in dot_positions:
                    draw.ellipse([x-4, y-4, x+4, y+4], fill=line_color)
                    vtxt = self._format_value(val)
                    
                    emoji = ENTITY_EMOJIS.get(ent)
                    display_text = f"{emoji} {ent}" if emoji else ent
                    
                    lb = pilmoji.getsize(display_text, font=self.font_label)
                    vb = draw.textbbox((0, 0), vtxt, font=self.font_value)
                    
                    bw, bh = max(lb[0], vb[2]-vb[0]) + 24, 48
                    bx0, by0 = max(chart_left, min(x - bw//2, chart_right - bw)), y - 60
                    draw.rounded_rectangle([bx0, by0, bx0+bw, by0+bh], radius=8, fill=(10, 10, 15), outline=(60, 60, 70), width=1)
                    
                    pilmoji.text((bx0 + 12, by0 + 4), display_text, fill='white', font=self.font_label)
                    draw.text((bx0+12, by0+26), vtxt, fill='#AAA', font=self.font_value)
    
                # Ranks
                for r in range(self.top_n):
                    rx = chart_left + int((r / max(self.top_n - 1, 1)) * chart_w)
                    if rx <= reveal_x_limit:
                        txt = f"#{r+1}"
                        bbox = draw.textbbox((0, 0), txt, font=self.font_rank)
                        draw.text((rx - (bbox[2]-bbox[0])//2, chart_bottom + 8), txt, fill=text_dim, font=self.font_rank)
    
                # Year & Title
                yr = str(int(float(time_idx)))
                yb = draw.textbbox((0, 0), yr, font=self.font_year)
                draw.text(((chart_left+chart_right-(yb[2]-yb[0]))//2, (chart_top+chart_bottom-(yb[3]-yb[1]))//2), yr, fill=year_color, font=self.font_year)
                self._draw_title(draw, W, H, zones, text_color)
    
                # Progress
                frac = frame_num / (total_frames - 1)
                draw.rounded_rectangle([chart_left, H-16, chart_right, H-12], radius=2, fill=grid_color)
                draw.rounded_rectangle([chart_left, H-16, chart_left + int(chart_w * frac), H-12], radius=2, fill=line_color)
    
                yield np.asarray(img)

        finally:
            shared_pilmoji.close()

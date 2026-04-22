from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pandas as pd
from typing import Generator

from .themes import Themes
from .layout import LayoutManager
from .emojis import ENTITY_EMOJIS
from pilmoji import Pilmoji


class BarChartRace:
    """
    Ultra-fast bar chart race renderer using Pillow (PIL).
    Renders directly to pixel buffers — 30-50× faster than matplotlib.
    """

    def __init__(self, df: pd.DataFrame, top_n: int = 10, theme: str = 'dark',
                 fmt: str = 'landscape', title: str = "",
                 smoothing: float = 0.015):
        self.df = df
        self.top_n = top_n
        self.theme = theme
        self.fmt = fmt
        self.title = title
        self.smoothing = smoothing

        categories = df.columns
        bar_colors = Themes.PALETTES.get(theme, Themes.PALETTES['dark'])['bars']
        self.colors = {cat: bar_colors[i % len(bar_colors)] for i, cat in enumerate(categories)}

        # Pre-load font (fallback to default if not available)
        try:
            self.font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
            self.font_value = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            self.font_year  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
            self.font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 38)
        except (OSError, IOError):
            try:
                self.font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
                self.font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                self.font_year  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
                self.font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            except (OSError, IOError):
                self.font_label = ImageFont.load_default()
                self.font_value = ImageFont.load_default()
                self.font_year  = ImageFont.load_default()
                self.font_title = ImageFont.load_default()

    def _draw_title(self, draw, W, H, zones, text_color):
        if not self.title: return
        
        # Simple wrapping
        words = self.title.split()
        lines = []
        current_line = []
        max_w = W * 0.9
        
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=self.font_title)
            if bbox[2] - bbox[0] <= max_w:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        # Draw lines
        line_h = 44
        ty = int(H * (1 - zones['title_y']))
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=self.font_title)
            tx = (W - (bbox[2] - bbox[0])) // 2
            draw.text((tx, ty + i * line_h), line, fill=text_color, font=self.font_title)

    def generate_frames(self) -> Generator[np.ndarray, None, None]:
        """Generator yielding RGB numpy arrays rendered via PIL."""
        specs = LayoutManager.FORMATS[self.fmt]
        W = specs['width']
        H = specs['height']
        zones = LayoutManager.get_safe_zones(self.fmt)
        palette = Themes.PALETTES.get(self.theme, Themes.PALETTES['dark'])

        is_landscape = self.fmt == 'landscape'

        # Layout constants (in pixels)
        chart_left   = int(W * zones['chart_left'])
        chart_right  = int(W * zones['chart_right'])
        chart_top    = int(H * (1 - zones['chart_top']))
        chart_bottom = int(H * (1 - zones['chart_bottom']))
        chart_w = chart_right - chart_left
        chart_h = chart_bottom - chart_top

        bar_h = int(chart_h / (self.top_n + 1) * 0.72)
        bar_gap = int(chart_h / (self.top_n + 1))
        bar_radius = max(bar_h // 4, 4)

        smooth_y = {}
        # Add 150 hold frames at the end (5 seconds at 30fps)
        indices = list(self.df.index)
        last_idx = indices[-1]
        num_hold_frames = 150
        indices += [last_idx] * num_hold_frames
        total_frames = len(indices)

        bg_color = palette['bg']
        text_color = palette['text']
        text_dim = palette['text_dim']
        grid_color = palette['grid']
        accent_color = palette['accent']

        # Pre-compute faded year watermark color (10% blend — subtle watermark)
        bg_r, bg_g, bg_b = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
        # On dark bg → blend toward white; on light bg → blend toward black
        bg_luma = (bg_r * 299 + bg_g * 587 + bg_b * 114) / 1000
        wm_r, wm_g, wm_b = (255, 255, 255) if bg_luma < 128 else (0, 0, 0)
        fade = 0.10
        year_color = (int(bg_r + (wm_r - bg_r) * fade),
                      int(bg_g + (wm_g - bg_g) * fade),
                      int(bg_b + (wm_b - bg_b) * fade))

        dummy_img = Image.new('RGB', (1, 1))
        shared_pilmoji = Pilmoji(dummy_img)

        try:
            for frame_num, time_idx in enumerate(indices):
                img = Image.new('RGB', (W, H), bg_color)
                draw = ImageDraw.Draw(img)
                
                shared_pilmoji.image = img
                shared_pilmoji.draw = draw
                pilmoji = shared_pilmoji

                row = self.df.loc[time_idx].dropna()
                sorted_entities = row.sort_values(ascending=False)
                top_entities = sorted_entities.head(self.top_n)
    
                n = len(top_entities)
                max_val = top_entities.max()
                if max_val <= 0:
                    max_val = 1
    
                # ── Compute smooth y-positions ───────────────────────
                target_y_map = {}
                for rank, entity in enumerate(top_entities.index):
                    target_y_map[entity] = rank  # 0 = top, n-1 = bottom

                # Progressively increase smoothing during the hold frames to snap into place
                current_smoothing = self.smoothing
                if frame_num >= total_frames - num_hold_frames:
                    hold_progress = (frame_num - (total_frames - num_hold_frames)) / num_hold_frames
                    current_smoothing = min(1.0, self.smoothing + hold_progress * 0.2)
    
                for entity in top_entities.index:
                    if entity not in smooth_y:
                        smooth_y[entity] = float(target_y_map[entity])
                    else:
                        smooth_y[entity] += current_smoothing * (target_y_map[entity] - smooth_y[entity])
    
                # ── Draw grid lines ──────────────────────────────────
                for i in range(5):
                    gx = chart_left + int(chart_w * i / 4)
                    draw.line([(gx, chart_top), (gx, chart_bottom)], fill=grid_color, width=1)
    
                # ── Draw bars ────────────────────────────────────────
                # Sort entities so overtaking bars (moving up, target - smooth < 0) are drawn LAST (on top)
                def draw_order(ent):
                    return target_y_map[ent] - smooth_y[ent]
                
                ordered_entities = sorted(top_entities.index, key=draw_order, reverse=True)

                for entity in ordered_entities:
                    val = top_entities[entity]
                    rank_y = smooth_y[entity]
    
                    bar_pixel_y = chart_top + int(rank_y * bar_gap) + (bar_gap - bar_h) // 2
                    bar_pixel_w = int((val / max_val) * chart_w * 0.85)
    
                    x0 = chart_left
                    y0 = bar_pixel_y
                    x1 = chart_left + bar_pixel_w
                    y1 = bar_pixel_y + bar_h
    
                    color = self.colors.get(entity, '#888888')
                    draw.rounded_rectangle([x0, y0, x1, y1], radius=bar_radius, fill=color)
    
                    # Entity label — inside bar if it fits, else outside
                    val_text = f'{val:,.0f}'
                    ly = y0 + (bar_h - 18) // 2
                    vy = y0 + (bar_h - 16) // 2
    
                    emoji = ENTITY_EMOJIS.get(entity)
                    display_text = f"{emoji} {entity}" if emoji else entity
    
                    # Pilmoji textbbox handles the emoji size perfectly
                    label_bbox = pilmoji.getsize(display_text, font=self.font_label)
                    label_w = label_bbox[0]
    
                    if label_w + 16 < bar_pixel_w:
                        # Label fits inside the bar
                        pilmoji.text((x0 + 8, ly), display_text, fill='white', font=self.font_label)
                        draw.text((x1 + 6, vy), val_text, fill=text_color, font=self.font_value)
                    else:
                        # Label outside bar, then value after it
                        pilmoji.text((x1 + 6, ly), display_text, fill=text_color, font=self.font_label)
                        draw.text((x1 + 6 + label_w + 6, vy), val_text, fill=text_dim, font=self.font_value)
    
                # ── Year watermark (centered) ─────────────────────────
                current_year = str(int(float(time_idx)))
                year_bbox = draw.textbbox((0, 0), current_year, font=self.font_year)
                yw = year_bbox[2] - year_bbox[0]
                yh = year_bbox[3] - year_bbox[1]
                year_x = (chart_left + chart_right - yw) // 2
                year_y = (chart_top + chart_bottom - yh) // 2
                draw.text((year_x, year_y), current_year,
                          fill=year_color, font=self.font_year)
    
                # ── Title ────────────────────────────────────────────
                self._draw_title(draw, W, H, zones, text_color)
    
                # ── Progress bar ─────────────────────────────────────
                progress_frac = frame_num / max(total_frames - 1, 1)
                prog_y = H - 16
                prog_h = 4
                draw.rounded_rectangle(
                    [chart_left, prog_y, chart_right, prog_y + prog_h],
                    radius=2, fill=grid_color
                )
                if progress_frac > 0.01:
                    fill_w = chart_left + int((chart_right - chart_left) * progress_frac)
                    draw.rounded_rectangle(
                        [chart_left, prog_y, fill_w, prog_y + prog_h],
                        radius=2, fill=accent_color
                    )
    
                # ── Yield as numpy array ─────────────────────────────
                yield np.asarray(img)
    
        finally:
            shared_pilmoji.close()

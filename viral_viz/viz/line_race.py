from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pandas as pd
from typing import Generator

from .themes import Themes
from .layout import LayoutManager


class LineRaceChart:
    """
    Animated ranked line chart renderer using Pillow.
    Shows top-N entities as points on a curve, sorted by value,
    with smooth transitions between time periods.
    """

    def __init__(self, df: pd.DataFrame, top_n: int = 10, theme: str = 'dark',
                 fmt: str = 'landscape', title: str = "",
                 smoothing: float = 0.08):
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
            self.font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
            self.font_axis  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
            self.font_rank  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
        except (OSError, IOError):
            try:
                self.font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
                self.font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
                self.font_year  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
                self.font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
                self.font_axis  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
                self.font_rank  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
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
        if len(points) < 2:
            return points
        if len(points) == 2:
            return points

        # Pad endpoints for Catmull-Rom
        padded = [points[0]] + list(points) + [points[-1]]
        curve = []
        for i in range(1, len(padded) - 2):
            segment = self._catmull_rom(padded[i-1], padded[i], padded[i+1], padded[i+2], num_points=16)
            curve.extend(segment)
        curve.append(points[-1])
        return curve

    def _format_value(self, val):
        """Format large numbers with B/M/K suffixes."""
        if val >= 1e9:
            return f"${val/1e9:,.0f}B"
        elif val >= 1e6:
            return f"${val/1e6:,.0f}M"
        elif val >= 1e3:
            return f"${val/1e3:,.0f}K"
        else:
            return f"{val:,.0f}"

    def generate_frames(self) -> Generator[np.ndarray, None, None]:
        """Generator yielding RGB numpy arrays."""
        specs = LayoutManager.FORMATS[self.fmt]
        W = specs['width']
        H = specs['height']
        zones = LayoutManager.get_safe_zones(self.fmt)
        palette = Themes.PALETTES.get(self.theme, Themes.PALETTES['dark'])

        chart_left   = int(W * zones['chart_left']) + 30
        chart_right  = int(W * zones['chart_right']) - 10
        chart_top    = int(H * (1 - zones['chart_top'])) + 20
        chart_bottom = int(H * (1 - zones['chart_bottom'])) - 30
        chart_w = chart_right - chart_left
        chart_h = chart_bottom - chart_top

        total_frames = len(self.df)

        bg_color = palette['bg']
        text_color = palette['text']
        text_dim = palette['text_dim']
        grid_color = palette['grid']
        accent_color = palette['accent']

        # Glow color (neon green like the reference)
        line_color = '#00E676'
        dot_color = '#00E676'
        glow_color = (0, 230, 118)

        # Year watermark color
        bg_r, bg_g, bg_b = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
        bg_luma = (bg_r * 299 + bg_g * 587 + bg_b * 114) / 1000
        wm_r, wm_g, wm_b = (255, 255, 255) if bg_luma < 128 else (0, 0, 0)
        fade = 0.10
        year_color = (int(bg_r + (wm_r - bg_r) * fade),
                      int(bg_g + (wm_g - bg_g) * fade),
                      int(bg_b + (wm_b - bg_b) * fade))

        # Smooth position tracking
        smooth_vals = {}
        smooth_ranks = {}
        reveal_frames = 60  # Reveal over 2 seconds at 30fps

        for frame_num, time_idx in enumerate(self.df.index):
            reveal_pct = min(frame_num / reveal_frames, 1.0) if frame_num < reveal_frames else 1.0
            
            img = Image.new('RGB', (W, H), bg_color)
            draw = ImageDraw.Draw(img)

            row = self.df.loc[time_idx].dropna()
            # Get current top entities and their ranks
            top_entities = row.sort_values(ascending=False).head(self.top_n)
            # Re-sort ascending for left-to-right drawing (#10 to #1)
            # Actually, reference image shows #1 on left or right?
            # Usually #10 on left, #1 on right (like a podium)
            top_entities = top_entities.sort_values(ascending=True)

            n = len(top_entities)
            if n == 0:
                yield np.asarray(img)
                continue

            max_val = top_entities.max()
            min_val = 0
            if max_val <= 0: max_val = 1

            # Update smooth positions
            current_top_indices = top_entities.index
            target_ranks = {entity: i for i, entity in enumerate(current_top_indices)}

            for entity in current_top_indices:
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
                    smooth_ranks[entity] += 0.05 * (target_rank - smooth_ranks[entity])

            # ── Y-axis grid lines & labels ────────────────────────
            num_grid = 5
            for i in range(num_grid + 1):
                gy = chart_bottom - int(chart_h * i / num_grid)
                draw.line([(chart_left, gy), (chart_right, gy)], fill=grid_color, width=1)
                grid_val = min_val + (max_val - min_val) * i / num_grid
                label = self._format_value(grid_val)
                draw.text((chart_left - 5, gy - 6), label, fill=text_dim,
                          font=self.font_axis, anchor="ra")

            # ── Compute dot positions ─────────────────────────────
            dot_positions = []
            reveal_x_limit = chart_left + int(reveal_pct * chart_w)

            for entity in current_top_indices:
                val = smooth_vals[entity]
                rank = smooth_ranks[entity]
                
                x = chart_left + int((rank / max(self.top_n - 1, 1)) * chart_w)
                y_frac = (val - min_val) / (max_val - min_val)
                y = chart_bottom - int(y_frac * chart_h)
                
                if x <= reveal_x_limit:
                    dot_positions.append((x, y, entity, val))
            
            # Sort dot_positions by X so the line draws correctly left-to-right
            dot_positions.sort(key=lambda d: d[0])

            # ── Draw smooth curve ─────────────────────────────────
            if len(dot_positions) >= 2:
                raw_points = [(dp[0], dp[1]) for dp in dot_positions]
                curve_points = self._smooth_curve(raw_points)
                
                # Area fill
                fill_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                fill_draw = ImageDraw.Draw(fill_layer)
                poly_points = [(chart_left, chart_bottom)] + curve_points + [(curve_points[-1][0], chart_bottom)]
                fill_draw.polygon(poly_points, fill=(0, 230, 118, 30))
                img.paste(fill_layer, (0, 0), fill_layer)

                # Draw glow (thicker, semi-transparent line behind)
                for i in range(len(curve_points) - 1):
                    x1, y1 = curve_points[i]
                    x2, y2 = curve_points[i + 1]
                    draw.line([(x1, y1), (x2, y2)], fill=grid_color, width=5)

                # Draw main line
                for i in range(len(curve_points) - 1):
                    x1, y1 = curve_points[i]
                    x2, y2 = curve_points[i + 1]
                    draw.line([(x1, y1), (x2, y2)], fill=line_color, width=2)

            # ── Draw dots and labels ──────────────────────────────
            for x, y, entity, val in dot_positions:
                # Outer glow dot
                draw.ellipse([x-6, y-6, x+6, y+6], fill=grid_color)
                # Inner dot
                draw.ellipse([x-4, y-4, x+4, y+4], fill=dot_color)

                # Floating Label Box (Glassmorphism look)
                val_text = self._format_value(val)
                label_bbox = draw.textbbox((0, 0), entity, font=self.font_label)
                val_bbox = draw.textbbox((0, 0), val_text, font=self.font_value)
                
                box_w = max(label_bbox[2]-label_bbox[0], val_bbox[2]-val_bbox[0]) + 24
                box_h = 48
                
                bx0 = x - box_w // 2
                by0 = y - 60
                bx1 = bx0 + box_w
                by1 = by0 + box_h
                
                # Clamp box to chart bounds
                if bx0 < chart_left:
                    bx1 += (chart_left - bx0)
                    bx0 = chart_left
                if bx1 > chart_right:
                    bx0 -= (bx1 - chart_right)
                    bx1 = chart_right

                # Draw box
                draw.rounded_rectangle([bx0, by0, bx1, by1], radius=8, fill=(10, 10, 15))
                draw.rounded_rectangle([bx0, by0, bx1, by1], radius=8, outline=(60, 60, 70), width=1)

                # Draw text inside box
                draw.text((bx0 + 12, by0 + 4), entity, fill='white', font=self.font_label)
                draw.text((bx0 + 12, by0 + 26), val_text, fill='#AAA', font=self.font_value)

            # ── Rank labels at bottom (fixed) ─────────────────────
            for r in range(self.top_n):
                rx = chart_left + int((r / max(self.top_n - 1, 1)) * chart_w)
                if rx <= reveal_x_limit:
                    rank_text = f"#{r + 1}"
                    rb = draw.textbbox((0, 0), rank_text, font=self.font_rank)
                    rw = rb[2] - rb[0]
                    draw.text((rx - rw // 2, chart_bottom + 8), rank_text,
                              fill=text_dim, font=self.font_rank)

            # ── Year watermark (centered) ─────────────────────────
            current_year = str(int(float(time_idx)))
            year_bbox = draw.textbbox((0, 0), current_year, font=self.font_year)
            yw = year_bbox[2] - year_bbox[0]
            yh = year_bbox[3] - year_bbox[1]
            year_x = (chart_left + chart_right - yw) // 2
            year_y = (chart_top + chart_bottom - yh) // 2
            draw.text((year_x, year_y), current_year,
                      fill=year_color, font=self.font_year)

            # ── Title ─────────────────────────────────────────────
            if self.title:
                bbox = draw.textbbox((0, 0), self.title, font=self.font_title)
                tw = bbox[2] - bbox[0]
                tx = (W - tw) // 2
                ty = int(H * (1 - zones['title_y']))
                draw.text((tx, ty), self.title, fill=text_color, font=self.font_title)

            # ── Progress bar ──────────────────────────────────────
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
                    radius=2, fill=line_color
                )

            yield np.asarray(img)

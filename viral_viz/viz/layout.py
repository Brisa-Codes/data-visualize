from typing import Dict, Tuple


class LayoutManager:
    """Safe zones and figure sizes for 16:9 and 9:16 layouts."""

    FORMATS = {
        'landscape': {'width': 1280, 'height': 720, 'dpi': 100},
        'portrait':  {'width': 720,  'height': 1280, 'dpi': 100}
    }

    @staticmethod
    def get_figure_size(fmt: str) -> Tuple[float, float]:
        specs = LayoutManager.FORMATS.get(fmt, LayoutManager.FORMATS['landscape'])
        return (specs['width'] / specs['dpi'], specs['height'] / specs['dpi'])

    @staticmethod
    def get_safe_zones(fmt: str) -> Dict[str, float]:
        if fmt == 'portrait':
            return {
                'title_y':       0.93,
                'chart_top':     0.88,
                'chart_bottom':  0.08,
                'chart_left':    0.06,
                'chart_right':   0.82,
                'year_x':        0.92,
                'year_y':        0.12,
            }
        else:
            return {
                'title_y':       0.95,
                'chart_top':     0.88,
                'chart_bottom':  0.08,
                'chart_left':    0.06,
                'chart_right':   0.92,
                'year_x':        0.92,
                'year_y':        0.12,
            }

    @staticmethod
    def apply_layout(fig, ax, fmt: str):
        zones = LayoutManager.get_safe_zones(fmt)
        fig.subplots_adjust(
            top=zones['chart_top'],
            bottom=zones['chart_bottom'],
            left=zones['chart_left'],
            right=zones['chart_right']
        )

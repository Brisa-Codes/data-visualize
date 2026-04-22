import matplotlib.pyplot as plt

class Themes:
    """Professional color palettes and typography for cinematic charts."""

    PALETTES = {
        'dark': {
            'bg':        '#0f0f13',
            'card_bg':   '#18182a',
            'text':      '#e8e8ec',
            'text_dim':  '#6b6b80',
            'grid':      '#2a2a3d',
            'accent':    '#BB86FC',
            'bars': [
                '#7C4DFF', '#00E5FF', '#FF6D00', '#00E676',
                '#FF4081', '#FFEA00', '#18FFFF', '#FF9100',
                '#69F0AE', '#EA80FC', '#B2FF59', '#40C4FF',
            ]
        },
        'light': {
            'bg':        '#f8f9fa',
            'card_bg':   '#ffffff',
            'text':      '#1a1a2e',
            'text_dim':  '#888899',
            'grid':      '#e8e8f0',
            'accent':    '#6200EE',
            'bars': [
                '#6200EE', '#0097A7', '#E64A19', '#2E7D32',
                '#C2185B', '#F9A825', '#00838F', '#D84315',
                '#1B5E20', '#8E24AA', '#827717', '#0277BD',
            ]
        }
    }

    @staticmethod
    def apply_theme(ax, fig, theme_name: str = 'dark'):
        """Applies theme to figure and axes. Returns palette dict."""
        palette = Themes.PALETTES.get(theme_name, Themes.PALETTES['dark'])

        fig.patch.set_facecolor(palette['bg'])
        ax.set_facecolor(palette['bg'])

        ax.grid(True, axis='x', color=palette['grid'], linestyle='-', alpha=0.5, linewidth=0.5)
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.tick_params(axis='both', colors=palette['text'], length=0, labelsize=0)
        ax.tick_params(axis='x', labelsize=0)

        return palette

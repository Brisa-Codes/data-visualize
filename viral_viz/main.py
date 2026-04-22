import click
import os
from data.fetcher import DataFetcher
from data.preprocessor import DataPreprocessor
from data.suggester import TrendSuggester
from audio.mixer import AudioMixer
from audio.sync import AudioSync
from export.packager import DualPackager
import pandas as pd

@click.command()
@click.option('--topic', help='Topic or World Bank indicator to fetch (e.g. NY.GDP.MKTP.CD)')
@click.option('--years', help='Year range, e.g. 1990-2023')
@click.option('--input', 'input_csv', help='Path to input CSV file')
@click.option('--style', default='dark', type=click.Choice(['dark', 'light']), help='Theme style')
@click.option('--speed', default='normal', type=click.Choice(['slow', 'normal', 'fast']), help='Animation speed')
@click.option('--format', 'fmt', default='landscape', type=click.Choice(['landscape', 'portrait', 'both']), help='Output format')
@click.option('--music', help='Path to background music file')
@click.option('--sfx', help='Path to ping sound effect')
@click.option('--output', default='./renders', help='Output directory')
@click.option('--suggest', is_flag=True, help='Get trending dataset ideas with viral scores')
@click.option('--title', default='', help='Title for the visualization overlay')
def cli(topic, years, input_csv, style, speed, fmt, music, sfx, output, suggest, title):
    """Viral Data Visualization Generator CLI"""
    
    if suggest:
        click.echo("🔥 Trending Datasets Ideas:")
        suggestions = TrendSuggester.get_suggestions()
        for idx, s in enumerate(suggestions, 1):
            click.echo(f"\n{idx}. {s['topic']}")
            click.echo(f"   Indicator: {s['indicator']}")
            click.echo(f"   Description: {s['description']}")
            click.echo(f"   Viral Score: {s['viral_score_est']:.1f}/100")
        return

    os.makedirs(output, exist_ok=True)
    
    df = None
    if input_csv:
        click.echo(f"Loading data from {input_csv}...")
        df = DataFetcher.from_csv(input_csv)
    elif topic and years:
        start_year, end_year = map(int, years.split('-'))
        click.echo(f"Fetching data from World Bank for {topic} ({start_year}-{end_year})...")
        df = DataFetcher.from_world_bank(topic, start_year, end_year)
    else:
        click.echo("Error: Please provide either --input or --topic with --years.")
        return
        
    click.echo("Preprocessing and interpolating frames...")
    fps = 60
    if speed == 'fast': seconds_per_period = 0.5
    elif speed == 'slow': seconds_per_period = 2.0
    else: seconds_per_period = 1.0
        
    df_clean = DataPreprocessor.clean_data(df)
    df_interpolated = DataPreprocessor.interpolate_frames(df_clean, fps=fps, seconds_per_period=seconds_per_period)
    
    click.echo("Analyzing rank changes for SFX synchronization...")
    rank_changes = AudioSync.get_rank_change_times(df_interpolated, fps)
    
    duration = len(df_interpolated) / fps
    click.echo(f"Animation duration: {duration:.2f} seconds.")
    
    audio_clip = None
    if music or sfx:
        click.echo("Mixing audio track...")
        mixer = AudioMixer(bg_music_path=music, sfx_ping_path=sfx)
        audio_clip = mixer.generate_audio(duration=duration, rank_change_times=rank_changes)
        
    click.echo("Rendering video frames...")
    base_name = "viral_viz_output"
    
    if fmt == 'both':
        outputs = DualPackager.export_both(
            df_interpolated, top_n=10, theme=style, fps=fps, 
            output_dir=output, base_name=base_name, audio_clip=audio_clip, title=title
        )
        click.echo(f"✅ Render complete! Files saved to: {', '.join(outputs)}")
    else:
        from viz.bar_race import BarChartRace
        from export.renderer import VideoRenderer
        
        race = BarChartRace(df_interpolated, top_n=10, theme=style, fmt=fmt, title=title)
        out_path = os.path.join(output, f"{base_name}_{fmt}.mp4")
        VideoRenderer.render_generator(race.generate_frames(), fps, out_path, audio_clip)
        click.echo(f"✅ Render complete! File saved to: {out_path}")

if __name__ == '__main__':
    cli()

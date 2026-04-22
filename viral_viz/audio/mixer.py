import os
from moviepy import AudioFileClip, CompositeAudioClip, AudioClip

class AudioMixer:
    """Mixes background music with dynamic sound effects."""
    
    def __init__(self, bg_music_path: str = None, sfx_ping_path: str = None):
        self.bg_music_path = bg_music_path
        self.sfx_ping_path = sfx_ping_path
        
    def generate_audio(self, duration: float, rank_change_times: list):
        """
        Creates an audio track for the video.
        - Loops or trims background music.
        - Applies a 2-second fade-out.
        - Adds ping SFX when #1 rank changes.
        """
        clips = []
        
        if self.bg_music_path and os.path.exists(self.bg_music_path):
            bg_clip = AudioFileClip(self.bg_music_path)
            
            if bg_clip.duration < duration:
                from moviepy.audio.fx.all import audio_loop
                bg_clip = audio_loop(bg_clip, duration=duration)
            else:
                bg_clip = bg_clip.subclip(0, duration)
                
            bg_clip = bg_clip.audio_fadeout(2.0)
            bg_clip = bg_clip.volumex(0.6)  # Level-matching background
            clips.append(bg_clip)
            
        if self.sfx_ping_path and os.path.exists(self.sfx_ping_path):
            for t in rank_change_times:
                if t < duration:
                    ping = AudioFileClip(self.sfx_ping_path).set_start(t).volumex(1.0)
                    clips.append(ping)
                    
        if clips:
            return CompositeAudioClip(clips)
        
        return AudioClip(lambda t: [0, 0], duration=duration)

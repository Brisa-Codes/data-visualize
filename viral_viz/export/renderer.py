import os
import imageio
from moviepy import VideoFileClip
from typing import Generator, Callable, Optional
import numpy as np


class VideoRenderer:
    """Frame-to-video pipeline using imageio/ffmpeg."""

    @staticmethod
    def render_generator(frame_gen: Generator[np.ndarray, None, None],
                         fps: int,
                         output_path: str,
                         audio_clip=None,
                         total_frames: int = 0,
                         on_progress: Optional[Callable[[int, int], None]] = None):
        """
        Streams frames to disk.  Calls on_progress(current, total) after
        every frame so the UI can update a progress bar.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        writer = imageio.get_writer(output_path, fps=fps, codec='libx264',
                                    macro_block_size=8)

        for i, frame in enumerate(frame_gen):
            writer.append_data(frame)
            if on_progress and total_frames > 0 and i % 10 == 0:
                on_progress(i + 1, total_frames)

        writer.close()

        if audio_clip is not None:
            video = VideoFileClip(output_path)
            video = video.set_audio(audio_clip)
            final_path = output_path.replace('.mp4', '_audio.mp4')
            video.write_videofile(final_path, codec="libx264",
                                  audio_codec="aac", logger=None)
            video.close()
            os.replace(final_path, output_path)

        return output_path

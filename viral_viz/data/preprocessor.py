import pandas as pd
import numpy as np

def ease_in_out_cubic(t: float) -> float:
    """Cubic easing function. t is between 0 and 1."""
    if t < 0.5:
        return 4 * t**3
    else:
        return 1 - ((-2 * t + 2)**3) / 2

class DataPreprocessor:
    """Handles cleaning, interpolation, and ranking of datasets."""

    @staticmethod
    def clean_data(df: pd.DataFrame, drop_threshold: float = 0.5) -> pd.DataFrame:
        """
        Drops columns that have too many missing values.
        """
        threshold = len(df) * drop_threshold
        df = df.dropna(axis=1, thresh=threshold)
        return df

    @staticmethod
    def interpolate_frames(df: pd.DataFrame, fps: int = 60,
                           seconds_per_period: float = 1.0,
                           max_duration: float = 30.0) -> pd.DataFrame:
        """
        Interpolates data between periods using cubic easing for cinematic bar transitions.
        Auto-caps total duration to max_duration seconds.
        """
        df = df.copy()

        # 1. Linear interpolation of missing years
        min_year = int(df.index.min())
        max_year = int(df.index.max())
        df = df.reindex(np.arange(min_year, max_year + 1))
        df = df.interpolate(method='linear').ffill().bfill()

        num_periods = len(df) - 1

        # 2. Auto-cap: if total duration would exceed max_duration, reduce seconds_per_period
        if num_periods * seconds_per_period > max_duration and num_periods > 0:
            seconds_per_period = max_duration / num_periods

        # 3. Frame generation with cubic easing
        frames_per_period = max(int(fps * seconds_per_period), 1)

        original_idx = df.index.values
        new_data = []
        new_indices = []
        columns = df.columns

        for i in range(num_periods):
            start_idx = original_idx[i]
            s1 = df.iloc[i].values
            s2 = df.iloc[i + 1].values

            for frame in range(frames_per_period):
                t = frame / frames_per_period
                eased_t = ease_in_out_cubic(t)
                s_t = s1 + (s2 - s1) * eased_t
                new_data.append(s_t)
                new_indices.append(start_idx + t)

        # Add the final frame
        new_data.append(df.iloc[-1].values)
        new_indices.append(original_idx[-1])

        df_eased = pd.DataFrame(new_data, index=new_indices, columns=columns)
        return df_eased

import pandas as pd

class AudioSync:
    """Calculates timestamps for sound effects based on data states."""
    
    @staticmethod
    def get_rank_change_times(df: pd.DataFrame, fps: int) -> list:
        """
        Analyzes the interpolated dataframe to find exactly when the #1 rank changes.
        Returns a list of timestamps in seconds.
        """
        rank_change_times = []
        current_leader = None
        
        for i in range(len(df)):
            row = df.iloc[i]
            leader = row.idxmax()
            
            if current_leader is None:
                current_leader = leader
            elif leader != current_leader:
                time_sec = i / fps
                rank_change_times.append(time_sec)
                current_leader = leader
                
        return rank_change_times

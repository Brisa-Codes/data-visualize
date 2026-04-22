import pandas as pd
import numpy as np
from typing import List, Dict

class TrendSuggester:
    """Calculates a 'Viral Score' for topics based on volatility and momentum."""
    
    @staticmethod
    def calculate_viral_score(df: pd.DataFrame) -> float:
        """
        Calculate viral score based on volatility (standard deviation sigma)
        and maximum delta (surprise factor).
        """
        pct_change = df.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
        
        # Volatility is the standard deviation of changes (Sigma)
        volatility = pct_change.std().mean() 
        
        # Max delta is the biggest single jump in the dataset
        max_delta = pct_change.max().max()
        
        if pd.isna(volatility): volatility = 0
        if pd.isna(max_delta): max_delta = 0
            
        score = (volatility * 0.6) + (max_delta * 0.4)
        return min(float(score * 100), 100.0)

    @staticmethod
    def get_suggestions() -> List[Dict]:
        """Returns trending datasets with pre-calculated estimated viral scores."""
        return [
            {
                "topic": "Fastest Growing GDP",
                "indicator": "NY.GDP.MKTP.CD",
                "description": "Gross Domestic Product. High volatility in emerging markets.",
                "viral_score_est": 85.4
            },
            {
                "topic": "Global Population Shifts",
                "indicator": "SP.POP.TOTL",
                "description": "Total population by country. Massive scale changes.",
                "viral_score_est": 42.1
            },
            {
                "topic": "Tech Adoption (Internet Users)",
                "indicator": "IT.NET.USER.ZS",
                "description": "Internet users (% of population). Explosive growth.",
                "viral_score_est": 92.7
            },
            {
                "topic": "CO2 Emissions by Country",
                "indicator": "EN.ATM.CO2E.KT",
                "description": "Carbon emissions over time. Highly debated, very shareable.",
                "viral_score_est": 78.2
            }
        ]

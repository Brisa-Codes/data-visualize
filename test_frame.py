import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import pandas as pd
from viral_viz.viz.bar_race import BarChartRace

data = {
    "year": [2020, 2021],
    "USA": [100, 110],
    "China": [90, 95]
}
df = pd.DataFrame(data).set_index("year")

chart = BarChartRace(df, top_n=2)
gen = chart.generate_frames()
frame1 = next(gen)

from PIL import Image
Image.fromarray(frame1).save("test_frame.png")
print("Saved test_frame.png")

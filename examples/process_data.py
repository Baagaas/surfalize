from pathlib import Path

import pandas as pd

data_path = Path.cwd() / 'data' / 'cropped' / 'results_fft_morph_depth.csv'

df = pd.read_excel(data_path)

print(df)
from pathlib import Path
import pandas as pd
import numpy as np

data_path = Path(r'\\vs-grp04.zih.tu-dresden.de\messda\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files\55fs\cropped_at_str_center_100um\fft-filter_P=5.32_filt-r=20_orders=7_stop\results_mean_height_std.xlsx')

df = pd.read_excel(data_path)

grouped = df.groupby(['Pulse_Duration', 'Fluence', 'Pulses'])[['Sa', 'Sq', 'Sdr', 'height_mean', 'height_std']].mean().reset_index()
grouped['std_relative'] = grouped['height_std'] / grouped['height_mean'] * 100
df = grouped

pulses = np.sort(df['Pulses'].unique())
fluences = np.sort(df['Fluence'].unique())

# ---------- numerical interpolation on a fine grid ----------
from scipy.interpolate import griddata  # type: ignore

# original scattered points
points = df[['Pulses', 'Fluence']].to_numpy()
values = df['Sq'].to_numpy()

# create a finer regular grid
pulse_grid = np.linspace(pulses.min(), pulses.max(), 500)
fluence_grid = np.linspace(fluences.min(), fluences.max(), 500)
P_grid, F_grid = np.meshgrid(pulse_grid, fluence_grid)

# interpolate values onto the fine grid
Z_grid = griddata(points, values, (P_grid, F_grid), method='nearest')
# if 'cubic' is too noisy or fails, try method='linear' or 'nearest'
# Z_grid = griddata(points, values, (P_grid, F_grid), method='linear')

import matplotlib.pyplot as plt

plt.figure(figsize=(6, 3))
im = plt.imshow(
    Z_grid,
    aspect='auto',
    origin='lower',
    extent=(pulse_grid.min(), pulse_grid.max(),
            fluence_grid.min(), fluence_grid.max()),
    cmap='viridis',
    interpolation='none',   # visual smoothing on top of numerical interpolation
)
# plt.colorbar(im, label='Structure height, µm')
# plt.colorbar(im, label='Relative Std. Dev. (%)')
plt.colorbar(im, label='Sq parameter, µm')
plt.xlabel('Pulse Number')
plt.ylabel('Fluence, J/cm²')
# plt.title('Silicon at 55 fs Pulse Duration')
plt.tight_layout()

# Overlay original datapoints: not filled, black outline
for _, row in df.iterrows():
    plt.scatter(
        row['Pulses'],
        row['Fluence'],
        facecolors='none',
        edgecolors='black',
        s=20,
        linewidths=0.5
    )

plt.show()

print(df)
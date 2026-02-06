from pathlib import Path
import pandas as pd
import numpy as np

data_path = Path(r'\\vs-grp04.zih.tu-dresden.de\messda\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files\55fs\cropped_at_str_center_600um\fft-filter_P=5.32_filt-r=20_orders=3\morphed_size_y=1px_x=5.32um\cropped_center_width=100um\results_mean_height_std.xlsx')

df = pd.read_excel(data_path)

grouped = df.groupby(['Pulse_Duration', 'Fluence', 'Pulses'])[['height_mean', 'height_std']].mean().reset_index()
grouped['std_relative'] = grouped['height_std'] / grouped['height_mean'] * 100
df = grouped

pulses = np.sort(df['Pulses'].unique())
fluences = np.sort(df['Fluence'].unique())

array_2d = np.full((len(fluences), len(pulses)), np.nan)

for i, fluence in enumerate(fluences):
    for j, pulse in enumerate(pulses):
        value = df[(df['Fluence'] == fluence) & (df['Pulses'] == pulse)]['height_mean']
        if not value.empty:
            array_2d[i, j] = value.values[0]

import matplotlib.pyplot as plt

plt.figure(figsize=(8, 6))
im = plt.imshow(
    array_2d,
    aspect='auto',
    origin='lower',
    extent=(pulses[0], pulses[-1], fluences[0], fluences[-1]),
    interpolation='bicubic'  # Use bicubic interpolation for higher resolution
)
plt.colorbar(im, label='Structure height, µm')
# plt.colorbar(im, label='Relative Std. Dev. (%)')
plt.xlabel('Pulse Number')
plt.ylabel('Fluence, J/cm²')
plt.title('Silicon at 55 fs Pulse Duratio')

# Overlay datapoints: not filled, black outline
for _, row in df.iterrows():
    plt.scatter(
        row['Pulses'],
        row['Fluence'],
        facecolors='none',
        edgecolors='black',
        s=60,
        linewidths=1
    )

plt.show()

print(df)
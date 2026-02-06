from pathlib import Path
import pandas as pd
import numpy as np

data_path = Path(r'\\vs-grp04.zih.tu-dresden.de\messda\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files\55fs\cropped_at_str_center_100um\fft-filter_P=5.32_filt-r=20_orders=7\morphed_size_y=1px_x=5.32um\results_mean_height_std.xlsx')

df = pd.read_excel(data_path)

grouped = df.groupby(['Pulse_Duration', 'Fluence', 'Pulses'])[['height_mean', 'height_std']].mean().reset_index()
grouped['std_relative'] = grouped['height_std'] / grouped['height_mean'] * 100
df = grouped

pulses = np.sort(df['Pulses'].unique())
fluences = np.sort(df['Fluence'].unique())

def create_2d_array(df, rows, rows_name_df, cols, cols_name_df, value_name='height_mean'):
    array_2d = np.full((len(rows), len(cols)), np.nan)
    for i, fluence in enumerate(rows):
        for j, pulse in enumerate(cols):
            value = df[(df[rows_name_df] == fluence) & (df[cols_name_df] == pulse)][value_name]
            if not value.empty:
                array_2d[i, j] = value.values[0]
    return array_2d

array_2d_height = create_2d_array(df, pulses, 'Pulses', fluences, 'Fluence', value_name='height_mean')
array_2d_stddev = create_2d_array(df, pulses, 'Pulses', fluences, 'Fluence', value_name='height_std')
array_2d_stddev_rel = create_2d_array(df, pulses, 'Pulses', fluences, 'Fluence', value_name='std_relative')

_and_stddev = np.empty((array_2d_height.shape[0], array_2d_height.shape[1] * 2))
_and_stddev[:, 0::2] = array_2d_height
_and_stddev[:, 1::2] = array_2d_stddev


def save_height_and_stddev_to_excel(array_2d, rows, cols, output_path):
    col_names = []
    for col in cols:
        col_names.extend([f"{col}", f"{col}"])
    output_df = pd.DataFrame(array_2d, index=rows, columns=col_names)
    output_df.index.name = 'Pulses'
    output_df.reset_index(inplace=True)
    output_df.to_excel(output_path, index=False)

def save_array_2d_to_excel(array_2d, rows, cols, output_path):
    output_df = pd.DataFrame(array_2d, index=rows, columns=cols)
    output_df.index.name = 'Pulses'
    output_df.reset_index(inplace=True)
    output_df.columns = ['Pulses'] + list(output_df.columns[1:])
    output_df.to_excel(output_path, index=False)

save_array_2d_to_excel(array_2d_height, pulses, fluences, data_path.parent / 'Height.xlsx')
save_array_2d_to_excel(array_2d_stddev, pulses, fluences, data_path.parent / 'StdDev.xlsx')
save_array_2d_to_excel(array_2d_stddev_rel, pulses, fluences, data_path.parent / 'StdDev_Relative.xlsx')
save_height_and_stddev_to_excel(_and_stddev, pulses, fluences, data_path.parent / 'Height_and_StdDev.xlsx')
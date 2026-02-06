from functools import partial
from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np
from surfalize.addons_bv import operation_batch, process_files, parameters, operations, help_fncs
from surfalize import Surface
import pandas as pd

from surfalize.batch import Batch

main_data_path = Path(
    r'E:\LocalData\EffPuls\Si\55fs'
    )
file_filter = 'Si_55fs_1.80Jcm2_009Pulses_*.sur'
structure_period = 5.32           
crop_width = 100
save_plots = True
filter_radius=100
orders=7
filter_type='pass'

material='Si'
pulse_duration='55fs'

# file list that has to be processed
files_init =['Si_55fs_1.80Jcm2_150Pulses_3']   
files = [f"{name}.sur" for name in files_init]
# files = [] # comment this line to process the above file list, if not commented - process all files in the directory above    
files = []



def crop_based_on_file(surf: Surface, processed_file_path: Path) -> None:
    file_name = processed_file_path.stem
    df = pd.read_excel(processed_file_path.parent.parent / 'center_positions.xlsx')
    
    value = df[df.iloc[:, 0] == file_name].iloc[0, 1]
    try:
        x = float(str(value))
    except (TypeError, ValueError):
        raise ValueError(f"Center position for file '{file_name}' is not a valid float: {value}")
    
    if x is None:
        raise ValueError(f"Center position for file '{file_name}' not found in 'center_positions.xlsx'.")
    else:
        operation_batch.crop_at_x_position(surf, x, crop_width=crop_width, debug_info=False)
        surf.level(inplace=True)  

def make_fft_filtering_pass(surf: Surface) -> None:
    surf.fill_nonmeasured(method='nearest', inplace=True)
    operation_batch.fft_filter_periodic(surf, type='pass', 
                        str_period_um=structure_period, filter_radius=filter_radius, orders=orders, plot_fft=False)

def make_fft_filtering_stop(surf: Surface) -> None:
    surf.fill_nonmeasured(method='nearest', inplace=True)
    operation_batch.fft_filter_periodic(surf, type='stop', 
                        str_period_um=structure_period, filter_radius=filter_radius, orders=orders, plot_fft=False)

def make_morph_filter(surf: Surface) -> None:
    operation_batch.filter_morph(surf, structure_size_um=(surf.step_y, structure_period))
    

def process_batch_mean_height_std(data_path, file_filter='*.sur', make_fft_filter=False, filter_type='pass', morph_filter=False):
    filepaths = data_path.glob(file_filter)
    # filepaths = batch_path.glob('Si_55fs_1.00Jcm2_150Pulses_1.sur')
    
    batch = Batch(filepaths)

    pattern = '<Material|str|>_' \
                '<Pulse_Duration|int||fs>_' \
                '<Fluence|float||Jcm2>_' \
                '<Pulses|int||Pulses>_' \
                '<Measurement|int>'
    batch.extract_from_filename(pattern)

    if make_fft_filter:
        if filter_type == 'stop':
            batch.custom_operation(make_fft_filtering_stop)
        elif filter_type == 'pass':
            batch.custom_operation(make_fft_filtering_pass)
    
    if morph_filter:
        batch.custom_operation(make_morph_filter)

    batch.Sa().Sq().Sdr()
    batch.custom_parameter(parameters.calc_mean_height_std)

    filename = f'results_{material}_{pulse_duration}fs_fft-filter_P={structure_period}_filt-r={filter_radius}_orders={orders}_type={filter_type}.xlsx'
    
    result = batch.execute(multiprocessing=False, saveto=data_path / filename)
    df = result.get_dataframe()
    print(df)
    print(f"Results saved to: {data_path / filename}")
    return df, filename

if __name__ == "__main__":
    data_path = main_data_path
    # # ===2 find structure center and crop around it===
    save_folder_name='cropped_at_str_center_100um'  

    # process_files.process_surface_files(data_path, process_func=crop_based_on_file, file_list=files,
    #                 file_filter='*.plux', save_processed=True, save_folder_name=save_folder_name, format='sur', save_plot=save_plots)
    
    data_path = data_path / save_folder_name

    #===3 apply FFT filtering===
    save_folder_name=f'fft-filter_P={structure_period}_filt-r={filter_radius}_orders={orders}_stop'
    
    process_files.process_surface_files(data_path, process_func=make_fft_filtering_pass, file_list=files, file_filter=file_filter,
                                        save_processed=True, save_folder_name=save_folder_name, 
                                        format='sur', save_plot=save_plots)

    data_path = data_path / save_folder_name

    #===4 apply morphological filtering===
    save_folder_name=f'morphed_size_y=1px_x={structure_period}um'
    
    process_files.process_surface_files(data_path, process_func=make_morph_filter, file_list=files, file_filter=file_filter,
                                        save_processed=True, save_folder_name=save_folder_name,
                                        format='sur', save_plot=save_plots)
    
    data_path = data_path / save_folder_name

    # # ==4 measure mean height std and save to excel==
    # data_path = Path(
    #     r'E:\LocalData\EffPuls\Si\55fs\cropped_at_str_center_100um'
    #     )        

    # df_pass, filename_pass = process_batch_mean_height_std(data_path, file_filter=file_filter, make_fft_filter=True, filter_type='pass', morph_filter=True)
    # df_stop, filename_stop = process_batch_mean_height_std(data_path, file_filter=file_filter, make_fft_filter=True, filter_type='stop', morph_filter=True)

    # # ===5 process data and plot===
    # def create_2d_array(df, rows_name_df, cols_name_df, value_name):
    #     rows = np.sort(df[rows_name_df].unique())
    #     cols = np.sort(df[cols_name_df].unique())
    #     array_2d = np.full((len(rows), len(cols)), np.nan)
    #     for i, fluence in enumerate(rows):
    #         for j, pulse in enumerate(cols):
    #             value = df[(df[rows_name_df] == fluence) & (df[cols_name_df] == pulse)][value_name]
    #             if not value.empty:
    #                 array_2d[i, j] = value.values[0]
    #     return array_2d
    
    # process data
    # filename_pass='results_Si_55fsfs_fft-filter_P=5.32_filt-r=20_orders=7_type=pass.xlsx'
    # filename_stop='results_Si_55fsfs_fft-filter_P=5.32_filt-r=20_orders=7_type=stop.xlsx'
    # df_pass = pd.read_excel(data_path / filename_pass)
    # df_stop = pd.read_excel(data_path / filename_stop)
    
    
    # grouped = df_pass.groupby(['Pulse_Duration', 'Fluence', 'Pulses'])[['Sa', 'Sq', 'Sdr', 'height_mean', 'height_std']].mean().reset_index()
    # grouped['std_relative'] = grouped['height_std'] / grouped['height_mean'] * 100
    # df_pass = grouped

    # grouped = df_stop.groupby(['Pulse_Duration', 'Fluence', 'Pulses'])[['Sa', 'Sq', 'Sdr', 'height_mean', 'height_std']].mean().reset_index()
    # grouped['std_relative'] = grouped['height_std'] / grouped['height_mean'] * 100
    # df_stop = grouped

    # pulses = np.sort(df_pass['Pulses'].unique())
    # fluences = np.sort(df_pass['Fluence'].unique())

    # height_pass = create_2d_array(df_pass, 'Pulses', 'Fluence', value_name='height_mean')
    # stddev_pass = create_2d_array(df_pass, 'Pulses', 'Fluence', value_name='height_std')
    # stddev_rel_pass = create_2d_array(df_pass, 'Pulses', 'Fluence', value_name='std_relative')

    # # Plot each row of height_pass in a single scatter plot
    # plt.figure(figsize=(8, 6))
    # for i, fluence in enumerate(fluences):
    #     plt.scatter(pulses, height_pass[:, i], label=f'Fluence {fluence}')
    # plt.xlabel('Pulses')
    # plt.ylabel('Height (mean)')
    # plt.title('Height vs Pulses for Different Fluences')
    # plt.legend(title='Fluence')
    # plt.tight_layout()
    # plt.show()





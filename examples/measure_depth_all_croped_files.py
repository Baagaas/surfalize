from surfalize import Surface, Batch
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
from pathlib import Path
from surfalize.addons_bv import parameters, operation_batch

from functools import partial

if __name__ == "__main__":
    data_path = Path.cwd() / 'data' / 'cropped_100um'
    crop_folder_name = 'cropped'
    file_name = 'Steel_55fs_1.8Jcm2_005Pulses_1'
    data_path = Path(
        r'\\vs-grp04.zih.tu-dresden.de\messda\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files\55fs\cropped_at_str_center_100um\fft-filter_P=5.32_filt-r=20_orders=7_stop'
        )        
    
    batch_path = data_path
    filepaths = (batch_path).glob('*.sur')
    # filepaths = (batch_path).glob('Si_55fs_1.00Jcm2_150Pulses_1.sur')
    
    batch = Batch(filepaths)

    pattern = '<Material|str|>_' \
    '<Pulse_Duration|int||fs>_' \
    '<Fluence|float||Jcm2>_' \
    '<Pulses|int||Pulses>_' \
    '<Measurement|int>'
    batch.extract_from_filename(pattern)
    
    batch.Sa().Sq().Sdr()
    batch.custom_parameter(parameters.calc_mean_height_std)

    result = batch.execute(multiprocessing=False, saveto=batch_path / 'results_mean_height_std.xlsx')
    df = result.get_dataframe()
    print(df)
    input("Press Enter to exit...")
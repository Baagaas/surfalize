from surfalize import Surface, Batch
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
from pathlib import Path
from surfalize.addons_bv.parameters import measure_fft_filtered_morphed_surface_depth
from surfalize.addons_bv.operations import crop_centered
from functools import partial

if __name__ == "__main__":
    data_path = Path.cwd() / 'data'
    crop_folder_name = 'cropped'
    file_name = 'Steel_55fs_1.8Jcm2_005Pulses_1'

    # path = data_path / (file_name + '.plux')
    # s1 = Surface.load(path)    
    # measure_fft_filtered_morphed_surface_depth(s1)
    # input("Press Enter to exit...")
    batch_path = data_path
    filepaths = (batch_path).glob('*.sur')
    # filepaths = (batch_path).glob('Si_55fs_1.00Jcm2_150Pulses_1.sur')
    batch = Batch(filepaths)
    batch.level() # type: ignore[attr-defined]

    crop_centered_part =  partial(crop_centered, crop_width=100, crop_height=0)
    batch.custom_operation(crop_centered_part)

    # batch.crop(box=(250,350,0,100), in_units=True) # type: ignore[attr-defined]

    # batch.remove_outliers()
    batch.fill_nonmeasured(method='nearest') # type: ignore[attr-defined]
    pattern = '<Material|str|>_' \
    '<Pulse_Duration|int||fs>_' \
    '<Fluence|float||Jcm2>_' \
    '<Pulses|int||Pulses>_' \
    '<Measurement|int>'
    batch.extract_from_filename(pattern)
    batch.custom_parameter(measure_fft_filtered_morphed_surface_depth)
    result = batch.execute(multiprocessing=False, saveto=batch_path / 'results_fft_morph_depth.xlsx')
    df = result.get_dataframe()
    print(df)
    input("Press Enter to exit...")
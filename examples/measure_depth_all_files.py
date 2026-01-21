from surfalize import Surface, Batch
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
from pathlib import Path
from surfalize.addons_bv.parameters import measure_fft_filtered_morphed_surface_depth

if __name__ == "__main__":
    data_path = Path.cwd() / 'data'
    crop_folder_name = 'cropped'
    file_name = 'Steel_55fs_1.8Jcm2_005Pulses_1'

    # path = data_path / (file_name + '.plux')
    # s1 = Surface.load(path)    
    # measure_fft_filtered_morphed_surface_depth(s1)
    # input("Press Enter to exit...")
    batch_path = data_path / 'cropped'
    filepaths = (batch_path).glob('*.sur')
    batch = Batch(filepaths)
    batch.level().remove_outliers().fill_nonmeasured(method='nearest').Sa().Sq().Sdr() # type: ignore[attr-defined]
    pattern = '<Material|str|>_' \
    '<Pulse_Duration|int||fs>_' \
    '<Fluence|float||Jcm2>_' \
    '<Pulses|int||Pulses>_' \
    '<Measurement|int>'
    batch.extract_from_filename(pattern)
    batch.custom_parameter(measure_fft_filtered_morphed_surface_depth)
    result = batch.execute(multiprocessing=False, saveto=batch_path / 'results_fft_morph_depth.csv')
    print(result)
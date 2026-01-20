from surfalize import Surface
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
from pathlib import Path
import cropper

data_path = Path.cwd() / 'data'
crop_folder_name = 'cropped'
file_name = 'Steel_55fs_1.8Jcm2_005Pulses_1'

path = data_path / (file_name + '.plux')
s1 = Surface.load(path)    

s1 = cropper.crop_visual(s1)

(data_path / crop_folder_name).mkdir(parents=True, exist_ok=True)
path = data_path / crop_folder_name / f'{file_name}.sur'

s1.save(path, 'sur')
surf_temp = Surface.load(path)

surf_temp.show()
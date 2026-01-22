from surfalize import Surface
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
from pathlib import Path
import surfalize.addons_bv.operations as operations_bv

def crop_and_save_single_file(file_path: Path, cropped_folder_path: Path = None, show_cropped: bool = False) -> None:
    surf = Surface.load(file_path) 
    surf = operations_bv.crop_visual(surf, crop_width=100, show_cropped=show_cropped, title=f"Cropping: {file_path.name}")
    if surf is not None and cropped_folder_path is not None:                    
        # Move the processed file to the cropped folder
        cropped_folder_path.mkdir(parents=True, exist_ok=True)
        cropped_file_path = cropped_folder_path / file_path.with_suffix('.sur').name
        surf.save(cropped_file_path, 'sur')
        print(f"Cropped surface saved to: {cropped_file_path}")

def crop_and_save_all_files(data_path, file_filter='*.plux', cropped_folder_name='cropped', show_cropped=False):
    data_path = Path(data_path)
    cropped_folder_path = data_path / cropped_folder_name
    files = list(data_path.glob(file_filter))

    for file_path in files:
        crop_and_save_single_file(file_path, cropped_folder_path, show_cropped)

if __name__ == "__main__":
    data_path = Path.cwd() / 'data'
    # data_path = Path(r'\\vs-grp04.zih.tu-dresden.de\messda\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files')
    crop_and_save_all_files(data_path=data_path, file_filter='*.plux')
    # crop_and_save_single_file(data_path / 'Steel_55fs_1.8Jcm2_005Pulses_1.plux', data_path / 'cropped')


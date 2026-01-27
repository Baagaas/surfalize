from sklearn.calibration import partial
from surfalize import Surface
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
from pathlib import Path
from surfalize.addons_bv import operation_batch
import surfalize.addons_bv.operations as operations_bv
   
def surf_process_func(file_path: Path, process_func, processed_folder_path: Path | None = None, format= 'sur', save_plot=False) -> None:
    # process_func should be a function that takes a Surface and processes it ()
    surf = Surface.load(file_path)
    if surf is not None:
        if process_func is not None:
            process_func(surf)
        # Move the processed file to the cropped folder
        if processed_folder_path is not None:
            processed_folder_path.mkdir(parents=True, exist_ok=True)
            processed_file_path = processed_folder_path / file_path.with_suffix('.'+format).name
        else:
            processed_file_path = file_path.with_suffix('.'+format)
        
        surf.save(processed_file_path, format=format)
        if save_plot:
            operation_batch.save_surf_fig(surf, processed_file_path)
        print(f"Cropped surface {processed_file_path.name} saved to: {processed_file_path.parent}")
        return surf
    else:
        print(f"No cropping performed for: {file_path.name}")
        return None

def process_surface_files(data_path, process_func, file_filter='*.plux', save_folder_name: str | None ='cropped', format='sur', save_plot=False):
    data_path = Path(data_path)
    if save_folder_name is not None:
        cropped_folder_path = data_path / save_folder_name
    else:
        cropped_folder_path = None
    files = list(data_path.glob(file_filter))

    for file_path in files:
        cropped_surf = surf_process_func(file_path, process_func, cropped_folder_path, format=format, save_plot=save_plot)
        if cropped_surf is None:
            print("Cropping process terminated by user.")
            break

def crop_and_save_single_file(file_path: Path,
                              crop_width=100, crop_height=0, 
                              cropped_folder_path: Path| None = None, 
                              show_cropped: bool = False) -> None:
    surf = Surface.load(file_path) 
    surf = operations_bv.crop_visual(surf, 
                                     crop_width=crop_width, crop_height=crop_height, 
                                     show_cropped=show_cropped, title=f"Cropping: {file_path.name}")
    if surf is not None and cropped_folder_path is not None:                    
        # Move the processed file to the cropped folder
        cropped_folder_path.mkdir(parents=True, exist_ok=True)
        cropped_file_path = cropped_folder_path / file_path.with_suffix('.sur').name
        surf.save(cropped_file_path, 'sur')
        print(f"Cropped surface {cropped_file_path.name} saved to: {cropped_file_path.parent}")
        return surf
    else:
        print(f"No cropping performed for: {file_path.name}")
        return None

def crop_and_save_all_files(data_path, 
                            crop_width=100, crop_height=0, 
                            file_filter='*.plux', cropped_folder_name='cropped', 
                            show_cropped=False):
    data_path = Path(data_path)
    cropped_folder_path = data_path / cropped_folder_name
    files = list(data_path.glob(file_filter))

    for file_path in files:
        cropped_surf = crop_and_save_single_file(file_path, 
                                                 crop_width=crop_width, crop_height=crop_height, 
                                                 cropped_folder_path=cropped_folder_path, 
                                                 show_cropped=show_cropped)
        if cropped_surf is None:
            print("Cropping process terminated by user.")
            break

if __name__ == "__main__":
    data_path = Path.cwd() / 'data'
    #perform visual cropping
    # data_path = Path(r'Y:\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files')
    # crop_and_save_all_files(data_path=data_path, 
    #                         crop_width=600, crop_height=0, 
    #                         file_filter='*1.8*005*.plux', show_cropped=False)
    # crop_and_save_single_file(data_path / 'Steel_55fs_1.8Jcm2_005Pulses_1.plux', data_path / 'cropped')

    # crop centered and save all files and plots
    # crop_centered_part =  partial(operation_batch.crop_centered, crop_width=100, crop_height=0, debug_info=True)
    # process_surface_files(data_path, crop_centered_part, file_filter='*.sur', save_folder_name='cropped_100um', format='sur', save_plot=True)

    # save only plots of surfaces
    data_path = Path.cwd() / 'data' / 'cropped_100um'
    crop_centered_part =  partial(operation_batch.crop_centered, crop_width=100, crop_height=0, debug_info=True)
    process_surface_files(data_path, None, file_filter='*.sur', save_folder_name=None, format='sur', save_plot=True)


from functools import partial
from pathlib import Path
from matplotlib import pyplot as plt
from surfalize import Surface
from surfalize.addons_bv import operation_batch
from tqdm import tqdm
import inspect

# TODO: add tqdm progress bar

def surf_process_func(file_path: Path, process_func, save_processed = False, processed_folder_path: Path | None = None, format= 'sur', save_plot=False, save_func=None) -> None:
    # process_func should be a function that takes a Surface and processes it ()
    surf = Surface.load(file_path)
    if surf is not None:      
        if processed_folder_path is not None:
            processed_folder_path.mkdir(parents=True, exist_ok=True)
            processed_file_path = processed_folder_path / file_path.with_suffix('.'+format).name
        else:
            processed_file_path = file_path.with_suffix('.'+format)
        
        if process_func is not None:
            sig = inspect.signature(process_func)
            if len(sig.parameters) > 1:
                process_func(surf, processed_file_path)
            else:
                process_func(surf)

        if save_processed:
            surf.save(processed_file_path, format=format)

        if save_plot:
            if save_func is not None:
                save_func(surf, processed_file_path)
            else:
                surf.plot_2d(save_to=str(processed_file_path.with_suffix('.png')))
                # print(f"Process surface \"{processed_file_path.name}\" saved to: {processed_file_path.parent}")
                plt.close()
        return surf
    else:
        print(f"surf_process_func: Cannot read the file: {file_path.name}")
        return None

def process_surface_files(data_path, process_func, file_list=[], file_filter='*.plux', save_processed=False, save_folder_name: str | None ='cropped', format='sur', save_plot=False):
    data_path = Path(data_path)
    if save_folder_name is not None:
        processed_folder_path = data_path / save_folder_name
    else:
        processed_folder_path = None
    
    if len(file_list) > 0:
        files = [data_path / f for f in file_list]
    else:
        files = list(data_path.glob(file_filter))

    for file_path in tqdm(files, desc="Processing files"):
        surf_process_func(file_path, process_func, 
                          save_processed=save_processed, processed_folder_path=processed_folder_path, format=format, 
                          save_plot=save_plot)

if __name__ == "__main__":
    data_path = Path.cwd() / 'data'

    # crop centered and save all files and plots
    # crop_centered_part =  partial(operation_batch.crop_centered, crop_width=100, crop_height=0, debug_info=True)
    # process_surface_files(data_path, crop_centered_part, file_filter='*.sur', save_folder_name='cropped_100um', format='sur', save_plot=True)

    # save only plots of surfaces
    # data_path = Path.cwd() / 'data' / 'cropped_100um'
    # data_path = Path(r'Y:\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files')
    # process_surface_files(data_path, None, file_filter='*.plux', save_folder_name=None, format='sur', save_plot=True)

    data_path = Path.cwd() / 'data'
    data_path = Path(r'Y:\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files')
    crop_at_str_center_part = partial(operation_batch.crop_at_str_center, 
                                      str_period_um=5.32, crop_width=600, 
                                      filter_radius=20, orders=3, plot_results=False)
    
    process_surface_files(data_path, crop_at_str_center_part, 
                          file_filter='*.plux', save_processed=True, save_folder_name='cropped_at_str_center_600um', format='sur', save_plot=True)
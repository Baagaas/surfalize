from functools import partial
from pathlib import Path

from matplotlib import pyplot as plt
from surfalize.addons_bv import operation_batch, process_files, parameters, operations, help_fncs
from surfalize import Surface
import pandas as pd

if __name__ == "__main__":
    
    # ===Parameters===
    structure_period = 5.32           
    process_manualy = True
    save_plots = True
    
    # to go through all file in the directory
    data_path = Path(
        r'\\vs-grp04.zih.tu-dresden.de\messda\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files\55fs'
        )
    # file list that has to be processed
    files_init =['Si_55fs_0.50Jcm2_009Pulses_1',
                 'Si_55fs_0.50Jcm2_009Pulses_2',
                 'Si_55fs_0.50Jcm2_009Pulses_3',
                 'Si_55fs_0.50Jcm2_015Pulses_1',
                 'Si_55fs_0.50Jcm2_015Pulses_2',
                 'Si_55fs_0.50Jcm2_015Pulses_3',
                 'Si_55fs_0.50Jcm2_045Pulses_1',
                 'Si_55fs_0.50Jcm2_045Pulses_2',
                 'Si_55fs_0.50Jcm2_045Pulses_3',
                 'Si_55fs_0.50Jcm2_070Pulses_1',
                 'Si_55fs_0.50Jcm2_070Pulses_2',
                 'Si_55fs_0.50Jcm2_070Pulses_3',
                 'Si_55fs_0.50Jcm2_150Pulses_1',
                 'Si_55fs_0.75Jcm2_009Pulses_1',
                 'Si_55fs_0.75Jcm2_009Pulses_2',
                 'Si_55fs_0.75Jcm2_009Pulses_3',
                 'Si_55fs_0.75Jcm2_045Pulses_1',
                 'Si_55fs_0.75Jcm2_045Pulses_2',
                 'Si_55fs_0.75Jcm2_045Pulses_3',
                 'Si_55fs_0.75Jcm2_070Pulses_1',
                 'Si_55fs_0.75Jcm2_070Pulses_2',
                 'Si_55fs_0.75Jcm2_070Pulses_3',
                 'Si_55fs_1.80Jcm2_015Pulses_1',
                 'Si_55fs_1.80Jcm2_015Pulses_2',
                 'Si_55fs_1.80Jcm2_015Pulses_3',]   
    files = [f"{name}.plux" for name in files_init]
    # files = [] # comment this line to process the above file list, if not commented - process all files in the directory above
    
    #===2 find structure center and crop around it===
    save_folder_name='cropped_at_str_center_100um'
    def find_center_and_save_to_file(surf: Surface, processed_file_path: Path, only_manual=False) -> None:        
        x = None
        if only_manual is not True:
            x = parameters.find_str_x_center(surf, str_period_um=5.319, filter_radius=20, orders=7, plot_results=False)
        if x is None:
            x, _ = operations.get_center_pos_visual(surf, title=f"File {processed_file_path.name}")
        
         # Prepare the new row as a DataFrame
        df_new = pd.DataFrame([{"file": processed_file_path.stem, "center x": x}])

        # Define the path to the Excel file
        excel_path = processed_file_path.parent / "center_positions.xlsx"

        if excel_path.exists():
            # If file exists, append without duplicating header
            df_existing = pd.read_excel(excel_path)
            # Remove any existing entry with the same file name
            df_existing = df_existing[df_existing["file"] != processed_file_path.name]
            # Combine and append the new row
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_excel(excel_path, index=False)
        else:
            # If file does not exist, create it
            df_new.to_excel(excel_path, index=False)


        crop_width = 100        
        if save_plots:        
            surf.level(inplace=True)
            surf.remove_outliers(inplace=True)
            fig, ax = surf.plot_2d()
            help_fncs.plot_add_rect_vertical(ax, x_center=x, crop_width=crop_width, crop_ind_color='red', linewidth=1)
            fig.savefig(str(processed_file_path.with_suffix('.png')), dpi=300, bbox_inches='tight')
            plt.close(fig)
    
    find_center_and_save_to_file_partial = partial(find_center_and_save_to_file, only_manual=process_manualy)

    process_files.process_surface_files(data_path, process_func=find_center_and_save_to_file_partial, file_list=files,
                    file_filter='*.plux', save_processed=False, save_folder_name=None, format='sur', save_plot=False)
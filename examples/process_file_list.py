from functools import partial
from pathlib import Path

from matplotlib import pyplot as plt
from surfalize.addons_bv import operation_batch, process_files, parameters, operations, help_fncs
from surfalize import Surface

if __name__ == "__main__":
    # data_path = Path.cwd() / 'data'
    data_path = Path(
        r'Y:\Sensofar\_Projects\Non-Industry\F-014003_ZIM_EffPlus_2nP_TUD\02_Project_Data\Materials\_Final PLUX Files\260fs'
        )
    
    # files=['Si_260fs_0.41Jcm2_005Pulses_1',
    #        'Si_260fs_0.41Jcm2_005Pulses_3',
    #        'Si_260fs_0.75Jcm2_020Pulses_1',
    #        'Si_260fs_1.0Jcm2_015Pulses_1',
    #        'Si_260fs_1.0Jcm2_015Pulses_2',
    #        'Si_260fs_1.0Jcm2_015Pulses_3',
    #        'Si_260fs_1.0Jcm2_020Pulses_1',
    #        'Si_260fs_1.0Jcm2_020Pulses_2',
    #        'Si_260fs_1.0Jcm2_020Pulses_3',
    #        'Si_260fs_1.5Jcm2_009Pulses_1',
    #        'Si_260fs_1.5Jcm2_009Pulses_2',
    #        'Si_260fs_1.5Jcm2_009Pulses_3',
    #        'Si_260fs_1.5Jcm2_015Pulses_1',
    #        'Si_260fs_1.5Jcm2_015Pulses_2',
    #        'Si_260fs_1.5Jcm2_015Pulses_3',
    #        'Si_260fs_1.5Jcm2_020Pulses_1',
    #        'Si_260fs_1.8Jcm2_005Pulses_1',
    #        'Si_260fs_1.8Jcm2_009Pulses_1',
    #        'Si_260fs_1.8Jcm2_009Pulses_2',
    #        'Si_260fs_1.8Jcm2_009Pulses_3',
    #        'Si_260fs_1.8Jcm2_015Pulses_1',
    #        'Si_260fs_1.8Jcm2_015Pulses_2',
    #        'Si_260fs_1.8Jcm2_015Pulses_3',
    #        'Si_260fs_1.8Jcm2_045Pulses_3',
    #        'Si_260fs_1.8Jcm2_070Pulses_1',]
    files_init =['Si_260fs_0.41Jcm2_005Pulses_1']
    
    files = [f"{name}.plux" for name in files_init]
    
    structure_period = 5.32           

    #2 find structure center and crop around it
    print("Step 2: Cropping around structure center")
    save_folder_name='cropped_at_str_center_100um'
    def find_center_and_crop(surf: Surface, processed_file_path: Path) -> None:
        crop_width = 100
        init_surf = Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y, metadata=surf.metadata.copy())
        x = operations.crop_visual(surf, crop_width=crop_width, crop_height=0, 
                                   show_cropped=False, title=f"Cropping")
        surf.level(inplace=True)
        
        init_surf.level(inplace=True)
        init_surf.remove_outliers(inplace=True)
        fig, ax = init_surf.plot_2d()
        help_fncs.plot_add_rect_vertical(ax, x_center=x, crop_width=crop_width, crop_ind_color='red', linewidth=2)
        fig.savefig(str(processed_file_path.with_suffix('.png')), dpi=300, bbox_inches='tight')
        plt.close(fig)
    

    process_files.process_surface_files(data_path, process_func=find_center_and_crop, file_list=files,
                    file_filter='*.plux', save_processed=True, save_folder_name=save_folder_name, format='sur', save_plot=False)
    
    data_path = data_path / save_folder_name
    
    files = [f"{name}.sur" for name in files_init]
    
    #3 apply FFT filtering
    print("Step 3: Applying FFT filtering")
    save_folder_name='fft-filter_P=5.32_filt-r=20_orders=7'
    def make_fft_filtering(surf: Surface) -> None:
        surf.fill_nonmeasured(method='nearest', inplace=True)
        operation_batch.fft_filter_periodic(surf, type='pass', 
                            str_period_um=structure_period, filter_radius=20, orders=7, plot_fft=False)
    
    process_files.process_surface_files(data_path, process_func=make_fft_filtering, file_list=files, file_filter='*.sur',
                                        save_processed=True, save_folder_name=save_folder_name, 
                                        format='sur', save_plot=True)

    data_path = data_path / save_folder_name

    #4 apply morphological filtering
    print("Step 4: Applying morphological filtering")
    save_folder_name='morphed_size_y=1px_x=5.32um'
    
    def make_morph_filter(surf: Surface) -> None:
        operation_batch.filter_morph(surf, structure_size_um=(surf.step_y, structure_period))
    
    process_files.process_surface_files(data_path, process_func=make_morph_filter, file_list=files, file_filter='*.sur',
                                        save_processed=True, save_folder_name=save_folder_name,
                                        format='sur', save_plot=True)
    
    data_path = data_path / save_folder_name
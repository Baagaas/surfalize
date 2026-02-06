from surfalize.addons_bv import operation_batch, help_fncs
from surfalize.surface import Surface
from matplotlib import pyplot as plt
import numpy as np
from scipy import ndimage  # type: ignore

def calc_mean_height_std(surf: Surface) -> dict:
    return {'height_mean': np.mean(surf.data), 'height_std': np.std(surf.data)} 

def calculate_morph_depth(surf: Surface, element_size_um=5.5, crop_edges=True, crop_edge_width_um=None,
                          plot_cross_section=False) -> tuple[float, float, float, float, Surface, Surface, Surface]:

    s_eroded = Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y)
    s_dilated = Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y)
    
    operation_batch.filter_erosion(s_eroded, structure_size_um=(surf.step_y, element_size_um))
    operation_batch.filter_dilation(s_dilated, structure_size_um=(surf.step_y, element_size_um))
    
    if crop_edges:
        if crop_edge_width_um is not None:
            cropped_area_width = crop_edge_width_um
        else:
            cropped_area_width = element_size_um*1.5
        operation_batch.crop_left_right(s_eroded, cropped_area_width)
        operation_batch.crop_left_right(s_dilated, cropped_area_width)
        surf=Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y)
        operation_batch.crop_left_right(surf, cropped_area_width)

    s_diff = Surface(s_dilated.data - s_eroded.data,
                        step_x=surf.step_x, step_y=surf.step_y)
    
    average_value_eroded = np.mean(s_eroded.data)
    average_value_dilated = np.mean(s_dilated.data)
    structure_depth = average_value_dilated - average_value_eroded
    depth_std = np.std(s_diff.data)

    if plot_cross_section:
        Y0 = s_eroded.size[0] // 2  # Middle row; change as needed
        y0_um = Y0 * surf.step_y
        plt.figure(figsize=(10, 4))
        plt.plot(np.arange(surf.size[1]) * surf.step_x, surf.data[Y0, :], label='Original')
        plt.plot(np.arange(s_eroded.size[1]) * s_dilated.step_x, s_dilated.data[Y0, :], label='Dilated')
        plt.plot(np.arange(s_eroded.size[1]) * s_eroded.step_x, s_eroded.data[Y0, :], label='Eroded')
        plt.plot(np.arange(s_eroded.size[1]) * s_diff.step_x, s_diff.data[Y0, :], label='Difference (Dilated - Eroded)')
        plt.title(f'Horizontal Cross-section at y={y0_um:.2f} µm (Y={Y0})')
        plt.xlabel('X [µm]')
        plt.ylabel('Height')
        plt.grid(True)
        plt.legend()
        plt.show(block=False)

    return (structure_depth, depth_std, 
            average_value_eroded, average_value_dilated, 
            s_eroded, s_dilated, s_diff)

def measure_fft_filtered_morphed_surface_depth(surf: Surface,
                                               str_period_um=5, filter_radius=0.02, orders=7, plot_fft=False) -> dict:
    # surf.level(inplace=True)
    # surf.remove_outliers(inplace=True)
    # surf.fill_nonmeasured(inplace=True, method='nearest')
    operation_batch.fft_filter_periodic(surf, type='pass', 
                        str_period_um=str_period_um, filter_radius=filter_radius, orders=orders, plot_fft=plot_fft)


    (depth, depth_std, 
     average_value_eroded, average_value_dilated,
     s_eroded, s_dilated, s_diff) = calculate_morph_depth(surf, element_size_um=str_period_um)

    # surf.show(block=False)
    # plt.title("Original Surface")
    # surf_filtered.show(block=False)
    # plt.title("FFT Filtered Surface")
    # s_diff.show(block=False)
    # plt.title("Difference Surface (Dilated - Eroded)")
    # print(f"Average eroded value: {average_value_eroded}")
    # print(f"Average dilated value: {average_value_dilated}")
    # print(f"Average difference (depth): {depth}")
    # print(f"Depth standard deviation: {depth_std}")
    return {'depth': depth, 'depth_std': depth_std}

def find_str_x_center(surf: Surface, str_period_um, filter_radius=20, orders=3, plot_results=False) -> float|None:
    surf = Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y, metadata=surf.metadata.copy())
    surf.level(inplace=True)
    surf.fill_nonmeasured(inplace=True)
    # operation_batch.fft_filter_periodic(surf, type='pass', str_period_um=str_period_um, filter_radius=filter_radius, orders=orders, plot_fft=False)
    
    if plot_results:
        _, ax = surf.plot_2d()
        ax.set_title('Fourier Filtered Surface for Center Finding')
        plt.show(block=True)

    _, _, _, _, s_eroded, s_dilated, s_diff = calculate_morph_depth(surf, str_period_um, crop_edges=False)
    
    if plot_results:
        _, ax = s_diff.plot_2d()
        ax.set_title('Structure depth Visualization using Morphological Operations')

    peak_position, _, _ = help_fncs.fit_gaussian_peak(s_diff, plot=plot_results)

    return peak_position

if __name__ == "__main__":
    from pathlib import Path
    file_path = Path(r'E:\LocalData\Programming\Python\surfalize\data\Si_55fs_1.80Jcm2_005Pulses_1.plux')
    surf = Surface.load(file_path)
    find_str_x_center(surf, str_period_um=5.319, filter_radius=20, orders=3, plot_results=True)
from surfalize.addons_bv.operations import fft_filter_periodic
from surfalize.surface import Surface
from matplotlib import pyplot as plt
import numpy as np
from scipy import ndimage  # type: ignore


def calculate_morph_depth(surf: Surface, element_size_um=5.5, crop_edges=True, crop_edge_width_um=None,
                          plot_cross_section=False):
    data = surf.data.copy()
    element_size = (1, int(element_size_um / surf.step_x))
    s_eroded = Surface(ndimage.grey_erosion(data, size=element_size),
                        step_x=surf.step_x, step_y=surf.step_y)
    s_dilated = Surface(ndimage.grey_dilation(data, size=element_size),
                        step_x=surf.step_x, step_y=surf.step_y)
    
    if crop_edges:
        if crop_edge_width_um is not None:
            cropped_area_width = crop_edge_width_um
        else:
            cropped_area_width = element_size_um*1.5
        box = (cropped_area_width, surf.width_um-cropped_area_width, 0, surf.height_um)
        s_eroded.crop(box, inplace=True)
        s_dilated.crop(box, inplace=True)
        surf=Surface(surf.data, step_x=surf.step_x, step_y=surf.step_y)
        surf.crop(box, inplace=True)

    average_value_eroded = np.mean(s_eroded.data) # TODO: make as operation
    average_value_dilated = np.mean(s_dilated.data) # TODO: make as operation
    s_diff = Surface(s_dilated.data - s_eroded.data,
                        step_x=surf.step_x, step_y=surf.step_y)
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
                                               str_period_um=1/0.188, filter_radius=0.01, orders=7, plot_fft=False) -> dict:
    # surf.level(inplace=True)
    # surf.remove_outliers(inplace=True)
    # surf.fill_nonmeasured(inplace=True, method='nearest')
    surf_filtered = fft_filter_periodic(surf, type='pass', 
                             str_period_um=str_period_um, filter_radius=filter_radius, orders=orders, plot_fft=plot_fft)


    (depth, depth_std, 
     average_value_eroded, average_value_dilated,
     s_eroded, s_dilated, s_diff) = calculate_morph_depth(surf_filtered, element_size_um=str_period_um)

    # surf.show(block=False)
    # plt.title("Original Surface")
    # surf_filtered.show(block=False)
    # plt.title("FFT Filtered Surface")
    s_diff.show(block=False)
    plt.title("Difference Surface (Dilated - Eroded)")
    # print(f"Average eroded value: {average_value_eroded}")
    # print(f"Average dilated value: {average_value_dilated}")
    # print(f"Average difference (depth): {depth}")
    # print(f"Depth standard deviation: {depth_std}")
    return {'depth': depth, 'depth_std': depth_std}
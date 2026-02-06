import matplotlib.pyplot as plt
from matplotlib.path import Path
import numpy as np
from scipy import ndimage # type: ignore
from surfalize.addons_bv import help_fncs, parameters
from surfalize.surface import Surface
import pandas as pd

def crop_centered(surf: Surface, crop_width=100, crop_height=0, debug_info=False) -> None:   
    x_center = surf.width_um / 2
    y_center = surf.height_um / 2

    if crop_width > 0:
        x0 = x_center - crop_width / 2
        x1 = x_center + crop_width / 2
    else:
        x0 = 0
        x1 = surf.width_um

    if crop_height > 0:
        y0 = y_center - crop_height / 2
        y1 = y_center + crop_height / 2
    else:
        y0 = 0
        y1 = surf.height_um

    # Adjust x0, x1 if out of bounds
        if x0 < 0:
            x0 = 0
            x1 = crop_width
        if x1 > surf.width_um:
            x1 = surf.width_um
            x0 = surf.width_um - crop_width

    # Adjust y0, y1 if out of bounds
        if y0 < 0:
            y0 = 0
            y1 = crop_height
        if y1 > surf.height_um:
            y1 = surf.height_um
            y0 = surf.height_um - crop_height
        
    box = (x0, x1, y0, y1)

    surf.crop(box=box, in_units=True, inplace=True)
    if debug_info:
        print(f"Cropped centered with box: {box} µm")

def crop_at_x_position(surf: Surface, center_x: float, crop_width: float, debug_info=False) -> None:
    crop_height = surf.height_um
    x0 = center_x - crop_width / 2
    x1 = center_x + crop_width / 2

    # Adjust x0, x1 if out of bounds
    if x0 < 0:
        x0 = 0
        x1 = crop_width
    if x1 > surf.width_um:
        x1 = surf.width_um
        x0 = surf.width_um - crop_width

    y0 = 0
    y1 = crop_height

    box = (x0, x1, y0, y1)
    surf.crop(box=box, in_units=True, inplace=True)
    if debug_info:
        print(f"Cropped at position {center_x} µm with box: {box} µm")

def crop_at_str_center(surf, str_period_um, crop_width, filter_radius=20, orders=3, plot_results=False) -> None:
    peak_position = parameters.find_str_x_center(surf, 
        str_period_um=str_period_um, filter_radius=filter_radius, orders=orders, plot_results=plot_results)
    
    crop_at_x_position(surf, center_x=peak_position, crop_width=crop_width, debug_info=plot_results)

def crop_left_right(surf: Surface, crop_width_um: float) -> None:
        box = (crop_width_um, surf.width_um-crop_width_um, 0, surf.height_um)
        surf.crop(box, inplace=True)

def fft_filter_periodic(surf: Surface, type='pass', str_period_um=5.319, filter_radius=20, orders=7, plot_fft=True) -> None:
    # Compute and visualize Fourier space
    data= surf.data.copy()
    rows, cols = surf.size
    fft_data = np.fft.fft2(data)
    fft_shifted = np.fft.fftshift(fft_data)

    # Plot Fourier transform with period units in 1/µm
    freq_x = np.fft.fftshift(np.fft.fftfreq(cols, d=surf.step_x))
    freq_y = np.fft.fftshift(np.fft.fftfreq(rows, d=surf.step_y))

    # Draw a circle on the real part of fft_shifted
    # Using physical units: center at (0, 0) 1/µm with radius 5.0 1/µm
    mask = np.zeros((rows, cols))
    rc=0.05
    for n in range(-orders, orders + 1):
        if n == 0:
            continue
        mask = help_fncs.fill_circle_in_matrix(
            mask, 0, n * 1 / str_period_um, 1 / filter_radius,
            step_x=surf.step_x, step_y=surf.step_y, use_physical_units=True
        )
    
    fft_filtered = np.copy(fft_shifted)
    if type == 'pass':
        fft_filtered[mask == 0] = 0
    elif type == 'stop':
        fft_filtered[mask == 1] = 0

    magnitude_spectrum = np.log1p(np.abs(fft_filtered))

    if plot_fft:
        fig_fft, ax_fft = plt.subplots(figsize=(8, 8))
        extent = (freq_x.min(), freq_x.max(), freq_y.min(), freq_y.max())
        im = ax_fft.imshow(magnitude_spectrum, cmap='gray', extent=extent, origin='lower')
        ax_fft.set_title('Fourier Transform of Surface')
        ax_fft.set_xlabel('Frequency X [1/µm]')
        ax_fft.set_ylabel('Frequency Y [1/µm]')
        plt.colorbar(im, ax=ax_fft, label='Log Magnitude')
        plt.show(block=True)

    # Reconstruct image from the shifted FFT

    reconstructed_data = np.fft.ifft2(np.fft.ifftshift(fft_filtered)).real
    
    surf.data = reconstructed_data

def filter_erosion(surf: Surface, structure_size_um: tuple[float, float]) -> None:
    element_size = (int(structure_size_um[0] / surf.step_x), int(structure_size_um[1] / surf.step_y))
    surf.data = ndimage.grey_erosion(surf.data, size=element_size)
    
def filter_dilation(surf: Surface, structure_size_um: tuple[float, float]) -> None:
    element_size = (int(structure_size_um[0] / surf.step_x), int(structure_size_um[1] / surf.step_y))
    surf.data = ndimage.grey_dilation(surf.data, size=element_size)
    
def filter_morph(surf: Surface, structure_size_um: tuple[float, float]) -> None:
    # TODO optimize by avoiding copying data multiple times
    s_eroded = Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y)
    s_dilated = Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y)
    
    filter_erosion(s_eroded, structure_size_um=structure_size_um)
    filter_dilation(s_dilated, structure_size_um=structure_size_um)
    
    surf.data = s_dilated.data - s_eroded.data
import numpy as np
from scipy import ndimage # type: ignore
from surfalize.addons_bv.help_fncs import fill_circle_in_matrix
from surfalize import Surface
import matplotlib.pyplot as plt
from pathlib import Path

class ClickHandler:
    def __init__(self, ax):
        self.ax = ax
        self.last_click = None  # Stores last clicked position as tuple
        self.esc_pressed =False
    
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        self.last_click = (event.xdata, event.ydata)
        print(f"Last click: {self.last_click}")
        plt.close(self.ax.figure)

    def on_key(self, event):
        if event.key == 'escape':
            print("Escape key pressed!")
            self.esc_pressed = True
            plt.close(self.ax.figure)


def crop_all_files(data_path):
    data_path = Path(data_path)
    crop_folder_name = 'cropped'
    cropped_folder = data_path / crop_folder_name
    cropped_folder.mkdir(parents=True, exist_ok=True)

    files = list(data_path.glob('*.plux'))

    for file_path in files:
        s1 = Surface.load(file_path) 
        s1 = crop_visual(s1)
        if s1 is None:
            break

        # Move the processed file to the cropped folder
        cropped_file_path = cropped_folder / file_path.with_suffix('.sur').name

        s1.save(cropped_file_path, 'sur')
        surf_temp = Surface.load(cropped_file_path)

        surf_temp.show()

def crop_visual(surf: Surface, crop_width=100, save_folder_path=None) -> Surface|None:   
    surf = Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y)
    surf_temp = surf.level().remove_outliers()
    fig, ax = surf_temp.plot_2d()
    handler = ClickHandler(ax)
    fig.canvas.mpl_connect('button_press_event', handler.on_click)
    fig.canvas.mpl_connect('key_press_event', handler.on_key)
    plt.show()

    # Calculate box (x0, x1, y0, y1) centered at last_click with crop_width and max height
    if handler.last_click and not handler.esc_pressed:
        x_center, y_center = handler.last_click
        x0 = x_center - crop_width / 2
        x1 = x_center + crop_width / 2
        y0 = 0
        y1 = surf.height_um
            
        if x0 < 0:
            box = (0, crop_width, y0, y1)
        if x1 > surf.width_um:
            box = (surf.width_um - crop_width, surf.width_um, y0, y1)
        else:
            box = (x0, x1, y0, y1)

        surf.crop(box=box, in_units=True, inplace=True)
        print(f"Cropped with box: {box}")
        if save_folder_path is not None:
            save_folder_path = Path(save_folder_path)

        return surf
    else:
        print("No click position saved or escape pressed")
        return None
    
def fft_filter_periodic(surf: Surface, type='pass', str_period_um=5, filter_radius=0.05, orders=7, plot_fft=True) -> Surface:
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
        mask = fill_circle_in_matrix(
            mask, 0, n * 1 / str_period_um, filter_radius,
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

    # Reconstruct image from the shifted FFT

    reconstructed_data = np.fft.ifft2(np.fft.ifftshift(fft_filtered)).real
    
    return Surface(reconstructed_data, step_x=surf.step_x, step_y=surf.step_y)
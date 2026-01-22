import numpy as np
from scipy import ndimage # type: ignore
from surfalize.addons_bv.help_fncs import fill_circle_in_matrix
from surfalize import Surface
import matplotlib.pyplot as plt

class ClickHandler:
    def __init__(self, ax, crop_width=100, crop_ind_color='red'):
        self.ax = ax
        self.last_click = None  # Stores last clicked position as tuple
        self.esc_pressed =False
        self.rect = None
        self.crop_width = crop_width  # Width of the cropping rectangle in data units
        self.crop_ind_color = crop_ind_color  # Color of the cropping rectangle
    
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        self.last_click = (event.xdata, event.ydata)
       
        # Remove previous rectangle if it exists
        if self.rect is not None:
            self.rect.remove()
        
        # Draw new rectangle centered at mouse position
        x_center, y_center = event.xdata, event.ydata
        print(f"Mouse moved to: ({x_center}, {y_center})")
        x0 = x_center - self.crop_width / 2
        y0 = 0
        height = self.ax.get_ylim()[1] - self.ax.get_ylim()[0]
        
        from matplotlib.patches import Rectangle
        self.rect = Rectangle((x0, y0), self.crop_width, height, 
                             linewidth=2, edgecolor=self.crop_ind_color, facecolor='none', linestyle='--')
        self.ax.add_patch(self.rect)
        self.ax.figure.canvas.draw_idle()

    def on_key_esc(self, event):
        if event.key == 'escape':
            print("Escape key pressed!")
            self.esc_pressed = True
            plt.close(self.ax.figure)

def crop_visual(surf: Surface, crop_width=100, crop_ind_color = 'red', show_cropped=False, title=None) -> Surface|None:   
    surf = Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y, metadata=surf.metadata.copy())
    surf_temp = surf.level().remove_outliers()
    
    # Plot surface for visual cropping
    fig, ax = surf_temp.plot_2d()
    if title is not None:
        fig.suptitle(title, fontsize=14, fontweight='bold')

    handler = ClickHandler(ax, crop_width=crop_width, crop_ind_color=crop_ind_color)
    fig.canvas.mpl_connect('button_press_event', handler.on_click)
    fig.canvas.mpl_connect('key_press_event', handler.on_key_esc)

    #show plot in full screen
    plt.show(block=False)
    plt.pause(0.1)
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.show()

    # Calculate box (x0, x1, y0, y1) centered at last_click with crop_width and max height
    if handler.last_click:
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

        if show_cropped:
            # Visualize cropped file
            fig, ax = surf.plot_2d()
            
            # Add key press event handler to close plot on escape press
            handler = ClickHandler(ax)
            fig.canvas.mpl_connect('key_press_event', handler.on_key_esc)
            
            #show plot in full screen
            plt.show(block=False)
            plt.pause(0.1)
            mng = plt.get_current_fig_manager()
            mng.window.state('zoomed')
            plt.show()

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
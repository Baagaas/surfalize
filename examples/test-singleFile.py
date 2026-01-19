from surfalize import Surface as sur
import matplotlib.pyplot as plt
import copy
from scipy import ndimage
import numpy as np

crop_width = 100

s1 = sur.load('examples/data/Steel_55fs_1.8Jcm2_005Pulses_1.plux')

metadata = s1.metadata
print(metadata)

s1.level(inplace=True)
s1.show()

s1.remove_outliers(inplace=True)
s1.show()


fig, ax = s1.plot_2d()

class ClickHandler:
    def __init__(self, ax):
        self.ax = ax
        self.last_click = None  # Stores last clicked position as tuple
    
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        self.last_click = (event.xdata, event.ydata)
        print(f"Last click: {self.last_click}")

handler = ClickHandler(ax)
fig.canvas.mpl_connect('button_press_event', handler.on_click)
plt.show()

# Calculate box (x0, x1, y0, y1) centered at last_click with crop_width and max height
if handler.last_click:
    x_center, y_center = handler.last_click
    x0 = x_center - crop_width / 2
    x1 = x_center + crop_width / 2
    y0 = 0
    y1 = s1.height_um
    box = (x0, x1, y0, y1)
    s1.crop(box=box, in_units=True, inplace=True)
    print(f"Cropped with box: {box}")
else:
    print("No click position saved")


eroded = ndimage.grey_erosion(s1.data, size=(50, 50))
dilated = ndimage.grey_dilation(s1.data, size=(50, 50))

s1.data = eroded
s1.show()

s1.data = dilated
s1.show()

s1.data = dilated - eroded
s1.show()

average_value = np.mean(s1.data)

print(f"Average height value: {average_value}")


# # Compute and visualize Fourier space
# fft_data = np.fft.fft2(s1.data)
# fft_shifted = np.fft.fftshift(fft_data)
# magnitude_spectrum = np.log1p(np.abs(fft_shifted))

# # Plot Fourier transform with period units in µm
# rows, cols = s1.size
# freq_x = np.fft.fftshift(np.fft.fftfreq(cols, d=s1.step_x))
# freq_y = np.fft.fftshift(np.fft.fftfreq(rows, d=s1.step_y))

# fig_fft, ax_fft = plt.subplots(figsize=(8, 8))
# extent = [freq_x.min(), freq_x.max(), freq_y.min(), freq_y.max()]
# im = ax_fft.imshow(magnitude_spectrum, cmap='gray', extent=extent, origin='lower')
# ax_fft.set_title('Fourier Transform of Surface')
# ax_fft.set_xlabel('Period X [µm]')
# ax_fft.set_ylabel('Period Y [µm]')
# plt.colorbar(im, ax=ax_fft, label='Log Magnitude')
# plt.show()




# print(f"FFT shape: {fft_shifted.shape}")
# print(f"Max magnitude: {np.abs(fft_shifted).max()}")


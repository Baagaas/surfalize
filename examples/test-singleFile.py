from surfalize import Surface as sur
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
from pathlib import Path

data_path = Path.cwd() / 'data'
cop_path = Path.cwd() / 'data'
crop_folder_name = 'cropped'
crop_width = 100
file_name = 'Steel_55fs_1.8Jcm2_005Pulses_1'

path = data_path / (file_name + '.plux')
s1 = sur.load(path)

metadata = s1.metadata
print(metadata)

s1.level(inplace=True)
s1.remove_outliers(inplace=True)

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
        
    if x0 < 0:
        box = (0, crop_width, y0, y1)
    if x1 > s1.width_um:
        box = (s1.width_um - crop_width, s1.width_um, y0, y1)
    else:
        box = (x0, x1, y0, y1)

    s1.crop(box=box, in_units=True, inplace=True)
    print(f"Cropped with box: {box}")
else:
    print("No click position saved")

(data_path / crop_folder_name).mkdir(parents=True, exist_ok=True)
path = data_path / crop_folder_name / f'{file_name}.sur'

s1.save(path, 'sur')
s2 = sur.load(path)

s2.show()

# Calculated depth using morph filtering
# eroded = ndimage.grey_erosion(s1.data, size=(50, 50))
# dilated = ndimage.grey_dilation(s1.data, size=(50, 50))

# s1.data = eroded
# s1.show()

# s1.data = dilated
# s1.show()

# s1.data = dilated - eroded
# s1.show()

# average_value = np.mean(s1.data)

# print(f"Average height value: {average_value}")





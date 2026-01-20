from surfalize import Surface
import matplotlib.pyplot as plt
from scipy import ndimage  # type: ignore
import numpy as np
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

def crop_visual(surf: Surface) -> Surface|None:
    data_path = Path.cwd() / 'data'
    crop_folder_name = 'cropped'
    crop_width = 100
    
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
        return surf
    else:
        print("No click position saved or escape pressed")
        return None
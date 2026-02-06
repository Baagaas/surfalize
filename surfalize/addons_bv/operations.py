from surfalize import Surface
import matplotlib.pyplot as plt

from surfalize.addons_bv import help_fncs

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
        
        x_center, y_center = event.xdata, event.ydata
        print(f"Mouse moved to: ({x_center}, {y_center})")
       
        # Remove previous rectangle if it exists
        if self.rect is not None:
            self.rect.remove()
        
        # Remove previous cross lines if they exist
        lines = [line for line in self.ax.lines]
        for line in lines:
            line.remove()

        self.rect = help_fncs.plot_add_rect_vertical(self.ax, x_center, self.crop_width, crop_ind_color=self.crop_ind_color, linewidth=2)

        # Draw a cross at the center of the rectangle
        min_size = min(self.ax.get_xlim()[1] - self.ax.get_xlim()[0], self.ax.get_ylim()[1] - self.ax.get_ylim()[0])
        cross_size = 0.1 * min_size

        # Horizontal line
        self.ax.plot(
            [x_center - cross_size / 2, x_center + cross_size / 2],
            [y_center, y_center],
            color=self.crop_ind_color, linewidth=1
        )
        # Vertical line
        self.ax.plot(
            [x_center, x_center],
            [y_center - cross_size / 2, y_center + cross_size / 2],
            color=self.crop_ind_color, linewidth=1
        )
        self.ax.figure.canvas.draw_idle()

    def on_key_esc(self, event):
        if event.key == 'escape':
            print("Escape key pressed!")
            self.esc_pressed = True
            plt.close(self.ax.figure)

def get_center_pos_visual(surf: Surface, crop_ind_color = 'red', title=None) -> tuple[float|None, float|None]:   
    # surf = Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y, metadata=surf.metadata.copy())
    surf_temp = surf.level().remove_outliers()
    
    # Plot surface for visual cropping
    fig, ax = surf_temp.plot_2d()
    if title is not None:
        fig.suptitle(title, fontsize=14, fontweight='bold')

    handler = ClickHandler(ax, crop_ind_color=crop_ind_color)
    fig.canvas.mpl_connect('button_press_event', handler.on_click)
    fig.canvas.mpl_connect('key_press_event', handler.on_key_esc)

    #show plot in full screen
    plt.show(block=False)
    plt.pause(0.1)
    mng = plt.get_current_fig_manager()
    try:
        if hasattr(mng, "window"):
            mng.window.state('zoomed')
    except AttributeError:
        print("Full screen mode not supported on this backend.")

    plt.show()

    # Calculate box (x0, x1, y0, y1) centered at last_click with crop_width and max height
    if handler.last_click:
        x_center, y_center = handler.last_click
        return x_center, y_center
    else:
        print("No click position saved or escape pressed")
        return None

def crop_visual(surf: Surface, crop_width=100, crop_height = 0, crop_ind_color = 'red', show_cropped=False, title=None) -> float | None:   
    # surf = Surface(surf.data.copy(), step_x=surf.step_x, step_y=surf.step_y, metadata=surf.metadata.copy())
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
    try:
        if hasattr(mng, "window"):
            mng.window.state('zoomed')
    except AttributeError:
        print("Full screen mode not supported on this backend.")

    plt.show()

    # Calculate box (x0, x1, y0, y1) centered at last_click with crop_width and max height
    if handler.last_click:
        x_center, y_center = handler.last_click
        
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

        surf.level(inplace=True)
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

        return x_center
    else:
        print("No click position saved or escape pressed")
        return None
    

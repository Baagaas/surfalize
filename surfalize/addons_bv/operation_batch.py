from matplotlib.path import Path
from surfalize.surface import Surface


def crop_centered(surf: Surface, crop_width=100, crop_height=0, debug_info=False) -> None:
    surf.level(inplace=True)
    
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

def save_surf_fig(surf: Surface, filepath: Path) -> None:
    surf.plot_2d(save_to=filepath.with_suffix('.png'))
from matplotlib import pyplot as plt
import numpy as np
from scipy.interpolate import griddata  # type: ignore


def _figsize_cm_to_inches(figsize_cm):
    """Convert a (width_cm, height_cm) tuple to matplotlib inches."""
    if figsize_cm is None:
        return None
    if len(figsize_cm) != 2:
        raise ValueError("figsize_cm must be a tuple of (width_cm, height_cm)")
    w_cm, h_cm = float(figsize_cm[0]), float(figsize_cm[1])
    return (w_cm / 2.54, h_cm / 2.54)


def plot_heatmap(
    x,
    y,
    values,
    px_mult=5,
    figsize=(6, 3),
    figsize_cm=None,
    x_label='',
    y_label='',
    title='',
    colorbar_label='',
    font_size_tick=11,
    font_size_label=12,
):
    # original scattered points
    def smallest_distance_1d(x) -> float:
        x = np.asarray(x, dtype=float)
        x = x[np.isfinite(x)]
        x = np.unique(x)  # ignore duplicates when computing spacing
        if x.size < 2:
            return float('nan')

        x.sort()
        return float(np.min(np.diff(x)))

    # create a finer regular grid
    px_mult = 10
    n_x = max(2, int(abs(x.min() - x.max()) / smallest_distance_1d(x)) + 1)
    n_y = max(2, int(abs(y.min() - y.max()) / smallest_distance_1d(y)) + 1)
    
    x_grid = np.linspace(x.min(), x.max(), n_x * px_mult)
    y_grid = np.linspace(y.min(), y.max(), n_y * px_mult)
    P_grid, F_grid = np.meshgrid(x_grid, y_grid)

    # interpolate values onto the fine grid
    points = np.column_stack((x, y))
    Z_grid = griddata(points, values, (P_grid, F_grid), method='nearest') # method= 'nearest' 'linear' 'cubic'

    figsize_in = _figsize_cm_to_inches(figsize_cm) or figsize
    plt.figure(figsize=figsize_in)
    im = plt.imshow(
        Z_grid,
        aspect='auto',
        origin='lower',
        extent=(x_grid.min(), x_grid.max(),
                y_grid.min(), y_grid.max()),
        cmap='viridis',
        interpolation='none',   # visual smoothing on top of numerical interpolation
    )

    # Overlay original datapoints: not filled, black outline
    for x_i, y_i in zip(x, y):
        plt.scatter(
            x_i,
            y_i,
            facecolors='none',
            edgecolors='black',
            s=20,
            linewidths=0.5
        )

    plt.xlabel(x_label, fontsize=font_size_label)
    plt.ylabel(y_label, fontsize=font_size_label)
    plt.title(title, fontsize=font_size_label)
    plt.tick_params(labelsize=font_size_tick)
    cbar = plt.colorbar(im, pad=0.02, shrink=1)
    cbar.set_label(colorbar_label, fontsize=font_size_label)
    cbar.ax.tick_params(labelsize=font_size_tick)

    plt.tight_layout()
    plt.show()

def plot_scatter(
    x: np.ndarray,
    y: np.ndarray,
    x_title: str = '',
    y_title: str = '',
    errors: np.ndarray | None = None,
    plot_legend_labels: list | None = None,
    legend_title: str = '',
    title: str = '',
    fig_size=(5, 5),
    figsize_cm=None,
    font_size_tick=11,
    font_size_label=12,
    show_legend=True
):
    if y.ndim == 2 and plot_legend_labels is not None and y.shape[0] != len(plot_legend_labels):
        raise ValueError("values rows must match length of plot_legend_labels")

    # Plot each row of height_pass in a single scatter plot
    markers = ['o', 's', '^', 'D', 'v', 'P', '*']  # Add more if needed
    figsize_in = _figsize_cm_to_inches(figsize_cm) or fig_size
    fig, ax = plt.subplots(figsize=figsize_in)
    
    if y.ndim == 2:
        for i in range(y.shape[0]):
            marker = markers[i % len(markers)]
            label = plot_legend_labels[i] if plot_legend_labels is not None else f'Row {i}'
            if errors is not None:
                ax.errorbar(x, y[i, :], yerr=errors[i, :], label=label, marker=marker, linestyle='None', capsize=3)
            else:
                ax.scatter(x, y[i, :], label=label, marker=marker)

    ax.set_xlabel(x_title, fontsize=font_size_label)
    ax.set_ylabel(y_title, fontsize=font_size_label)
    ax.tick_params(labelsize=font_size_tick)
    ax.set_title(title, fontsize=font_size_label)    

    if show_legend:
        ax.legend(
            title=legend_title,
            loc='upper left',
            bbox_to_anchor=(1.02, 1.0),
            borderaxespad=0.0,
        fontsize=font_size_tick, title_fontsize=font_size_label
    )

    plt.tight_layout()
    plt.show()
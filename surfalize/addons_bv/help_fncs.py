from matplotlib.patches import Rectangle
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit  # type: ignore

def fill_circle_in_matrix(matrix, c_row, c_column, rc, step_x=1.0, step_y=1.0, use_physical_units=False):
    """
    Fill a circle with ones in the given matrix.
    
    Parameters:
    -----------
    matrix : np.ndarray
        The 2D array to fill
    c_row : float
        Center row coordinate (pixels if use_physical_units=False, 1/µm if True)
    c_column : float
        Center column coordinate (pixels if use_physical_units=False, 1/µm if True)
    rc : float
        Radius (pixels if use_physical_units=False, 1/µm if True)
    step_x : float
        Physical spacing between columns in µm (only used if use_physical_units=True)
    step_y : float
        Physical spacing between rows in µm (only used if use_physical_units=True)
    use_physical_units : bool
        If True, c_row, c_column, and rc are in physical units (1/µm)
    
    Returns:
    --------
    matrix : np.ndarray
        Modified matrix with circle filled
    """
    rows, cols = matrix.shape

    if use_physical_units:
        # Convert physical coordinates to pixel coordinates
        # Physical frequency units are in 1/µm
        # After fftshift, (0, 0) frequency is at the center of the matrix
        
        # Pixel spacing in frequency domain
        freq_step_y = 1.0 / (rows * step_y)  # Frequency resolution in y
        freq_step_x = 1.0 / (cols * step_x)  # Frequency resolution in x
        
        # Convert center coordinates from 1/µm to pixels
        # Add center offset since (0, 0) frequency is at matrix center after fftshift
        c_row_px = rows // 2 + c_row / freq_step_y
        c_column_px = cols // 2 + c_column / freq_step_x
        
        # For non-isotropic spacing, use scaled distance
        # Create a grid of coordinates
        Y, X = np.ogrid[:rows, :cols]
        # Scale distances by frequency resolution to get physical distances
        dist_from_center = np.sqrt(((Y - c_row_px) * freq_step_y)**2 + ((X - c_column_px) * freq_step_x)**2)
        
        # Create mask for the circle in physical units
        circle_mask = dist_from_center <= rc
    else:
        c_row_px = c_row
        c_column_px = c_column
        rc_px = rc
        
        # Create a grid of coordinates
        Y, X = np.ogrid[:rows, :cols]
        dist_from_center = np.sqrt((Y - c_row_px)**2 + (X - c_column_px)**2)
        
        # Create mask for the circle
        circle_mask = dist_from_center <= rc_px

    # Fill the circle area with ones
    matrix[circle_mask] = 1

    return matrix

def fit_gaussian_peak(surface, plot=True) -> tuple[float|None, float|None, np.ndarray|None]:
    """
    Fit a Gaussian to the column-averaged height data of a surface.
    
    Parameters:
    -----------
    surface : surfalize.surface.Surface
        The surface to analyze
    plot : bool
        Whether to plot the data and fit
        
    Returns:
    --------
    peak_position : float
        The position of the peak in µm
    stddev : float
        The standard deviation of the Gaussian in µm
    popt : ndarray
        Optimal parameters [amplitude, mean, stddev, offset]
    """
    rows, cols = surface.size
    data = surface.data.copy()
    row_sum = data.sum(axis=0)
    row_avg = row_sum / rows
    
    # Define Gaussian function
    def gaussian(x, amplitude, mean, stddev, offset):
        return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2)) + offset
    
    # Prepare x data
    x_data = np.arange(cols) * surface.step_y
    
    # Initial guess for parameters
    initial_guess = [
        row_avg.max() - row_avg.min(),  # amplitude
        x_data[np.argmax(row_avg)],      # mean (initial peak position)
        50,                               # stddev
        row_avg.min()                     # offset
    ]
    
    # Fit the Gaussian
    try:
        popt, pcov = curve_fit(gaussian, x_data, row_avg, p0=initial_guess)
        fit_success = True
    except Exception as e:
        fit_success = False
        popt = None
   
    if fit_success:
        # Extract peak position
        peak_position = popt[1]
        stddev = popt[2]
    
        # Plot the data and fit
        if plot:
            plt.figure()
            plt.plot(x_data, row_avg, label='Data')
            plt.plot(x_data, gaussian(x_data, *popt), 'r--', label='Gaussian Fit')
            plt.axvline(peak_position, color='g', linestyle=':', label=f'Peak: {peak_position:.2f} µm')
            plt.xlabel('Position (µm)')
            plt.ylabel('Average Height')
            plt.legend()
            plt.show()
        
        # print(f"Peak position: {peak_position:.2f} µm")
        # print(f"Standard Deviation: {stddev:.2f} µm")
        
        return peak_position, stddev, popt
    else:
        print("Gaussian fit was not successful.")
        return None, None, None

def plot_add_rect_vertical(ax, x_center, crop_width, crop_ind_color='red', linewidth=2) -> Rectangle:
    # Draw new rectangle centered at mouse position
    x0 = x_center - crop_width / 2
    y0 = 0
    height = ax.get_ylim()[1] - ax.get_ylim()[0]
    
    rect = Rectangle((x0, y0), crop_width, height, 
                        linewidth=linewidth, edgecolor=crop_ind_color, facecolor='none', linestyle='--')
    ax.add_patch(rect)
    return rect

if __name__ == "__main__":
    # Parameters
    rows, cols = 200, 200
    c_row, c_column = 50, 100  # Center of the circle
    rc = 10  # Radius of the circle

    matrix = np.zeros((rows, cols))

    matrix = fill_circle_in_matrix(matrix, 100, 50, rc)
    matrix = fill_circle_in_matrix(matrix, 100, 100, rc)
    matrix = fill_circle_in_matrix(matrix, 100, 150, rc)

    # Show the result
    plt.imshow(matrix, cmap='gray')
    plt.title('Matrix with Filled Circle')
    plt.show()
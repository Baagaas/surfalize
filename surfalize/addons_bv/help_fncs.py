import numpy as np
import matplotlib.pyplot as plt


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
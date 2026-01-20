import numpy as np
import matplotlib.pyplot as plt


def fill_circle_in_matrix(matrix, c_row, c_column, rc):
    """
    Fill a circle of radius rc centered at (c_row, c_column) with ones in the given matrix.
    """
    rows, cols = matrix.shape

    # Create a grid of coordinates
    Y, X = np.ogrid[:rows, :cols]
    dist_from_center = np.sqrt((Y - c_row)**2 + (X - c_column)**2)

    # Create mask for the circle
    circle_mask = dist_from_center <= rc

    # Fill the circle area with ones
    matrix[circle_mask] = 1

    return matrix

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